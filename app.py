import json
import os
from datetime import datetime, timedelta
from flask import Flask, render_template, jsonify
import psutil

app = Flask(__name__)

LOG_DIR = "logs"
CSV_PATH = os.path.join(LOG_DIR, "health.csv")
JSON_PATH = os.path.join(LOG_DIR, "health.json")

# Config thresholds
CPU_WARN = 85
RAM_WARN = 85
DISK_WARN = 90

def load_health_data():
    """Load health data from JSON log"""
    if not os.path.exists(JSON_PATH):
        return []
    try:
        with open(JSON_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def get_latest_metrics():
    """Get the most recent metrics"""
    data = load_health_data()
    if data:
        return data[-1]
    return None

def get_metrics_for_hours(hours=1):
    """Get metrics from the last N hours"""
    data = load_health_data()
    if not data:
        return []
    
    try:
        cutoff_time = datetime.now() - timedelta(hours=hours)
        filtered = []
        for item in data:
            ts = datetime.fromisoformat(item["timestamp"])
            if ts >= cutoff_time:
                filtered.append(item)
        return filtered
    except Exception:
        return data[-100:] if len(data) > 100 else data

def get_alert_status(metrics):
    """Check if metrics trigger alerts"""
    alerts = []
    if metrics["cpu_percent"] >= CPU_WARN:
        alerts.append({"type": "cpu", "message": f"High CPU: {metrics['cpu_percent']}%"})
    if metrics["ram_percent"] >= RAM_WARN:
        alerts.append({"type": "ram", "message": f"High RAM: {metrics['ram_percent']}%"})
    if metrics["disk_percent"] >= DISK_WARN:
        alerts.append({"type": "disk", "message": f"High Disk: {metrics['disk_percent']}%"})
    return alerts

@app.route("/")
def dashboard():
    return render_template("dashboard.html")

@app.route("/api/current")
def api_current():
    """Get current system metrics"""
    metrics = get_latest_metrics()
    if metrics:
        alerts = get_alert_status(metrics)
        return jsonify({
            "success": True,
            "data": metrics,
            "alerts": alerts,
            "status": "alert" if alerts else "ok"
        })
    return jsonify({"success": False, "error": "No data available"})

@app.route("/api/history/<int:hours>")
def api_history(hours=1):
    """Get metrics history for the last N hours"""
    data = get_metrics_for_hours(hours)
    return jsonify({
        "success": True,
        "data": data,
        "hours": hours
    })

@app.route("/api/stats")
def api_stats():
    """Get aggregate statistics"""
    data = get_metrics_for_hours(1)
    if not data:
        return jsonify({"success": False, "error": "No data available"})
    
    cpu_vals = [d["cpu_percent"] for d in data]
    ram_vals = [d["ram_percent"] for d in data]
    disk_vals = [d["disk_percent"] for d in data]
    
    stats = {
        "cpu": {
            "current": cpu_vals[-1] if cpu_vals else 0,
            "avg": round(sum(cpu_vals) / len(cpu_vals), 1) if cpu_vals else 0,
            "max": max(cpu_vals) if cpu_vals else 0,
            "min": min(cpu_vals) if cpu_vals else 0,
        },
        "ram": {
            "current": ram_vals[-1] if ram_vals else 0,
            "avg": round(sum(ram_vals) / len(ram_vals), 1) if ram_vals else 0,
            "max": max(ram_vals) if ram_vals else 0,
            "min": min(ram_vals) if ram_vals else 0,
        },
        "disk": {
            "current": disk_vals[-1] if disk_vals else 0,
            "avg": round(sum(disk_vals) / len(disk_vals), 1) if disk_vals else 0,
            "max": max(disk_vals) if disk_vals else 0,
            "min": min(disk_vals) if disk_vals else 0,
        }
    }
    return jsonify({"success": True, "data": stats})

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
