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
        self.control_mode: str = "AUTO"  # "AUTO" or "MANUAL"
        self.last_stage_transition_time: float = 0.0
        self.last_restore_action_time: float = 0.0

        # Initialize hardware adapter
        self.adapter.initialize()
        
        mode_str = "MONITOR_ONLY (Simulated, Coils Safe)" if self.monitor_only else "ACTIVE (Hardware Actuation Enabled)"
        logger.info(
            f"[RelayController] Initialized in {mode_str}. Control Mode: {self.control_mode}. "
            f"Peak Threshold: {self.threshold_kw} kW. Hysteresis: {self.hysteresis_kw} kW."
        )

    def evaluate_demand(
        self,
        active_power_kw: float,
        current_time: Optional[float] = None,
        apparent_power_va: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Evaluates current load against peak demand ceiling and safe operating limit:
        - Priority Shedding Order: Relay 1 OFF 1st -> (delay) -> Relay 2 OFF 2nd -> (delay) -> Relay 3 OFF 3rd
        - Anti-Surge Staggered Restoration: Relay 3 ON 1st -> (delay) -> Relay 2 ON 2nd -> (delay) -> Relay 1 ON 3rd
        """
        now = current_time if current_time is not None else time.time()
        action_taken = "NONE"

        # Determine effective demand (taking the higher of active kW or apparent kVA to protect power ceiling)
        effective_kw = float(active_power_kw or 0.0)
        if apparent_power_va is not None and apparent_power_va > 0.0:
            effective_kw = max(effective_kw, round(apparent_power_va / 1000.0, 4))

        restore_threshold = max(0.0, (self.threshold_kw or 0.0) - self.hysteresis_kw)

        # In MANUAL mode, operator controls relays directly without automated state-machine overrides
        if self.control_mode == "MANUAL":
            return self._build_report(active_power_kw, action_taken="MANUAL_HOLD", effective_demand_kw=effective_kw, restore_threshold=restore_threshold)

        # If threshold is unconfigured, remain in passive NORMAL state without guessing
        if self.threshold_kw is None or self.threshold_kw <= 0:
            self.current_state = RelayState.NORMAL
            return self._build_report(active_power_kw, action_taken, "Peak threshold unconfigured")

        warning_threshold = self.threshold_kw * self.warning_ratio

        # ----------------------------------------------------------------------
        # DEMAND EXCEEDS SAFE OPERATING THRESHOLD -> PRIORITY SHEDDING
        # Priority order: Relay 1 sheds 1st, then Relay 2, then Relay 3
        # ----------------------------------------------------------------------
        if effective_kw > self.threshold_kw:
            if not self.channels[1].is_shed:
                # Stage 1: Turn off Relay 1 (Opportunistic load) FIRST
                action_taken = self._command_channel(1, shed=True, timestamp=now)
                self.current_state = RelayState.STAGE_1_SHED
                self.last_stage_transition_time = now

            elif (not self.channels[2].is_shed and 
                  (now - self.last_stage_transition_time) >= self.min_trip_time_seconds):
                # Stage 2: Turn off Relay 2 (Flexible load) SECOND after dwell delay
                action_taken = self._command_channel(2, shed=True, timestamp=now)
                self.current_state = RelayState.STAGE_2_SHED
                self.last_stage_transition_time = now

            elif (not self.channels[3].is_shed and 
                  (now - self.last_stage_transition_time) >= self.min_trip_time_seconds):
                # Stage 3: Extreme ceiling surge -> Turn off Relay 3 (Protected load) LAST after dwell delay
                action_taken = self._command_channel(3, shed=True, timestamp=now)
                self.current_state = RelayState.STAGE_3_SHED
                self.last_stage_transition_time = now

        # ----------------------------------------------------------------------
        # DEMAND IN WARNING BAND
        # ----------------------------------------------------------------------
        elif effective_kw > warning_threshold:
            # If any relays are currently shed, do NOT restore yet (hysteresis)
            if any(ch.is_shed for ch in self.channels.values()):
                self.current_state = RelayState.WARNING
            else:
                self.current_state = RelayState.WARNING

        # ----------------------------------------------------------------------
        # DEMAND SAFELY BELOW RESTORATION THRESHOLD -> STAGGERED RESTART
        # ----------------------------------------------------------------------
        elif effective_kw <= restore_threshold:
            if any(ch.is_shed for ch in self.channels.values()):
                self.current_state = RelayState.RESTORING

                # Restore highest priority shed load first (Relay 3 -> Relay 2 -> Relay 1)
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

        return self._build_report(active_power_kw, action_taken, effective_demand_kw=effective_kw, restore_threshold=restore_threshold)

    def _command_channel(self, channel_id: int, shed: bool, timestamp: float) -> str:
        ch = self.channels[channel_id]
        ch.is_shed = shed
        ch.last_state_change_time = timestamp

        action_name = f"{'SHED' if shed else 'RESTORE'}_CH{channel_id}"
        mode_prefix = "[MONITOR_ONLY]" if self.monitor_only else "[ACTIVE]"

        logger.info(
            f"{mode_prefix} {action_name}: {ch.name} -> "
            f"{'SHED / OFF (Contact Opened)' if shed else 'RESTORED / ON (Contact Closed)'}."
        )

        # Dispatch command to hardware adapter
        self.adapter.set_relay(channel_id, shed)
        return action_name

    def manual_command(self, channel_id: int, action: str) -> str:
        """Manual operator override for testing and interactive SCADA actuation."""
        now = time.time()
        act_up = (action or "").upper()

        if act_up == "SET_MODE_AUTO":
            self.control_mode = "AUTO"
            logger.info("[RelayController] Switched to AUTONOMOUS ceiling load shedding mode.")
            return "AUTO_ENABLED"
        elif act_up == "SET_MODE_MANUAL":
            self.control_mode = "MANUAL"
            logger.info("[RelayController] Switched to MANUAL SCADA operator override mode.")
            return "MANUAL_ENABLED"
        elif act_up == "SET_POLARITY_ACTIVE_LOW":
            if hasattr(self.adapter, "set_polarity"):
                self.adapter.set_polarity(active_low=True)
            return "POLARITY_ACTIVE_LOW"
        elif act_up == "SET_POLARITY_ACTIVE_HIGH":
            if hasattr(self.adapter, "set_polarity"):
                self.adapter.set_polarity(active_low=False)
            return "POLARITY_ACTIVE_HIGH"
        elif act_up == "TEST_PULSE":
            if hasattr(self.adapter, "test_pulse"):
                self.adapter.test_pulse()
            return "PULSE_TEST_DONE"
        elif act_up == "EMERGENCY_RESTORE_ALL":
            self.control_mode = "MANUAL"
            self.emergency_restore_all()
            return "ALL_RESTORED"
        elif act_up in ("SHED", "OFF"):
            self.control_mode = "MANUAL"
            if channel_id in self.channels:
                act = self._command_channel(channel_id, shed=True, timestamp=now)
                self.last_stage_transition_time = now
                return act
        elif act_up in ("RESTORE", "ON"):
            self.control_mode = "MANUAL"
            if channel_id in self.channels:
                act = self._command_channel(channel_id, shed=False, timestamp=now)
                self.last_restore_action_time = now
                return act
        return "UNKNOWN_ACTION"

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

    def _build_report(
        self,
        active_power_kw: float,
        action_taken: str,
        note: Optional[str] = None,
        effective_demand_kw: Optional[float] = None,
        restore_threshold: Optional[float] = None
    ) -> Dict[str, Any]:
        eff_kw = effective_demand_kw if effective_demand_kw is not None else round(active_power_kw, 3)
        res_kw = restore_threshold if restore_threshold is not None else max(0.0, (self.threshold_kw or 0.0) - self.hysteresis_kw)
        return {
            "state": self.current_state,
            "mode": "MONITOR_ONLY" if self.monitor_only else "ACTIVE",
            "control_mode": self.control_mode,
            "active_low": getattr(self.adapter, "active_low", True),
            "active_power_kw": round(active_power_kw, 3),
            "effective_demand_kw": round(eff_kw, 3),
            "threshold_kw": self.threshold_kw,
            "restore_threshold_kw": round(res_kw, 3),
            "action_taken": action_taken,
            "warning": self.current_state in (RelayState.WARNING, RelayState.STAGE_1_SHED, RelayState.STAGE_2_SHED, RelayState.STAGE_3_SHED),
            "delay_seconds": self.min_trip_time_seconds,
            "restart_delay_seconds": self.min_restart_delay_seconds,
            "priority_order": "Relay 1 (1st) -> Relay 2 (2nd) -> Relay 3 (3rd)",
            "channels": {ch_id: ch.to_dict() for ch_id, ch in self.channels.items()},
            "note": note
        }

    def get_status(self) -> Dict[str, Any]:
        return {
            "current_state": self.current_state,
            "mode": "MONITOR_ONLY" if self.monitor_only else "ACTIVE",
            "threshold_kw": self.threshold_kw,
            "delay_seconds": self.min_trip_time_seconds,
            "restart_delay_seconds": self.min_restart_delay_seconds,
            "channels": {ch_id: ch.to_dict() for ch_id, ch in self.channels.items()}
        }

    def cleanup(self) -> None:
        self.adapter.cleanup()
