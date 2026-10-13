"""
Relay Control & Peak-Demand State Machine for Factory Energy Autopilot.

Hardware-independent 3-relay peak demand controller:
  - Channel 1 (Priority 1): Lowest priority / opportunistic load (sheds first)
  - Channel 2 (Priority 2): Medium priority / flexible load (sheds second)
  - Channel 3 (Priority 3): Critical / protected load (sheds last / safety protected)

Safety rules:
  1. Strictly runs in MONITOR_ONLY mode until hardware and safety configuration are verified.
  2. Never invents GPIO pins, relay polarity, or peak-demand thresholds.
  3. Uses hysteresis and anti-surge restart delays to prevent contactor chattering.
"""

import time
import logging
from typing import Dict, Any, Optional, List
from config import TelemetryConfig, config as default_config
from hardware_adapters import BaseRelayAdapter, create_relay_adapter

logger = logging.getLogger("RelayControl")


class RelayState:
    NORMAL = "NORMAL"
    WARNING = "WARNING"
    STAGE_1_SHED = "STAGE_1_SHED"
    STAGE_2_SHED = "STAGE_2_SHED"
    STAGE_3_SHED = "STAGE_3_SHED"
    RESTORING = "RESTORING"


class RelayChannelInfo:
    def __init__(self, channel_id: int, name: str, priority: int):
        self.channel_id = channel_id
        self.name = name
        self.priority = priority
        self.is_shed: bool = False
        self.last_state_change_time: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "channel_id": self.channel_id,
            "name": self.name,
            "priority": self.priority,
            "is_shed": self.is_shed,
            "state": "SHED" if self.is_shed else "OPERATIONAL"
        }


class RelayController:
    """
    Hardware-independent peak-demand state machine managing 3-channel relay shedding.
    Connects to an underlying BaseRelayAdapter for hardware pin operations.
    """

    def __init__(
        self,
        adapter: Optional[BaseRelayAdapter] = None,
        config: Optional[TelemetryConfig] = None,
        monitor_only: Optional[bool] = None
    ):
        self.config = config or default_config
        self.adapter = adapter or create_relay_adapter(self.config)
        
        # Enforce MONITOR_ONLY mode by default unless explicitly configured
        if monitor_only is not None:
            self.monitor_only = monitor_only
        else:
            self.monitor_only = self.config.relay_monitor_only

        # Thresholds (never invent thresholds; if None, controller passively observes)
        self.threshold_kw: Optional[float] = self.config.peak_demand_threshold_kw
        self.warning_ratio: float = self.config.warning_threshold_ratio
        self.hysteresis_kw: float = self.config.restore_hysteresis_kw
        self.min_trip_time_seconds: float = self.config.min_trip_time_seconds
        self.min_restart_delay_seconds: float = self.config.min_restart_delay_seconds

        # 3 Channels
        self.channels: Dict[int, RelayChannelInfo] = {
            1: RelayChannelInfo(1, "Relay 1 (Opportunistic Load)", priority=1),
            2: RelayChannelInfo(2, "Relay 2 (Flexible Load)", priority=2),
            3: RelayChannelInfo(3, "Relay 3 (Protected Load)", priority=3)
        }

        self.current_state: str = RelayState.NORMAL
        self.last_stage_transition_time: float = 0.0
        self.last_restore_action_time: float = 0.0

        # Initialize hardware adapter
        self.adapter.initialize()
        
        mode_str = "MONITOR_ONLY (Simulated, Coils Safe)" if self.monitor_only else "ACTIVE (Hardware Actuation Enabled)"
        logger.info(
            f"[RelayController] Initialized in {mode_str}. "
            f"Peak Threshold: {self.threshold_kw} kW. Hysteresis: {self.hysteresis_kw} kW."
        )

    def evaluate_demand(self, active_power_kw: float, current_time: Optional[float] = None) -> Dict[str, Any]:
        """
        Evaluates current active power against peak demand threshold and advances the state machine.
        Returns a detailed decision report.
        """
        now = current_time if current_time is not None else time.time()
        action_taken = "NONE"

        # If threshold is unconfigured, remain in passive NORMAL state without guessing
        if self.threshold_kw is None or self.threshold_kw <= 0:
            self.current_state = RelayState.NORMAL
            return self._build_report(active_power_kw, action_taken, "Peak threshold unconfigured")

        warning_threshold = self.threshold_kw * self.warning_ratio
        restore_threshold = max(0.0, self.threshold_kw - self.hysteresis_kw)

        # ----------------------------------------------------------------------
        # DEMAND EXCEEDS PEAK THRESHOLD -> EVALUATE SHEDDING
        # ----------------------------------------------------------------------
        if active_power_kw > self.threshold_kw:
            if not self.channels[1].is_shed:
                # Stage 1: Shed Channel 1 (Opportunistic)
                action_taken = self._command_channel(1, shed=True, timestamp=now)
                self.current_state = RelayState.STAGE_1_SHED
                self.last_stage_transition_time = now

            elif (not self.channels[2].is_shed and 
                  (now - self.last_stage_transition_time) >= self.min_trip_time_seconds):
                # Stage 2: Shed Channel 2 (Flexible) after dwell time
                action_taken = self._command_channel(2, shed=True, timestamp=now)
                self.current_state = RelayState.STAGE_2_SHED
                self.last_stage_transition_time = now

            elif (not self.channels[3].is_shed and 
                  (now - self.last_stage_transition_time) >= (self.min_trip_time_seconds * 2)):
                # Stage 3: Extreme emergency peak -> Channel 3 (Protected)
                action_taken = self._command_channel(3, shed=True, timestamp=now)
                self.current_state = RelayState.STAGE_3_SHED
                self.last_stage_transition_time = now

        # ----------------------------------------------------------------------
        # DEMAND IN WARNING BAND
        # ----------------------------------------------------------------------
        elif active_power_kw > warning_threshold:
            # If any relays are currently shed, do NOT restore yet (hysteresis)
            if any(ch.is_shed for ch in self.channels.values()):
                self.current_state = RelayState.WARNING
            else:
                self.current_state = RelayState.WARNING

        # ----------------------------------------------------------------------
        # DEMAND BELOW RESTORATION THRESHOLD -> SEQUENTIAL RESTORE
        # ----------------------------------------------------------------------
        elif active_power_kw <= restore_threshold:
            if any(ch.is_shed for ch in self.channels.values()):
                self.current_state = RelayState.RESTORING

                # Restore highest priority shed load first (Channel 3 -> 2 -> 1)
                # Enforce anti-inrush restart delay between consecutive restorations
                if (now - self.last_restore_action_action_check(now)) >= self.min_restart_delay_seconds:
                    for ch_id in (3, 2, 1):
                        if self.channels[ch_id].is_shed:
                            # Verify min trip time on this specific channel
                            if (now - self.channels[ch_id].last_state_change_time) >= self.min_trip_time_seconds:
                                action_taken = self._command_channel(ch_id, shed=False, timestamp=now)
                                self.last_restore_action_time = now
                                break
            else:
                self.current_state = RelayState.NORMAL

        return self._build_report(active_power_kw, action_taken)

    def _command_channel(self, channel_id: int, shed: bool, timestamp: float) -> str:
        ch = self.channels[channel_id]
        ch.is_shed = shed
        ch.last_state_change_time = timestamp

        action_name = f"{'SHED' if shed else 'RESTORE'}_CH{channel_id}"
        mode_prefix = "[MONITOR_ONLY]" if self.monitor_only else "[ACTIVE]"

        logger.info(
            f"{mode_prefix} {action_name}: {ch.name} -> "
            f"{'SHED (Contact Opened)' if shed else 'RESTORED (Contact Closed)'}."
        )

        # Dispatch command to hardware adapter (which respects monitor_only internally)
        self.adapter.set_relay(channel_id, shed)
        return action_name

    def emergency_restore_all(self) -> None:
        """Safety override: restores all relay channels immediately."""
        now = time.time()
        logger.warning("[RelayController] EMERGENCY RESTORE ALL: Re-engaging all 3 relay channels.")
        for ch_id in (1, 2, 3):
            if self.channels[ch_id].is_shed:
                self._command_channel(ch_id, shed=False, timestamp=now)
        self.current_state = RelayState.NORMAL

    def last_restore_action_action_check(self, now: float) -> float:
        return self.last_restore_action_time if self.last_restore_action_time > 0 else (now - self.min_restart_delay_seconds)

    def _build_report(self, active_power_kw: float, action_taken: str, note: Optional[str] = None) -> Dict[str, Any]:
        return {
            "state": self.current_state,
            "mode": "MONITOR_ONLY" if self.monitor_only else "ACTIVE",
            "active_power_kw": round(active_power_kw, 2),
            "threshold_kw": self.threshold_kw,
            "action_taken": action_taken,
            "warning": self.current_state in (RelayState.WARNING, RelayState.STAGE_1_SHED, RelayState.STAGE_2_SHED, RelayState.STAGE_3_SHED),
            "channels": {ch_id: ch.to_dict() for ch_id, ch in self.channels.items()},
            "note": note
        }

    def get_status(self) -> Dict[str, Any]:
        return {
            "current_state": self.current_state,
            "mode": "MONITOR_ONLY" if self.monitor_only else "ACTIVE",
            "threshold_kw": self.threshold_kw,
            "channels": {ch_id: ch.to_dict() for ch_id, ch in self.channels.items()}
        }

    def cleanup(self) -> None:
        self.adapter.cleanup()
