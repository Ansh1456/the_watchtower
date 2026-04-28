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
import threading
import sys
import os
import json
import tkinter as tk
from tkinter import scrolledtext, messagebox

CONFIG_FILE = "watchtower_config.json"

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

class AgentGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Watchtower Telemetry Agent")
        self.root.geometry("500x450")
        self.root.resizable(False, False)
        
        self.is_running = False
        self.agent_thread = None
        
        # Setup UI
        tk.Label(root, text="Server URL (e.g., https://your-watchtower.onrender.com):").pack(pady=(10, 0))
        self.url_entry = tk.Entry(root, width=50)
        self.url_entry.pack()
        
        tk.Label(root, text="Agent Token:").pack(pady=(10, 0))
        self.token_entry = tk.Entry(root, width=50)
        self.token_entry.pack()
        
        self.auto_start_var = tk.BooleanVar()
        self.auto_start_cb = tk.Checkbutton(root, text="Auto-Start Agent on Launch", variable=self.auto_start_var)
        self.auto_start_cb.pack(pady=(5, 0))
        
        self.btn_frame = tk.Frame(root)
        self.btn_frame.pack(pady=10)
        
        self.start_btn = tk.Button(self.btn_frame, text="Start Agent", command=self.start, bg="green", fg="white", width=15)
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = tk.Button(self.btn_frame, text="Stop Agent", command=self.stop, bg="red", fg="white", width=15, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        tk.Label(root, text="Activity Log:").pack()
        self.log_area = scrolledtext.ScrolledText(root, width=55, height=12, state=tk.DISABLED)
        self.log_area.pack()
        
        self.log("[*] Watchtower Agent Ready.")
        self.load_config()

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    config = json.load(f)
                    self.url_entry.insert(0, config.get("url", ""))
                    self.token_entry.insert(0, config.get("token", ""))
                    self.auto_start_var.set(config.get("auto_start", False))
                    
                    if self.auto_start_var.get() and self.url_entry.get() and self.token_entry.get():
                        # Start automatically but allow the UI to load first
                        self.root.after(500, self.start)
            except Exception as e:
                self.log(f"[!] Could not load config: {e}")
        else:
            self.url_entry.insert(0, "https://")

    def save_config(self, url, token, auto_start):
        try:
            with open(CONFIG_FILE, "w") as f:
                json.dump({"url": url, "token": token, "auto_start": auto_start}, f)
        except Exception as e:
            self.log(f"[!] Could not save config: {e}")

    def log(self, message):
        self.log_area.config(state=tk.NORMAL)
        self.log_area.insert(tk.END, message + "\n")
        self.log_area.see(tk.END)
        self.log_area.config(state=tk.DISABLED)

    def start(self):
        url = self.url_entry.get().strip()
        token = self.token_entry.get().strip()
        
        if not url or not token or url == "https://":
            messagebox.showerror("Error", "Valid Server URL and Token are required.")
            return
            
        self.save_config(url, token, self.auto_start_var.get())
        
        self.is_running = True
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.url_entry.config(state=tk.DISABLED)
        self.token_entry.config(state=tk.DISABLED)
        
        self.log("[*] Starting Watchtower Agent...")
        self.log(f"[*] Connecting to {url}")
        
        self.agent_thread = threading.Thread(target=self.run_agent, args=(url, token, 3), daemon=True)
        self.agent_thread.start()

    def stop(self):
        self.is_running = False
        self.log("[*] Stopping Watchtower Agent...")
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.url_entry.config(state=tk.NORMAL)
        self.token_entry.config(state=tk.NORMAL)

    def run_agent(self, server_url, token, interval):
        headers = {
            "Authorization": f"Token {token}",
            "Content-Type": "application/json"
        }
        push_endpoint = f"{server_url.rstrip('/')}/api/telemetry/push/"
        
        os_sys = platform.system()
        processor = get_processor_name()
        cores = psutil.cpu_count()
        ram_total = round(psutil.virtual_memory().total / (1024**3), 2)
        boot_time = psutil.boot_time()
        
        while self.is_running:
            try:
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
                
                response = requests.post(push_endpoint, json=payload, headers=headers, timeout=5)
                if response.status_code == 200:
                    self.log(f"[+] Synced | CPU: {cpu}% | RAM: {ram}% | DSK: {disk}%")
                else:
                    self.log(f"[-] Sync failed: HTTP {response.status_code} - {response.text}")
                    
            except requests.exceptions.RequestException as e:
                self.log(f"[!] Connection Error: {e}")
                
            # Wait for interval but check if stopped
            for _ in range(interval * 10):
                if not self.is_running:
                    break
                time.sleep(0.1)
                
        self.log("[*] Agent Stopped.")

def start_agent_cli(server_url, token, interval):
    print(f"[*] Starting Watchtower Agent...")
    print(f"[*] Connecting to {server_url} with interval {interval}s")
    
    headers = {
        "Authorization": f"Token {token}",
        "Content-Type": "application/json"
    }
    
    push_endpoint = f"{server_url.rstrip('/')}/api/telemetry/push/"
    
    os_sys = platform.system()
    processor = get_processor_name()
    cores = psutil.cpu_count()
    ram_total = round(psutil.virtual_memory().total / (1024**3), 2)
    boot_time = psutil.boot_time()
    
    try:
        while True:
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
    # If arguments are provided, use the CLI. Otherwise, launch the GUI.
    if len(sys.argv) > 1:
        parser = argparse.ArgumentParser(description="Watchtower Telemetry Edge Agent")
        parser.add_argument("--url", required=True, help="Watchtower Server URL (e.g., http://127.0.0.1:8000)")
        parser.add_argument("--token", required=True, help="API Authentication Token")
        parser.add_argument("--interval", type=int, default=3, help="Sync interval in seconds (default: 3)")
        
        args = parser.parse_args()
        start_agent_cli(args.url, args.token, args.interval)
    else:
        root = tk.Tk()
        app = AgentGUI(root)
        root.mainloop()
