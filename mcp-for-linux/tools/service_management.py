import subprocess

def register(mcp):
    @mcp.tool()
    def restart_service(service_name: str) -> dict:
        """Restart a system service (e.g., nginx, apache2)."""
        try:
            result = subprocess.run(["systemctl", "restart", service_name], capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                return {"status": f"Service '{service_name}' restarted successfully."}
            else:
                return {"error": result.stderr.strip()}
        except Exception as e:
            return {"error": str(e)}

    @mcp.tool()
    def get_service_status(service_name: str) -> dict:
        """Get the status of a system service."""
        try:
            result = subprocess.run(["systemctl", "status", service_name], capture_output=True, text=True, timeout=10)
            return {
                "service": service_name,
                "status_output": result.stdout,
                "is_active": "active" in result.stdout,
                "return_code": result.returncode
            }
        except Exception as e:
            return {"error": str(e)}
