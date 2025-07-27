def register(mcp):
    @mcp.tool()
    def get_help() -> str:
        """Get help information about available Linux debugging tools"""
        return """
🐧 LINUX DEBUG AGENT HELP GUIDE

🔍 AVAILABLE TOOLS:

💻 System Monitoring:
• "Check CPU usage", "Get memory usage", "Show disk usage", "Get network statistics"
• "Show system information", "Get hardware information"

📊 Process Management:
• "List running processes", "Show top processes by CPU usage", "Kill process with PID 1234"

🔒 Security & Users:
• "Check failed login attempts", "Show active users", "Check sudo access for username"
• "List users", "Add user <name>", "Delete user <name>"

🌐 Network Monitoring:
• "Show open ports", "Check network connections", "Ping google.com"

📋 Log Analysis:
• "Show recent system logs", "Get error logs from system"

⚙️ Service Management:
• "Restart nginx service", "Check status of apache2 service"

📁 File System:
• "Find large files over 100MB", "Check disk health", "View file /etc/hosts"

🐳 Container Management:
• "Get Docker status", "Show Docker containers"

📦 Package Management:
• "Check for package updates", "Search for package nginx"

🔥 Firewall Management:
• "Get firewall status", "Allow port 80", "Deny port 22"

🎯 EXAMPLE QUERIES:
• "What's using the most CPU and memory?"
• "Are there any failed login attempts?"
• "Show me all open ports and their processes"
• "Find large files taking up disk space"
• "Check if Docker containers are running"
• "Any available package updates?"
• "Add a new user named 'testuser'"
• "Show me the firewall status"

💡 TIP: Ask questions in natural language about your Linux system!
"""
