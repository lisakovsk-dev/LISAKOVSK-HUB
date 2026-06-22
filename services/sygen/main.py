import sys
import subprocess
import os

if __name__ == "__main__":
    print("🧠 Preparing Sygen environment...")

    # 1. Устанавливаем Gemini CLI глобально
    print("📦 Installing Gemini CLI...")
    install_result = subprocess.run(["npm", "install", "-g", "@google/gemini-cli"])
    if install_result.returncode != 0:
        print("❌ Failed to install Gemini CLI.")
        sys.exit(1)
    print("✅ Gemini CLI installed.")

    # 2. Настраиваем авторизацию через API-ключ (самый простой способ для сервера)
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        os.environ["GEMINI_API_KEY"] = api_key
        print("✅ Gemini API Key configured.")
    else:
        print("⚠️ GEMINI_API_KEY not found. Please add it to Render environment variables.")

    # 3. Запускаем Sygen
    print("🧠 Starting Sygen orchestrator...")
    subprocess.run(["sygen"])