import socket
import requests
import subprocess
import platform
import psutil
import statistics
import json
import re
from datetime import datetime

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return "Offline / None"

def get_public_ip_and_geo():
    try:
        res = requests.get("https://ipapi.co/json/", timeout=3).json()
        return {
            "ip": res.get("ip", "Offline"),
            "city": res.get("city", "Unknown"),
            "country": res.get("country_name", "Unknown"),
            "org": res.get("org", "No ISP Connection")
        }
    except Exception:
        return {
            "ip": "Offline", "city": "Unknown",
            "country": "Unknown", "org": "No ISP Connection"
        }

def get_gateway_and_dns():
    gateway = "Not Found"
    dns = "Not Found"
    try:
        result = subprocess.run(["route", "-n", "get", "default"], capture_output=True, text=True, check=True)
        for line in result.stdout.splitlines():
            if "gateway" in line:
                gateway = line.split(":")[1].strip()
    except Exception:
        gateway = "Unreachable"

    try:
        result = subprocess.run(["scutil", "--dns"], capture_output=True, text=True, check=True)
        dns_servers = []
        for line in result.stdout.splitlines():
            if "nameserver[" in line:
                server = line.split(":")[-1].strip()
                if server not in dns_servers:
                    dns_servers.append(server)
        if dns_servers:
            dns = ", ".join(dns_servers[:2])
    except Exception:
        dns = "Unreachable"

    return gateway, dns

def get_interface_stats():
    try:
        net_io = psutil.net_io_counters()
        bytes_sent_mb = round(net_io.bytes_sent / (1024 * 1024), 2)
        bytes_recv_mb = round(net_io.bytes_recv / (1024 * 1024), 2)
        return f"{bytes_sent_mb} MB Sent / {bytes_recv_mb} MB Recv"
    except Exception:
        return "N/A"

def run_diagnostics(host="8.8.8.8", count=2):
    param = "-n" if platform.system().lower() == "windows" else "-c"
    command = ["ping", param, str(count), "-W", "1000", host] if platform.system().lower() != "darwin" else ["ping", "-c", str(count), "-t", "1", host]
    latencies = []
    packet_loss = 100.0
    internet_available = False
    
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=3)
        output = result.stdout
        if result.returncode == 0:
            internet_available = True
            
        for line in output.splitlines():
            if "time=" in line:
                try:
                    parts = line.split("time=")
                    time_val = float(parts[1].split(" ")[0].replace("ms", ""))
                    latencies.append(time_val)
                except ValueError:
                    continue
                    
        if platform.system().lower() == "darwin":
            for line in output.splitlines():
                if "packet loss" in line:
                    parts = line.split(",")
                    for part in parts:
                        if "packet loss" in part:
                            loss_str = part.strip().split("%")[0]
                            packet_loss = float(loss_str)
        else:
            received = len(latencies)
            packet_loss = ((count - received) / count) * 100.0

        avg_latency = sum(latencies) / len(latencies) if latencies else 0.0
        jitter = round(statistics.stdev(latencies), 2) if len(latencies) > 1 else 0.0
        
        return internet_available, round(avg_latency, 2), round(packet_loss, 2), jitter, latencies
    except Exception:
        return False, 0.0, 100.0, 0.0, []

def scan_security_ports(target_ip):
    """Fast non-blocking port scan of common critical services."""
    common_ports = {
        22: "SSH (Remote Admin)",
        53: "DNS (Name Resolution)",
        80: "HTTP (Web Management)",
        443: "HTTPS (Secure Web)",
        445: "SMB (File Sharing)"
    }
    scan_results = []
    if target_ip in ["Not Found", "Unreachable", "Offline / None"]:
        target_ip = "127.0.0.1"

    for port, service in common_ports.items():
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.3)
        status = "CLOSED"
        try:
            result = s.connect_ex((target_ip, port))
            if result == 0:
                status = "OPEN"
        except Exception:
            status = "FILTERED"
        finally:
            s.close()
        
        scan_results.append({
            "port": port,
            "service": service,
            "status": status
        })
    return scan_results

def run_traceroute(target="8.8.8.8", max_hops=6):
    hops = []
    try:
        cmd = ["traceroute", "-m", str(max_hops), "-q", "1", "-w", "1", target]
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=8)
        for line in res.stdout.splitlines()[1:]:
            parts = line.strip().split()
            if len(parts) >= 2:
                hop_num = parts[0]
                ip_match = re.search(r"\((.*?)\)", line) or re.search(r"(\d+\.\d+\.\d+\.\d+)", line)
                ip = ip_match.group(1) if ip_match else parts[1]
                time_match = re.search(r"(\d+\.?\d*)\s*ms", line)
                rtt = time_match.group(1) + " ms" if time_match else "*"
                hops.append({
                    "hop": hop_num,
                    "host": parts[1] if parts[1] != "*" else "Request Timed Out",
                    "ip": ip if ip != "*" else "N/A",
                    "rtt": rtt
                })
    except Exception:
        hops.append({"hop": "1", "host": "Gateway Local Hop", "ip": "Unreachable", "rtt": "*"})
    return hops

def generate_ai_analysis(internet, avg_lat, loss, jitter, gateway, geo_info, target_host):
    if not internet:
        return {
            "status": "OFFLINE",
            "wave_state": "off",
            "wave_label": "NETWORK OFF / DISCONNECTED",
            "title": f"Target Unreachable: {target_host}",
            "summary": f"Could not establish probe connection with target '{target_host}'. Local link dropped or target is blocking ICMP requests.",
            "recommendations": [
                "Check physical Wi-Fi/Ethernet connection.",
                "Verify if target host exists and allows ICMP echo.",
                "Reconnect to local SSID access point."
            ]
        }
    if loss > 0.0:
        return {
            "status": "BAD",
            "wave_state": "bad",
            "wave_label": "BAD / PACKET DROP DETECTED",
            "title": f"Packet Drop Anomaly ({loss}%)",
            "summary": f"Detected packet loss against '{target_host}'. Wireless RF interference, bufferbloat, or ISP route congestion.",
            "recommendations": [
                "Check for Wi-Fi channel congestion.",
                "Reduce heavy background streaming or upload tasks.",
                "Inspect local access point bufferbloat."
            ]
        }
    if avg_lat > 90.0 or jitter > 25.0:
        return {
            "status": "WEAK",
            "wave_state": "weak",
            "wave_label": "WEAK / HIGH LATENCY & JITTER",
            "title": f"Latency & Jitter Spikes ({avg_lat} ms)",
            "summary": f"High response times towards '{target_host}'. Geographic transit distance or intermediate routing delay.",
            "recommendations": [
                "Move closer to wireless access point.",
                "Check route transit peering with ISP.",
                "Enable router QoS (Quality of Service)."
            ]
        }
    return {
        "status": "GOOD",
        "wave_state": "good",
        "wave_label": "EXCELLENT / OPTIMAL SIGNAL",
        "title": f"Optimal Path to {target_host}",
        "summary": f"Clean link performance towards '{target_host}'. Latency stabilized at {avg_lat} ms with minimal jitter ({jitter} ms) and zero loss.",
        "recommendations": [
            "Network state is fully optimal.",
            f"WAN gateway path to {geo_info.get('org', 'ISP')} is stable.",
            "No manual remediation required."
        ]
    }

def trigger_system_notification(title, message):
    if platform.system().lower() == "darwin":
        clean_msg = message.replace('"', '')
        clean_title = title.replace('"', '')
        script = f'display notification "{clean_msg}" with title "{clean_title}"'
        try:
            subprocess.run(["osascript", "-e", script], check=False)
        except Exception:
            pass