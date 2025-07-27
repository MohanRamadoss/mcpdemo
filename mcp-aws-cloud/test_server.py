#!/usr/bin/env python3
"""
Simple test to verify AWS MCP server can start
"""
import subprocess
import sys
import time
import os

def test_server_startup():
    """Test if the AWS server can start without errors"""
    print("🧪 Testing AWS MCP Server startup...")
    
    if not os.path.exists("aws_server.py"):
        print("❌ aws_server.py not found")
        return False
    
    try:
        # Start the server process
        process = subprocess.Popen(
            ["python3", "aws_server.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait a moment for startup
        time.sleep(2)
        
        # Check if process is still running
        if process.poll() is None:
            print("✅ Server started successfully")
            process.terminate()
            process.wait()
            return True
        else:
            stdout, stderr = process.communicate()
            print(f"❌ Server failed to start")
            print(f"STDOUT: {stdout}")
            print(f"STDERR: {stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing server: {e}")
        return False

if __name__ == "__main__":
    if test_server_startup():
        print("🎉 Server test passed!")
        sys.exit(0)
    else:
        print("💥 Server test failed!")
        sys.exit(1)
