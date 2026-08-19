import time
import sys
import threading
from diagnostic_engine import get_local_ip, get_public_ip, get_gateway_and_dns, run_diagnostics, evaluate_network_health

# ANSI Color Codes for a beautiful terminal UI
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    CRITICAL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

# Global flag to stop the loading animation
is_loading = True

def animated_loading(text):
    """Creates a smooth terminal loading animation."""
    chars = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    i = 0
    while is_loading:
        sys.stdout.write('\r' + Colors.BLUE + text + " " + chars[i % len(chars)] + Colors.ENDC)
        sys.stdout.flush()
        time.sleep(0.1)
        i += 1
    # Clear the line when done
    sys.stdout.write('\r' + ' ' * (len(text) + 5) + '\r')
    sys.stdout.flush()

def print_header():
    print(Colors.HEADER + Colors.BOLD + "="*55)
    print("      SMART NETWORK DIAGNOSTIC ASSISTANT v1.0")
    print("="*55 + Colors.ENDC)

def run_cli_app():
    global is_loading
    print_header()
    input(Colors.BOLD + "\nPress [ENTER] to start the Smart Network Scan..." + Colors.ENDC)
    print("")
    
    # Start the loading animation in the background
    is_loading = True
    loading_thread = threading.Thread(target=animated_loading, args=("Analyzing network parameters",))
    loading_thread.start()
    
    # --- FETCH DATA (The Engine) ---
    local_ip = get_local_ip()
    public_ip = get_public_ip()
    gateway, dns = get_gateway_and_dns()
    internet, avg_lat, loss = run_diagnostics()
    status, title, suggestion = evaluate_network_health(internet, avg_lat, loss)
    
    # Stop animation and wait for thread to close safely
    is_loading = False
    loading_thread.join()
    
    # --- DISPLAY LOGIC ---
    # Determine Status Color
    if status == "HEALTHY":
        status_color = Colors.GREEN
    elif status == "MODERATE":
        status_color = Colors.WARNING
    else:
        status_color = Colors.CRITICAL

    # Print the Final Report
    print(Colors.BOLD + "[+] NETWORK INFORMATION" + Colors.ENDC)
    print(f" ├─ Local IP Address   : {Colors.BLUE}{local_ip}{Colors.ENDC}")
    print(f" ├─ Public IP Address  : {Colors.BLUE}{public_ip}{Colors.ENDC}")
    print(f" ├─ Default Gateway    : {Colors.BLUE}{gateway}{Colors.ENDC}")
    print(f" └─ DNS Server(s)      : {Colors.BLUE}{dns}{Colors.ENDC}")

    print(Colors.BOLD + "\n[+] PERFORMANCE METRICS" + Colors.ENDC)
    print(f" ├─ Internet Status    : {'Connected' if internet else 'Disconnected'}")
    print(f" ├─ Average Latency    : {avg_lat} ms")
    print(f" └─ Packet Loss        : {loss}%")

    print(Colors.BOLD + "\n[+] SMART DIAGNOSIS" + Colors.ENDC)
    print(f" ├─ Health Status      : {status_color}[{status}] {title}{Colors.ENDC}")
    print(f" └─ Recommendation     : {suggestion}\n")
    
    print(Colors.HEADER + "="*55 + Colors.ENDC)

if __name__ == "__main__":
    try:
        run_cli_app()
    except KeyboardInterrupt:
        is_loading = False
        print(Colors.CRITICAL + "\n\n[!] Scan cancelled by user." + Colors.ENDC)
        sys.exit()