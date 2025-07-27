#!/bin/bash

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
REMOTE_DIR="/opt/mcp-linux"
SERVICE_NAME="mcp-linux"

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to validate SSH connection
validate_ssh() {
    local host=$1
    local ssh_key=$2
    local user=${3:-ubuntu}
    
    print_status "Validating SSH connection to $user@$host..."
    
    if ! ssh -i "$ssh_key" -o ConnectTimeout=10 -o BatchMode=yes "$user@$host" "echo 'SSH connection successful'" 2>/dev/null; then
        print_error "Cannot connect to $user@$host via SSH"
        print_error "Please check:"
        print_error "  - SSH key path: $ssh_key"
        print_error "  - Host connectivity: $host"
        print_error "  - Username: $user"
        print_error "  - SSH key permissions (should be 600)"
        return 1
    fi
    
    print_success "SSH connection validated"
    return 0
}

# Function to create deployment package
create_deployment_package() {
    print_status "Creating deployment package..."
    
    cd "$PROJECT_DIR"
    
    # Create temporary directory
    local temp_dir=$(mktemp -d)
    local package_file="$temp_dir/mcp-linux-deploy.tar.gz"
    
    # Create deployment package
    tar -czf "$package_file" \
        --exclude='.git' \
        --exclude='venv' \
        --exclude='__pycache__' \
        --exclude='*.pyc' \
        --exclude='.env' \
        --exclude='logs/*' \
        --exclude='deployment/docker' \
        --exclude='deployment/kubernetes' \
        --exclude='deployment/terraform' \
        .
    
    echo "$package_file"
}

# Function to deploy to remote server
deploy_to_remote() {
    local host=$1
    local ssh_key=$2
    local user=${3:-ubuntu}
    local google_api_key=${4:-""}
    
    print_status "Deploying MCP Linux Agent to $user@$host"
    
    # Validate SSH first
    if ! validate_ssh "$host" "$ssh_key" "$user"; then
        return 1
    fi
    
    # Create deployment package
    local package_file=$(create_deployment_package)
    
    # Copy package to remote server
    print_status "Copying deployment package to remote server..."
    scp -i "$ssh_key" "$package_file" "$user@$host:/tmp/mcp-linux-deploy.tar.gz"
    
    # Deploy on remote server
    print_status "Installing MCP Linux Agent on remote server..."
    ssh -i "$ssh_key" "$user@$host" bash << EOF
set -e

# Install system dependencies
print_status() {
    echo -e "\033[0;34m[INFO]\033[0m \$1"
}

print_success() {
    echo -e "\033[0;32m[SUCCESS]\033[0m \$1"
}

print_status "Installing system dependencies..."
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-venv git curl htop ufw fail2ban

# Create application directory
print_status "Setting up application directory..."
sudo mkdir -p $REMOTE_DIR
sudo chown $user:$user $REMOTE_DIR

# Backup existing installation
if [ -d "$REMOTE_DIR/current" ]; then
    print_status "Backing up existing installation..."
    sudo mv $REMOTE_DIR/current $REMOTE_DIR/backup-\$(date +%Y%m%d-%H%M%S) 2>/dev/null || true
fi

# Extract new deployment
print_status "Extracting deployment package..."
mkdir -p $REMOTE_DIR/current
tar -xzf /tmp/mcp-linux-deploy.tar.gz -C $REMOTE_DIR/current
chown -R $user:$user $REMOTE_DIR/current

# Set up Python environment
print_status "Setting up Python virtual environment..."
cd $REMOTE_DIR/current
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Create environment file
print_status "Creating environment configuration..."
cat > .env << ENVEOF
GOOGLE_API_KEY=${google_api_key}
PYTHONPATH=$REMOTE_DIR/current
PYTHONUNBUFFERED=1
MCP_ENVIRONMENT=production
LOG_LEVEL=INFO
ENVEOF

# Create logs directory
mkdir -p logs
chmod 755 logs

# Create systemd service
print_status "Creating systemd service..."
sudo tee /etc/systemd/system/$SERVICE_NAME.service > /dev/null << SERVICEEOF
[Unit]
Description=MCP Linux Debug Agent
After=network.target
Wants=network.target

[Service]
Type=simple
User=$user
Group=$user
WorkingDirectory=$REMOTE_DIR/current
Environment=PATH=$REMOTE_DIR/current/venv/bin
EnvironmentFile=$REMOTE_DIR/current/.env
ExecStart=$REMOTE_DIR/current/venv/bin/python main.py --http
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

# Security settings
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=$REMOTE_DIR

[Install]
WantedBy=multi-user.target
SERVICEEOF

# Enable and start service
print_status "Starting MCP Linux service..."
sudo systemctl daemon-reload
sudo systemctl enable $SERVICE_NAME
sudo systemctl restart $SERVICE_NAME

# Configure firewall (optional)
print_status "Configuring firewall..."
sudo ufw allow ssh
sudo ufw allow 8080
sudo ufw --force enable || true

# Clean up
rm -f /tmp/mcp-linux-deploy.tar.gz

print_success "MCP Linux Agent deployed successfully!"
print_status "Service status:"
sudo systemctl status $SERVICE_NAME --no-pager -l

print_status "Testing HTTP endpoint..."
sleep 5
curl -f http://localhost:8080/health || echo "Health check endpoint not ready yet"

print_success "Deployment completed!"
echo "🌐 HTTP API available at: http://$host:8080"
echo "📋 Check logs with: sudo journalctl -u $SERVICE_NAME -f"
echo "🔄 Restart service with: sudo systemctl restart $SERVICE_NAME"
EOF
    
    # Clean up local package
    rm -f "$package_file"
    
    print_success "Remote deployment completed!"
    print_status "🌐 HTTP API available at: http://$host:8080"
    
    # Test connection
    print_status "Testing remote API endpoint..."
    sleep 2
    if curl -f -s "http://$host:8080/health" >/dev/null 2>&1; then
        print_success "Remote API is responding!"
    else
        print_warning "Remote API not yet responding (may need a few moments to start)"
    fi
}

# Function to run MCP client via SSH tunnel
run_ssh_tunnel_client() {
    local host=$1
    local ssh_key=$2
    local user=${3:-ubuntu}
    local local_port=${4:-8081}
    
    print_status "Setting up SSH tunnel to MCP server..."
    
    # Validate SSH connection
    if ! validate_ssh "$host" "$ssh_key" "$user"; then
        return 1
    fi
    
    print_status "Creating SSH tunnel: localhost:$local_port -> $host:8080"
    
    # Start SSH tunnel in background
    ssh -i "$ssh_key" -L "$local_port:localhost:8080" -N -f "$user@$host"
    local tunnel_pid=$!
    
    print_success "SSH tunnel established (PID: $tunnel_pid)"
    print_status "MCP server accessible at: http://localhost:$local_port"
    
    # Function to cleanup tunnel
    cleanup_tunnel() {
        print_status "Cleaning up SSH tunnel..."
        kill $tunnel_pid 2>/dev/null || true
        # Also kill any remaining SSH tunnels
        pkill -f "ssh.*-L $local_port:localhost:8080" 2>/dev/null || true
    }
    
    # Set trap to cleanup on exit
    trap cleanup_tunnel EXIT
    
    print_status "Testing tunnel connection..."
    sleep 2
    if curl -f -s "http://localhost:$local_port/health" >/dev/null 2>&1; then
        print_success "Tunnel is working! Server accessible locally."
        
        # Optionally run the client
        read -p "Do you want to run the MCP client now? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            cd "$PROJECT_DIR"
            if [ -f "advanced_linux_client.py" ]; then
                print_status "Starting MCP client (connecting via SSH tunnel)..."
                # Note: This would need modification to support HTTP client mode
                echo "Note: You can use the HTTP API at http://localhost:$local_port"
                echo "Or modify the client to connect via HTTP instead of STDIO"
            else
                print_error "advanced_linux_client.py not found"
            fi
        fi
        
        print_status "Press Ctrl+C to close the tunnel"
        # Keep tunnel alive
        while true; do
            sleep 60
            if ! kill -0 $tunnel_pid 2>/dev/null; then
                print_error "SSH tunnel died, exiting"
                break
            fi
        done
    else
        print_error "Tunnel connection failed"
        cleanup_tunnel
        return 1
    fi
}

# Function to execute remote commands
execute_remote_command() {
    local host=$1
    local ssh_key=$2
    local command=$3
    local user=${4:-ubuntu}
    
    print_status "Executing remote command on $host: $command"
    ssh -i "$ssh_key" "$user@$host" "$command"
}

# Function to check remote server status
check_remote_status() {
    local host=$1
    local ssh_key=$2
    local user=${3:-ubuntu}
    
    print_status "Checking MCP Linux Agent status on $host..."
    
    ssh -i "$ssh_key" "$user@$host" << 'EOF'
echo "🖥️ System Information:"
echo "Hostname: $(hostname)"
echo "OS: $(lsb_release -d 2>/dev/null | cut -f2 || cat /etc/os-release | grep PRETTY_NAME | cut -d'"' -f2)"
echo "Uptime: $(uptime -p)"
echo ""

echo "📦 MCP Service Status:"
sudo systemctl status mcp-linux --no-pager -l || echo "Service not found"
echo ""

echo "🌐 HTTP Endpoint Test:"
curl -s http://localhost:8080/health | python3 -m json.tool 2>/dev/null || echo "HTTP endpoint not responding"
echo ""

echo "📋 Recent Logs:"
sudo journalctl -u mcp-linux --since "5 minutes ago" --no-pager -l | tail -10 || echo "No recent logs"
EOF
}

# Function to update remote installation
update_remote() {
    local host=$1
    local ssh_key=$2
    local user=${3:-ubuntu}
    
    print_status "Updating MCP Linux Agent on $host..."
    
    # Create new deployment package
    local package_file=$(create_deployment_package)
    
    # Copy to remote
    scp -i "$ssh_key" "$package_file" "$user@$host:/tmp/mcp-linux-update.tar.gz"
    
    # Update on remote
    ssh -i "$ssh_key" "$user@$host" << 'EOF'
set -e

cd /opt/mcp-linux

# Stop service
sudo systemctl stop mcp-linux

# Backup current version
if [ -d "current" ]; then
    mv current backup-$(date +%Y%m%d-%H%M%S)
fi

# Extract new version
mkdir -p current
tar -xzf /tmp/mcp-linux-update.tar.gz -C current
chown -R ubuntu:ubuntu current

# Update Python dependencies
cd current
source venv/bin/activate 2>/dev/null || python3 -m venv venv && source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Copy environment file from backup if exists
if [ -f "../backup-$(ls -1 ../ | grep backup- | tail -1)/.env" ]; then
    cp "../backup-$(ls -1 ../ | grep backup- | tail -1)/.env" .env
fi

# Restart service
sudo systemctl start mcp-linux
sudo systemctl status mcp-linux --no-pager

# Clean up
rm -f /tmp/mcp-linux-update.tar.gz

echo "Update completed successfully!"
EOF
    
    rm -f "$package_file"
    print_success "Remote update completed!"
}

# Function to show help
show_help() {
    cat << 'EOF'
MCP Linux SSH Deployment Script

Usage: ./ssh_deploy.sh [COMMAND] [OPTIONS]

Commands:
  deploy <host> <ssh_key> [user] [api_key]    Deploy MCP to remote server
  tunnel <host> <ssh_key> [user] [port]       Create SSH tunnel for client access
  status <host> <ssh_key> [user]              Check remote server status
  update <host> <ssh_key> [user]              Update remote installation
  exec <host> <ssh_key> "command" [user]      Execute remote command
  help                                         Show this help

Examples:
  # Deploy to remote server
  ./ssh_deploy.sh deploy 192.168.1.100 ~/.ssh/id_rsa ubuntu "your-api-key"
  
  # Create SSH tunnel for local access
  ./ssh_deploy.sh tunnel 192.168.1.100 ~/.ssh/id_rsa ubuntu 8081
  
  # Check remote status
  ./ssh_deploy.sh status 192.168.1.100 ~/.ssh/id_rsa
  
  # Update remote installation
  ./ssh_deploy.sh update 192.168.1.100 ~/.ssh/id_rsa
  
  # Execute remote command
  ./ssh_deploy.sh exec 192.168.1.100 ~/.ssh/id_rsa "sudo systemctl restart mcp-linux"

Prerequisites:
  - SSH access to remote server
  - SSH key with proper permissions (chmod 600)
  - Remote server running Ubuntu/Debian
  - Python 3.8+ on remote server

Notes:
  - Default user is 'ubuntu' (can be overridden)
  - Default remote directory is /opt/mcp-linux
  - Service runs on port 8080
  - Firewall automatically configured for SSH and port 8080
EOF
}

# Main script logic
main() {
    case "${1:-help}" in
        "deploy")
            if [ $# -lt 3 ]; then
                print_error "Usage: $0 deploy <host> <ssh_key> [user] [google_api_key]"
                exit 1
            fi
            deploy_to_remote "$2" "$3" "${4:-ubuntu}" "${5:-}"
            ;;
        "tunnel")
            if [ $# -lt 3 ]; then
                print_error "Usage: $0 tunnel <host> <ssh_key> [user] [local_port]"
                exit 1
            fi
            run_ssh_tunnel_client "$2" "$3" "${4:-ubuntu}" "${5:-8081}"
            ;;
        "status")
            if [ $# -lt 3 ]; then
                print_error "Usage: $0 status <host> <ssh_key> [user]"
                exit 1
            fi
            check_remote_status "$2" "$3" "${4:-ubuntu}"
            ;;
        "update")
            if [ $# -lt 3 ]; then
                print_error "Usage: $0 update <host> <ssh_key> [user]"
                exit 1
            fi
            update_remote "$2" "$3" "${4:-ubuntu}"
            ;;
        "exec")
            if [ $# -lt 4 ]; then
                print_error "Usage: $0 exec <host> <ssh_key> \"command\" [user]"
                exit 1
            fi
            execute_remote_command "$2" "$3" "$4" "${5:-ubuntu}"
            ;;
        "help"|*)
            show_help
            ;;
    esac
}

main "$@"
