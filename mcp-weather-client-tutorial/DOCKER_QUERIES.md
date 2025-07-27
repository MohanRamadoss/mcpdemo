# 🐳 Querying MCP Weather Server with Docker

This guide shows you multiple ways to query and interact with your MCP Weather Server running in Docker.

## 🚀 Quick Start

```bash
# Start the HTTP server
./scripts/docker-run.sh http

# Run the query demo
chmod +x scripts/query_docker.sh
./scripts/query_docker.sh
```

## 📡 Method 1: HTTP API Queries

The simplest way to query the server is through HTTP endpoints:

### Basic Queries
```bash
# Check server health
curl http://localhost:8080/health

# Get server information
curl http://localhost:8080/

# List available tools
curl http://localhost:8080/tools

# Pretty print JSON responses
curl -s http://localhost:8080/health | python3 -m json.tool
```

### Example Responses
```json
// Health check response
{
  "status": "healthy", 
  "service": "MCP Weather Server"
}

// Tools response
{
  "tools": [
    {
      "name": "get_forecast",
      "description": "Get weather forecast for coordinates",
      "parameters": {
        "latitude": {"type": "number"},
        "longitude": {"type": "number"}
      }
    }
  ]
}
```

## 🤖 Method 2: Interactive AI Client

### Option A: Run in Docker Container
```bash
# Start interactive client in container
docker-compose --profile client run --rm weather-client

# Or run specific container
docker run -it --network mcp-weather-client-tutorial_mcp-network \
  -e GOOGLE_API_KEY=your_key_here \
  mcp-weather-client-tutorial_weather-client
```

### Option B: Run Locally
```bash
# Run client locally (connects to Docker server)
python3 advanced_client.py weather_server.py
```

### Example AI Queries
```
🌍 Weather Query: help
🌍 Weather Query: weather alerts in California  
🌍 Weather Query: forecast for coordinates 40.7128, -74.0060
🌍 Weather Query: coordinates for Singapore
🌍 Weather Query: what's the weather like in Texas?
```

## ⚡ Method 3: Docker Exec Commands

Execute commands directly in running containers:

```bash
# Check if container is running
docker ps | grep mcp-weather

# Execute Python commands
docker exec mcp-weather-http python3 -c "print('Hello from container')"

# Check container processes
docker exec mcp-weather-http ps aux

# Access interactive shell
docker exec -it mcp-weather-http /bin/bash

# Test weather server module
docker exec mcp-weather-http python3 -c "
import sys
sys.path.append('/app')
from weather_server import mcp
print('✅ Weather server module loaded successfully')
"
```

## 📋 Method 4: Container Logs

Monitor and debug using logs:

```bash
# View real-time logs
docker-compose logs -f weather-http-server

# View last 50 log entries
docker-compose logs --tail=50 weather-http-server

# View logs with timestamps
docker-compose logs -t weather-http-server

# View all container logs
docker-compose logs

# Follow logs for specific container
docker logs -f mcp-weather-http
```

## 🌤️ Method 5: Weather-Specific Queries

### Using Interactive Client
The most powerful way to query weather data:

```bash
# Start the client
python3 advanced_client.py weather_server.py

# Example weather queries:
Query: help                                    # Get usage guide
Query: weather alerts in California            # US weather alerts
Query: forecast for coordinates 40.7128, -74.0060  # NYC forecast
Query: coordinates for Tokyo                   # International coordinates
Query: weather information for London          # International weather info
```

### Query Types by Category

| Category | Example Query | Tool Used |
|----------|---------------|-----------|
| **US Alerts** | "weather alerts in Texas" | `get_alerts` |
| **US Forecast** | "forecast for 40.7128, -74.0060" | `get_forecast` |
| **Coordinates** | "coordinates for Singapore" | `get_coordinates` |
| **International** | "weather info for Tokyo" | `get_international_weather_info` |
| **Help** | "help" or "what can I ask?" | `get_help` |

## 🐳 Method 6: Docker Compose Management

### Service Management
```bash
# Start HTTP server only
docker-compose up -d weather-http-server

# Start with specific profile
docker-compose --profile http up -d

# Start interactive client
docker-compose --profile client up weather-client

# Scale HTTP server
docker-compose up --scale weather-http-server=2 -d

# Stop all services
docker-compose down

# Stop specific service
docker-compose stop weather-http-server
```

### Status and Monitoring
```bash
# Check container status
docker-compose ps

# View resource usage
docker stats

# Inspect container
docker inspect mcp-weather-http

# View container networks
docker network ls | grep mcp
```

## 🔧 Method 7: Advanced Docker Queries

### Custom Container Runs
```bash
# Run one-off commands
docker-compose run --rm weather-server python3 -c "
from weather_server import mcp
print('Server initialized successfully')
"

# Test with custom environment
docker-compose run --rm -e LOG_LEVEL=DEBUG weather-server python3 weather_server.py

# Run with volume mounts
docker run -it --rm \
  -v $(pwd):/app \
  -p 8080:8080 \
  mcp-weather-client-tutorial_weather-server \
  python3 scripts/http_server.py
```

### Debugging Commands
```bash
# Test network connectivity
docker exec mcp-weather-http ping google.com

# Check Python environment
docker exec mcp-weather-http python3 -c "
import sys
print('Python version:', sys.version)
print('Installed packages:')
import pkg_resources
for pkg in pkg_resources.working_set:
    print(f'  {pkg.key}=={pkg.version}')
"

# Test weather API connectivity
docker exec mcp-weather-http python3 -c "
import httpx
import asyncio
async def test():
    async with httpx.AsyncClient() as client:
        response = await client.get('https://api.weather.gov')
        print(f'NWS API Status: {response.status_code}')
asyncio.run(test())
"
```

## 🎯 Common Query Patterns

### 1. Health Monitoring
```bash
# Continuous health monitoring
watch -n 5 'curl -s http://localhost:8080/health | python3 -m json.tool'

# Health check with alerts
curl -f http://localhost:8080/health || echo "❌ Server unhealthy"
```

### 2. Load Testing
```bash
# Simple load test
for i in {1..10}; do
  curl -s http://localhost:8080/health >/dev/null &
done
wait
echo "Load test completed"

# Using Apache Bench (if available)
ab -n 100 -c 10 http://localhost:8080/health
```

### 3. Development Workflow
```bash
# Development cycle
docker-compose down                    # Stop services
./scripts/docker-run.sh build        # Rebuild with changes
./scripts/docker-run.sh http         # Start HTTP server
./scripts/docker-run.sh test-http    # Test functionality
```

## 🔍 Troubleshooting Docker Queries

### Common Issues

1. **Container not running**
   ```bash
   # Check status
   docker-compose ps
   
   # Start if needed
   ./scripts/docker-run.sh http
   ```

2. **Connection refused**
   ```bash
   # Check port mapping
   docker port mcp-weather-http
   
   # Check if port is in use
   lsof -i :8080
   ```

3. **Permission errors**
   ```bash
   # Check logs
   docker-compose logs weather-http-server
   
   # Fix permissions
   sudo chown -R $USER:$USER logs/
   ```

## 📊 Query Performance Tips

1. **Use HTTP endpoints** for simple status checks
2. **Use interactive client** for complex weather queries
3. **Monitor container resources** with `docker stats`
4. **Use logs** for debugging and monitoring
5. **Scale containers** for high load scenarios

---

## 🚀 Single Command Docker Queries

For quick one-off queries without interactive sessions:

### Setup
```bash
# Make the script executable
chmod +x scripts/docker_query_cmd.sh

# Ensure HTTP server is running
./scripts/docker-run.sh http
```

### Direct Command Examples

```bash
# Get weather forecast for NYC
./scripts/docker_query_cmd.sh forecast "Get forecast for coordinates 40.7128, -74.0060"

# Get weather alerts for California
./scripts/docker_query_cmd.sh alerts "weather alerts in California"

# Get coordinates for Singapore
./scripts/docker_query_cmd.sh coords "coordinates for Singapore"

# Get help
./scripts/docker_query_cmd.sh help

# Custom query
./scripts/docker_query_cmd.sh query "weather alerts in Texas"
```

### Raw Docker Exec Commands

If you prefer direct docker exec commands:

```bash
# Weather forecast query
docker exec mcp-weather-http python3 -c "
import asyncio
import sys
sys.path.insert(0, '/app')
from weather_server import get_forecast
async def main():
    result = await get_forecast(40.7128, -74.0060)
    print(result)
asyncio.run(main())
"

# Weather alerts query
docker exec mcp-weather-http python3 -c "
import asyncio
import sys
sys.path.insert(0, '/app')
from weather_server import get_alerts
async def main():
    result = await get_alerts('CA')
    print(result)
asyncio.run(main())
"

# City coordinates query
docker exec mcp-weather-http python3 -c "
import asyncio
import sys
sys.path.insert(0, '/app')
from weather_server import get_coordinates
async def main():
    result = await get_coordinates('Singapore')
    print(result)
asyncio.run(main())
"
```

### One-Line Weather Queries

```bash
# NYC Weather Forecast
docker exec mcp-weather-http python3 -c "import asyncio, sys; sys.path.insert(0, '/app'); from weather_server import get_forecast; asyncio.run(get_forecast(40.7128, -74.0060))"

# California Weather Alerts  
docker exec mcp-weather-http python3 -c "import asyncio, sys; sys.path.insert(0, '/app'); from weather_server import get_alerts; print(asyncio.run(get_alerts('CA')))"

# Singapore Coordinates
docker exec mcp-weather-http python3 -c "import asyncio, sys; sys.path.insert(0, '/app'); from weather_server import get_coordinates; print(asyncio.run(get_coordinates('Singapore')))"
```

## 🎉 You're Ready!

Now you can query your MCP Weather Server using any of these Docker methods. The interactive AI client provides the most natural experience, while HTTP endpoints are perfect for programmatic access.

**Quick commands to remember:**
```bash
./scripts/query_docker.sh          # Full demo
./scripts/docker-run.sh http       # Start HTTP server  
./scripts/docker-run.sh test-http  # Test HTTP endpoints
python3 advanced_client.py weather_server.py  # AI client
```
