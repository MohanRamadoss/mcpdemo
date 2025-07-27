import subprocess

def register(mcp):
    @mcp.resource("cron://{user}")
    def get_cron_jobs(user: str) -> str:
        """Get cron jobs for a specific user."""
        try:
            result = subprocess.run(["crontab", "-l", "-u", user], capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout
            else:
                return f"No cron jobs found for user '{user}' or error: {result.stderr.strip()}"
        except Exception as e:
            return f"Error getting cron jobs: {str(e)}"
