import sys
import subprocess
import os
from pathlib import Path

if __name__ == "__main__":
    print("🧠 Preparing Sygen environment...")
    
    # Убедимся, что конфиг есть
    config_dir = Path.cwd() / ".sygen"
    config_dir.mkdir(parents=True, exist_ok=True)
    
    # Устанавливаем переменную для автоматического согласия
    os.environ["SYGEN_AUTO_ACCEPT"] = "true"
    
    # Запускаем Sygen с флагом неинтерактивного режима
    print("🧠 Starting Sygen orchestrator...")
    subprocess.run([
        "sygen",
        "--config", str(config_dir / "config.json"),
        "--no-input",  # отключаем интерактивный ввод
        "--accept-disclaimer"  # автоматически соглашаемся с условиями
    ])