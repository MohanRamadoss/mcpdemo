#!/bin/bash

# Update system
apt-get update && apt-get upgrade -y

# Install dependencies
apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    git \
    curl \
    htop \
    nginx \
    docker.io \
    docker-compose \
    ufw \
    fail2ban

# Enable and start services
systemctl enable docker
systemctl start docker
systemctl enable nginx
systemctl start nginx

# Add ubuntu user to docker group
usermod -aG docker ubuntu

# Configure firewall
ufw allow ssh
ufw allow 80
ufw allow 8080
ufw --force enable

# Create application directory
mkdir -p /opt/mcp-linux
cd /opt/mcp-linux

# Clone the repository (you'll need to replace with your repo)
git clone https://github.com/yourusername/mcp-linux-agent.git .

# Set up Python environment
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Create environment file
cat > .env << EOF
GOOGLE_API_KEY=${google_api_key}
PYTHONPATH=/opt/mcp-linux
PYTHONUNBUFFERED=1
MCP_ENVIRONMENT=production
LOG_LEVEL=INFO
EOF

# Create systemd service
cat > /etc/systemd/system/mcp-linux.service << EOF
[Unit]
Description=MCP Linux Debug Agent
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/opt/mcp-linux
Environment=PATH=/opt/mcp-linux/venv/bin
ExecStart=/opt/mcp-linux/venv/bin/python main.py --http
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable and start the service
systemctl daemon-reload
systemctl enable mcp-linux
systemctl start mcp-linux

# Configure nginx reverse proxy
cat > /etc/nginx/sites-available/mcp-linux << EOF
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# Enable nginx site
ln -s /etc/nginx/sites-available/mcp-linux /etc/nginx/sites-enabled/
rm /etc/nginx/sites-enabled/default
systemctl reload nginx

# Set proper permissions
chown -R ubuntu:ubuntu /opt/mcp-linux
