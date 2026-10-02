# Hardware Handover & Scalability

Factory Energy Autopilot is designed as a hardware-agnostic intelligence layer. During development and for the hackathon presentation, it utilizes a deterministic Software Simulator to guarantee demo consistency and mathematically valid AI evaluation.

However, the architecture natively supports real-world PLC/Meter integration via the `EnergyDataSource` abstraction.

## Hardware Data Pipeline

```text
[ Physical Asset ] 
       ↓ 
[ L&T Energy Meter (e.g., WCG-200) ]
       ↓ (Reads current via CT clamps)
[ RS-485 Modbus RTU / TCP ]
       ↓ 
[ Arduino UNO Q / Industrial Gateway ]
       ↓ (Extracts registers, translates to JSON)
[ HTTP POST ]
       ↓
[ Factory Energy Autopilot API Layer ]
       ↓
[ FactoryState ]
```

## `UnoQDataSource` Implementation

To connect real hardware post-hackathon, implement the `UnoQDataSource` subclass of `EnergyDataSource`. 

**Do NOT hardcode meter register addresses in the backend.** 
The UNO Q acts as the edge translator. It should read the Modbus registers (e.g., Active Power, Voltage, PF) and transmit the canonical `EnergyReading` JSON schema to the backend.

### Expected JSON Schema from UNO Q

```json
{
  "timestamp": "2026-10-02T14:32:00Z",
  "factory_id": "fac_01",
  "asset_id": "CMP-001",
  "active_power_kw": 24.5,
  "energy_kwh": 0.1,
  "machine_state": "RUNNING",
  "data_source": "UNO_Q",
  "data_quality": "GOOD"
}
```

The backend AI pipeline (XGBoost Forecaster, Isolation Forest, OR-Tools Optimizer) requires **zero** changes to operate on real hardware data, provided the data conforms to this schema.
