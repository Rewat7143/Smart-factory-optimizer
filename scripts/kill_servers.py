import subprocess
import os
import signal
import re

def kill_port(port):
    try:
        output = subprocess.check_output(f"lsof -t -i:{port}", shell=True, text=True)
        pids = output.strip().split('\n')
        for pid in pids:
            if pid:
                print(f"Killing PID {pid} on port {port}")
                os.kill(int(pid), signal.SIGKILL)
    except Exception as e:
        print(f"Port {port} clear or kill failed: {e}")

kill_port(8000)
kill_port(3005)
