System Health Checker

A lightweight Python utility that monitors system performance in real time and logs key system statistics including CPU, memory, disk usage, network activity, and battery levels. The data is saved in CSV and JSON formats for easy analysis, visualization, or integration with other tools.

Overview

The script continuously records system health metrics at adjustable intervals and writes each sample to structured log files. It’s designed to be simple, efficient, and easily extendable—ideal for learning how to monitor systems, automate tasks, or integrate performance monitoring into other Python-based tools.

Features

Real-time monitoring of:

CPU utilization (%)

RAM usage (%)

Disk usage (%)

Network speed (Rx/Tx in kbps)

Battery percentage (if available)

Logs output to:

health.csv — for spreadsheet or time-series analysis

health.json — for structured data parsing

Automatic alerts for high CPU, RAM, or disk usage

Adjustable sampling intervals and alert thresholds

Modular structure for easy customization

Lightweight and cross-platform

Tech Stack

Language: Python 3
Libraries:

psutil — system metrics collection

json, csv, datetime, os — standard Python libraries for data handling
Platform: Windows, macOS, Linux

Setup & Usage

Clone the repository
git clone https://github.com/ayaan117/system-health-checker.git
cd system-health-checker

Set up a virtual environment
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt

Run the health checker
python health_check.py

Metrics will be displayed in real time and saved in the /logs directory.
Press Ctrl + C to stop the script.

Output Example

Example entry from health.json:
{
"timestamp": "2025-10-17T18:45:00",
"cpu_percent": 14.3,
"ram_percent": 47.8,
"disk_percent": 52.1,
"net_rx_kbps": 101.2,
"net_tx_kbps": 88.7,
"battery_percent": 97
}

Configuration

At the top of health_check.py you can adjust sampling intervals and warning thresholds:
INTERVAL_SEC = 15
CPU_WARN = 85
RAM_WARN = 85
DISK_WARN = 90

Learning Objectives

This project demonstrates:

Using Python for system-level automation and monitoring

File handling and data serialization (JSON, CSV)

Working with third-party libraries (psutil)

Writing modular and maintainable code with error handling

Future Improvements

Add a Flask dashboard for real-time visualizations

Email or desktop notifications for high usage alerts

Expanded cross-platform support

Cloud integration with AWS CloudWatch or Grafana

Author
Ayaan