import os
import subprocess

def register(mcp):
    @mcp.tool()
    def get_system_logs(lines: int = 50) -> dict:
        """Get recent system log entries"""
        try:
            log_files = ["/var/log/syslog", "/var/log/messages", "/var/log/system.log"]
            log_content = []
            for log_file in log_files:
                if os.path.exists(log_file):
                    try:
                        with open(log_file, "r") as f:
                            log_content.extend(f.readlines()[-lines:])
                            break
                    except PermissionError:
                        continue
            if not log_content:
                try:
                    result = subprocess.run(["journalctl", "-n", str(lines), "--no-pager"], capture_output=True, text=True, timeout=10)
                    if result.returncode == 0:
                        log_content = result.stdout.splitlines()
                except (subprocess.TimeoutExpired, FileNotFoundError):
                    pass
            return {"log_entries": log_content[-lines:] if log_content else ["No log entries available"]}
        except Exception as e:
            return {"error": str(e)}

    @mcp.tool()
    def get_error_logs(lines: int = 20) -> dict:
        """Get recent error log entries"""
        try:
            try:
                result = subprocess.run(["journalctl", "-p", "err", "-n", str(lines), "--no-pager"], capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    return {"error_logs": result.stdout.splitlines()}
            except (subprocess.TimeoutExpired, FileNotFoundError):
                pass
            log_files = ["/var/log/syslog", "/var/log/messages"]
            for log_file in log_files:
                if os.path.exists(log_file):
                    try:
                        result = subprocess.run(["grep", "-i", "error", log_file], capture_output=True, text=True, timeout=10)
                        if result.returncode == 0:
                            return {"error_logs": result.stdout.splitlines()[-lines:]}
                    except (subprocess.TimeoutExpired, FileNotFoundError):
                        continue
            return {"error_logs": ["No error logs found"]}
        except Exception as e:
            return {"error": str(e)}
