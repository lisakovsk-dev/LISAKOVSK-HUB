import sys
import subprocess
import os
from pathlib import Path

if __name__ == "__main__":
    print("🧠 Preparing Sygen environment...")

    # Устанавливаем Gemini CLI в локальную папку node_modules
    print("📦 Installing Gemini CLI locally...")
    
    # Создаём папку для npm-пакетов
    npm_prefix = Path.cwd() / "npm_packages"
    npm_prefix.mkdir(exist_ok=True)
    
    # Устанавливаем Gemini CLI с указанием префикса
    install_result = subprocess.run(
        ["npm", "install", "@google/gemini-cli", "--prefix", str(npm_prefix)],
        capture_output=True,
        text=True
    )
    
    if install_result.returncode != 0:
        print("❌ Failed to install Gemini CLI.")
        print(install_result.stderr)
        sys.exit(1)
    
    print("✅ Gemini CLI installed locally.")
    
    # Добавляем локальную папку с бинарниками в PATH
    bin_path = npm_prefix / "node_modules" / ".bin"
    os.environ["PATH"] = f"{bin_path}:{os.environ.get('PATH', '')}"
    
    # Проверяем, что gemini доступен
    check_result = subprocess.run(["gemini", "--version"], capture_output=True, text=True)
    if check_result.returncode == 0:
        print(f"✅ Gemini CLI version: {check_result.stdout.strip()}")
    else:
        print("⚠️ Gemini CLI installed but not found in PATH.")

    # Настраиваем авторизацию через API-ключ
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        os.environ["GEMINI_API_KEY"] = api_key
        print("✅ Gemini API Key configured.")
    else:
        print("⚠️ GEMINI_API_KEY not found. Add it to Render environment variables.")

    # Запускаем Sygen
    print("🧠 Starting Sygen orchestrator...")
    subprocess.run(["sygen"])