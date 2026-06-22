import sys
import subprocess
import os
from pathlib import Path

if __name__ == "__main__":
    print("🧠 Preparing Sygen environment...")
    
    # Создаём папку для конфига
    config_dir = Path("/app/.sygen")
    config_dir.mkdir(parents=True, exist_ok=True)
    
    # Копируем конфиг, если его нет
    config_file = config_dir / "config.json"
    if not config_file.exists():
        import shutil
        shutil.copy("/app/services/sygen/.sygen/config.json", config_file)
        print("✅ Sygen config copied.")

    # Устанавливаем Gemini CLI локально
    npm_prefix = Path.cwd() / "npm_packages"
    npm_prefix.mkdir(exist_ok=True)
    
    install_result = subprocess.run(
        ["npm", "install", "@google/gemini-cli", "--prefix", str(npm_prefix)],
        capture_output=True, text=True
    )
    
    if install_result.returncode != 0:
        print("❌ Failed to install Gemini CLI.")
        print(install_result.stderr)
        sys.exit(1)
    
    print("✅ Gemini CLI installed locally.")
    
    bin_path = npm_prefix / "node_modules" / ".bin"
    os.environ["PATH"] = f"{bin_path}:{os.environ.get('PATH', '')}"
    
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        os.environ["GEMINI_API_KEY"] = api_key
        print("✅ Gemini API Key configured.")
    
    # Запускаем Sygen с указанием конфига
    print("🧠 Starting Sygen orchestrator...")
    subprocess.run(["sygen", "--config", "/app/.sygen/config.json"])