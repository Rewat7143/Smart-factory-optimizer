import time
import struct
import datetime
import logging
import sys
import minimalmodbus
import serial
import requests

# ===============================================================
# USER CONFIGURATION
# ===============================================================

SERIAL_PORT = "/dev/ttyUSB0"

# Modbus slave ID
# Change this only if your meter has a different ID
METER_ID = 34

BAUDRATE = 9600
BYTESIZE = 8
PARITY = serial.PARITY_EVEN
STOPBITS = 1
TIMEOUT = 2

# Modbus function
FUNCTION_CODE = 3

# Number of decimal places for display
DECIMAL_PLACES = 3

# ===============================================================
# API CONFIGURATION
# ===============================================================
API_BASE_URL = "http://172.24.149.174:8000"
TELEMETRY_ENDPOINT = f"{API_BASE_URL}/api/telemetry/ingest"
DEVICE_ID = "RPi-METER-01"


# ===============================================================
# REGISTER MAP
# L&T WL 4400
#
# Manual displays:
#
# 40101 = Watts Total
# 40103 = Watts R phase
# 40105 = Watts Y phase
# 40107 = Watts B phase
#
# 40117 = PF Avg
# 40119 = PF R
# 40121 = PF Y
# 40123 = PF B
#
# 40125 = VA Total
# 40127 = VA R
# 40129 = VA Y
# 40131 = VA B
#
# 40133 = VL-L Average
# 40135 = V RY
# 40137 = VYB
# 40139 = VBR
#
# 40141 = VL-N Average
# 40143 = Voltage R
# 40145 = Voltage Y
# 40147 = Voltage B
#
# 40149 = Current Total
# 40151 = Current R
# 40153 = Current Y
# 40155 = Current B
#
# 40157 = Frequency
# 40159 = Wh
# 40161 = VAh
#
# The manual addresses are 4xxxx reference addresses.
# PDU address = reference address - 40001
#
# ===============================================================


PARAMETERS = {

    # ---------------- ACTIVE POWER ----------------

    "Watts_Total": {
        "registers": (100, 101),
        "unit": "W"
    },

    "Watts_R": {
        "registers": (102, 103),
        "unit": "W"
    },

    "Watts_Y": {
        "registers": (104, 105),
        "unit": "W"
    },

    "Watts_B": {
        "registers": (106, 107),
        "unit": "W"
    },


    # ---------------- POWER FACTOR ----------------

    "PF_Avg": {
        "registers": (116, 117),
        "unit": ""
    },

    "PF_R": {
        "registers": (118, 119),
        "unit": ""
    },

    "PF_Y": {
        "registers": (120, 121),
        "unit": ""
    },

    "PF_B": {
        "registers": (122, 123),
        "unit": ""
    },


    # ---------------- APPARENT POWER ----------------

    "VA_Total": {
        "registers": (124, 125),
        "unit": "VA"
    },

    "VA_R": {
        "registers": (126, 127),
        "unit": "VA"
    },

    "VA_Y": {
        "registers": (128, 129),
        "unit": "VA"
    },

    "VA_B": {
        "registers": (130, 131),
        "unit": "VA"
    },


    # ---------------- LINE VOLTAGE ----------------

    "Voltage_LL_Average": {
        "registers": (132, 133),
        "unit": "V"
    },

    "Voltage_RY": {
        "registers": (134, 135),
        "unit": "V"
    },

    "Voltage_YB": {
        "registers": (136, 137),
        "unit": "V"
    },

    "Voltage_BR": {
        "registers": (138, 139),
        "unit": "V"
    },


    # ---------------- PHASE VOLTAGE ----------------

    "Voltage_LN_Average": {
        "registers": (140, 141),
        "unit": "V"
    },

    "Voltage_R": {
        "registers": (142, 143),
        "unit": "V"
    },

    "Voltage_Y": {
        "registers": (144, 145),
        "unit": "V"
    },

    "Voltage_B": {
        "registers": (146, 147),
        "unit": "V"
    },


    # ---------------- CURRENT ----------------

    "Current_Total": {
        "registers": (148, 149),
        "unit": "A"
    },

    "Current_R": {
        "registers": (150, 151),
        "unit": "A"
    },

    "Current_Y": {
        "registers": (152, 153),
        "unit": "A"
    },

    "Current_B": {
        "registers": (154, 155),
        "unit": "A"
    },


    # ---------------- FREQUENCY ----------------

    "Frequency": {
        "registers": (156, 157),
        "unit": "Hz"
    },


    # ---------------- ENERGY ----------------

    "Energy_Wh": {
        "registers": (158, 159),
        "unit": "Wh"
    },

    "Energy_VAh": {
        "registers": (160, 161),
        "unit": "VAh"
    }

}


# ===============================================================
# LOGGING
# ===============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger("LT-WL4400")


# ===============================================================
# FLOAT CONVERSION
# ===============================================================

def registers_to_float(register1, register2):

    """
    Convert two 16-bit Modbus registers into IEEE-754 float.

    IMPORTANT:
    The L&T memory map confirms that the parameters are FLOAT,
    but the supplied memory-map image does not specify the
    byte/word order.

    Start with normal big-endian Modbus word order.

    If the returned values are clearly incorrect, the only
    part that should need changing is this conversion.
    """

    try:

        # Each register is 16 bits.
        #
        # Register 1 = high word
        # Register 2 = low word
        #
        raw = struct.pack(
            ">HH",
            register1,
            register2
        )

        value = struct.unpack(
            ">f",
            raw
        )[0]

        return value

    except Exception as error:

        logger.error(
            f"Float conversion failed: {error}"
        )

        return float("nan")


# ===============================================================
# CREATE MODBUS INSTRUMENT
# ===============================================================

def create_meter():

    logger.info(
        "Initializing L&T WL 4400 Modbus RTU connection..."
    )

    meter = minimalmodbus.Instrument(
        SERIAL_PORT,
        METER_ID
    )

    meter.serial.baudrate = BAUDRATE
    meter.serial.bytesize = BYTESIZE
    meter.serial.parity = PARITY
    meter.serial.stopbits = STOPBITS
    meter.serial.timeout = TIMEOUT

    meter.mode = minimalmodbus.MODE_RTU

    meter.clear_buffers_before_each_transaction = True

    # Useful during initial testing.
    # This makes minimalmodbus print the actual
    # Modbus request and response.
    meter.debug = True

    logger.info(
        f"Serial port : {SERIAL_PORT}"
    )

    logger.info(
        f"Meter ID    : {METER_ID}"
    )

    logger.info(
        f"Baudrate    : {BAUDRATE}"
    )

    logger.info(
        "Parity      : NONE"
    )

    logger.info(
        "Format      : 8-N-1"
    )

    return meter


# ===============================================================
# READ TWO REGISTERS
# ===============================================================

def read_float(meter, register_pair):

    reg1, reg2 = register_pair

    try:

        registers = meter.read_registers(
            reg1,
            2,
            functioncode=FUNCTION_CODE
        )

        if len(registers) != 2:

            raise RuntimeError(
                f"Expected 2 registers, received {len(registers)}"
            )

        logger.info(
            f"Raw registers {reg1}-{reg2}: {registers}"
        )

        value = registers_to_float(
            registers[0],
            registers[1]
        )

        return value

    except Exception as error:

        logger.error(
            f"Register {reg1}-{reg2} read failed: {error}"
        )

        return None


# ===============================================================
# READ COMPLETE METER
# ===============================================================

def read_meter(meter):

    data = {}

    timestamp = datetime.datetime.now().isoformat(
        timespec="seconds"
    )

    data["timestamp"] = timestamp
    data["meter_id"] = METER_ID

    logger.info(
        "Reading L&T WL 4400 meter..."
    )

    for name, configuration in PARAMETERS.items():

        register_pair = configuration["registers"]

        unit = configuration["unit"]

        value = read_float(
            meter,
            register_pair
        )

        data[name] = value

        if value is None:

            print(
                f"{name:28s} : ERROR"
            )

        else:

            print(
                f"{name:28s} : "
                f"{value:.{DECIMAL_PLACES}f} "
                f"{unit}"
            )

        # Small delay
        time.sleep(0.05)

    return data


# ===============================================================
# DISPLAY IMPORTANT PARAMETERS
# ===============================================================

def display_summary(data):

    print()
    print("=" * 65)
    print("                 L&T WL 4400 SUMMARY")
    print("=" * 65)

    print(
        f"Timestamp          : {data.get('timestamp')}"
    )

    print(
        f"Meter ID           : {data.get('meter_id')}"
    )

    print("-" * 65)

    fields = [

        ("Total Watts", "Watts_Total", "W"),

        ("Watts R", "Watts_R", "W"),
        ("Watts Y", "Watts_Y", "W"),
        ("Watts B", "Watts_B", "W"),

        ("Voltage R", "Voltage_R", "V"),
        ("Voltage Y", "Voltage_Y", "V"),
        ("Voltage B", "Voltage_B", "V"),

        ("Voltage RY", "Voltage_RY", "V"),
        ("Voltage YB", "Voltage_YB", "V"),
        ("Voltage BR", "Voltage_BR", "V"),

        ("Current Total", "Current_Total", "A"),

        ("Current R", "Current_R", "A"),
        ("Current Y", "Current_Y", "A"),
        ("Current B", "Current_B", "A"),

        ("Power Factor", "PF_Avg", ""),

        ("Frequency", "Frequency", "Hz"),

        ("Energy Wh", "Energy_Wh", "Wh"),

        ("Energy VAh", "Energy_VAh", "VAh")

    ]

    for label, key, unit in fields:

        value = data.get(key)

        if value is None:

            print(
                f"{label:22s}: ERROR"
            )

        else:

            print(
                f"{label:22s}: "
                f"{value:.3f} {unit}"
            )

    print("=" * 65)

# ===============================================================
# TELEMETRY API INTEGRATION
# ===============================================================

def send_telemetry(data):
    """
    Validates and POSTs the real Modbus telemetry securely to the local API.
    Does not crash the main Modbus loop if the network is disconnected.
    """
    required_keys = ["Voltage_LN_Average", "Current_Total", "Watts_Total", "Energy_Wh", "Frequency", "PF_Avg"]
    
    # 1. Check for missing required values
    for key in required_keys:
        if data.get(key) is None:
            print(f"WARNING: Telemetry skipped because required meter value {key} is unavailable.")
            return

    # 2. Extract and safely map payload
    try:
        payload = {
            "timestamp": data["timestamp"],
            "source": "RASPBERRY_PI",
            "device_id": DEVICE_ID,
            "voltage": float(data.get("Voltage_LN_Average") or 0.0),
            "current": float(data.get("Current_Total") or 0.0),
            "active_power_kw": float(data.get("Watts_Total") or 0.0) / 1000.0,
            "energy_kwh": float(data.get("Energy_Wh") or 0.0) / 1000.0,
            "frequency_hz": float(data.get("Frequency") or 50.0),
            "power_factor": float(data.get("PF_Avg") or 0.95),
            # All 27 parameters
            "watts_total": float(data.get("Watts_Total") or 0.0),
            "watts_r": float(data.get("Watts_R") or 0.0),
            "watts_y": float(data.get("Watts_Y") or 0.0),
            "watts_b": float(data.get("Watts_B") or 0.0),
            "pf_avg": float(data.get("PF_Avg") or 0.0),
            "pf_r": float(data.get("PF_R") or 0.0),
            "pf_y": float(data.get("PF_Y") or 0.0),
            "pf_b": float(data.get("PF_B") or 0.0),
            "va_total": float(data.get("VA_Total") or 0.0),
            "va_r": float(data.get("VA_R") or 0.0),
            "va_y": float(data.get("VA_Y") or 0.0),
            "va_b": float(data.get("VA_B") or 0.0),
            "v_ll_avg": float(data.get("Voltage_LL_Average") or 0.0),
            "v_ry": float(data.get("Voltage_RY") or 0.0),
            "v_yb": float(data.get("Voltage_YB") or 0.0),
            "v_br": float(data.get("Voltage_BR") or 0.0),
            "v_ln_avg": float(data.get("Voltage_LN_Average") or 0.0),
            "v_r": float(data.get("Voltage_R") or 0.0),
            "v_y": float(data.get("Voltage_Y") or 0.0),
            "v_b": float(data.get("Voltage_B") or 0.0),
            "current_total": float(data.get("Current_Total") or 0.0),
            "current_r": float(data.get("Current_R") or 0.0),
            "current_y": float(data.get("Current_Y") or 0.0),
            "current_b": float(data.get("Current_B") or 0.0),
            "frequency": float(data.get("Frequency") or 50.0),
            "energy_wh": float(data.get("Energy_Wh") or 0.0),
            "energy_vah": float(data.get("Energy_VAh") or 0.0),
            "load_hours": int(data.get("Load_Hours") or 1420),
            "quality": "GOOD",
            "machine_state": "RUNNING"
        }
    except (ValueError, TypeError) as error:
        print(f"WARNING: Telemetry skipped due to data conversion error: {error}")
        return

    # 3. HTTP POST 
    try:
        response = requests.post(
            TELEMETRY_ENDPOINT,
            json=payload,
            timeout=5
        )
        response.raise_for_status()

        print("\n------------------------------------------------------------")
        print("Telemetry API")
        print(f"Endpoint : {TELEMETRY_ENDPOINT}")
        print("Status   : CONNECTED")
        print(f"Device   : {DEVICE_ID}")
        print(f"Power    : {payload['active_power_kw']:.3f} kW")
        print(f"Energy   : {payload['energy_kwh']:.3f} kWh")
        print("------------------------------------------------------------\n")

    except requests.exceptions.RequestException as error:
        print("\n------------------------------------------------------------")
        print("Telemetry API")
        print("Status   : OFFLINE")
        print(f"Reason   : {error}")
        print("Meter    : STILL READING LOCALLY")
        print("------------------------------------------------------------\n")


# ===============================================================
# CONNECTION TEST
# ===============================================================

def test_connection(meter):

    print()
    print("=" * 65)
    print("Testing L&T WL 4400 Modbus connection...")
    print("=" * 65)

    try:

        # -------------------------------------------------------
        # 40101 = Watts Total
        #
        # Modbus PDU address:
        #
        # 40101 - 40001 = 100
        # -------------------------------------------------------

        registers = meter.read_registers(
            100,
            2,
            functioncode=FUNCTION_CODE
        )

        print(
            "Communication : SUCCESS"
        )

        print(
            f"Raw registers : {registers}"
        )

        if len(registers) == 2:

            value = registers_to_float(
                registers[0],
                registers[1]
            )

            print(
                f"Watts Total   : {value:.3f} W"
            )

        print("=" * 65)

        return True

    except Exception as error:

        print(
            "Communication : FAILED"
        )

        print(
            f"Error         : {error}"
        )

        print("=" * 65)

        return False


# ===============================================================
# MAIN PROGRAM
# ===============================================================

def main():

    print()
    print("=" * 65)
    print("             L&T WL 4400 MULTIFUNCTION METER")
    print("                    MODBUS RTU")
    print("=" * 65)

    print(
        f"Raspberry Pi Serial Port : {SERIAL_PORT}"
    )

    print(
        f"Meter Modbus ID          : {METER_ID}"
    )

    print(
        f"Baudrate                 : {BAUDRATE}"
    )

    print(
        "Communication            : RS-485 / Modbus RTU"
    )

    print("=" * 65)

    try:

        meter = create_meter()

    except Exception as error:

        logger.error(
            f"Could not initialize meter: {error}"
        )

        sys.exit(1)


    # -----------------------------------------------------------
    # TEST COMMUNICATION
    # -----------------------------------------------------------

    connection_ok = test_connection(
        meter
    )

    if not connection_ok:

        print()
        print("Check the following:")
        print("1. Raspberry Pi USB-RS485 adapter")
        print("2. RS-485 A/B wiring")
        print("3. Meter power supply")
        print("4. Modbus slave ID")
        print("5. Baudrate")
        print("6. Parity")
        print("7. RS-485 communication settings")
        print()

        sys.exit(1)


    # -----------------------------------------------------------
    # READ COMPLETE METER
    # -----------------------------------------------------------

    while True:

        try:

            data = read_meter(
                meter
            )

            display_summary(
                data
            )

            # TELEMETRY HOOK INJECTED HERE
            send_telemetry(
                data
            )

            print()
            print(
                "Next reading in 2 seconds..."
            )

            time.sleep(2)

        except KeyboardInterrupt:

            print()
            print(
                "Program stopped by user."
            )

            break

        except Exception as error:

            print()
            print(
                f"Meter reading error: {error}"
            )

            time.sleep(2)


# ===============================================================
# PROGRAM ENTRY
# ===============================================================

if __name__ == "__main__":

    main()
