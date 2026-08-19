import sys
import os
import platform

print("=" * 50)
print("     SMART NETWORK ASSISTANT - SYSTEM CHECK")
print("=" * 50)

# 1. Check Python Version
print(f"[-] Python Executable : {sys.executable}")
print(f"[-] Python Version    : {sys.version.split()[0]}")
if sys.version_info < (3, 8):
    print("[!] WARNING: Python version is older than 3.8.")
else:
    print("[OK] Python version is compatible.")

print("-" * 50)

# 2. Check Required Python Packages
required_packages = ["requests", "psutil"]
for pkg in required_packages:
    try:
        __import__(pkg)
        print(f"[OK] Library '{pkg}' is installed and accessible.")
    except ImportError:
        print(f"[!] ERROR: Library '{pkg}' is MISSING! Run: pip install {pkg}")

print("-" * 50)

# 3. Check Tkinter GUI Availability
try:
    import tkinter as tk
    root = tk.Tk()
    root.withdraw()  # Hide test window immediately
    print("[OK] Tkinter GUI module is installed and working.")
except Exception as e:
    print(f"[!] ERROR: Tkinter failed to initialize: {e}")

print("-" * 50)

# 4. Check Project File Connections
required_files = ["diagnostic_engine.py", "app_ui.py"]
for f in required_files:
    if os.path.exists(f):
        print(f"[OK] Project file '{f}' found.")
    else:
        print(f"[!] ERROR: Project file '{f}' is missing from the folder!")

print("=" * 50)
print("System check complete!")