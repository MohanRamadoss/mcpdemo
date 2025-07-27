import psutil

def register(mcp):
    @mcp.tool()
    def list_processes(limit: int = 20) -> dict:
        """List running processes with details."""
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_percent', 'status']):
                try:
                    processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            sorted_procs = sorted(processes, key=lambda p: p.get('cpu_percent', 0), reverse=True)
            return {"processes": sorted_procs[:limit]}
        except Exception as e:
            return {"error": str(e)}

    @mcp.tool()
    def get_top_processes(limit: int = 10) -> dict:
        """Get top processes by combined CPU and memory usage."""
        try:
            procs = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    procs.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            sorted_procs = sorted(procs, key=lambda p: (p.get('cpu_percent', 0) + p.get('memory_percent', 0)), reverse=True)
            return {"top_processes": sorted_procs[:limit]}
        except Exception as e:
            return {"error": str(e)}

    @mcp.tool()
    def kill_process(pid: int) -> dict:
        """Kill a process by its PID."""
        try:
            process = psutil.Process(pid)
            process_name = process.name()
            process.terminate()
            try:
                process.wait(timeout=3)
                return {"status": f"Process {pid} ({process_name}) terminated."}
            except psutil.TimeoutExpired:
                process.kill()
                return {"status": f"Process {pid} ({process_name}) forcefully killed."}
        except psutil.NoSuchProcess:
            return {"error": f"Process with PID {pid} not found."}
        except psutil.AccessDenied:
            return {"error": f"Permission denied to kill process {pid}."}
        except Exception as e:
            return {"error": str(e)}
        except Exception as e:
            return {"error": str(e)}
