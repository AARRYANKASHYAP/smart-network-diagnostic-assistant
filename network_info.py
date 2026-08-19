import socket
import requests
import subprocess
import platform

def get_local_ip():
    """Gets the local IP address of the machine."""
    try:
        # Create a dummy socket connection to find local active IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return "Unable to get Local IP"

def get_public_ip():
    """Gets the public IP address using an external web service."""
    try:
        response = requests.get("https://api.ipify.org?format=json", timeout=3)
        return response.json().get("ip")
    except Exception:
        return "Unable to get Public IP (No Internet?)"

def get_gateway_and_dns():
    """Extracts Default Gateway and DNS on macOS/Linux."""
    gateway = "Unknown"
    dns = "Unknown"
    
    try:
        # macOS specific route command to find default gateway
        result = subprocess.run(["route", "-n", "get", "default"], capture_output=True, text=True, check=True)
        for line in result.stdout.splitlines():
            if "gateway" in line:
                gateway = line.split(":")[1].strip()
    except Exception:
        gateway = "Not Found"

    try:
        # macOS specific command to check DNS servers from network setup
        result = subprocess.run(["scutil", "--dns"], capture_output=True, text=True, check=True)
        dns_servers = []
        for line in result.stdout.splitlines():
            if "nameserver[" in line:
                server = line.split(":")[-1].strip()
                if server not in dns_servers:
                    dns_servers.append(server)
        if dns_servers:
            dns = ", ".join(dns_servers[:2]) # Take up to first 2 DNS servers
    except Exception:
        dns = "Not Found"

    return gateway, dns

if __name__ == "__main__":
    print("--- Network Information Test ---")
    print(f"Local IP: {get_local_ip()}")
    print(f"Public IP: {get_public_ip()}")
    gw, dns_val = get_gateway_and_dns()
    print(f"Default Gateway: {gw}")
    print(f"DNS Server(s): {dns_val}")