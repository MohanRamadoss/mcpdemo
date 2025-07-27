import subprocess

def register(mcp):
    @mcp.tool()
    def list_users() -> dict:
        """List all local users on the system."""
        try:
            with open('/etc/passwd', 'r') as f:
                users = [line.split(':')[0] for line in f]
            return {"users": users}
        except Exception as e:
            return {"error": str(e)}

    @mcp.tool()
    def add_user(username: str) -> dict:
        """Add a new system user."""
        try:
            result = subprocess.run(["useradd", "-m", username], capture_output=True, text=True)
            if result.returncode == 0:
                return {"status": f"User '{username}' added successfully."}
            else:
                return {"error": result.stderr.strip()}
        except Exception as e:
            return {"error": str(e)}

    @mcp.tool()
    def delete_user(username: str) -> dict:
        """Delete a system user and their home directory."""
        try:
            result = subprocess.run(["userdel", "-r", username], capture_output=True, text=True)
            if result.returncode == 0:
                return {"status": f"User '{username}' deleted successfully."}
            else:
                return {"error": result.stderr.strip()}
        except Exception as e:
            return {"error": str(e)}
