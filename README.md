# 🌐 Smart Network Diagnostic Assistant & AIOps Telemetry Suite

[![Python Version](https://img.shields.io/badge/python-3.9%20%7C%203.10%20%7C%203.11%20%7C%203.12-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-macOS%20%7C%20Linux%20%7C%20Windows-lightgrey.svg)]()
[![ChartJS](https://img.shields.io/badge/visualizations-Chart.js-FF6384?style=flat&logo=chartdotjs&logoColor=white)](https://www.chartjs.org/)

An autonomous, real-time network telemetry framework, security auditor, and AIOps diagnostic engine written in Python. 

The application decouples low-level socket, routing, and kernel inspection from the presentation layer, delivering a live **Split-Screen Cyberpunk Telemetry Web Dashboard** featuring rolling ICMP time-series graphs, multi-hop traceroute path discovery, local port audits, target switching, and native desktop notifications.

---

## 📸 Key Highlights & UI Preview

* **Split-Screen Horizontal Layout:** Clean division between diagnostic intelligence/routing configuration (left) and live telemetry streams/distribution matrices (right).
* **Live Signal Waveform:** Dynamic 4-bar signal visualizer indicating network states:
  * 🟢 **OPTIMAL / EXCELLENT:** Sub-50ms latency, zero packet loss, minimal jitter.
  * 🟡 **WEAK / CONGESTED:** Latency > 90ms or Jitter > 25ms.
  * 🔴 **BAD / PACKET LOSS:** High drop rate, intermediate hop congestion.
  * ⚫ **OFFLINE:** Complete transport disconnection / Gateway unreachable.

---

## ⚡ Features Overview

### 1. 🔍 Routing & Interface Discovery
- **Local IP Extraction:** Dynamically identifies active network interfaces using dummy UDP routing sockets (`socket.getsockname()`) without hardcoded adapter names.
- **Kernel Routing Inspection:** Parses default gateway and configured DNS resolvers via macOS `route -n get default` and `scutil --dns` subprocess hooks.
- **Public WAN & ISP Peering:** Identifies external IPv4 address, City/Region, Country, and ISP/ASN organization details.
- **Cumulative Hardware Traffic:** Monitors system-level interface I/O metrics (Total Megabytes Sent / Received via `psutil`).

### 2. 📊 Precision Telemetry & Statistical Jitter
- **ICMP RTT Latency Probing:** Real-time round-trip latency measurements with sub-millisecond precision.
- **Jitter Variance Calculation:** Uses sample standard deviation ($\sigma$) across probe windows to detect jitter spikes that cause bufferbloat or VoIP/gaming stutter:
  $$\text{Jitter} = \sqrt{\frac{1}{N-1} \sum_{i=1}^{N} (x_i - \bar{x})^2}$$
- **Rolling Latency Chart:** Continuous Chart.js line graph displaying the rolling past 15 seconds to 1 minute of telemetry updates.
- **Metric Distribution Matrix:** Side-by-side bar chart benchmarking average latency, jitter variance, and packet loss percentages.

### 3. 🤖 AIOps Diagnostic & Root-Cause Engine
- Evaluates live network health in real-time.
- Correlates latency variance, drop rates, and routing parameters to produce contextual root-cause analyses and targeted remediation actions (e.g., distinguishing between RF interference, bufferbloat, and Layer 1 transport dropouts).

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