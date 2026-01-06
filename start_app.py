import subprocess
import os
import sys
import threading

def run_backend():
    print("🚀 Starting Backend (FastAPI)...")
    # Using python -m to run from root context
    cmd = [sys.executable, "-m", "uvicorn", "backend.main:app", "--reload", "--port", "8000"]
    subprocess.run(cmd, cwd=os.path.dirname(os.path.abspath(__file__)))

def run_frontend():
    print("🚀 Starting Frontend (React/Vite)...")
    # Using shell=True specifically for npm on Windows to find the executable in path
    cmd = "npm run dev --prefix frontend"
    subprocess.run(cmd, shell=True, cwd=os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    t1 = threading.Thread(target=run_backend)
    t2 = threading.Thread(target=run_frontend)

    t1.start()
    t2.start()

    try:
        t1.join()
        t2.join()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down server...")
        sys.exit(0)
