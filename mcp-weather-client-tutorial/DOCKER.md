# Docker Deployment Guide 🐳

This guide explains how to deploy and run the MCP Weather Server using Docker and Docker Compose.

## 📋 Prerequisites

- Docker Engine 20.10+ installed
- Docker Compose 2.0+ installed
- At least 1GB free disk space
- Internet connection for weather data

## 🚀 Quick Start

### 1. Build and Run Server
```bash
# Make script executable
chmod +x scripts/docker-run.sh

# Build the application
./scripts/docker-run.sh build

# Start the weather server
./scripts/docker-run.sh server
```

### 2. Run Interactive Client
```bash
# In a new terminal, start the client
./scripts/docker-run.sh client
```

### 3. Alternative: HTTP Server
```bash
# Start HTTP server (accessible at http://localhost:8080)
./scripts/docker-run.sh http
```

## 🔧 Available Commands

| Command | Description |
|---------|-------------|
| `./scripts/docker-run.sh build` | Build Docker images |
| `./scripts/docker-run.sh server` | Start weather server only |
| `./scripts/docker-run.sh client` | Start interactive client |
| `./scripts/docker-run.sh http` | Start HTTP server on port 8080 |
| `./scripts/docker-run.sh stop` | Stop all services |
| `./scripts/docker-run.sh logs` | Show logs for all services |
| `./scripts/docker-run.sh status` | Show container status |
| `./scripts/docker-run.sh clean` | Clean up containers and images |

## 📁 Project Structure

```
mcp-weather-client-tutorial/
├── Dockerfile              # Container definition
├── docker-compose.yml      # Multi-service orchestration
├── requirements.txt        # Python dependencies
├── .dockerignore           # Build optimization
├── scripts/
│   └── docker-run.sh       # Management script
├── logs/                   # Container logs (mounted)
└── DOCKER.md              # This documentation
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file for custom configuration:

```bash
# Google AI API Key
GOOGLE_API_KEY=your_api_key_here

# Server settings
MCP_HOST=0.0.0.0
MCP_PORT=8080
LOG_LEVEL=INFO
```

### Volume Mounts

- `./logs:/app/logs` - Log files
- `./.env:/app/.env` - Environment configuration

## 🌐 HTTP Server Usage

The HTTP server is now working successfully! When running with HTTP profile:

```bash
# Start HTTP server
./scripts/docker-run.sh http

# Test the server
./scripts/docker-run.sh test-http
```

### Available Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Server information and available endpoints |
| `/health` | GET | Health check - returns server status |
| `/tools` | GET/POST | Available MCP tools information |

### Example Usage

```bash
# Check server status
curl http://localhost:8080/health

# Get server information
curl http://localhost:8080/

# List available tools
curl http://localhost:8080/tools

# Or open in browser
open http://localhost:8080
```

### Test the Server

```bash
# Run automated tests
python3 scripts/test_http_client.py

# Or use the Docker script
./scripts/docker-run.sh test-http
```

## ✅ Success! Your MCP Weather Server is Working

The logs show:
- ✅ Manual HTTP server implementation started successfully
- ✅ Server accessible on http://0.0.0.0:8080
- ✅ Health checks passing
- ✅ Web browser access working
- ✅ All endpoints responding correctly

## 🎯 Next Steps

1. **Browser Testing**: Open http://localhost:8080 in your browser
2. **API Testing**: Use curl or Postman to test endpoints
3. **Integration**: Connect your applications to the HTTP API
4. **Extension**: Add more tools to the weather server

## 📊 Monitoring

### Check Container Status
```bash
./scripts/docker-run.sh status
```

### View Logs
```bash
# All services
./scripts/docker-run.sh logs

# Specific service
./scripts/docker-run.sh logs weather-server
```

### Resource Usage
```bash
# Real-time stats
docker stats

# Container inspection
docker inspect mcp-weather-server
```

## 🔍 Troubleshooting

### Common Issues

1. **Port Already in Use**
   ```bash
   # Check what's using port 8080
   lsof -i :8080
   
   # Kill process if needed
   kill -9 <PID>
   ```

2. **Permission Denied**
   ```bash
   # Fix script permissions
   chmod +x scripts/docker-run.sh
   ```

3. **Docker Not Running**
   ```bash
   # Start Docker daemon
   sudo systemctl start docker
   ```

4. **Build Failures**
   ```bash
   # Clean build cache
   docker builder prune -a
   
   # Rebuild without cache
   ./scripts/docker-run.sh build
   ```

### Debug Mode

Run containers with debug output:

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG

# Run with verbose output
docker-compose up --verbose
```

## 🚀 Production Deployment

### 1. Optimize Dockerfile

For production, consider:
- Multi-stage builds for smaller images
- Security scanning
- Health checks
- Resource limits

### 2. Environment-Specific Configurations

```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  weather-server:
    # ...existing config...
    deploy:
      replicas: 2
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 256M
```

### 3. Load Balancing

Use nginx or traefik for load balancing:

```yaml
# Add to docker-compose.yml
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - weather-server
```

## 📈 Scaling

### Horizontal Scaling
```bash
# Scale weather server
docker-compose up --scale weather-server=3
```

### Resource Limits
```yaml
services:
  weather-server:
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
```

## 🔒 Security

### Best Practices

1. **Non-root User**: Containers run as non-root user
2. **Secret Management**: Use Docker secrets for sensitive data
3. **Network Isolation**: Services communicate through dedicated network
4. **Image Scanning**: Scan images for vulnerabilities

```bash
# Scan image for vulnerabilities
docker scan mcp-weather-server:latest
```

## 🧹 Maintenance

### Regular Cleanup
```bash
# Remove unused containers and images
./scripts/docker-run.sh clean

# Prune system
docker system prune -af
```

### Updates
```bash
# Pull latest base images
docker-compose pull

# Rebuild with latest dependencies
./scripts/docker-run.sh build
```

---

**Need Help?** 📞
- Check the main README.md for application usage
- View container logs: `./scripts/docker-run.sh logs`
- Open an issue on GitHub for Docker-specific problems
