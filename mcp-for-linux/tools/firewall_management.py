import subprocess

def register(mcp):
    @mcp.tool()
    def get_firewall_status() -> dict:
        """Get the status of the UFW firewall."""
        try:
            result = subprocess.run(["ufw", "status"], capture_output=True, text=True)
            return {"status": result.stdout.strip()}
        except Exception as e:
            return {"error": str(e)}

    @mcp.tool()
    def allow_port(port: int, protocol: str = "tcp") -> dict:
        """Allow traffic on a specific port."""
        try:
            result = subprocess.run(["ufw", "allow", str(port), f"/{protocol}"], capture_output=True, text=True)
            return {"status": result.stdout.strip()}
        except Exception as e:
            return {"error": str(e)}

    @mcp.tool()
    def deny_port(port: int, protocol: str = "tcp") -> dict:
        """Deny traffic on a specific port."""
        try:
            result = subprocess.run(["ufw", "deny", str(port), f"/{protocol}"], capture_output=True, text=True)
            return {"status": result.stdout.strip()}
        except Exception as e:
            return {"error": str(e)}
