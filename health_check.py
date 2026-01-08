import json, time, os
from datetime import datetime
import psutil

# ---- Config ----
INTERVAL_SEC = 15            # how often to sample
CPU_WARN = 85                 # %
RAM_WARN = 85                 # %
DISK_WARN = 90                # %
NET_SAMPLE_SEC = 3            # for a brief rx/tx measurement

LOG_DIR = "logs"
CSV_PATH = os.path.join(LOG_DIR, "health.csv")
JSON_PATH = os.path.join(LOG_DIR, "health.json")

def ensure_dirs():
    os.makedirs(LOG_DIR, exist_ok=True)
    if not os.path.exists(CSV_PATH):
        with open(CSV_PATH, "w", encoding="utf-8") as f:
            f.write("timestamp,cpu_percent,ram_percent,disk_percent,net_rx_kbps,net_tx_kbps,battery_percent\n")

def net_sample(seconds=NET_SAMPLE_SEC):
    s1 = psutil.net_io_counters()
    time.sleep(seconds)
    s2 = psutil.net_io_counters()
    rx_kbps = (s2.bytes_recv - s1.bytes_recv) * 8 / 1024 / seconds
    tx_kbps = (s2.bytes_sent - s1.bytes_sent) * 8 / 1024 / seconds
    return round(rx_kbps, 1), round(tx_kbps, 1)

def get_battery():
    try:
        batt = psutil.sensors_battery()
        return None if not batt else int(batt.percent)
    except Exception:
        return None

def alert_if_needed(metrics):
    alerts = []
    if metrics["cpu_percent"] >= CPU_WARN: alerts.append(f"High CPU: {metrics['cpu_percent']}%")
    if metrics["ram_percent"] >= RAM_WARN: alerts.append(f"High RAM: {metrics['ram_percent']}%")
    if metrics["disk_percent"] >= DISK_WARN: alerts.append(f"High Disk: {metrics['disk_percent']}%")
    if alerts:
        print("ALERT: " + " | ".join(alerts))

def write_logs(metrics):
    # CSV
    with open(CSV_PATH, "a", encoding="utf-8") as f:
        f.write("{timestamp},{cpu_percent},{ram_percent},{disk_percent},{net_rx_kbps},{net_tx_kbps},{battery_percent}\n".format(**metrics))
    # JSON (append list)
    data = []
    if os.path.exists(JSON_PATH):
        try:
            with open(JSON_PATH, "r", encoding="utf-8") as jf:
                data = json.load(jf)
        except Exception:
            data = []
    data.append(metrics)
    with open(JSON_PATH, "w", encoding="utf-8") as jf:
        json.dump(data, jf, indent=2)

def main():
    ensure_dirs()
    print("System Health Checker running... Press Ctrl+C to stop.")
    while True:
        ts = datetime.now().isoformat(timespec="seconds")
        cpu = psutil.cpu_percent(interval=1)
        ram = psutil.virtual_memory().percent
        disk = psutil.disk_usage(os.getenv("SystemDrive", "C:")).percent
        rx, tx = net_sample()
        batt = get_battery()

        metrics = {
            "timestamp": ts,
            "cpu_percent": cpu,
            "ram_percent": ram,
            "disk_percent": disk,
            "net_rx_kbps": rx,
            "net_tx_kbps": tx,
            "battery_percent": batt if batt is not None else ""
        }
        print(metrics)
        alert_if_needed(metrics)
        write_logs(metrics)
        time.sleep(max(1, INTERVAL_SEC - 1 - NET_SAMPLE_SEC))

if __name__ == "__main__":
    main()
