import sys
import asyncio
from typing import Optional
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

import google.generativeai as genai
from dotenv import load_dotenv
import os

class AWSMCPClient:
    def __init__(self):
        # Initialize session and client objects
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        
        # Load environment variables from current directory .env file
        env_path = os.path.join(os.path.dirname(__file__), '.env')
        load_dotenv(env_path)
        
        # Configure Google AI with API key from .env file
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            # Try to get from current directory .env file directly
            if os.path.exists('.env'):
                load_dotenv('.env')
                api_key = os.getenv("GOOGLE_API_KEY")
        
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables. Please check your .env file.")
        
        genai.configure(api_key=api_key)
        print(f"✅ Configured Gemini 2.5 Flash with API key: {api_key[:8]}...")
        
        # Use Gemini 2.5 Flash model
        self.model = genai.GenerativeModel('gemini-2.5-flash')
    
    async def connect_to_server(self, server_script_path: str):
        """Connect to AWS MCP server"""
        try:
            # Check if server script exists
            if not os.path.exists(server_script_path):
                raise FileNotFoundError(f"Server script not found: {server_script_path}")
            
            print(f"🔄 Starting AWS MCP server: {server_script_path}")
            
            server_params = StdioServerParameters(
                command="python3",
                args=[server_script_path],
                env=None
            )

            stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
            self.stdio, self.write = stdio_transport
            self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))

            print("🤝 Initializing MCP session...")
            await self.session.initialize()

            # List available tools
            response = await self.session.list_tools()
            tools = response.tools
            print(f"\n🌩️ Connected to AWS MCP server with {len(tools)} tools:")
            for tool in tools:
                print(f"  • {tool.name}")
            
        except Exception as e:
            print(f"❌ Failed to connect to server: {e}")
            print("\n🔧 Troubleshooting tips:")
            print("1. Make sure aws_server.py exists and is executable")
            print("2. Check that all dependencies are installed (run: pip install -r requirements.txt)")
            print("3. Verify AWS credentials are configured (run: aws sts get-caller-identity)")
            print("4. Try running the server directly: python3 aws_server.py")
            raise

    async def process_query(self, query: str) -> str:
        """Process AWS query using Gemini 2.5 Flash and available tools"""
        if not self.session:
            return "❌ Not connected to MCP server. Please restart the client."
        
        try:
            response = await self.session.list_tools()
            available_tools = response.tools
            
            # Format tools for Gemini
            tools_description = "\n".join([
                f"🛠️ Tool: {tool.name}\n📝 Description: {tool.description}\n⚙️ Parameters: {tool.inputSchema}\n"
                for tool in available_tools
            ])
            
            # AWS-specific system prompt
            system_prompt = f"""You are an advanced AWS cloud management assistant powered by Gemini 2.5 Flash with access to these AWS tools:

{tools_description}

🔍 TOOL USAGE INSTRUCTIONS:
When you need to use a tool, respond with ONLY a clean JSON object in this format:
{{"tool_call": {{"name": "tool_name", "arguments": {{"param1": "value1", "param2": "value2"}}}}}}

📋 EXAMPLES:
- List instances in region: {{"tool_call": {{"name": "list_ec2_instances", "arguments": {{"region": "us-east-1"}}}}}}
- List ALL instances: {{"tool_call": {{"name": "list_all_ec2_instances", "arguments": {{}}}}}}
- Regional summary: {{"tool_call": {{"name": "get_ec2_instances_by_region", "arguments": {{}}}}}}
- Start instance: {{"tool_call": {{"name": "start_ec2_instance", "arguments": {{"instance_id": "i-1234567890abcdef0", "region": "us-east-1"}}}}}}
- List S3 buckets: {{"tool_call": {{"name": "list_s3_buckets", "arguments": {{}}}}}}
- Lambda functions: {{"tool_call": {{"name": "list_lambda_functions", "arguments": {{"region": "us-east-1"}}}}}}
- Help: {{"tool_call": {{"name": "get_aws_help", "arguments": {{}}}}}}

🌩️ AWS REGIONS & MULTI-REGION SUPPORT:
- Default region is us-east-1 unless specified
- Use "list_all_ec2_instances" to see instances across ALL regions
- Use "get_ec2_instances_by_region" for regional summary
- Common regions: us-east-1, us-west-2, eu-west-1, ap-southeast-1

🔍 TROUBLESHOOTING MISSING INSTANCES:
If user expects more instances than shown:
1. Check if they want all regions: use "list_all_ec2_instances"
2. Check regional distribution: use "get_ec2_instances_by_region"
3. Verify the specific region they're asking about

🎯 Always prioritize accuracy and provide clear AWS resource information.
"""

            # Check for help requests
            help_keywords = ["help", "example", "query", "what can", "how to", "commands", "options"]
            if any(keyword in query.lower() for keyword in help_keywords):
                try:
                    result = await self.session.call_tool("get_aws_help", {})
                    content = result.content[0].text if hasattr(result, 'content') and result.content else str(result.content)
                    return content
                except Exception as e:
                    return "I can help you manage AWS resources! Try asking about EC2 instances, S3 buckets, Lambda functions, or costs."

            full_prompt = f"{system_prompt}\n\n🌩️ User query: {query}"
            
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
                        
                        print(f"⚡ Executing AWS tool: {tool_name} with args: {tool_args}")
                        
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
                        final_prompt = f"""🌩️ AWS CLOUD ANALYSIS REQUEST

User Query: "{query}"
AWS Tool Used: {tool_name}
Tool Arguments: {tool_args}

📊 AWS DATA RECEIVED:
{content}

🎯 INSTRUCTIONS:
Analyze the AWS data and provide a comprehensive, well-formatted response that:
1. Directly answers the user's AWS question
2. Highlights important cloud resource information
3. Uses clear, technical language appropriate for AWS users
4. Formats data in an easy-to-read structure
5. Includes relevant recommendations or next steps if applicable
6. Shows costs, resource IDs, and statuses clearly

Please provide your AWS analysis now:"""
                        
                        final_response = self.model.generate_content(
                            final_prompt,
                            generation_config=generation_config
                        )
                        return f"🌩️ AWS Cloud Information:\n\n{final_response.text}"
                        
                except (json.JSONDecodeError, KeyError) as e:
                    print(f"❌ JSON parsing error: {e}")
                    return f"I attempted to use an AWS tool but encountered a parsing issue. Here's what I received: {response_text}"
            
            return response_text
            
        except Exception as e:
            return f"⚠️ Error processing AWS query: {str(e)}"

    async def chat_loop(self):
        """Run interactive AWS cloud management chat"""
        print("\n🌩️ AWS Cloud Management MCP Client Started!")
        print("=" * 60)
        print("💡 TIP: Type 'help' to see what AWS operations you can perform")
        print("💡 TIP: Try 'list ec2 instances' or 'show s3 buckets'")
        print("💡 TIP: Type 'quit' to exit")
        print("=" * 60)

        while True:
            try:
                query = input("\n☁️ AWS Query: ").strip()

                if query.lower() == 'quit':
                    print("👋 Thanks for using AWS MCP client!")
                    break

                if not query:
                    print("❓ Please enter an AWS query or type 'help' for examples.")
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
        print("Usage: python3 aws_client.py <path_to_aws_server.py>")
        print("Example: python3 aws_client.py aws_server.py")
        sys.exit(1)

    try:
        client = AWSMCPClient()
        await client.connect_to_server(sys.argv[1])
        await client.chat_loop()
    except Exception as e:
        print(f"❌ Failed to start MCP client: {e}")
        sys.exit(1)
    finally:
        if 'client' in locals():
            await client.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
