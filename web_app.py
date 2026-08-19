import os
import sys
import time
import json
import threading
import webbrowser
from urllib.parse import urlparse, parse_qs
from http.server import HTTPServer, BaseHTTPRequestHandler
from diagnostic_engine import (
    get_local_ip, get_public_ip_and_geo, get_gateway_and_dns,
    run_diagnostics, get_interface_stats, run_traceroute,
    scan_security_ports, generate_ai_analysis, trigger_system_notification
)

# Shared In-Memory State
CURRENT_TARGET = "8.8.8.8"
CURRENT_TELEMETRY = {}
ROLLING_HISTORY = []
HOPS_CACHE = []
PORT_SCAN_CACHE = []
LAST_STATUS = "INITIALIZING"

def background_security_worker():
    """Asynchronous worker scanning ports and traceroutes."""
    global HOPS_CACHE, PORT_SCAN_CACHE
    while True:
        try:
            gateway, _ = get_gateway_and_dns()
            PORT_SCAN_CACHE = scan_security_ports(gateway)
            HOPS_CACHE = run_traceroute(target=CURRENT_TARGET, max_hops=6)
        except Exception:
            pass
        time.sleep(15)

def background_monitoring_daemon():
    """Continuous fast telemetry daemon updating every 3 seconds."""
    global CURRENT_TELEMETRY, ROLLING_HISTORY, LAST_STATUS, CURRENT_TARGET
    while True:
        try:
            local_ip = get_local_ip()
            geo_info = get_public_ip_and_geo()
            gateway, dns = get_gateway_and_dns()
            stats = get_interface_stats()
            internet, avg_lat, loss, jitter, raw_pings = run_diagnostics(host=CURRENT_TARGET, count=2)
            
            ai_report = generate_ai_analysis(internet, avg_lat, loss, jitter, gateway, geo_info, CURRENT_TARGET)
            status = ai_report["status"]

            if status != LAST_STATUS and LAST_STATUS != "INITIALIZING":
                trigger_system_notification(
                    f"Network State: {status}",
                    f"{ai_report['title']} (Latency: {avg_lat}ms, Loss: {loss}%)"
                )
            LAST_STATUS = status

            sample = {
                "timestamp": time.strftime("%H:%M:%S"),
                "target": CURRENT_TARGET,
                "status": status,
                "wave_state": ai_report["wave_state"],
                "wave_label": ai_report["wave_label"],
                "title": ai_report["title"],
                "summary": ai_report["summary"],
                "recommendations": ai_report["recommendations"],
                "local_ip": local_ip,
                "public_ip": geo_info["ip"],
                "geo_location": f"{geo_info['city']}, {geo_info['country']}",
                "isp_org": geo_info["org"],
                "gateway": gateway,
                "dns": dns,
                "bandwidth_usage": stats,
                "avg_latency": avg_lat,
                "jitter": jitter,
                "loss": loss,
                "hops": HOPS_CACHE,
                "ports": PORT_SCAN_CACHE
            }

            CURRENT_TELEMETRY = sample
            
            ROLLING_HISTORY.append(sample)
            if len(ROLLING_HISTORY) > 20:
                ROLLING_HISTORY.pop(0)

        except Exception:
            pass
        time.sleep(3)

DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Smart Network Telemetry & Security Suite</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }
        body { background: #070D18; color: #E2E8F0; padding: 18px; min-height: 100vh; overflow-x: hidden; }
        
        /* Top Navbar */
        .top-navbar { display: flex; justify-content: space-between; align-items: center; background: #0F172A; border: 1px solid #1E293B; padding: 12px 20px; border-radius: 12px; margin-bottom: 18px; box-shadow: 0 10px 25px -5px rgba(0,0,0,0.5); }
        .brand { display: flex; align-items: center; gap: 10px; }
        .brand h1 { font-size: 18px; font-weight: 700; color: #F8FAFC; }
        .pulse-dot { display: inline-block; width: 9px; height: 9px; border-radius: 50%; background: #10B981; animation: pulse 1.5s infinite; }
        @keyframes pulse { 0% { transform: scale(0.9); opacity: 0.7; } 50% { transform: scale(1.2); opacity: 1; } 100% { transform: scale(0.9); opacity: 0.7; } }
        
        /* Target Switcher Controls */
        .target-switcher { display: flex; align-items: center; gap: 8px; background: #070D18; border: 1px solid #1E293B; padding: 4px 10px; border-radius: 8px; }
        .target-input { background: transparent; border: none; color: #38BDF8; font-family: monospace; font-size: 13px; font-weight: 700; outline: none; width: 140px; }
        
        .header-actions { display: flex; align-items: center; gap: 10px; }
        .btn { background: #1E293B; color: #E2E8F0; border: 1px solid #334155; padding: 6px 14px; border-radius: 8px; font-weight: 600; cursor: pointer; font-size: 12.5px; transition: all 0.2s; }
        .btn:hover { background: #334155; color: white; }
        .btn-primary { background: #2563EB; border-color: #3B82F6; color: white; }
        .btn-primary:hover { background: #1D4ED8; }

        /* Split-Screen Main Layout */
        .split-layout { display: grid; grid-template-columns: 1fr 1.15fr; gap: 18px; }
        .col-left, .col-right { display: flex; flex-direction: column; gap: 16px; }

        .panel { background: #0F172A; border: 1px solid #1E293B; border-radius: 12px; padding: 18px; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.3); }
        .panel-header { font-size: 11px; font-weight: 700; text-transform: uppercase; color: #64748B; margin-bottom: 10px; letter-spacing: 0.8px; display: flex; justify-content: space-between; align-items: center; }

        /* Wave Signal Display */
        .wave-box { display: flex; justify-content: space-between; align-items: center; background: #070D18; border: 1px solid #1E293B; border-radius: 10px; padding: 14px; }
        .wave-status-text { font-size: 16px; font-weight: 800; font-family: monospace; }
        .wave-bars { display: flex; align-items: flex-end; gap: 5px; height: 32px; }
        .bar { width: 8px; border-radius: 3px; background: #1E293B; transition: height 0.3s, background-color 0.3s; }
        
        .good .b1 { height: 10px; background: #10B981; }
        .good .b2 { height: 18px; background: #10B981; }
        .good .b3 { height: 25px; background: #10B981; }
        .good .b4 { height: 32px; background: #10B981; }
        .good-text { color: #10B981; }

        .weak .b1 { height: 10px; background: #F59E0B; }
        .weak .b2 { height: 18px; background: #F59E0B; }
        .weak .b3, .weak .b4 { height: 8px; background: #1E293B; }
        .weak-text { color: #F59E0B; }

        .bad .b1 { height: 10px; background: #EF4444; }
        .bad .b2, .bad .b3, .bad .b4 { height: 8px; background: #1E293B; }
        .bad-text { color: #EF4444; }

        .off .b1, .off .b2, .off .b3, .off .b4 { height: 6px; background: #475569; }
        .off-text { color: #64748B; }

        /* AI Banner */
        .ai-banner { background: rgba(7, 13, 24, 0.7); border-left: 5px solid #10B981; border-radius: 10px; padding: 16px; border-top: 1px solid #1E293B; border-right: 1px solid #1E293B; border-bottom: 1px solid #1E293B; }
        .ai-banner h3 { color: #10B981; font-size: 14.5px; margin-bottom: 6px; }
        .ai-banner p { font-size: 13px; color: #CBD5E1; line-height: 1.45; margin-bottom: 8px; }
        .ai-banner ul { margin-left: 16px; font-size: 12px; color: #94A3B8; }

        /* Grids & Cards */
        .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
        .grid-4 { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; }
        .stat-card { background: #070D18; border: 1px solid #1E293B; padding: 12px; border-radius: 10px; }
        .stat-label { font-size: 10.5px; text-transform: uppercase; color: #64748B; font-weight: 700; margin-bottom: 3px; }
        .stat-value { font-size: 14.5px; font-weight: 700; color: #F8FAFC; font-family: monospace; }
        .highlight { color: #38BDF8; }

        .chart-container { background: #070D18; border: 1px solid #1E293B; border-radius: 10px; padding: 14px; margin-bottom: 10px; }
        
        table { width: 100%; border-collapse: collapse; font-size: 12px; }
        th, td { padding: 7px 10px; border-bottom: 1px solid #1E293B; }
        th { color: #64748B; font-size: 10.5px; text-transform: uppercase; }

        /* Port Badges */
        .badge-open { background: rgba(239, 68, 68, 0.15); color: #EF4444; padding: 3px 8px; border-radius: 6px; font-weight: 700; font-size: 11px; border: 1px solid rgba(239, 68, 68, 0.3); }
        .badge-closed { background: rgba(16, 185, 129, 0.15); color: #10B981; padding: 3px 8px; border-radius: 6px; font-weight: 700; font-size: 11px; border: 1px solid rgba(16, 185, 129, 0.3); }

        @media (max-width: 1024px) { .split-layout { grid-template-columns: 1fr; } }
    </style>
</head>
<body>

    <div class="top-navbar">
        <div class="brand">
            <span class="pulse-dot"></span>
            <h1>Smart Network Telemetry Suite</h1>
        </div>

        <div class="target-switcher">
            <span style="font-size: 11px; color: #64748B; font-weight: 700;">PROBE TARGET:</span>
            <input id="targetInput" class="target-input" value="8.8.8.8" onkeydown="if(event.key==='Enter') setTarget()" />
            <button class="btn btn-primary" style="padding: 3px 8px; font-size: 11px;" onclick="setTarget()">Apply</button>
        </div>

        <div class="header-actions">
            <span id="lastSync" style="font-size: 11.5px; font-family: monospace; color: #94A3B8;">Syncing...</span>
            <button class="btn" onclick="window.print()">🖨️ PDF</button>
            <button class="btn" onclick="downloadJSON()">📥 JSON</button>
        </div>
    </div>

    <div class="split-layout">
        
        <div class="col-left">
            
            <div class="panel">
                <div class="panel-header">Link Quality & Signal Waveform</div>
                <div id="waveCard" class="wave-box good">
                    <div>
                        <div style="font-size: 10.5px; color: #64748B; font-weight: 700; text-transform: uppercase;">Current Link State</div>
                        <div id="waveStatusText" class="wave-status-text good-text">OPTIMAL SIGNAL</div>
                    </div>
                    <div class="wave-bars">
                        <div class="bar b1"></div>
                        <div class="bar b2"></div>
                        <div class="bar b3"></div>
                        <div class="bar b4"></div>
                    </div>
                </div>
            </div>

            <div class="panel">
                <div class="panel-header">AIOps Diagnostic & Root-Cause Intelligence</div>
                <div id="aiBanner" class="ai-banner">
                    <h3 id="aiTitle">🤖 Optimal Path Established</h3>
                    <p id="aiSummary">All telemetry metrics reflect optimal link health. Zero packet drop observed.</p>
                    <ul id="aiRecs"><li>Link path is operating normally.</li></ul>
                </div>
            </div>

            <div class="panel">
                <div class="panel-header">Gateway & Interface Configuration</div>
                <div class="grid-2">
                    <div class="stat-card"><div class="stat-label">Local IP</div><div class="stat-value highlight" id="localIp">--</div></div>
                    <div class="stat-card"><div class="stat-label">Public IP</div><div class="stat-value highlight" id="publicIp">--</div></div>
                    <div class="stat-card"><div class="stat-label">Default Gateway</div><div class="stat-value" id="gateway">--</div></div>
                    <div class="stat-card"><div class="stat-label">DNS Server</div><div class="stat-value" id="dns">--</div></div>
                </div>
            </div>

            <div class="panel">
                <div class="panel-header">Gateway Security & Critical Port Audit</div>
                <table>
                    <thead>
                        <tr><th>Port</th><th>Service Protocol</th><th>Status</th></tr>
                    </thead>
                    <tbody id="portBody">
                        <tr><td>Port 22</td><td>SSH Remote Admin</td><td><span class="badge-closed">SCANNING...</span></td></tr>
                    </tbody>
                </table>
            </div>

        </div>

        <div class="col-right">

            <div class="panel">
                <div class="panel-header">Live Telemetry Metrics Matrix</div>
                <div class="grid-4">
                    <div class="stat-card"><div class="stat-label">RTT Latency</div><div class="stat-value" id="avgLat">-- ms</div></div>
                    <div class="stat-card"><div class="stat-label">Jitter Var</div><div class="stat-value" id="jitter">-- ms</div></div>
                    <div class="stat-card"><div class="stat-label">Packet Loss</div><div class="stat-value" id="loss">-- %</div></div>
                    <div class="stat-card"><div class="stat-label">ISP Transit</div><div class="stat-value" id="ispOrg" style="font-size: 12px;">--</div></div>
                </div>
            </div>

            <div class="panel">
                <div class="panel-header">Live RTT Latency Stream (ms)</div>
                <div class="chart-container">
                    <canvas id="liveChart" height="100"></canvas>
                </div>
            </div>

            <div class="panel">
                <div class="panel-header">Telemetry Metric Distribution</div>
                <div class="chart-container">
                    <canvas id="distChart" height="90"></canvas>
                </div>
            </div>

            <div class="panel">
                <div class="panel-header">Multi-Hop Routing Path (Traceroute)</div>
                <table>
                    <thead>
                        <tr><th>Hop</th><th>Host Identifier</th><th>IP Address</th><th>RTT</th></tr>
                    </thead>
                    <tbody id="hopsBody">
                        <tr><td>Hop 1</td><td>Gateway</td><td style="color:#38BDF8;">Analyzing...</td><td>*</td></tr>
                    </tbody>
                </table>
            </div>

        </div>

    </div>

    <script>
        const ctx1 = document.getElementById('liveChart').getContext('2d');
        const liveChart = new Chart(ctx1, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'RTT Latency (ms)',
                    data: [],
                    borderColor: '#38BDF8',
                    backgroundColor: 'rgba(56, 189, 248, 0.15)',
                    borderWidth: 2,
                    tension: 0.35,
                    fill: true,
                    pointRadius: 3.5,
                    pointBackgroundColor: '#38BDF8'
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: { beginAtZero: true, grid: { color: '#1E293B' }, ticks: { color: '#64748B' } },
                    x: { grid: { color: '#1E293B' }, ticks: { color: '#64748B' } }
                },
                plugins: { legend: { display: false } }
            }
        });

        const ctx2 = document.getElementById('distChart').getContext('2d');
        const distChart = new Chart(ctx2, {
            type: 'bar',
            data: {
                labels: ['Latency (ms)', 'Jitter (ms)', 'Loss (%)'],
                datasets: [{
                    data: [0, 0, 0],
                    backgroundColor: ['#38BDF8', '#A855F7', '#10B981'],
                    borderRadius: 5
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: { beginAtZero: true, grid: { color: '#1E293B' }, ticks: { color: '#64748B' } },
                    x: { grid: { color: '#1E293B' }, ticks: { color: '#64748B' } }
                },
                plugins: { legend: { display: false } }
            }
        });

        let rollingHistoryCache = [];

        async function fetchTelemetry() {
            try {
                const res = await fetch('/api/telemetry');
                const data = await res.json();
                if (!data.current.timestamp) return;

                const cur = data.current;
                rollingHistoryCache = data.history;

                document.getElementById('lastSync').innerText = 'Synced at ' + cur.timestamp;
                document.getElementById('localIp').innerText = cur.local_ip;
                document.getElementById('publicIp').innerText = cur.public_ip;
                document.getElementById('gateway').innerText = cur.gateway;
                document.getElementById('dns').innerText = cur.dns;
                document.getElementById('avgLat').innerText = cur.avg_latency + ' ms';
                document.getElementById('jitter').innerText = cur.jitter + ' ms';
                document.getElementById('loss').innerText = cur.loss + '%';
                document.getElementById('ispOrg').innerText = cur.isp_org;

                // AIOps
                document.getElementById('aiTitle').innerText = '🤖 ' + cur.title;
                document.getElementById('aiSummary').innerText = cur.summary;
                if (cur.recommendations) {
                    document.getElementById('aiRecs').innerHTML = cur.recommendations.map(r => `<li>${r}</li>`).join('');
                }

                // Wave Box
                const waveCard = document.getElementById('waveCard');
                const waveText = document.getElementById('waveStatusText');
                waveCard.className = 'wave-box ' + cur.wave_state;
                waveText.className = 'wave-status-text ' + cur.wave_state + '-text';
                waveText.innerText = cur.wave_label;

                // Charts
                liveChart.data.labels.push(cur.timestamp);
                liveChart.data.datasets[0].data.push(cur.avg_latency);
                if (liveChart.data.labels.length > 8) {
                    liveChart.data.labels.shift();
                    liveChart.data.datasets[0].data.shift();
                }
                liveChart.update();

                distChart.data.datasets[0].data = [cur.avg_latency, cur.jitter, cur.loss];
                distChart.update();

                // Traceroute
                if (cur.hops && cur.hops.length > 0) {
                    document.getElementById('hopsBody').innerHTML = cur.hops.map(h => 
                        `<tr><td>Hop ${h.hop}</td><td>${h.host}</td><td style="color:#38BDF8; font-family:monospace;">${h.ip}</td><td style="font-weight:600;">${h.rtt}</td></tr>`
                    ).join('');
                }

                // Port Security Audit
                if (cur.ports && cur.ports.length > 0) {
                    document.getElementById('portBody').innerHTML = cur.ports.map(p => {
                        const badgeClass = p.status === 'OPEN' ? 'badge-open' : 'badge-closed';
                        return `<tr><td>Port ${p.port}</td><td>${p.service}</td><td><span class="${badgeClass}">${p.status}</span></td></tr>`;
                    }).join('');
                }
            } catch (err) {}
        }

        async function setTarget() {
            const newTarget = document.getElementById('targetInput').value.trim();
            if (newTarget) {
                await fetch('/api/set_target?host=' + encodeURIComponent(newTarget));
                liveChart.data.labels = [];
                liveChart.data.datasets[0].data = [];
            }
        }

        function downloadJSON() {
            const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(rollingHistoryCache, null, 2));
            const downloadAnchor = document.createElement('a');
            downloadAnchor.setAttribute("href", dataStr);
            downloadAnchor.setAttribute("download", "network_telemetry_report.json");
            document.body.appendChild(downloadAnchor);
            downloadAnchor.click();
            downloadAnchor.remove();
        }

        setInterval(fetchTelemetry, 3000);
        fetchTelemetry();
    </script>
</body>
</html>"""

class TelemetryServer(BaseHTTPRequestHandler):
    def do_GET(self):
        global CURRENT_TARGET
        parsed_url = urlparse(self.path)
        
        if parsed_url.path == "/api/telemetry":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            payload = {
                "current": CURRENT_TELEMETRY,
                "history": ROLLING_HISTORY
            }
            self.wfile.write(json.dumps(payload).encode("utf-8"))
            
        elif parsed_url.path == "/api/set_target":
            query_params = parse_qs(parsed_url.query)
            if "host" in query_params:
                CURRENT_TARGET = query_params["host"][0]
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "updated", "target": CURRENT_TARGET}).encode("utf-8"))
            
        else:
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(DASHBOARD_HTML.encode("utf-8"))

    def log_message(self, format, *args):
        return

def main():
    print("=" * 65)
    print(" 🚀 SMART NETWORK TELEMETRY, SECURITY & TARGET CONTROL")
    print("=" * 65)
    
    # 1. Start continuous monitoring daemon
    threading.Thread(target=background_monitoring_daemon, daemon=True).start()
    
    # 2. Start asynchronous traceroute & port audit worker
    threading.Thread(target=background_security_worker, daemon=True).start()
    
    time.sleep(1)
    
    # 3. Start Local HTTP Server
    port = 8080
    server = HTTPServer(("127.0.0.1", port), TelemetryServer)
    url = f"http://127.0.0.1:{port}"
    
    print(f"📡 Telemetry & Security Engine is ACTIVE...")
    print(f"🌐 Split Dashboard live at: {url}")
    print("=" * 65)
    print(" ℹ️  Press [Ctrl + C] in this terminal to STOP the suite.")
    print("=" * 65 + "\n")
    
    webbrowser.open(url)
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\n🛑 Suite stopped by user.")
        server.server_close()
        sys.exit()

if __name__ == "__main__":
    main()