import { useState, useEffect, useRef, useCallback } from 'react';

export type AlertSeverity = 'INFO' | 'WARNING' | 'HIGH' | 'CRITICAL';

export interface AlertState {
  id: string;
  severity: AlertSeverity;
  message: string;
  timestamp: number;
  acknowledged: boolean;
  silencedUntil: number | null;
}

class AudioEngine {
  private ctx: AudioContext | null = null;

  init() {
    if (!this.ctx) {
      this.ctx = new (window.AudioContext || (window as any).webkitAudioContext)();
    }
    if (this.ctx.state === 'suspended') {
      this.ctx.resume();
    }
  }

  playTone(freq: number, type: OscillatorType, duration: number, sweeps: number = 1) {
    if (!this.ctx) return;
    const now = this.ctx.currentTime;
    const osc = this.ctx.createOscillator();
    const gain = this.ctx.createGain();

    osc.type = type;
    osc.connect(gain);
    gain.connect(this.ctx.destination);

    // Envelope
    gain.gain.setValueAtTime(0, now);
    gain.gain.linearRampToValueAtTime(0.3, now + 0.05);
    gain.gain.setValueAtTime(0.3, now + duration - 0.05);
    gain.gain.linearRampToValueAtTime(0, now + duration);

    // Pitch sweep (industrial siren effect)
    if (sweeps > 1) {
        osc.frequency.setValueAtTime(freq, now);
        for(let i = 1; i <= sweeps; i++) {
           const time = now + (duration / sweeps) * i;
           osc.frequency.linearRampToValueAtTime(freq * 1.5, time - (duration/sweeps)*0.5);
           osc.frequency.linearRampToValueAtTime(freq, time);
        }
    } else {
        osc.frequency.setValueAtTime(freq, now);
    }

    osc.start(now);
    osc.stop(now + duration);
  }

  playWarning() {
    this.playTone(440, 'square', 0.3);
  }

  playHigh() {
    this.playTone(600, 'sawtooth', 1.0, 3);
  }

  playCritical() {
    this.playTone(800, 'square', 2.0, 6);
  }
}

export function useAudioAlerts() {
  const [soundEnabled, setSoundEnabled] = useState(false);
  const [activeAlert, setActiveAlert] = useState<AlertState | null>(null);
  const engineRef = useRef<AudioEngine | null>(null);
  const lastPlayedRef = useRef<number>(0);
  const timerRef = useRef<any>(null);

  useEffect(() => {
    engineRef.current = new AudioEngine();
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    }
  }, []);

  const enableSound = useCallback(() => {
    engineRef.current?.init();
    setSoundEnabled(true);
  }, []);

  const testAlarm = useCallback(() => {
    engineRef.current?.init();
    engineRef.current?.playWarning();
  }, []);

  const acknowledge = useCallback(() => {
    if (activeAlert) setActiveAlert({ ...activeAlert, acknowledged: true, silencedUntil: null });
  }, [activeAlert]);

  const silence = useCallback((seconds: number) => {
    if (activeAlert) setActiveAlert({ ...activeAlert, silencedUntil: Date.now() + seconds * 1000 });
  }, [activeAlert]);

  const clearAlert = useCallback(() => {
    setActiveAlert(null);
  }, []);

  // Update alert state from outside
  const updateAlertCondition = useCallback((condition: 'NORMAL' | 'WARNING' | 'HIGH' | 'CRITICAL', message: string, id: string) => {
    if (condition === 'NORMAL') {
      if (activeAlert?.id === id) setActiveAlert(null);
      return;
    }

    setActiveAlert(prev => {
      // If same ID and same severity, keep existing state (ack/silence)
      if (prev && prev.id === id && prev.severity === condition) {
         return prev;
      }
      return {
        id,
        severity: condition,
        message,
        timestamp: Date.now(),
        acknowledged: false,
        silencedUntil: null
      };
    });
  }, [activeAlert]);

  // Alert loop
  useEffect(() => {
    if (timerRef.current) clearInterval(timerRef.current);

    timerRef.current = setInterval(() => {
      if (!soundEnabled || !activeAlert || !engineRef.current) return;
      if (activeAlert.acknowledged) return;
      if (activeAlert.silencedUntil && Date.now() < activeAlert.silencedUntil) return;

      const now = Date.now();
      // Repeat interval: HIGH = 5s, CRITICAL = 2s, WARNING = once (or 10s)
      let repeatInterval = 10000;
      if (activeAlert.severity === 'CRITICAL') repeatInterval = 2000;
      else if (activeAlert.severity === 'HIGH') repeatInterval = 5000;

      if (now - lastPlayedRef.current >= repeatInterval) {
        lastPlayedRef.current = now;
        if (activeAlert.severity === 'WARNING') engineRef.current.playWarning();
        else if (activeAlert.severity === 'HIGH') engineRef.current.playHigh();
        else if (activeAlert.severity === 'CRITICAL') engineRef.current.playCritical();
      }
    }, 1000);

    return () => clearInterval(timerRef.current);
  }, [soundEnabled, activeAlert]);

  return {
    soundEnabled,
    enableSound,
    setSoundEnabled,
    testAlarm,
    activeAlert,
    acknowledge,
    silence,
    clearAlert,
    updateAlertCondition
  };
}
