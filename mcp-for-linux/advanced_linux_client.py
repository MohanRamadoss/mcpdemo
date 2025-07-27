import sys
import asyncio
from typing import Optional
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

import google.generativeai as genai
from dotenv import load_dotenv
import os

# Load environment variables from parent directory .env file
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
load_dotenv(env_path)

class MCPLinuxClient:
    def __init__(self):
        # Initialize session and client objects
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        
        # Configure Google AI with API key from .env file
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables. Please check your .env file.")
        
        genai.configure(api_key=api_key)
        print(f"✅ Configured Gemini 2.5 Flash with API key: {api_key[:8]}...")
        
        # Use Gemini 2.5 Flash model
        self.model = genai.GenerativeModel('gemini-2.5-flash')
    
    async def connect_to_server(self, server_script_path: str):
        """Connect to Linux MCP server"""
        server_params = StdioServerParameters(
            command="python3",
            args=[server_script_path],
            env=None
        )

        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))

        await self.session.initialize()

        # List available tools
        response = await self.session.list_tools()
        tools = response.tools
        print(f"\n🐧 Connected to Linux MCP server with {len(tools)} tools:", [tool.name for tool in tools[:10]], "..." if len(tools) > 10 else "")

    async def process_query(self, query: str) -> str:
        """Process Linux system query using Gemini 2.5 Flash and available tools"""
        response = await self.session.list_tools()
        available_tools = response.tools
        
        # Format tools for Gemini (truncate if too many)
        tools_description = "\n".join([
            f"🛠️ Tool: {tool.name}\n📝 Description: {tool.description}\n"
            for tool in available_tools[:20]  # Limit to prevent prompt overflow
        ])
        
        if len(available_tools) > 20:
            tools_description += f"\n... and {len(available_tools) - 20} more tools available"
        
        # Linux-specific system prompt
        system_prompt = f"""You are an advanced Linux system administrator assistant powered by Gemini 2.5 Flash with access to these system tools:

{tools_description}

🔍 TOOL USAGE INSTRUCTIONS:
When you need to use a tool, respond with ONLY a clean JSON object in this format:
{{"tool_call": {{"name": "tool_name", "arguments": {{"param1": "value1", "param2": value2}}}}}}

📋 EXAMPLES:
- CPU usage: {{"tool_call": {{"name": "get_cpu_usage", "arguments": {{}}}}}}
- Memory info: {{"tool_call": {{"name": "get_memory_usage", "arguments": {{}}}}}}
- Process list: {{"tool_call": {{"name": "list_processes", "arguments": {{"limit": 10}}}}}}
- Service status: {{"tool_call": {{"name": "get_service_status", "arguments": {{"service_name": "nginx"}}}}}}
- System logs: {{"tool_call": {{"name": "get_system_logs", "arguments": {{"lines": 20}}}}}}
- Help: {{"tool_call": {{"name": "get_help", "arguments": {{}}}}}}

🐧 LINUX ADMINISTRATION:
- Monitor system performance and resource usage
- Manage processes and services
- Analyze system logs and troubleshoot issues
- Check system security and user access

🎯 Always prioritize system security and provide clear technical information.
"""

        # Check for help requests
        help_keywords = ["help", "example", "query", "what can", "how to", "commands", "options"]
        if any(keyword in query.lower() for keyword in help_keywords):
            try:
                result = await self.session.call_tool("get_help", {})
                content = result.content[0].text if hasattr(result, 'content') and result.content else str(result.content)
                return content
            except Exception as e:
                return "I can help you manage Linux systems! Try asking about CPU usage, memory, processes, services, or system logs."

        full_prompt = f"{system_prompt}\n\n🐧 User query: {query}"
        
        try:
            generation_config = {
                "temperature": 0.2,
                "top_p": 0.9,
                "top_k": 50,
                "max_output_tokens": 2000,
                "response_mime_type": "text/plain"
            }
            
            response = self.model.generate_content(
                full_prompt,
                generation_config=generation_config
            )
            response_text = response.text.strip()
            
            print(f"🤖 Gemini 2.5 Flash response: {response_text[:100]}...")
            
            # Check if response contains a tool call
            if response_text.startswith('{"tool_call"') or '"tool_call"' in response_text:
                try:
                    import json
                    json_start = response_text.find('{"tool_call"')
                    if json_start != -1:
                        brace_count = 0
                        json_end = json_start
                        for i, char in enumerate(response_text[json_start:], json_start):
                            if char == '{':
                                brace_count += 1
                            elif char == '}':
                                brace_count -= 1
                                if brace_count == 0:
                                    json_end = i + 1
                                    break
                        
                        tool_call_json = response_text[json_start:json_end]
                        print(f"🔧 Tool call JSON: {tool_call_json}")
                        
                        tool_call = json.loads(tool_call_json)
                        tool_name = tool_call["tool_call"]["name"]
                        tool_args = tool_call["tool_call"]["arguments"]
                        
                        print(f"⚡ Executing Linux tool: {tool_name} with args: {tool_args}")
                        
                        # Execute tool call
                        result = await self.session.call_tool(tool_name, tool_args)
                        
                        # Extract content from result
                        if hasattr(result, 'content'):
                            if isinstance(result.content, list) and len(result.content) > 0:
                                content = result.content[0].text if hasattr(result.content[0], 'text') else str(result.content[0])
                            else:
                                content = str(result.content)
                        else:
                            content = str(result)
                        
                        # Generate enhanced response
                        final_prompt = f"""🐧 LINUX SYSTEM ANALYSIS REQUEST

User Query: "{query}"
Linux Tool Used: {tool_name}
Tool Arguments: {tool_args}

📊 SYSTEM DATA RECEIVED:
{content}

🎯 INSTRUCTIONS:
Analyze the Linux system data and provide a comprehensive, well-formatted response that:
1. Directly answers the user's system administration question
2. Highlights important system information, alerts, or issues
3. Uses clear, technical language appropriate for system administrators
4. Formats data in an easy-to-read structure
5. Includes relevant recommendations, troubleshooting steps, or next actions
6. Shows resource usage, process IDs, and system statuses clearly

Please provide your Linux system analysis now:"""
                        
                        final_response = self.model.generate_content(
                            final_prompt,
                            generation_config=generation_config
                        )
                        return f"🐧 Linux System Information:\n\n{final_response.text}"
                        
                except (json.JSONDecodeError, KeyError) as e:
                    print(f"❌ JSON parsing error: {e}")
                    return f"I attempted to use a Linux tool but encountered a parsing issue. Here's what I received: {response_text}"
            
            return response_text
            
        except Exception as e:
            return f"⚠️ Error processing Linux query: {str(e)}"

    async def chat_loop(self):
        """Run interactive Linux system administration chat"""
        print("\n🐧 Linux System Administration MCP Client Started!")
        print("=" * 60)
        print("💡 TIP: Ask about system performance, processes, services, or logs")
        print("💡 TIP: Try 'What is using the most CPU?' or 'Check memory usage'")
        print("💡 TIP: Type 'help' for complete command guide")
        print("💡 TIP: Type 'quit' to exit")
        print("=" * 60)

        while True:
            try:
                query = input("\n🖥️ Linux Query: ").strip()

                if query.lower() == 'quit':
                    print("👋 Thanks for using Linux MCP client!")
                    break

                if not query:
                    print("❓ Please enter a Linux system query or type 'help' for examples.")
                    continue

                response = await self.process_query(query)
                print("\n" + "="*60)
                print(response)
                print("="*60)

            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {str(e)}")

    async def cleanup(self):
        """Clean up resources"""
        await self.exit_stack.aclose()

async def main():
    if len(sys.argv) < 2:
        print("Usage: python3 advanced_linux_client.py <path_to_linux_server.py>")
        print("Example: python3 advanced_linux_client.py main.py")
        sys.exit(1)

    client = MCPLinuxClient()
    try:
        await client.connect_to_server(sys.argv[1])
        await client.chat_loop()
    finally:
        await client.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
    async def cleanup(self):
        """Clean up resources"""
        await self.exit_stack.aclose()

async def main():
    if len(sys.argv) < 2:
        print("Usage: python3 advanced_linux_client.py <path_to_server_script>")
        print("Example: python3 advanced_linux_client.py main.py")
        sys.exit(1)

    client = MCPLinuxClient()
    try:
        await client.connect_to_server(sys.argv[1])
        await client.chat_loop()
    finally:
        await client.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
