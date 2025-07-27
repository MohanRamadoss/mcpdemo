import psutil
import os
import subprocess

def register(mcp):
    @mcp.resource("system://metrics/cpu")
    def get_cpu_stats() -> dict:
        """Get current CPU usage statistics."""
        return {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "cpu_cores": psutil.cpu_count()
        }

    @mcp.resource("system://metrics/memory")
    def get_memory_usage() -> dict:
        """Get current memory usage statistics."""
        mem = psutil.virtual_memory()
        return {
            "total": mem.total,
            "available": mem.available,
            "used": mem.used,
            "percent": mem.percent
        }

    @mcp.resource("system://logs/syslog/{lines}")
    def get_syslog_tail(lines: int = 50) -> dict:
        """Get the tail of the system log."""
        log_file = "/var/log/syslog" if os.path.exists("/var/log/syslog") else "/var/log/messages"
        if not os.path.exists(log_file):
            return {"error": "No system log file found."}
        try:
            with open(log_file, "r") as f:
                return {"log_tail": f.readlines()[-lines:]}
        except Exception as e:
            return {"error": str(e)}

    @mcp.resource("system://logs/errors/{lines}")
    def get_error_logs(lines: int = 20) -> dict:
        """Get recent error log entries."""
        try:
            result = subprocess.run(["journalctl", "-p", "err", "-n", str(lines), "--no-pager"], capture_output=True, text=True)
            if result.returncode == 0 and result.stdout:
                return {"error_logs": result.stdout.splitlines()}
            return {"error_logs": ["No recent error logs found in journal."]}
        except Exception:
            return {"error_logs": ["journalctl not available or failed."]}
