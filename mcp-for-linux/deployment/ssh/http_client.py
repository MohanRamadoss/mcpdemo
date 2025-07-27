#!/usr/bin/env python3
"""
HTTP-based MCP Linux Client for remote server connections
"""
import sys
import asyncio
import aiohttp
import json
import logging

import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()

class MCPLinuxHTTPClient:
    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url.rstrip('/')
        
        # Configure logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Configure Google AI
        api_key = os.getenv("GOOGLE_API_KEY", "AIzaSyC2YmGx9-_yx9QzW3D0qCEgvV03U9zik9E")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Available tools (mock the MCP tools structure)
        self.available_tools = [
            {
                "name": "get_cpu_usage",
                "description": "Get current CPU usage statistics",
                "parameters": {}
            },
            {
                "name": "get_memory_usage", 
                "description": "Get current memory usage statistics",
                "parameters": {}
            },
            {
                "name": "list_processes",
                "description": "List running processes with details",
                "parameters": {"limit": {"type": "integer", "default": 20}}
            },
            {
                "name": "get_top_processes",
                "description": "Get top processes by CPU and memory usage", 
                "parameters": {"limit": {"type": "integer", "default": 10}}
            },
            {
                "name": "get_system_logs",
                "description": "Get recent system log entries",
                "parameters": {"lines": {"type": "integer", "default": 50}}
            },
            {
                "name": "get_service_status",
                "description": "Get status of a system service",
                "parameters": {"service_name": {"type": "string"}}
            },
            {
                "name": "get_help",
                "description": "Get help information about available tools",
                "parameters": {}
            }
        ]

    async def test_connection(self) -> bool:
        """Test connection to remote MCP server"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/health", timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        self.logger.info(f"✅ Connected to MCP server: {data}")
                        return True
                    else:
                        self.logger.error(f"❌ Server returned status {response.status}")
                        return False
        except Exception as e:
            self.logger.error(f"❌ Connection failed: {e}")
            return False

    async def call_tool_via_http(self, tool_name: str, parameters: dict = None) -> dict:
        """Call a tool via HTTP API (simulated)"""
        # Note: This is a simulation since the current HTTP server doesn't expose individual tools
        # In a real implementation, you'd need specific endpoints for each tool
        
        if parameters is None:
            parameters = {}
            
        try:
            async with aiohttp.ClientSession() as session:
                # For now, we'll use the health endpoint and simulate tool responses
                async with session.get(f"{self.base_url}/health") as response:
                    if response.status == 200:
                        # Simulate tool responses based on tool name
                        if tool_name == "get_help":
                            return {
                                "success": True,
                                "content": """
🐧 LINUX DEBUG AGENT HTTP CLIENT

Available commands:
• "Check CPU usage" - Get system CPU statistics
• "Show memory usage" - Get memory information  
• "List processes" - Show running processes
• "Get system logs" - Show recent log entries
• "Check service status nginx" - Check specific service

Note: This is an HTTP client connecting to a remote MCP server.
For full functionality, use the SSH tunnel with the native MCP client.
"""
                            }
                        elif tool_name == "get_cpu_usage":
                            return {
                                "success": True, 
                                "content": "CPU usage information would be retrieved from the remote server"
                            }
                        else:
                            return {
                                "success": True,
                                "content": f"Tool '{tool_name}' executed with parameters: {parameters}"
                            }
                    else:
                        return {"success": False, "error": f"HTTP {response.status}"}
                        
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def process_query(self, query: str) -> str:
        """Process a query using Gemini and simulated tool calls"""
        
        # Format tools for Gemini
        tools_description = "\n".join([
            f"🔧 Tool: {tool['name']}\n📝 Description: {tool['description']}\n"
            for tool in self.available_tools
        ])
        
        system_prompt = f"""You are a Linux system administrator assistant with access to these tools via HTTP:

{tools_description}

🔍 TOOL USAGE:
When you need to use a tool, respond with a JSON object:
{{"tool_call": {{"name": "tool_name", "arguments": {{"param": "value"}}}}}}

📋 EXAMPLES:
- CPU info: {{"tool_call": {{"name": "get_cpu_usage", "arguments": {{}}}}}}
- Process list: {{"tool_call": {{"name": "list_processes", "arguments": {{"limit": 10}}}}}}
- Service status: {{"tool_call": {{"name": "get_service_status", "arguments": {{"service_name": "nginx"}}}}}}
- Help: {{"tool_call": {{"name": "get_help", "arguments": {{}}}}}}

🎯 Analyze the user query and provide appropriate tool calls or direct responses.
"""

        # Check for help requests
        if any(keyword in query.lower() for keyword in ["help", "what can", "commands"]):
            result = await self.call_tool_via_http("get_help")
            return result.get("content", "Help information not available")

        try:
            # Get Gemini response
            response = self.model.generate_content(
                f"{system_prompt}\n\n🐧 User query: {query}",
                generation_config={
                    "temperature": 0.2,
                    "max_output_tokens": 1500
                }
            )
            
            response_text = response.text.strip()
            
            # Check for tool calls
            if '"tool_call"' in response_text:
                try:
                    import json
                    json_start = response_text.find('{"tool_call"')
                    if json_start != -1:
                        json_end = response_text.find('}', json_start) + 1
                        tool_call_json = response_text[json_start:json_end + response_text[json_end:].find('}')]
                        
                        tool_call = json.loads(tool_call_json)
                        tool_name = tool_call["tool_call"]["name"]
                        tool_args = tool_call["tool_call"].get("arguments", {})
                        
                        self.logger.info(f"🔧 Calling tool: {tool_name}")
                        
                        # Execute tool
                        result = await self.call_tool_via_http(tool_name, tool_args)
                        
                        if result.get("success"):
                            return f"🐧 Remote Linux Server Response:\n\n{result['content']}"
                        else:
                            return f"❌ Tool execution failed: {result.get('error', 'Unknown error')}"
                            
                except json.JSONDecodeError:
                    pass
            
            return response_text
            
        except Exception as e:
            return f"⚠️ Error processing query: {str(e)}"

    async def chat_loop(self):
        """Run interactive chat loop"""
        print(f"\n🐧 MCP Linux HTTP Client Connected to {self.base_url}")
        print("=" * 70)
        print("💡 TIP: Type 'help' to see available commands")
        print("💡 TIP: This client connects to remote MCP server via HTTP")
        print("💡 TIP: Type 'quit' to exit")
        print("=" * 70)

        # Test connection first
        if not await self.test_connection():
            print("❌ Failed to connect to remote MCP server")
            print(f"📍 Check if server is running at: {self.base_url}")
            return

        while True:
            try:
                query = input("\n🐧 Linux Query: ").strip()

                if query.lower() == 'quit':
                    print("👋 Disconnecting from remote server...")
                    break

                if not query:
                    print("❓ Please enter a system query or type 'help'")
                    continue

                response = await self.process_query(query)
                print("\n" + "="*70)
                print(response)
                print("="*70)

            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {str(e)}")

async def main():
    """Main function"""
    base_url = "http://localhost:8080"
    
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    
    print(f"🌐 Connecting to remote MCP server at: {base_url}")
    
    client = MCPLinuxHTTPClient(base_url)
    await client.chat_loop()

if __name__ == "__main__":
    asyncio.run(main())
