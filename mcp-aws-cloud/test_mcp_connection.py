#!/usr/bin/env python3
"""
Test MCP connection specifically
"""
import asyncio
import subprocess
import sys
import time
import os
from contextlib import AsyncExitStack

async def test_mcp_stdio_connection():
    """Test MCP stdio connection specifically"""
    print("🔧 Testing MCP STDIO Connection...")
    
    try:
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client
        
        print("✅ MCP imports successful")
        
        # Test server startup with minimal logging
        print("🚀 Testing server startup with stdio...")
        
        exit_stack = AsyncExitStack()
        
        server_params = StdioServerParameters(
            command="python3",
            args=["aws_server.py"],
            env=os.environ.copy()
        )
        
        print("📡 Creating stdio transport...")
        stdio_transport = await exit_stack.enter_async_context(stdio_client(server_params))
        stdio, write = stdio_transport
        
        print("🤝 Creating client session...")
        session = await exit_stack.enter_async_context(ClientSession(stdio, write))
        
        print("⚡ Initializing session...")
        await session.initialize()
        
        print("📋 Listing tools...")
        response = await session.list_tools()
        tools = response.tools
        
        print(f"✅ Successfully connected! Found {len(tools)} tools:")
        for tool in tools:
            print(f"  • {tool.name}")
        
        await exit_stack.aclose()
        return True
        
    except Exception as e:
        print(f"❌ MCP connection failed: {e}")
        print(f"Error type: {type(e).__name__}")
        if 'exit_stack' in locals():
            await exit_stack.aclose()
        return False

async def main():
    """Run MCP connection test"""
    print("🧪 MCP Connection Test\n")
    
    if await test_mcp_stdio_connection():
        print("\n🎉 MCP connection test passed!")
        print("💡 You can now run: python3 aws_client.py aws_server.py")
    else:
        print("\n❌ MCP connection test failed!")
        print("💡 Check the error messages above for troubleshooting.")

if __name__ == "__main__":
    asyncio.run(main())
