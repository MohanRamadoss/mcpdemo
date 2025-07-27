#!/bin/bash

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🌩️ AWS MCP Quick Start${NC}"
echo "=================================="

# Check if we're in the right directory
if [ ! -f "aws_server.py" ]; then
    echo -e "${RED}❌ aws_server.py not found. Make sure you're in the mcp-aws-cloud directory.${NC}"
    exit 1
fi

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3 not found. Please install Python 3.8+${NC}"
    exit 1
fi

# Check and install dependencies
echo -e "${YELLOW}📦 Checking dependencies...${NC}"
if python3 -c "import boto3, mcp, google.generativeai, fastmcp" 2>/dev/null; then
    echo -e "${GREEN}✅ All dependencies are installed${NC}"
else
    echo -e "${YELLOW}⚠️ Missing dependencies. Installing...${NC}"
    
    # Make install script executable and run it
    chmod +x install_dependencies.sh
    ./install_dependencies.sh
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Failed to install dependencies${NC}"
        exit 1
    fi
fi

# Test the setup
echo -e "${YELLOW}🧪 Testing setup...${NC}"
if python3 test_local.py; then
    echo -e "${GREEN}✅ Setup test passed!${NC}"
else
    echo -e "${YELLOW}⚠️ Some tests failed, but you can still try running the server.${NC}"
fi

echo
echo -e "${BLUE}🚀 Starting AWS MCP Server...${NC}"
echo "You can now use these sample queries:"
echo "• 'List EC2 instances'"
echo "• 'Show S3 buckets'" 
echo "• 'Get Lambda functions'"
echo "• 'help' for more options"
echo
echo "Press Ctrl+C to stop the server"
echo "=================================="

# Start the client
python3 aws_client.py aws_server.py
