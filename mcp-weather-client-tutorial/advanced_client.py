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

class MCPClient:
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
        
        # Use Gemini 2.5 Flash model (latest and most capable)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
    
    async def connect_to_server(self, server_script_path: str):
        """Connect to an MCP server

        Args:
            server_script_path: Path to the server script (.py or .js)
        """
        is_python = server_script_path.endswith('.py')
        is_js = server_script_path.endswith('.js')
        if not (is_python or is_js):
            raise ValueError("Server script must be a .py or .js file")

        command = "python" if is_python else "node"
        server_params = StdioServerParameters(
            command=command,
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
        print("\nConnected to server with tools:", [tool.name for tool in tools])

    async def process_query(self, query: str) -> str:
        """Process a query using Gemini 2.5 Flash and available tools"""
        response = await self.session.list_tools()
        available_tools = response.tools
        
        # Format tools for Gemini with enhanced structure for 2.5 Flash
        tools_description = "\n".join([
            f"🛠️ Tool: {tool.name}\n📝 Description: {tool.description}\n⚙️ Parameters: {tool.inputSchema}\n"
            for tool in available_tools
        ])
        
        # Enhanced system prompt optimized for Gemini 2.5 Flash
        system_prompt = f"""You are an advanced weather assistant powered by Gemini 2.5 Flash with access to these weather tools:

{tools_description}

🔍 TOOL USAGE INSTRUCTIONS:
When you need to use a tool, respond with ONLY a clean JSON object in this format:
{{"tool_call": {{"name": "tool_name", "arguments": {{"param1": "value1", "param2": "value2"}}}}}}

📋 EXAMPLES:
- Weather alerts: {{"tool_call": {{"name": "get_alerts", "arguments": {{"state": "CA"}}}}}}
- US Forecast: {{"tool_call": {{"name": "get_forecast", "arguments": {{"latitude": 40.7128, "longitude": -74.0060}}}}}}
- City coordinates: {{"tool_call": {{"name": "get_coordinates", "arguments": {{"city": "Singapore"}}}}}}
- International weather info: {{"tool_call": {{"name": "get_international_weather_info", "arguments": {{"location": "Singapore"}}}}}}
- Help/Examples: {{"tool_call": {{"name": "get_help", "arguments": {{}}}}}}

🌍 IMPORTANT RULES:
- For international locations (non-US), use get_coordinates or get_international_weather_info
- Weather forecasts only work for US locations
- Always explain limitations for international requests
- If user asks about weather in international cities, use appropriate international tools

💬 If the user asks about what they can query, examples, or help, use the get_help tool.
🎯 Always prioritize accuracy and clarity in your responses.
"""

        # Check if user is asking for help or examples
        help_keywords = ["help", "example", "query", "what can", "how to", "what to ask", "commands", "options"]
        if any(keyword in query.lower() for keyword in help_keywords):
            try:
                result = await self.session.call_tool("get_help", {})
                # Extract text content properly
                content = result.content[0].text if hasattr(result, 'content') and result.content else str(result.content)
                return content
            except Exception as e:
                return "I can help you with weather queries! Try asking about weather alerts for US states or forecasts for US coordinates. For international locations, I can provide coordinates and guidance."

        # Enhanced international location detection
        international_cities = [
            "singapore", "london", "tokyo", "paris", "berlin", "rome", "madrid", "sydney", 
            "toronto", "beijing", "shanghai", "hong kong", "seoul", "mumbai", "delhi", 
            "bangkok", "kuala lumpur", "jakarta", "manila", "melbourne", "amsterdam", 
            "zurich", "vienna", "stockholm", "copenhagen", "vancouver", "mexico city", 
            "sao paulo", "rio de janeiro", "buenos aires", "cairo", "lagos", 
            "johannesburg", "dubai", "tel aviv", "riyadh"
        ]
        
        # Check if user is asking about international weather
        query_lower = query.lower()
        detected_city = None
        
        for city in international_cities:
            if city in query_lower:
                detected_city = city
                break
        
        # Handle direct tool calls like "get_international_weather_info singapore"
        if query_lower.startswith("get_international_weather_info"):
            parts = query.split()
            if len(parts) > 1:
                location = " ".join(parts[1:]).title()
                try:
                    result = await self.session.call_tool("get_international_weather_info", {"location": location})
                    # Extract text content properly
                    content = result.content[0].text if hasattr(result, 'content') and result.content else str(result.content)
                    return content
                except Exception as e:
                    return f"Error getting international weather info: {str(e)}"
            else:
                return "Please specify a location. Example: 'get_international_weather_info Singapore'"
        
        # Handle coordinate requests like "get_coordinates singapore"
        if query_lower.startswith("get_coordinates"):
            parts = query.split()
            if len(parts) > 1:
                city = " ".join(parts[1:]).title()
                try:
                    result = await self.session.call_tool("get_coordinates", {"city": city})
                    # Extract text content properly
                    content = result.content[0].text if hasattr(result, 'content') and result.content else str(result.content)
                    return content
                except Exception as e:
                    return f"Error getting coordinates: {str(e)}"
            else:
                return "Please specify a city. Example: 'get_coordinates Singapore'"
        
        # Auto-detect international weather requests
        weather_keywords = ["weather", "forecast", "temperature", "conditions", "climate"]
        if detected_city and any(weather in query_lower for weather in weather_keywords):
            try:
                result = await self.session.call_tool("get_international_weather_info", {"location": detected_city.title()})
                # Extract text content properly
                content = result.content[0].text if hasattr(result, 'content') and result.content else str(result.content)
                return content
            except Exception:
                pass

        # Initial prompt to Gemini 2.5 Flash
        full_prompt = f"{system_prompt}\n\n🌤️ User query: {query}"
        
        try:
            # Optimized generation settings for Gemini 2.5 Flash
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
                    # Enhanced JSON extraction for Gemini 2.5 Flash
                    json_start = response_text.find('{"tool_call"')
                    if json_start != -1:
                        # Find the matching closing brace with better parsing
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
                        
                        print(f"⚡ Executing tool: {tool_name} with args: {tool_args}")
                        
                        # Execute tool call
                        result = await self.session.call_tool(tool_name, tool_args)
                        
                        # Extract text content properly from result
                        if hasattr(result, 'content'):
                            if isinstance(result.content, list) and len(result.content) > 0:
                                content = result.content[0].text if hasattr(result.content[0], 'text') else str(result.content[0])
                            else:
                                content = str(result.content)
                        else:
                            content = str(result)
                        
                        # Enhanced final response generation with Gemini 2.5 Flash
                        final_prompt = f"""🌤️ WEATHER ANALYSIS REQUEST

User Query: "{query}"
Tool Used: {tool_name}
Tool Arguments: {tool_args}

📊 WEATHER DATA RECEIVED:
{content}

🎯 INSTRUCTIONS:
Analyze the weather data and provide a comprehensive, well-formatted response that:
1. Directly answers the user's question
2. Highlights important weather information
3. Uses clear, engaging language
4. Formats data in an easy-to-read structure
5. Includes relevant warnings or recommendations if applicable

Please provide your analysis now:"""
                        
                        final_response = self.model.generate_content(
                            final_prompt,
                            generation_config=generation_config
                        )
                        return f"📍 Weather Information:\n\n{final_response.text}"
                        
                except (json.JSONDecodeError, KeyError) as e:
                    print(f"❌ JSON parsing error: {e}")
                    print(f"🔍 Response text: {response_text}")
                    return f"I attempted to use a weather tool but encountered a parsing issue. Here's what I received: {response_text}"
            
            return response_text
            
        except Exception as e:
            return f"⚠️ Error processing query with Gemini 2.5 Flash: {str(e)}"

    async def chat_loop(self):
        """Run an interactive chat loop"""
        print("\n🌤️ MCP Weather Client with Gemini 2.5 Flash Started!")
        print("=" * 60)
        print("💡 TIP: Type 'help' to see what queries you can ask")
        print("💡 TIP: Try 'weather in Singapore' or 'coordinates for Tokyo'")
        print("💡 TIP: Type 'quit' to exit")
        print("=" * 60)

        while True:
            try:
                query = input("\n🌍 Weather Query: ").strip()

                if query.lower() == 'quit':
                    print("👋 Thanks for using the weather client!")
                    break

                if not query:
                    print("❓ Please enter a weather query or type 'help' for examples.")
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

    async def test_connection():
        client = MCPClient()
        print("Chat interface methods added successfully!")

async def main():
    if len(sys.argv) < 2:
        print("Usage: python advanced_client.py <path_to_server_script>")
        sys.exit(1)

    client = MCPClient()
    try:
        await client.connect_to_server(sys.argv[1])
        await client.chat_loop()
    finally:
        await client.cleanup()

if __name__ == "__main__":
    asyncio.run(main())