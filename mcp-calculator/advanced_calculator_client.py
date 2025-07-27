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

class MCPCalculatorClient:
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
        """Connect to Calculator MCP server"""
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
        print("\n🧮 Connected to Calculator MCP server with tools:", [tool.name for tool in tools])

    async def process_query(self, query: str) -> str:
        """Process mathematical query using Gemini 2.5 Flash and available tools"""
        response = await self.session.list_tools()
        available_tools = response.tools
        
        # Format tools for Gemini
        tools_description = "\n".join([
            f"🛠️ Tool: {tool.name}\n📝 Description: {tool.description}\n⚙️ Parameters: {tool.inputSchema}\n"
            for tool in available_tools
        ])
        
        # Calculator-specific system prompt
        system_prompt = f"""You are an advanced mathematical assistant powered by Gemini 2.5 Flash with access to these calculator tools:

{tools_description}

🔍 TOOL USAGE INSTRUCTIONS:
When you need to use a tool, respond with ONLY a clean JSON object in this format:
{{"tool_call": {{"name": "tool_name", "arguments": {{"param1": value1, "param2": value2}}}}}}

📋 EXAMPLES:
- Addition: {{"tool_call": {{"name": "add", "arguments": {{"a": 15, "b": 27}}}}}}
- Division: {{"tool_call": {{"name": "divide", "arguments": {{"a": 100, "b": 4}}}}}}
- Square root: {{"tool_call": {{"name": "sqrt", "arguments": {{"a": 144}}}}}}
- Factorial: {{"tool_call": {{"name": "factorial", "arguments": {{"a": 5}}}}}}
- Trigonometry: {{"tool_call": {{"name": "sin", "arguments": {{"a": 30}}}}}}
- Power: {{"tool_call": {{"name": "power", "arguments": {{"a": 2, "b": 3}}}}}}

🔢 IMPORTANT RULES:
- Always use numerical values, not strings, for mathematical parameters
- For trigonometric functions, angles are in degrees
- Factorial requires non-negative integers only
- Division by zero is not allowed

🎯 Always prioritize mathematical accuracy and provide clear explanations.
"""

        full_prompt = f"{system_prompt}\n\n🧮 User query: {query}"
        
        try:
            generation_config = {
                "temperature": 0.1,  # Lower temperature for math precision
                "top_p": 0.9,
                "top_k": 50,
                "max_output_tokens": 1500,
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
                        
                        print(f"⚡ Executing calculator tool: {tool_name} with args: {tool_args}")
                        
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
                        final_prompt = f"""🧮 MATHEMATICAL CALCULATION ANALYSIS

User Query: "{query}"
Calculator Tool Used: {tool_name}
Tool Arguments: {tool_args}

📊 CALCULATION RESULT:
{content}

🎯 INSTRUCTIONS:
Provide a clear, educational response that:
1. States the mathematical operation performed
2. Shows the calculation result clearly
3. Explains the mathematical concept if helpful
4. Provides context or verification if appropriate
5. Uses proper mathematical notation and formatting

Please provide your mathematical analysis now:"""
                        
                        final_response = self.model.generate_content(
                            final_prompt,
                            generation_config=generation_config
                        )
                        return f"🧮 Mathematical Result:\n\n{final_response.text}"
                        
                except (json.JSONDecodeError, KeyError) as e:
                    print(f"❌ JSON parsing error: {e}")
                    return f"I attempted to use a calculator tool but encountered a parsing issue. Here's what I received: {response_text}"
            
            return response_text
            
        except Exception as e:
            return f"⚠️ Error processing mathematical query: {str(e)}"

    async def chat_loop(self):
        """Run interactive calculator chat"""
        print("\n🧮 Calculator MCP Client with Gemini 2.5 Flash Started!")
        print("=" * 60)
        print("💡 TIP: Ask mathematical questions like 'What is 15 + 27?'")
        print("💡 TIP: Try 'Calculate the square root of 144'")
        print("💡 TIP: Type 'quit' to exit")
        print("=" * 60)

        while True:
            try:
                query = input("\n🔢 Math Query: ").strip()

                if query.lower() == 'quit':
                    print("👋 Thanks for using the calculator client!")
                    break

                if not query:
                    print("❓ Please enter a mathematical query.")
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
        print("Usage: python3 advanced_calculator_client.py <path_to_calculator_server.py>")
        print("Example: python3 advanced_calculator_client.py mcp_server.py")
        sys.exit(1)

    client = MCPCalculatorClient()
    try:
        await client.connect_to_server(sys.argv[1])
        await client.chat_loop()
    finally:
        await client.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
• "What is 7 factorial?"
• "Divide 156 by 12"

🎯 TIP: You can ask in natural language! I'll understand and perform the calculations for you.
"""

    async def chat_loop(self):
        """Run an interactive chat loop"""
        print("\n🧮 MCP Scientific Calculator with Gemini 2.5 Flash Started!")
        print("=" * 65)
        print("💡 TIP: Type 'help' to see available mathematical operations")
        print("💡 TIP: Ask math questions in natural language")
        print("💡 TIP: Type 'quit' to exit")
        print("=" * 65)

        while True:
            try:
                query = input("\n🧮 Math Query: ").strip()

                if query.lower() == 'quit':
                    print("👋 Thanks for using the calculator!")
                    break

                if not query:
                    print("❓ Please enter a mathematical query or type 'help' for examples.")
                    continue

                response = await self.process_query(query)
                print("\n" + "="*65)
                print(response)
                print("="*65)

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
        print("Usage: python3 advanced_calculator_client.py <path_to_server_script>")
        print("Example: python3 advanced_calculator_client.py mcp_server.py")
        sys.exit(1)

    client = MCPCalculatorClient()
    try:
        await client.connect_to_server(sys.argv[1])
        await client.chat_loop()
    finally:
        await client.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
