#!/usr/bin/env python3
"""
Test script for AWS MCP server local setup
"""
import os
import sys
import subprocess

def test_python_environment():
    """Test Python and package installation"""
    print("🐍 Testing Python Environment...")
    
    # Check Python version
    python_version = sys.version_info
    if python_version.major >= 3 and python_version.minor >= 8:
        print(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
    else:
        print(f"❌ Python version too old: {python_version}")
        return False
    
    # Check required packages
    required_packages = [
        ('mcp', 'mcp'),
        ('boto3', 'boto3'),
        ('google.generativeai', 'google-generativeai'),
        ('fastmcp', 'fastmcp'),
        ('dotenv', 'python-dotenv')
    ]
    
    missing_packages = []
    for import_name, package_name in required_packages:
        try:
            __import__(import_name)
            print(f"✅ {package_name} installed")
        except ImportError:
            print(f"❌ {package_name} not installed")
            missing_packages.append(package_name)
    
    if missing_packages:
        print(f"\n💡 To install missing packages, run:")
        print(f"pip3 install {' '.join(missing_packages)}")
        print(f"Or run: ./install_dependencies.sh")
        return False
    
    return True

def test_aws_credentials():
    """Test AWS credentials and connectivity"""
    print("\n🌩️ Testing AWS Credentials...")
    
    try:
        import boto3
        session = boto3.Session()
        sts = session.client('sts')
        identity = sts.get_caller_identity()
        
        print(f"✅ AWS Account: {identity.get('Account')}")
        print(f"✅ AWS User: {identity.get('Arn')}")
        return True
        
    except ImportError:
        print("❌ boto3 not installed")
        return False
    except Exception as e:
        print(f"❌ AWS credentials error: {e}")
        print("💡 Try running: aws configure")
        return False

def test_google_api():
    """Test Google AI API key"""
    print("\n🤖 Testing Google AI API...")
    
    api_key = os.getenv("GOOGLE_API_KEY", "AIzaSyC2YmGx9-_yx9QzW3D0qCEgvV03U9zik9E")
    if api_key and len(api_key) > 20:
        print(f"✅ Google AI API Key configured ({api_key[:8]}...)")
        return True
    else:
        print("❌ Google AI API Key not configured")
        return False

def test_aws_server():
    """Test if AWS server starts correctly"""
    print("\n🔧 Testing AWS MCP Server...")
    
    if not os.path.exists("aws_server.py"):
        print("❌ aws_server.py not found in current directory")
        return False
    
    try:
        # Test server imports
        import aws_server
        print("✅ AWS server imports successfully")
        return True
    except ImportError as e:
        print(f"❌ AWS server import error: {e}")
        print("💡 Try installing missing dependencies")
        return False
    except Exception as e:
        print(f"❌ AWS server error: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 AWS MCP Local Setup Test\n")
    
    tests = [
        test_python_environment,
        test_aws_credentials, 
        test_google_api,
        test_aws_server
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("="*50)
    print(f"📊 Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All tests passed! You can use the AWS MCP server.")
        print("\n🚀 Quick Start:")
        print("python3 aws_client.py aws_server.py")
    elif passed == 0:
        print("❌ All tests failed. Please install dependencies first:")
        print("chmod +x install_dependencies.sh && ./install_dependencies.sh")
    else:
        print("⚠️ Some tests failed. Please fix the issues above.")
        
        if passed >= 2:  # At least Python and one credential system works
            print("\n💡 You can still try running:")
            print("python3 aws_server.py")

if __name__ == "__main__":
    main()
