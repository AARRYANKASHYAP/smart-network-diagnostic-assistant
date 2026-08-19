import sys
import requests
import psutil

def test_environment():
    print("Python version:", sys.version)
    print("Requests library version:", requests.__version__)
    print("Psutil library version:", psutil.__version__)
    print("\nEnvironment setup is successful!")

if __name__ == "__main__":
    test_environment()
