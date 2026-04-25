import platform
import psutil
import time
import speedtest
from django.core.cache import cache
from accounts.models import SystemLog
from django.utils import timezone

def get_network_speed():
    try:
        st = speedtest.Speedtest()
        download = st.download() / 1_000_000  # Mbps
        upload = st.upload() / 1_000_000      # Mbps
        return {
            "download": round(download, 2),
            "upload": round(upload, 2)
        }
    except:
        return {
            "download": 0,
            "upload": 0
        }

def get_system_info():
    # Cache system info for 5 seconds to prevent high CPU overhead from repetitive psutil calls
    cached_info = cache.get('system_info_cache')
    if cached_info:
        return cached_info

    uptime_seconds = time.time() - psutil.boot_time()
    uptime_hours = round(uptime_seconds / 3600, 2)
    disk = psutil.disk_usage('/')
    
    cpu = psutil.cpu_percent(interval=0.1)
    ram = psutil.virtual_memory().percent
    
    info = {
        "os": platform.system(),
        "processor": platform.processor(),
        "cpu_usage": cpu,
        "cpu_cores": psutil.cpu_count(),
        "ram_total": round(psutil.virtual_memory().total / (1024**3), 2),
        "ram_percent": ram,
        "disk_usage": disk.percent,
        "disk_total": round(disk.total / (1024**3), 2),
        "disk_free": round(disk.free / (1024**3), 2),
        "uptime": uptime_hours
    }
    
    # Periodically log system state (at most once every 60 seconds)
    last_log = SystemLog.objects.order_by('-created_at').first()
    if not last_log or (timezone.now() - last_log.created_at).total_seconds() > 60:
        SystemLog.objects.create(cpu_usage=cpu, ram_usage=ram, disk_usage=disk.percent)
        
    cache.set('system_info_cache', info, 5)
    return info

def get_user_system_info(user=None):
    info = get_system_info().copy()
    if user:
        try:
            profile = user.userprofile
            if profile.latest_cpu is not None:
                info['cpu_usage'] = profile.latest_cpu
            if profile.latest_ram is not None:
                info['ram_percent'] = profile.latest_ram
            if profile.latest_disk is not None:
                info['disk_usage'] = profile.latest_disk
            if profile.latest_disk_total is not None:
                info['disk_total'] = profile.latest_disk_total
            if profile.latest_disk_free is not None:
                info['disk_free'] = profile.latest_disk_free
        except:
            pass
    return info

def get_top_processes(limit=5):
    """Fetch top CPU-consuming processes, sorted by highest CPU usage."""
    processes = []
    for proc in psutil.process_iter(['name', 'cpu_percent']):
        try:
            val = proc.info.get('cpu_percent')
            proc.info['cpu_percent'] = val if val is not None else 0.0
            processes.append(proc.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    # Sort by CPU usage descending
    processes.sort(key=lambda p: p['cpu_percent'], reverse=True)
    return processes[:limit]

def get_system_summary(is_admin=True, processes=None):
    """Generate dynamic textual system summary branch mapped by role."""
    # Ensure baseline data is fetched properly
    info = cache.get('system_info_cache')
    if not info:
        info = get_system_info()
        
    cpu = info.get('cpu_usage', 0.0)
    ram = info.get('ram_percent', 0.0)
    
    # Detailed ADMIN logic with conditions
    if is_admin:
        if cpu > 80:
            summary = f"<span class='text-rose-500'>CRITICAL WARNING:</span> Core capacity maxing at <span class='font-bold'>{cpu}%</span>. "
        elif cpu > 50:
            summary = f"<span class='text-amber-500'>CAUTION:</span> CPU usage is elevated across threads (<span class='font-bold'>{cpu}%</span>). "
        else:
            summary = f"System operations nominal. CPU stable at <span class='text-[#00d4ff] font-bold'>{cpu}%</span>, memory footprint at <span class='text-emerald-400 font-bold'>{ram}%</span>. "
            
        if processes and len(processes) > 0 and cpu > 10:
            # Process level reasoning analysis
            top_name = processes[0].get('name', 'Unknown')
            top_cpu = processes[0].get('cpu_percent', 0.0)
            summary += f"Root cause analysis indicates '<span class='font-mono text-white'>{top_name}</span>' as the primary consumer (~{top_cpu}% execution tax)."
            
        return summary
    
    # Simplified USER logic 
    else:
        if cpu > 80:
            return "Your system is under intense computational load right now. You may experience slowness."
        elif cpu > 50:
            return "Your system is currently busy but safely operating within parameters."
        else:
            return "Your machine is running smoothly over optimal health thresholds."
