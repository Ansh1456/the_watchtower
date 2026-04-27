"""
Watchtower Telemetry Agent
Version 3.0

This script runs on the operator's machine and automatically
pushes CPU, RAM, and Disk telemetry to the Watchtower Command Center.
"""

import time
import psutil
import requests
import argparse
import platform
import subprocess

def get_processor_name():
    if platform.system() == "Windows":
        return platform.processor()
    elif platform.system() == "Darwin":
        try:
            return subprocess.check_output(['sysctl', '-n', 'machdep.cpu.brand_string']).strip().decode()
        except:
            return platform.processor()
    elif platform.system() == "Linux":
        try:
            with open('/proc/cpuinfo', 'r') as f:
                for line in f:
                    if 'model name' in line:
                        return line.split(':')[1].strip()
        except:
            pass
    return platform.processor() or "Unknown Processor"

def start_agent(server_url, token, interval):
    print(f"[*] Starting Watchtower Agent...")
    print(f"[*] Connecting to {server_url} with interval {interval}s")
    
    headers = {
        "Authorization": f"Token {token}",
        "Content-Type": "application/json"
    }
    
    push_endpoint = f"{server_url.rstrip('/')}/api/telemetry/push/"
    
    # Static Hardware Info
    os_sys = platform.system()
    processor = get_processor_name()
    cores = psutil.cpu_count()
    ram_total = round(psutil.virtual_memory().total / (1024**3), 2)
    boot_time = psutil.boot_time()
    
    try:
        while True:
            # Gather Stats
            cpu = psutil.cpu_percent(interval=0.5)
            ram = psutil.virtual_memory().percent
            disk_usage = psutil.disk_usage('/')
            disk = disk_usage.percent
            disk_total = round(disk_usage.total / (1024**3), 2)
            disk_free = round(disk_usage.free / (1024**3), 2)
            uptime_hours = round((time.time() - boot_time) / 3600, 2)
            
            payload = {
                "cpu": cpu,
                "ram": ram,
                "disk": disk,
                "disk_total": disk_total,
                "disk_free": disk_free,
                "os_sys": os_sys,
                "processor": processor,
                "cores": cores,
                "ram_total": ram_total,
                "uptime": uptime_hours
            }
            
            # Send to Watchtower
            try:
                response = requests.post(push_endpoint, json=payload, headers=headers, timeout=5)
                if response.status_code == 200:
                    print(f"[+] Synced | CPU: {cpu}% | RAM: {ram}% | DSK: {disk}%")
                else:
                    print(f"[-] Sync failed: HTTP {response.status_code} - {response.text}")
            except requests.exceptions.RequestException as e:
                print(f"[!] Connection Error: {e}")
                
            time.sleep(interval)
            
    except KeyboardInterrupt:
        print("\n[*] Watchtower Agent Shutting Down.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Watchtower Telemetry Edge Agent")
    parser.add_argument("--url", required=True, help="Watchtower Server URL (e.g., http://127.0.0.1:8000)")
    parser.add_argument("--token", required=True, help="API Authentication Token")
    parser.add_argument("--interval", type=int, default=3, help="Sync interval in seconds (default: 3)")
    
    args = parser.parse_args()
    start_agent(args.url, args.token, args.interval)
