import platform
import psutil
import time
import speedtest


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

    uptime_seconds = time.time() - psutil.boot_time()
    uptime_hours = round(uptime_seconds / 3600, 2)

    disk = psutil.disk_usage('/')

    return {
        "os": platform.system(),
        "processor": platform.processor(),

        "cpu_usage": psutil.cpu_percent(interval=1),
        "cpu_cores": psutil.cpu_count(),

        "ram_total": round(psutil.virtual_memory().total / (1024**3), 2),
        "ram_percent": psutil.virtual_memory().percent,

        "disk_usage": disk.percent,
        "disk_total": round(disk.total / (1024**3), 2),
        "disk_free": round(disk.free / (1024**3), 2),

        "uptime": uptime_hours
    }