import os
import signal
import subprocess
import sys
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

processes = {}


def start_process(name, script):
    print(f"🚀 تشغيل {name}...")
    return subprocess.Popen(
        [sys.executable, os.path.join(BASE_DIR, script)],
        cwd=BASE_DIR,
    )


def stop_all(*_):
    print("\n🛑 إيقاف BOT SYRIA...")
    for process in processes.values():
        if process.poll() is None:
            process.terminate()

    for process in processes.values():
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()

    sys.exit(0)


signal.signal(signal.SIGINT, stop_all)
signal.signal(signal.SIGTERM, stop_all)

print("================================")
print("       BOT SYRIA SYSTEM")
print("================================")

processes["server"] = start_process("Web Server", "server.py")
time.sleep(2)

processes["bot"] = start_process("Telegram Bot", "bot.py")

print("")
print("✅ BOT SYRIA يعمل")
print("🌐 Web: http://127.0.0.1:8080")
print("🤖 Telegram Bot: يعمل")
print("")

while True:
    for name, process in list(processes.items()):
        if process.poll() is not None:
            print(f"⚠️ {name} توقف — إعادة التشغيل...")
            script = "server.py" if name == "server" else "bot.py"
            processes[name] = start_process(name, script)

    time.sleep(3)
