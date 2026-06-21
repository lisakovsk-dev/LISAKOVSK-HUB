import sys
import subprocess

if __name__ == "__main__":
    print("🧠 Starting Sygen orchestrator...")
    subprocess.run([sys.executable, "-m", "sygen"], check=True)