import os
import subprocess
import time

if __name__ == "__main__":
    # Проверяем, что конфиг существует (иначе запускаем onboard)
    if not os.path.exists("/root/.nanobot/config.json"):
        print("⚙️ Initializing nanobot config...")
        subprocess.run(["nanobot", "onboard"], check=True)
    
    # Запускаем шлюз
    print("🚀 Starting nanobot gateway...")
    subprocess.run(["nanobot", "gateway"], check=True)