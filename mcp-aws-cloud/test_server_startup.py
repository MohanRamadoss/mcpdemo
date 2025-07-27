#!/usr/bin/env python3
"""
Test AWS MCP server startup and basic functionality
"""
import subprocess
import sys
import time
import os
import signal

def test_server_import():
    """Test if the server can be imported"""
    print("🧪 Testing server import...")
    try:
        import aws_server
        print("✅ Server imports successfully")
        return True
    except Exception as e:
        print(f"❌ Server import failed: {e}")
        return False

def test_server_startup():
    """Test if the server can start in HTTP mode"""
    print("🧪 Testing server startup in HTTP mode...")
    
    try:
        # Start server in HTTP mode
        process = subprocess.Popen(
            [sys.executable, "aws_server.py", "--http"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            preexec_fn=os.setsid  # Create new process group
        )
        
        # Wait for startup
        time.sleep(3)
        
        # Check if process is running
        if process.poll() is None:
            print("✅ Server started in HTTP mode")
            
            # Try to get some output
            try:
                stdout, stderr = process.communicate(timeout=2)
            except subprocess.TimeoutExpired:
                stdout = "Server running..."
                stderr = ""
            
            # Terminate the process group
            os.killpg(os.getpgid(process.pid), signal.SIGTERM)
            
            if stdout:
                print(f"📝 Server output: {stdout[:200]}...")
            
            return True
        else:
            stdout, stderr = process.communicate()
            print(f"❌ Server failed to start")
            print(f"STDOUT: {stdout}")
            print(f"STDERR: {stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing server startup: {e}")
        return False

def test_health_check():
    """Test health check functionality"""
    print("🧪 Testing health check tool...")
    try:
        import aws_server
        result = aws_server.health_check()
        
        if isinstance(result, dict) and result.get("status") == "healthy":
            print("✅ Health check passed")
            print(f"📊 AWS Available: {result.get('aws_available', False)}")
            return True
        else:
            print(f"❌ Health check failed: {result}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def main():
    """Run all startup tests"""
    print("🚀 AWS MCP Server Startup Test\n")
    
    tests = [
        test_server_import,
        test_health_check,
        test_server_startup
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("="*50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Server should work with the client.")
        print("\n🚀 You can now run:")
        print("python3 aws_client.py aws_server.py")
    else:
        print(f"⚠️ {total - passed} tests failed. Check the errors above.")
        
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
