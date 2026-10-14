#!/usr/bin/env python3
import os
import sys
import paramiko
from scp import SCPClient

PI_HOST = "192.168.0.103"
PI_USER = "smartgrid"
PI_PASS = "smartgrid"
LOCAL_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "raspberry_pi"))
REMOTE_DIR = "/home/smartgrid/factory-energy-autopilot/raspberry_pi"

print(f"Connecting to {PI_USER}@{PI_HOST}...")
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    ssh.connect(PI_HOST, username=PI_USER, password=PI_PASS, timeout=10)
    print("Connected!")

    # 1. Upload updated files
    with SCPClient(ssh.get_transport()) as scp:
        for f in ["config.py", "hardware_adapters.py", "relay_control.py", ".env", "normalizer.py", "api_client.py", "main.py"]:
            local_f = os.path.join(LOCAL_DIR, f)
            if os.path.exists(local_f):
                print(f"Uploading {f}...")
                scp.put(local_f, remote_path=REMOTE_DIR)

    # 2. Clear any old stuck NaN records in sqlite queue
    clean_sql = (
        f"cd {REMOTE_DIR} && sqlite3 telemetry_queue.db "
        "\"UPDATE telemetry_outbox SET application_synced = 1 WHERE payload_json LIKE '%nan%' OR payload_json LIKE '%NaN%';\""
    )
    stdin, stdout, stderr = ssh.exec_command(clean_sql)
    stdout.channel.recv_exit_status()

    # 3. Restart systemd service
    print("Restarting telemetry service on Raspberry Pi...")
    cmd = (
        f"echo '{PI_PASS}' | sudo -S systemctl restart energy-autopilot-telemetry.service && "
        "sleep 4 && "
        "journalctl -u energy-autopilot-telemetry -n 25 --no-pager"
    )
    stdin, stdout, stderr = ssh.exec_command(cmd)
    print("\nLATEST LOGS FROM RASPBERRY PI:")
    print(stdout.read().decode())

except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
finally:
    ssh.close()
