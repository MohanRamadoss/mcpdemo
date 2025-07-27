import psutil
import os
from datetime import datetime
import time

def register(mcp):
    @mcp.tool()
    def get_cpu_usage() -> dict:
        """Get current CPU usage statistics"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_cores = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()
            return {
                "cpu_percent": cpu_percent,
                "cpu_cores": cpu_cores,
                "cpu_frequency": {
                    "current": cpu_freq.current if cpu_freq else "N/A",
                    "min": cpu_freq.min if cpu_freq else "N/A",
                    "max": cpu_freq.max if cpu_freq else "N/A"
                },
                "load_average": os.getloadavg()
            }
        except Exception as e:
            return {"error": str(e)}

    @mcp.tool()
    def get_memory_usage() -> dict:
        """Get current memory usage statistics"""
        try:
            mem = psutil.virtual_memory()
            swap = psutil.swap_memory()
            return {
                "memory": {
                    "total": mem.total, "available": mem.available, "used": mem.used,
                    "percent": mem.percent, "free": mem.free
                },
                "swap": {
                    "total": swap.total, "used": swap.used, "free": swap.free, "percent": swap.percent
                }
            }
        except Exception as e:
            return {"error": str(e)}

    @mcp.tool()
    def get_disk_usage() -> dict:
        """Get disk usage information for all mounted filesystems"""
        try:
            disk_usage = []
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    disk_usage.append({
                        "device": partition.device, "mountpoint": partition.mountpoint,
                        "fstype": partition.fstype, "total": usage.total, "used": usage.used,
                        "free": usage.free, "percent": usage.percent
                    })
                except PermissionError:
                    continue
            return {"disk_usage": disk_usage}
        except Exception as e:
            return {"error": str(e)}

    @mcp.tool()
    def get_network_stats() -> dict:
        """Get network interface statistics"""
        try:
            net_stats = psutil.net_io_counters(pernic=True)
            network_info = []
            for interface, stats in net_stats.items():
                network_info.append({
                    "interface": interface, "bytes_sent": stats.bytes_sent, "bytes_recv": stats.bytes_recv,
                    "packets_sent": stats.packets_sent, "packets_recv": stats.packets_recv,
                    "errors_in": stats.errin, "errors_out": stats.errout,
                    "drops_in": stats.dropin, "drops_out": stats.dropout
                })
            return {"network_stats": network_info}
        except Exception as e:
            return {"error": str(e)}
