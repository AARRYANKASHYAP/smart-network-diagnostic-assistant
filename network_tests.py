import subprocess
import platform
import time

def check_internet_connection(host="8.8.8.8"):
    """Checks if there is active internet connectivity by pinging a public DNS host."""
    param = "-n" if platform.system().lower() == "windows" else "-c"
    command = ["ping", param, "1", host]
    
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=3)
        return result.returncode == 0
    except Exception:
        return False

def run_ping_test(host="8.8.8.8", count=4):
    """Runs multiple pings to measure response time and calculate packet loss."""
    param = "-n" if platform.system().lower() == "windows" else "-c"
    command = ["ping", param, str(count), host]
    
    latencies = []
    packet_loss = 100.0
    
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=10)
        output = result.stdout
        
        # Parse output depending on OS
        for line in output.splitlines():
            if "time=" in line:
                # Extract time value (e.g., time=14.2 ms)
                try:
                    parts = line.split("time=")
                    time_val = float(parts[1].split(" ")[0].replace("ms", ""))
                    latencies.append(time_val)
                except ValueError:
                    continue
                    
        # Calculate packet loss and average response time
        if platform.system().lower() == "darwin":  # macOS parsing
            for line in output.splitlines():
                if "packet loss" in line:
                    # Example: "4 packets transmitted, 4 received, 0.0% packet loss"
                    parts = line.split(",")
                    for part in parts:
                        if "packet loss" in part:
                            loss_str = part.strip().split("%")[0]
                            packet_loss = float(loss_str)
        else:
            # Generic fallback or default logic
            received = len(latencies)
            packet_loss = ((count - received) / count) * 100.0

        avg_latency = sum(latencies) / len(latencies) if latencies else 0.0
        return round(avg_latency, 2), round(packet_loss, 2), latencies
        
    except Exception as e:
        print(f"Ping test error: {e}")
        return 0.0, 100.0, []

if __name__ == "__main__":
    print("--- Network Connectivity & Performance Test ---")
    internet_status = check_internet_connection()
    print(f"Internet Available: {internet_status}")
    
    if internet_status:
        avg_time, loss, raw_times = run_ping_test()
        print(f"Average Response Time (Latency): {avg_time} ms")
        print(f"Packet Loss: {loss}%")
        print(f"Raw Ping Latencies: {raw_times}")
    else:
        print("Skipping performance tests because internet connection is unavailable.")