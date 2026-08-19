# 🌐 Smart Network Diagnostic Assistant & AIOps Telemetry Suite

[![Python Version](https://img.shields.io/badge/python-3.9%20%7C%203.10%20%7C%203.11%20%7C%203.12-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-macOS%20%7C%20Linux%20%7C%20Windows-lightgrey.svg)]()
[![Visualizations](https://img.shields.io/badge/visualizations-Chart.js-FF6384?style=flat&logo=chartdotjs&logoColor=white)](https://www.chartjs.org/)

An autonomous, real-time network telemetry suite, gateway security auditor, and AIOps diagnostic engine written in Python. 

The application decouples low-level socket, routing, and kernel inspection from the presentation layer, delivering a live **Split-Screen Cyberpunk Telemetry Web Dashboard** featuring rolling ICMP time-series graphs, multi-hop traceroute path discovery, local port audits, target switching, and native desktop notifications.

---

## 📸 Interface & Layout Architecture

The web dashboard is organized in a responsive **Split-Screen Horizontal Layout**:
* **Left Panel:** Real-time Animated Link Signal Waveform, AIOps Diagnostic Analysis with automated recommendations, Gateway & IP Interface discovery, and Gateway Security Port Scanner.
* **Right Panel:** Live Telemetry Metrics Matrix (RTT, Jitter, Packet Loss, ISP Peering), Rolling 15s–1min RTT Latency Stream, Metric Distribution Bar Chart, and Multi-Hop Traceroute Edge Path.

---

## ⚡ Core Feature Matrix

### 1. 🔍 Routing & Interface Discovery
- **Dynamic Interface Discovery:** Uses non-transmitting UDP routing sockets (`socket.getsockname()`) targeted toward external IP endpoints to dynamically discover the active local IP interface without hardcoded adapter names.
- **Kernel Routing Table Hooks:** Extracts default gateway and DNS resolvers via macOS `route -n get default` and `scutil --dns` subprocess utilities.
- **Public WAN & ISP Geolocation:** Queries external peering APIs to identify WAN IPv4 address, City, Country, and ISP/ASN organization details.
- **Cumulative Hardware Traffic:** Tracks real-time system interface I/O metrics (Total Megabytes Sent / Received via `psutil`).

### 2. 📊 Precision Telemetry & Statistical Jitter
- **ICMP RTT Latency Probing:** Real-time round-trip latency measurements with sub-millisecond precision.
- **Jitter Variance Calculation:** Computes sample standard deviation ($\sigma$) across probe windows to detect jitter spikes that cause bufferbloat or real-time streaming/gaming stutter:
  $$\text{Jitter} = \sqrt{\frac{1}{N-1} \sum_{i=1}^{N} (x_i - \bar{x})^2}$$
- **Rolling Latency Chart:** Continuous Chart.js line graph displaying the rolling past 15 seconds to 1 minute of telemetry updates.
- **Metric Distribution Matrix:** Side-by-side bar chart benchmarking average latency, jitter variance, and packet loss percentages.

### 3. 🤖 AIOps Diagnostic & Root-Cause Engine
- Correlates latency variance, drop rates, and routing parameters in real-time.
- Classifies network health into discrete operational states:
  - 🟢 **OPTIMAL / EXCELLENT:** Sub-50ms latency, 0% loss, minimal jitter.
  - 🟡 **WEAK / CONGESTED:** Latency > 90ms or Jitter > 25ms (Bufferbloat / Wi-Fi channel overlap).
  - 🔴 **BAD / PACKET DROP:** Intermediate hop congestion or dropped packets.
  - ⚫ **OFFLINE:** Complete transport disconnection / Gateway unreachable.

### 4. 🛡️ Security Audit & Multi-Hop Traceroute
- **Gateway Port Audit:** Fast asynchronous non-blocking TCP socket scanning on critical management ports:
  - `Port 22` (SSH - Remote Administration)
  - `Port 53` (DNS - Name Resolution)
  - `Port 80` (HTTP - Web Gateway Interface)
  - `Port 443` (HTTPS - Secure Web Interface)
  - `Port 445` (SMB - Local File Sharing)
- **Multi-Hop Traceroute Topology:** Traces the packet route across edge transit routers, displaying intermediate hop hostnames, IP addresses, and hop RTTs.

### 5. 🎛️ Interactive Controls & Data Persistence
- **On-Demand Target Switcher:** Dynamically change probe targets (`8.8.8.8`, `1.1.1.1`, `github.com`, custom LAN IPs) directly from the web navbar without restarting Python.
- **Native OS Desktop Notifications:** Automatically pushes macOS notification alerts via AppleScript (`osascript`) upon network status transitions or connection drops.
- **Exporting Options:** - **1-Click PDF Export:** Clean CSS `@media print` styling for generating academic and diagnostic PDF reports.
  - **1-Click JSON Export:** Downloads rolling time-series logs (`network_telemetry_report.json`) for data analysis.

---

## 🛠️ Architecture & Data Flow
[Target Switcher]
                                     │
                                     ▼
+---------------------------------------------------------------------------------+
|                                 web_app.py                                      |
|    • Multi-Threaded Daemon (3s fast telemetry loop)                             |
|    • Asynchronous Security Worker (15s Traceroute & Port Scan loop)             |
|    • Local Embedded HTTP Server (http://127.0.0.1:8080)                         |
+----------------------------------------+----------------------------------------+
│
▼
+---------------------------------------------------------------------------------+
|                           diagnostic_engine.py                                  |
|  • socket (UDP dummy routing, TCP handshake scans)                              |
|  • subprocess (ICMP ping, kernel route tables, scutil, traceroute, osascript)   |
|  • psutil (Adapter cumulative throughput)                                       |
|  • requests (Public IP & ISP Geolocation API)                                   |
|  • statistics (Jitter calculation)                                              |
|  • AIOps Decision Matrix (Rule-based state evaluation)                          |
+----------------------------------------+----------------------------------------+
│
▼
+---------------------------------------------------------------------------------+
|                       Responsive Split-Screen UI                                |
|  • Left Panel: Signal Wave, AIOps Engine, IP Routing, Port Security Table       |
|  • Right Panel: Live Metrics Grid, Rolling Chart.js Stream, Traceroute Hop Path |
+---------------------------------------------------------------------------------+


---

## 🚀 Getting Started

### 1. Prerequisites
- **Python 3.9+** installed on macOS, Linux, or Windows.

### 2. Installation
Clone the repository and install required third-party dependencies:

```bash
# Clone the repository
git clone [https://github.com/YOUR_USERNAME/smart-network-diagnostic-assistant.git](https://github.com/YOUR_USERNAME/smart-network-diagnostic-assistant.git)

# Navigate into project directory
cd smart-network-diagnostic-assistant

# Install required packages
pip3 install requests psutil

📄 License
Distributed under the MIT License. See LICENSE for more information.

3. Launching the ApplicationExecute the main application launcher: ### python3 web_app.py

Test Scenario,Action,Expected Output
1. Baseline State,Keep Wi-Fi connected normally,"🟢 OPTIMAL SIGNAL wave, low latency (<20 ms), green AIOps banner."
2. Target Switcher,Enter 1.1.1.1 or github.com and click Apply,Charts and traceroute table re-index and stream telemetry to the new target.
3. Disconnection Test,Turn off Mac Wi-Fi,"⚫ OFFLINE wave, native macOS alert banner pops up, 100% packet loss detected."
4. Auto-Recovery Test,Turn Wi-Fi back on,Dashboard auto-reconnects within 3 seconds without refreshing the browser.
5. PDF / JSON Export,Click 🖨️ PDF or 📥 JSON,Opens formatted print preview or downloads time-series telemetry JSON.

### 📜 Technology Stack

Language: Python 3
Networking & System Primitives: socket, subprocess, requests, psutil, statistics
Web & Presentation: Vanilla HTML5, Modern CSS (Glassmorphism), JavaScript (ES6), Chart.js (CDN)
OS Automation: AppleScript (osascript) for macOS notifications

### 🚀 Step 2: Push Your New Changes to GitHub

Open your VS Code terminal in your project directory and run these 3 quick commands:

#### 1. Check modified files & stage everything:
```bash
git add .