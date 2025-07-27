from mcp.server.fastmcp import FastMCP
import sys
import os
import psutil
import subprocess
import logging
import json
import socket
import platform
import time
from datetime import datetime
import shutil

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP(
    "Linux Debug Agent",
    description="A Linux system debugging and monitoring agent with comprehensive system tools",
    version="1.0.0"
)

# === CPU Tools ===
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
        return {"error": f"Failed to get CPU usage: {str(e)}"}

# === Memory Tools ===
@mcp.tool()
def get_memory_usage() -> dict:
    """Get current memory usage statistics"""
    try:
        mem = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        return {
            "memory": {
                "total": mem.total,
                "available": mem.available,
                "used": mem.used,
                "percent": mem.percent,
                "free": mem.free
            },
            "swap": {
                "total": swap.total,
                "used": swap.used,
                "free": swap.free,
                "percent": swap.percent
            }
        }
    except Exception as e:
        return {"error": f"Failed to get memory usage: {str(e)}"}

# === Process Tools ===
@mcp.tool()
def list_processes(limit: int = 20) -> dict:
    """List running processes with details"""
    try:
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_percent', 'status', 'create_time']):
            try:
                processes.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        # Sort by CPU usage and limit results
        sorted_processes = sorted(processes, key=lambda p: p.get('cpu_percent', 0), reverse=True)
        return {"processes": sorted_processes[:limit]}
    except Exception as e:
        return {"error": f"Failed to list processes: {str(e)}"}

@mcp.tool()
def get_top_processes(limit: int = 10) -> dict:
    """Get top processes by CPU and memory usage"""
    try:
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'username']):
            try:
                proc_info = proc.info
                proc_info['total_usage'] = proc_info.get('cpu_percent', 0) + proc_info.get('memory_percent', 0)
                processes.append(proc_info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        # Sort by combined CPU + memory usage
        top_processes = sorted(processes, key=lambda p: p.get('total_usage', 0), reverse=True)
        return {"top_processes": top_processes[:limit]}
    except Exception as e:
        return {"error": f"Failed to get top processes: {str(e)}"}

@mcp.tool()
def kill_process(pid: int) -> dict:
    """Kill a process by PID"""
    try:
        process = psutil.Process(pid)
        process_name = process.name()
        process.terminate()
        
        # Wait for termination
        try:
            process.wait(timeout=5)
            return {"status": f"Process {pid} ({process_name}) terminated successfully"}
        except psutil.TimeoutExpired:
            # Force kill if termination timeout
            process.kill()
            return {"status": f"Process {pid} ({process_name}) forcefully killed"}
            
    except psutil.NoSuchProcess:
        return {"error": f"Process {pid} not found"}
    except psutil.AccessDenied:
        return {"error": f"Access denied to kill process {pid}"}
    except Exception as e:
        return {"error": f"Failed to kill process {pid}: {str(e)}"}

# === System Log Tools ===
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
                        log_lines = f.readlines()
                        log_content.extend(log_lines[-lines:])
                        break
                except PermissionError:
                    continue
        
        if not log_content:
            # Try journalctl as fallback
            try:
                result = subprocess.run(
                    ["journalctl", "-n", str(lines), "--no-pager"],
                    capture_output=True, text=True, timeout=10
                )
                if result.returncode == 0:
                    log_content = result.stdout.splitlines()
            except (subprocess.TimeoutExpired, FileNotFoundError):
                pass
        
        return {"log_entries": log_content[-lines:] if log_content else ["No log entries available"]}
    except Exception as e:
        return {"error": f"Failed to get system logs: {str(e)}"}

@mcp.tool()
def get_error_logs(lines: int = 20) -> dict:
    """Get recent error log entries"""
    try:
        # Try to get error logs using journalctl
        try:
            result = subprocess.run(
                ["journalctl", "-p", "err", "-n", str(lines), "--no-pager"],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                return {"error_logs": result.stdout.splitlines()}
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        # Fallback to grep error patterns in syslog
        log_files = ["/var/log/syslog", "/var/log/messages"]
        for log_file in log_files:
            if os.path.exists(log_file):
                try:
                    result = subprocess.run(
                        ["grep", "-i", "error", log_file],
                        capture_output=True, text=True, timeout=10
                    )
                    if result.returncode == 0:
                        error_lines = result.stdout.splitlines()
                        return {"error_logs": error_lines[-lines:]}
                except (subprocess.TimeoutExpired, FileNotFoundError):
                    continue
        
        return {"error_logs": ["No error logs found"]}
    except Exception as e:
        return {"error": f"Failed to get error logs: {str(e)}"}

# === Service Management Tools ===
@mcp.tool()
def restart_service(service_name: str) -> dict:
    """Restart a system service"""
    try:
        result = subprocess.run(
            ["systemctl", "restart", service_name],
            capture_output=True, text=True, timeout=30
        )
        
        if result.returncode == 0:
            return {"status": f"Service '{service_name}' restarted successfully"}
        else:
            return {"error": f"Failed to restart service '{service_name}': {result.stderr.strip()}"}
    except subprocess.TimeoutExpired:
        return {"error": f"Timeout while restarting service '{service_name}'"}
    except Exception as e:
        return {"error": f"Failed to restart service '{service_name}': {str(e)}"}

@mcp.tool()
def get_service_status(service_name: str) -> dict:
    """Get status of a system service"""
    try:
        result = subprocess.run(
            ["systemctl", "status", service_name],
            capture_output=True, text=True, timeout=10
        )
        
        return {
            "service": service_name,
            "status_output": result.stdout,
            "is_active": "active" in result.stdout,
            "return_code": result.returncode
        }
    except subprocess.TimeoutExpired:
        return {"error": f"Timeout while checking service '{service_name}'"}
    except Exception as e:
        return {"error": f"Failed to get service status '{service_name}': {str(e)}"}

# === Disk Usage Tools ===
@mcp.tool()
def get_disk_usage() -> dict:
    """Get disk usage information for all mounted filesystems"""
    try:
        disk_usage = []
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                disk_usage.append({
                    "device": partition.device,
                    "mountpoint": partition.mountpoint,
                    "fstype": partition.fstype,
                    "total": usage.total,
                    "used": usage.used,
                    "free": usage.free,
                    "percent": (usage.used / usage.total) * 100
                })
            except PermissionError:
                continue
        
        return {"disk_usage": disk_usage}
    except Exception as e:
        return {"error": f"Failed to get disk usage: {str(e)}"}

# === Network Tools ===
@mcp.tool()
def get_network_stats() -> dict:
    """Get network interface statistics"""
    try:
        net_stats = psutil.net_io_counters(pernic=True)
        network_info = []
        
        for interface, stats in net_stats.items():
            network_info.append({
                "interface": interface,
                "bytes_sent": stats.bytes_sent,
                "bytes_recv": stats.bytes_recv,
                "packets_sent": stats.packets_sent,
                "packets_recv": stats.packets_recv,
                "errors_in": stats.errin,
                "errors_out": stats.errout,
                "drops_in": stats.dropin,
                "drops_out": stats.dropout
            })
        
        return {"network_stats": network_info}
    except Exception as e:
        return {"error": f"Failed to get network stats: {str(e)}"}

# === Security & Authentication Tools ===
@mcp.tool()
def check_failed_logins(lines: int = 20) -> dict:
    """Check for failed login attempts"""
    try:
        # Check auth logs for failed attempts
        auth_logs = ["/var/log/auth.log", "/var/log/secure"]
        failed_logins = []
        
        for log_file in auth_logs:
            if os.path.exists(log_file):
                try:
                    result = subprocess.run(
                        ["grep", "-i", "failed", log_file],
                        capture_output=True, text=True, timeout=10
                    )
                    if result.returncode == 0:
                        failed_logins.extend(result.stdout.splitlines()[-lines:])
                        break
                except (subprocess.TimeoutExpired, FileNotFoundError):
                    continue
        
        return {"failed_logins": failed_logins[-lines:] if failed_logins else ["No failed login attempts found"]}
    except Exception as e:
        return {"error": f"Failed to check failed logins: {str(e)}"}

@mcp.tool()
def get_active_users() -> dict:
    """Get currently logged in users"""
    try:
        result = subprocess.run(
            ["who"],
            capture_output=True, text=True, timeout=5
        )
        
        users = []
        if result.returncode == 0:
            for line in result.stdout.splitlines():
                parts = line.split()
                if len(parts) >= 3:
                    users.append({
                        "user": parts[0],
                        "terminal": parts[1],
                        "login_time": " ".join(parts[2:])
                    })
        
        return {"active_users": users}
    except Exception as e:
        return {"error": f"Failed to get active users: {str(e)}"}

@mcp.tool()
def check_sudo_access(username: str) -> dict:
    """Check if a user has sudo privileges"""
    try:
        result = subprocess.run(
            ["sudo", "-l", "-U", username],
            capture_output=True, text=True, timeout=5
        )
        
        has_sudo = result.returncode == 0
        return {
            "user": username,
            "has_sudo": has_sudo,
            "sudo_rules": result.stdout if has_sudo else "No sudo access"
        }
    except Exception as e:
        return {"error": f"Failed to check sudo access: {str(e)}"}

# === Network Monitoring Tools ===
@mcp.tool()
def get_open_ports() -> dict:
    """Get list of open ports and listening services"""
    try:
        connections = psutil.net_connections(kind='inet')
        listening_ports = []
        
        for conn in connections:
            if conn.status == 'LISTEN':
                try:
                    process = psutil.Process(conn.pid) if conn.pid else None
                    process_name = process.name() if process else "Unknown"
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    process_name = "Unknown"
                
                listening_ports.append({
                    "address": conn.laddr.ip,
                    "port": conn.laddr.port,
                    "pid": conn.pid,
                    "process": process_name
                })
        
        return {"open_ports": listening_ports}
    except Exception as e:
        return {"error": f"Failed to get open ports: {str(e)}"}

@mcp.tool()
def check_network_connections() -> dict:
    """Check active network connections"""
    try:
        connections = psutil.net_connections(kind='inet')
        active_connections = []
        
        for conn in connections:
            if conn.status == 'ESTABLISHED':
                try:
                    process = psutil.Process(conn.pid) if conn.pid else None
                    process_name = process.name() if process else "Unknown"
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    process_name = "Unknown"
                
                active_connections.append({
                    "local_address": f"{conn.laddr.ip}:{conn.laddr.port}",
                    "remote_address": f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else "N/A",
                    "status": conn.status,
                    "pid": conn.pid,
                    "process": process_name
                })
        
        return {"active_connections": active_connections}
    except Exception as e:
        return {"error": f"Failed to get network connections: {str(e)}"}

@mcp.tool()
def ping_host(hostname: str, count: int = 4) -> dict:
    """Ping a host to check connectivity"""
    try:
        result = subprocess.run(
            ["ping", "-c", str(count), hostname],
            capture_output=True, text=True, timeout=30
        )
        
        return {
            "hostname": hostname,
            "success": result.returncode == 0,
            "output": result.stdout,
            "error": result.stderr if result.returncode != 0 else None
        }
    except subprocess.TimeoutExpired:
        return {"error": f"Ping to {hostname} timed out"}
    except Exception as e:
        return {"error": f"Failed to ping {hostname}: {str(e)}"}

# === System Information Tools ===
@mcp.tool()
def get_system_info() -> dict:
    """Get comprehensive system information"""
    try:
        uname = platform.uname()
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        
        return {
            "hostname": uname.node,
            "system": uname.system,
            "release": uname.release,
            "version": uname.version,
            "machine": uname.machine,
            "processor": uname.processor,
            "boot_time": boot_time.isoformat(),
            "uptime_seconds": time.time() - psutil.boot_time(),
            "python_version": platform.python_version()
        }
    except Exception as e:
        return {"error": f"Failed to get system info: {str(e)}"}

@mcp.tool()
def get_hardware_info() -> dict:
    """Get hardware information"""
    try:
        cpu_info = {}
        mem_info = psutil.virtual_memory()
        
        # Try to get CPU info from /proc/cpuinfo
        try:
            with open("/proc/cpuinfo", "r") as f:
                cpu_lines = f.readlines()
                for line in cpu_lines:
                    if "model name" in line:
                        cpu_info["model"] = line.split(":")[1].strip()
                        break
        except:
            cpu_info["model"] = "Unknown"
        
        return {
            "cpu": {
                "model": cpu_info.get("model", "Unknown"),
                "cores": psutil.cpu_count(logical=False),
                "threads": psutil.cpu_count(logical=True),
                "frequency": psutil.cpu_freq()._asdict() if psutil.cpu_freq() else {}
            },
            "memory": {
                "total_gb": round(mem_info.total / (1024**3), 2),
                "available_gb": round(mem_info.available / (1024**3), 2)
            }
        }
    except Exception as e:
        return {"error": f"Failed to get hardware info: {str(e)}"}

# === File System Tools ===
@mcp.tool()
def find_large_files(directory: str = "/", size_mb: int = 100, limit: int = 10) -> dict:
    """Find large files in the system"""
    try:
        result = subprocess.run(
            ["find", directory, "-type", "f", "-size", f"+{size_mb}M", "-exec", "ls", "-lh", "{}", "+"],
            capture_output=True, text=True, timeout=60
        )
        
        large_files = []
        if result.returncode == 0:
            lines = result.stdout.splitlines()
            for line in lines[:limit]:
                parts = line.split()
                if len(parts) >= 9:
                    large_files.append({
                        "size": parts[4],
                        "path": " ".join(parts[8:]),
                        "permissions": parts[0],
                        "owner": parts[2]
                    })
        
        return {"large_files": large_files}
    except subprocess.TimeoutExpired:
        return {"error": "Find operation timed out"}
    except Exception as e:
        return {"error": f"Failed to find large files: {str(e)}"}

@mcp.tool()
def check_disk_health() -> dict:
    """Check disk health using smartctl if available"""
    try:
        # Get list of disk devices
        disks = []
        for partition in psutil.disk_partitions():
            if partition.device.startswith('/dev/'):
                device = partition.device.rstrip('0123456789')  # Remove partition numbers
                if device not in disks:
                    disks.append(device)
        
        disk_health = []
        for disk in disks[:5]:  # Limit to first 5 disks
            try:
                result = subprocess.run(
                    ["smartctl", "-H", disk],
                    capture_output=True, text=True, timeout=10
                )
                
                health_status = "Unknown"
                if "PASSED" in result.stdout:
                    health_status = "PASSED"
                elif "FAILED" in result.stdout:
                    health_status = "FAILED"
                
                disk_health.append({
                    "device": disk,
                    "health": health_status,
                    "smart_available": result.returncode == 0
                })
            except (subprocess.TimeoutExpired, FileNotFoundError):
                disk_health.append({
                    "device": disk,
                    "health": "Unknown",
                    "smart_available": False,
                    "note": "smartctl not available"
                })
        
        return {"disk_health": disk_health}
    except Exception as e:
        return {"error": f"Failed to check disk health: {str(e)}"}

# === Docker Tools (if Docker is available) ===
@mcp.tool()
def get_docker_status() -> dict:
    """Get Docker containers and images status"""
    try:
        # Check if Docker is installed and running
        docker_version = subprocess.run(
            ["docker", "--version"],
            capture_output=True, text=True, timeout=5
        )
        
        if docker_version.returncode != 0:
            return {"error": "Docker is not installed or not accessible"}
        
        # Get containers
        containers_result = subprocess.run(
            ["docker", "ps", "-a", "--format", "json"],
            capture_output=True, text=True, timeout=10
        )
        
        containers = []
        if containers_result.returncode == 0:
            for line in containers_result.stdout.splitlines():
                if line.strip():
                    containers.append(json.loads(line))
        
        # Get images
        images_result = subprocess.run(
            ["docker", "images", "--format", "json"],
            capture_output=True, text=True, timeout=10
        )
        
        images = []
        if images_result.returncode == 0:
            for line in images_result.stdout.splitlines():
                if line.strip():
                    images.append(json.loads(line))
        
        return {
            "docker_version": docker_version.stdout.strip(),
            "containers": containers,
            "images": images
        }
    except subprocess.TimeoutExpired:
        return {"error": "Docker command timed out"}
    except Exception as e:
        return {"error": f"Failed to get Docker status: {str(e)}"}

# === Resource Usage History ===
@mcp.resource("system://usage/history/{duration}")
def get_usage_history(duration: str) -> str:
    """Get system usage history for specified duration (1h, 24h, 7d)"""
    try:
        # This would typically read from monitoring data
        # For now, return current snapshot with timestamp
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        
        timestamp = datetime.now().isoformat()
        
        usage_data = {
            "timestamp": timestamp,
            "duration": duration,
            "cpu_percent": cpu_percent,
            "memory_percent": memory.percent,
            "load_average": os.getloadavg(),
            "note": f"Current snapshot for {duration} monitoring"
        }
        
        return json.dumps(usage_data, indent=2)
    except Exception as e:
        return f"Error getting usage history: {str(e)}"

# === System Configuration Resources ===
@mcp.resource("config://system/{config_type}")
def get_system_config(config_type: str) -> str:
    """Get system configuration files"""
    config_files = {
        "network": "/etc/network/interfaces",
        "hosts": "/etc/hosts",
        "fstab": "/etc/fstab",
        "crontab": "/etc/crontab",
        "ssh": "/etc/ssh/sshd_config",
        "nginx": "/etc/nginx/nginx.conf",
        "apache": "/etc/apache2/apache2.conf"
    }
    
    if config_type not in config_files:
        return f"Unknown config type: {config_type}. Available: {', '.join(config_files.keys())}"
    
    config_file = config_files[config_type]
    
    try:
        if os.path.exists(config_file):
            with open(config_file, "r") as f:
                content = f.read()
            return f"Configuration file: {config_file}\n\n{content}"
        else:
            return f"Configuration file not found: {config_file}"
    except PermissionError:
        return f"Permission denied reading: {config_file}"
    except Exception as e:
        return f"Error reading {config_file}: {str(e)}"

# === Package Management Tools ===
@mcp.tool()
def check_package_updates() -> dict:
    """Check for available package updates"""
    try:
        # Try different package managers
        if shutil.which("apt"):
            # Debian/Ubuntu
            result = subprocess.run(
                ["apt", "list", "--upgradable"],
                capture_output=True, text=True, timeout=30
            )
            
            updates = []
            if result.returncode == 0:
                lines = result.stdout.splitlines()[1:]  # Skip header
                for line in lines[:20]:  # Limit to 20 updates
                    if "/" in line:
                        updates.append(line.split("/")[0])
            
            return {"package_manager": "apt", "available_updates": updates}
            
        elif shutil.which("yum"):
            # RHEL/CentOS
            result = subprocess.run(
                ["yum", "check-update"],
                capture_output=True, text=True, timeout=30
            )
            
            updates = result.stdout.splitlines()[:20]
            return {"package_manager": "yum", "available_updates": updates}
            
        else:
            return {"error": "No supported package manager found"}
            
    except subprocess.TimeoutExpired:
        return {"error": "Package check timed out"}
    except Exception as e:
        return {"error": f"Failed to check package updates: {str(e)}"}

@mcp.tool()
def search_package(package_name: str) -> dict:
    """Search for a package in repositories"""
    try:
        if shutil.which("apt"):
            result = subprocess.run(
                ["apt", "search", package_name],
                capture_output=True, text=True, timeout=15
            )
            
            return {
                "package_manager": "apt",
                "search_results": result.stdout.splitlines()[:10]
            }
            
        elif shutil.which("yum"):
            result = subprocess.run(
                ["yum", "search", package_name],
                capture_output=True, text=True, timeout=15
            )
            
            return {
                "package_manager": "yum",
                "search_results": result.stdout.splitlines()[:10]
            }
            
        else:
            return {"error": "No supported package manager found"}
            
    except subprocess.TimeoutExpired:
        return {"error": "Package search timed out"}
    except Exception as e:
        return {"error": f"Failed to search package: {str(e)}"}

# Update the help tool
@mcp.tool()
def get_help() -> str:
    """Get help information about available Linux debugging tools"""
    return """
🐧 LINUX DEBUG AGENT HELP GUIDE

🔍 AVAILABLE TOOLS:

💻 System Monitoring:
• "Check CPU usage" or "Show CPU stats"
• "Get memory usage" or "Check RAM"
• "Show disk usage" or "Check disk space"
• "Get network statistics"
• "Show system information"
• "Get hardware information"

📊 Process Management:
• "List running processes"
• "Show top processes by CPU usage"
• "Kill process with PID 1234"

🔒 Security & Users:
• "Check failed login attempts"
• "Show active users"
• "Check sudo access for username"

🌐 Network Monitoring:
• "Show open ports"
• "Check network connections"
• "Ping google.com"

📋 Log Analysis:
• "Show recent system logs"
• "Get error logs from system"

⚙️ Service Management:
• "Restart nginx service"
• "Check status of apache2 service"

📁 File System:
• "Find large files over 100MB"
• "Check disk health"

🐳 Container Management:
• "Get Docker status"
• "Show Docker containers"

📦 Package Management:
• "Check for package updates"
• "Search for package nginx"

🎯 EXAMPLE QUERIES:
• "What's using the most CPU and memory?"
• "Are there any failed login attempts?"
• "Show me all open ports and their processes"
• "Find large files taking up disk space"
• "Check if Docker containers are running"
• "Any available package updates?"

💡 TIP: Ask questions in natural language about your Linux system!
"""

if __name__ == "__main__":
    logger.info("Starting Linux Debug Agent MCP Server...")
    
    # Check if we should run with STDIO (for MCP client) or other transport
    transport = "stdio"  # Default to STDIO for MCP client compatibility
    
    if len(sys.argv) > 1 and sys.argv[1] == "--http":
        transport = "http"
        logger.info("Server will use HTTP transport")
    else:
        logger.info("Server will use STDIO transport for MCP client")
    
    try:
        if transport == "http":
            mcp.run(transport="http", port=8080)
        else:
            mcp.run(transport="stdio")
    except Exception as e:
        logger.error(f"Error starting server: {e}")
        sys.exit(1)
