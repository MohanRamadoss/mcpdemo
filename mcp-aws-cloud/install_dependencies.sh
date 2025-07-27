#!/bin/bash

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🔧 Installing AWS MCP Dependencies${NC}"
echo "=================================="

# Check if we're in a virtual environment
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo -e "${GREEN}✅ Virtual environment detected: $VIRTUAL_ENV${NC}"
else
    echo -e "${YELLOW}⚠️ No virtual environment detected. Consider using 'python3 -m venv venv && source venv/bin/activate'${NC}"
fi

# Upgrade pip first
echo -e "${BLUE}📦 Upgrading pip...${NC}"
python3 -m pip install --upgrade pip

# Install requirements
echo -e "${BLUE}📦 Installing requirements from requirements.txt...${NC}"
if [ -f "requirements.txt" ]; then
    python3 -m pip install -r requirements.txt
else
    echo -e "${RED}❌ requirements.txt not found${NC}"
    exit 1
fi

# Verify installations
echo -e "${BLUE}🧪 Verifying installations...${NC}"

required_packages=("mcp" "boto3" "google.generativeai" "fastmcp" "dotenv")
failed_packages=()

for package in "${required_packages[@]}"; do
    if python3 -c "import $package" 2>/dev/null; then
        echo -e "${GREEN}✅ $package${NC}"
    else
        echo -e "${RED}❌ $package${NC}"
        failed_packages+=("$package")
    fi
done

if [ ${#failed_packages[@]} -eq 0 ]; then
    echo -e "${GREEN}🎉 All dependencies installed successfully!${NC}"
    echo -e "${BLUE}💡 You can now run: python3 aws_client.py aws_server.py${NC}"
else
    echo -e "${RED}❌ Failed to install: ${failed_packages[*]}${NC}"
    exit 1
fi
