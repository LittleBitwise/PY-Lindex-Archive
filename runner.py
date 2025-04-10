import subprocess
import sys

while True:
    try:
        print("Starting script...")
        subprocess.run([sys.executable, "archive.py"], check=True)
    except subprocess.CalledProcessError as e:
        print("Script crashed.\nReason:", e.output, "\nstderr:", e.stderr)
