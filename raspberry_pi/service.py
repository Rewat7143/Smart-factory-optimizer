#!/usr/bin/env python3
"""
Factory Energy Autopilot — Telemetry Service Wrapper.
Delegates to main.py's TelemetryService for unified daemon execution.
"""
from main import TelemetryService, main

RaspberryPiTelemetryService = TelemetryService

if __name__ == "__main__":
    main()
