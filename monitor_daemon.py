import time
import sys
from diagnostic_engine import run_diagnostics, get_gateway_and_dns, trigger_system_notification

def start_daemon(interval_seconds=30):
    print("=" * 60)
    print(" 📡 CONTINUOUS NETWORK TELEMETRY DAEMON STARTED")
    print(f" ⏱️ Interval: Every {interval_seconds} seconds (Press Ctrl+C to stop)")
    print("=" * 60)
    
    last_status = "HEALTHY"
    
    try:
        while True:
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            internet, avg_lat, loss, jitter, _ = run_diagnostics(count=2)
            
            if not internet:
                current_status = "CRITICAL"
                msg = f"Network Disconnected! 100% Packet Loss."
            elif loss > 0.0 or avg_lat > 150.0:
                current_status = "WARNING"
                msg = f"Network Anomaly: Latency {avg_lat}ms, Loss {loss}%"
            else:
                current_status = "HEALTHY"
                msg = f"Link Normal: Latency {avg_lat}ms, Jitter {jitter}ms"
                
            print(f"[{timestamp}] Status: [{current_status}] | {msg}")
            
            # Trigger OS alert on status changes or critical states
            if current_status != last_status or current_status == "CRITICAL":
                trigger_system_notification(
                    f"Network Alert: [{current_status}]",
                    msg
                )
                last_status = current_status
                
            time.sleep(interval_seconds)
            
    except KeyboardInterrupt:
        print("\n\n[!] Monitoring daemon stopped by user.")
        sys.exit()

if __name__ == "__main__":
    start_daemon(interval_seconds=15)