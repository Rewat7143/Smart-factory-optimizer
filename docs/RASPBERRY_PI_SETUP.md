# Raspberry Pi 4B Real Meter Telemetry, Relay Control & Cloud Backup

## L&T WL 4400 Modbus RTU • 3-Relay Peak Demand Controller • FastAPI Backend • Google Sheets Backup

---

### 1. Architecture & Component Abstraction

The edge service is structured around a **hardware-adapter architecture** that separates physical serial and GPIO pin interactions from business logic:

```
                      +-----------------------------+
                      |   L&T WL 4400 Energy Meter   |
                      |   (PCC Main Incomer 415V)   |
                      +--------------+--------------+
                                     | RS-485 Modbus RTU (9600-8-E-1, Slave ID: 34)
                                     v
                      +-----------------------------+
                      |       Raspberry Pi 4B       |
                      |   (/dev/ttyUSB0 or AMA0)    |
                      +--------------+--------------+
                                     |
               +---------------------+---------------------+
               |                                           |
               v                                           v
+-------------------------------+             +-------------------------------+
|     Meter Hardware Adapter     |             |    Relay Hardware Adapter     |
|   (RPi4BModbus / UNO_Q stub)  |             |  (RPi.GPIO / UNO_Q Digital)   |
+--------------+----------------+             +---------------+---------------+
               |                                               |
               v                                               v
+-------------------------------+             +-------------------------------+
|    Telemetry Processing       |             |   3-Relay Peak-Demand FSM     |
|   (Canonical JSON Schema)     |             | (MONITOR_ONLY Safety Default) |
+--------------+----------------+             +---------------+---------------+
               |                                               |
               +-----------------------+-----------------------+
                                       |
                                       v
                         +---------------------------+
                         |   Local Durable Outbox    |
                         |  (SQLite WAL, Zero Loss)  |
                         +-------------+-------------+
                                       |
                        +--------------+--------------+
                        |                             |
                        v                             v
        +-----------------------+     +-------------------------------+
        |  FastAPI App Backend  |     |     Google Sheets Backup      |
        | POST /telemetry/ingest|     |   Spreadsheet: 1_ncPDlzt...   |
        | Live Control & Twin   |     |   Tab: TELEMETRY (12 Columns) |
        +-----------------------+     +-------------------------------+
```

* **Hardware-Specific Adapters** (`hardware_adapters.py`):
  * Meter acquisition: Handles `minimalmodbus`/`serial` byte framing, timeout handling, and floating-point registers.
  * Relay actuation: Handles `RPi.GPIO` pin configuration, active-low/active-high logic, and coil energization.
* **Hardware-Independent Modules**:
  * Telemetry normalization (`normalizer.py`): Normalizes raw registers into canonical schema.
  * API integration (`api_client.py`): HTTP client for FastAPI endpoints.
  * Google Sheets client (`sheets_client.py`): Cloud backup with deduplication.
  * Peak demand controller (`relay_control.py`): Mathematical state machine, priority shedding, dwell timers, and hysteresis.
  * Durable outbox (`queue_manager.py`, `recovery_worker.py`): SQLite WAL storage and outage recovery.

---

### 2. Runtime Interface

The edge software exposes two primary interfaces:

1. **`main.py` — Primary Runtime Entrypoint**:
   * Reads real meter data via hardware adapter.
   * Evaluates the 3-relay peak demand state machine.
   * Ingests telemetry into the existing FastAPI backend (`POST /api/telemetry/ingest`).
   * Backs up to Google Sheets (`TELEMETRY` tab).
   * Persists readings to SQLite outbox (`telemetry_queue.db`) and drains queues automatically.
   * Single command to run:
     ```bash
     python3 main.py
     ```

2. **`relay_control.py` — Peak Demand State Machine**:
   * Manages 3-channel priority shedding:
     * **Channel 1 (Priority 1)**: Lowest priority / opportunistic load (sheds first).
     * **Channel 2 (Priority 2)**: Medium priority / flexible load (sheds second).
     * **Channel 3 (Priority 3)**: Critical / protected load (sheds last, safety protected).
   * **Mandatory Safety Rule**: Runs strictly in `MONITOR_ONLY` mode by default. Physical coils are never actuated until hardware pins, polarity, and operator approval are verified.
   * Does not invent thresholds: if `PEAK_DEMAND_THRESHOLD_KW` is not set in `.env`, it remains in passive monitoring without guessing.

---

### 3. File Manifest: What Must Be Copied to the Raspberry Pi

To deploy on the Raspberry Pi 4B, copy only the `raspberry_pi/` directory and your Google Cloud credentials:

| File Name | Purpose | Required on Pi |
|:---|:---|:---:|
| `main.py` | Unified daemon runtime entrypoint | **YES** |
| `relay_control.py` | 3-relay peak demand state machine | **YES** |
| `hardware_adapters.py` | Hardware-specific Modbus and GPIO adapters | **YES** |
| `config.py` | Centralized configuration loader | **YES** |
| `meter_reader.py` | Modbus RTU reader compatibility interface | **YES** |
| `normalizer.py` | JSON payload and Google Sheets row normalizer | **YES** |
| `queue_manager.py` | Local SQLite durable outbox (WAL mode) | **YES** |
| `api_client.py` | HTTP client for FastAPI backend | **YES** |
| `sheets_client.py` | Google Sheets client with dedup ledger | **YES** |
| `recovery_worker.py` | Chronological queue drainer and backfill worker | **YES** |
| `health_monitor.py` | Terminal status dashboard | **YES** |
| `service.py` | Backward-compatibility wrapper delegating to `main.py` | **YES** |
| `.env` | Environment configuration (created from `.env.example`) | **YES** |
| `service-account.json` | Google Cloud Service Account credentials | **YES** |
| `requirements.txt` | Python dependencies manifest | **YES** |
| `setup_pi.sh` | Automated setup script | Optional (Recommended) |
| `energy-autopilot-telemetry.service` | Systemd service unit file | Optional (For auto-boot) |

---

### 4. Hardware Wiring & Pinout Guide

#### A. L&T WL 4400 RS-485 Terminals
| Terminal Marking | Function | Wiring Target |
|:---|:---|:---|
| **A / D+** | RS-485 Non-inverting (+) | Connect to USB-to-RS485 **A+ / D+** pin |
| **B / D-** | RS-485 Inverting (-) | Connect to USB-to-RS485 **B- / D-** pin |
| **G / COM** | RS-485 Common Ground / Shield | Connect to cable shield & USB adapter GND |
| **L1, L2, L3, N** | 3-Phase Voltage Sensing | Potential Transformers or fused 415V/230V bus |
| **S1, S2 (I1, I2, I3)**| Current Transformers (CT) | 5A / 1A secondary CT outputs with correct polarity |
| **Aux Supply** | 85–265V AC / 100–300V DC | Dedicated control power supply |

#### B. 3-Relay Industrial Module Connections (Raspberry Pi 4B)
* **VCC**: Connect to Raspberry Pi Pin 2 or 4 (5V Power).
* **GND**: Connect to Raspberry Pi Pin 6 or 14 (Ground).
* **IN1, IN2, IN3**: Connect to user-selected BCM GPIO pins (configured in `.env` via `RELAY_1_PIN`, `RELAY_2_PIN`, `RELAY_3_PIN`).
* **Relay Mode**: Set `RELAY_MODE=MONITOR_ONLY` during initial commissioning. Set `RELAY_ACTIVE_LOW=true` for standard optocoupled active-low relay boards.

---

### 5. Step-by-Step Installation & Commands

#### Step 1: Copy Code to Raspberry Pi
```bash
rsync -avz factory-energy-autopilot/raspberry_pi/ pi@<PI_IP>:/home/pi/factory-energy-autopilot/raspberry_pi/
scp path/to/service-account.json pi@<PI_IP>:/home/pi/factory-energy-autopilot/raspberry_pi/service-account.json
```

#### Step 2: Run Setup Script
```bash
cd /home/pi/factory-energy-autopilot/raspberry_pi
chmod +x setup_pi.sh
./setup_pi.sh
```

#### Step 3: Configure Environment (`.env`)
```bash
nano .env
```
Ensure these keys are set:
```ini
SERIAL_PORT=/dev/ttyUSB0
METER_ID=34
ENERGY_API_BASE_URL=http://<YOUR_BACKEND_IP>:8000
GOOGLE_SHEETS_SPREADSHEET_ID=1_ncPDlztJQT71G8hxazyF-EYrEvzwi8h_2BRPLXP5nQ
GOOGLE_SERVICE_ACCOUNT_JSON=service-account.json
HARDWARE_PLATFORM=RPI4B
RELAY_MODE=MONITOR_ONLY
PEAK_DEMAND_THRESHOLD_KW=85.0
```

#### Step 4: The Single Command to Start the Service
To run interactively in the terminal:
```bash
python3 main.py
```

To run as a systemd background service across reboots:
```bash
sudo systemctl start energy-autopilot-telemetry.service
sudo systemctl status energy-autopilot-telemetry.service
```

---

### 6. Tomorrow's Arduino UNO Q Migration Guide

#### A. Architectural Comparison
| Subsystem | Raspberry Pi 4B (Today) | Arduino UNO Q (Tomorrow) | Migration Impact |
|:---|:---|:---|:---|
| **Operating Environment** | Linux Debian / Full Python 3 | Microcontroller / Embedded C++ or MicroPython | Telemetry logic ported or run via host serial bridge |
| **Meter Modbus Interface** | `minimalmodbus` over USB-RS485 (`/dev/ttyUSB0`) | RS-485 Shield on UART (Serial1) via `ArduinoModbus` | Handled by `ArduinoUnoQMeterAdapter` |
| **Relay GPIO Control** | `RPi.GPIO` (BCM Pin Addressing) | `digitalWrite()` on pins D2, D3, D4 | Handled by `ArduinoUnoQRelayAdapter` |
| **HTTP API & Google Sheets** | Native `requests` and `gspread` | Limited RAM; requires WiFi/LTE shield or serial JSON gateway | Best operated as an intelligent edge gateway streaming to host |
| **Local SQLite Queue** | Native SQLite WAL database | No onboard filesystem for SQLite | Outbox stays on host gateway or uses SD card SPI |

#### B. Migration Strategy
1. **Host-Attached Mode (Recommended & Smallest Migration)**:
   * Arduino UNO Q runs lightweight firmware reading L&T Modbus and switching relays.
   * UNO Q connects via USB (`/dev/ttyACM0`) to an edge host (or local gateway).
   * Set `HARDWARE_PLATFORM=UNO_Q` in `.env`.
   * `ArduinoUnoQMeterAdapter` and `ArduinoUnoQRelayAdapter` in `hardware_adapters.py` handle communication with zero changes to the backend, spreadsheet, or queue!
2. **Standalone Embedded Mode**:
   * If UNO Q is standalone, flash C++ firmware with the same register addresses (100–163) and the 3-relay state machine.
   * Send HTTP POST directly to `/api/telemetry/ingest` using the Arduino HTTP client library.

> [!WARNING]
> **No Zero-Change Promise**: True standalone Arduino microcontrollers have restricted RAM (often 2KB to 32KB) which cannot run SQLite WAL or Python's `gspread`. Therefore, standalone mode requires either an embedded C++ translation or a lightweight serial-bridge gateway topology.

---

### 7. Verification Checklist

1. **Hardware Telemetry Test**:
   ```bash
   python3 main.py --check-hardware
   ```
2. **Queue Drain Test**:
   ```bash
   python3 main.py --drain-queue
   ```
3. **Automated Unit Tests**:
   ```bash
   pytest backend/tests/test_rpi_pipeline.py backend/tests/test_relay_and_adapters.py
   ```
