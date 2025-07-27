# MCP Weather Client Tutorial 🌤️

A step-by-step tutorial for building an MCP (Model Context Protocol) client that connects to weather servers and uses Google Gemini 2.5 Flash AI for natural language interactions.

## What is MCP?

MCP (Model Context Protocol) is a protocol that allows AI models like Gemini or Claude to interact with external tools and data sources through a standardized interface. Think of it as a bridge between AI and real-world applications.

## What This Project Contains

- **`advanced_client.py`**: A Gemini 2.5 Flash-powered MCP client for natural language weather queries
- **`weather_server.py`**: An MCP weather server providing real-time weather data and tools
- **`mcp_client.py`**: A simple HTTP client (for comparison)
- **Step-by-step tutorial**: Learn how to build MCP clients from scratch

## Features

✅ **Interactive Chat Interface**: Ask questions in natural language  
✅ **Automatic Tool Selection**: Gemini 2.5 Flash decides which tools to use  
✅ **Advanced AI Processing**: Powered by Google's latest Gemini 2.5 Flash model  
✅ **Enhanced Performance**: Improved response quality and speed  
✅ **Weather Data**: Get forecasts and alerts for any US location  
✅ **International Support**: Get coordinates and guidance for global cities  
✅ **Error Handling**: Graceful error handling and resource cleanup  
✅ **Modular Design**: Easy to extend with new servers and tools  

## Quick Start

### Prerequisites

- Python 3.8+
- Google AI API key
- Internet connection

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/mcp-weather-client-tutorial.git
cd mcp-weather-client-tutorial

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies (ensure you have the latest google-generativeai)
pip install --upgrade mcp google-generativeai python-dotenv httpx fastmcp
```

### Setup

1. **Your Google AI API key is already configured** for Gemini 2.5 Flash

2. **Optional: Create a `.env` file** to override the default:
```bash
echo "GOOGLE_API_KEY=your_custom_api_key_here" > .env
```

3. **Run the client**:
```bash
python3 advanced_client.py weather_server.py
```

### Usage Examples

Once connected, you can ask questions like:

**🇺🇸 US Weather Queries:**
- "What are the weather alerts in California?"
- "Get the forecast for New York City coordinates 40.7128, -74.0060"
- "Are there any weather alerts in Texas?"
- "What's the weather forecast for San Francisco coordinates 37.7749, -122.4194?"
- "Weather forecast for Chicago coordinates 41.8781, -87.6298"
- "Show me active alerts for NY"

**🌍 International Location Queries:**
- "What are the coordinates for Singapore?"
- "Get coordinates for London"
- "Weather information for Tokyo"
- "How do I get weather for Paris?"

**❓ Need Help?**
- Type "help" for a complete guide
- Ask "what can I query?" for examples

## Important Usage Guidelines

To get the most accurate weather information, please specify:

### For US Weather Forecasts:
* **Provide specific coordinates:** Use latitude and longitude for precise forecasts  
  - Example: "What's the forecast for New York City coordinates 40.7128, -74.0060?"
  - Example: "Weather forecast for Chicago coordinates 41.8781, -87.6298"

### For US Weather Alerts:
* **Specify a US state:** Use either full state names or 2-letter codes  
  - Example: "Are there any weather warnings in Texas?"
  - Example: "Show me active alerts for NY"
  - Example: "What are the weather alerts in California?"

### For International Locations:
* **Request coordinates first:** Get lat/lng coordinates for international cities  
  - Example: "What are the coordinates for Singapore?"
  - Example: "Get coordinates for London"
* **Note:** Weather forecasts only work for US locations due to API limitations

### Quick Tips:
- 🎯 Be specific with your location requests
- 🌍 For international weather, use external services like Weather.com or AccuWeather
- 📍 Always include coordinates for US forecasts when possible
- 🔍 Type "help" if you need guidance on available queries

## Project Structure

```
mcp-weather-client-tutorial/
├── advanced_client.py      # Gemini-powered MCP client
├── weather_server.py       # Weather MCP server
├── mcp_client.py           # Simple HTTP client (for comparison)
├── README.md               # This file
├── .env                    # API keys (not in git)
└── .gitignore              # Git ignore file
```

## How It Works

1. **Client connects** to the weather MCP server
2. **User asks** a question in natural language
3. **Gemini 2.5 Flash** analyzes the question with advanced reasoning
4. **AI decides** which weather tools to use automatically
5. **Client executes** the appropriate tool calls
6. **Weather data** is fetched from the National Weather Service API
7. **Gemini 2.5 Flash** processes and formats the data intelligently
8. **User receives** a comprehensive, well-formatted weather response

## Architecture

```
User Query → Gemini 2.5 Flash → Smart Tool Selection → MCP Server → Weather API → Enhanced Response
```

## Learning Path

This project demonstrates:

1. **MCP Protocol Basics**: Understanding client-server communication
2. **Async Programming**: Handling concurrent operations
3. **API Integration**: Connecting to external services
4. **AI Integration**: Using Gemini for natural language processing
5. **Error Handling**: Graceful error management
6. **Resource Management**: Proper cleanup and lifecycle management

## Customization

### Adding New Tools

To add new weather tools, modify `weather_server.py`:

```python
@mcp.tool()
async def get_radar_data(latitude: float, longitude: float) -> str:
    """Get radar data for a location."""
    # Your implementation here
    pass
```

### Adding New Servers

Create new server files following the same pattern as `weather_server.py`.

## Troubleshooting

### Common Issues

1. **Import Errors**: Make sure all dependencies are installed
3. **Connection Errors**: Ensure the server script path is correct
4. **Weather API Errors**: Check your internet connection

### Debug Mode

Add debug prints to see what's happening:

```python
# In advanced_client.py
print(f"Available tools: {[tool.name for tool in response.tools]}")
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Acknowledgments

- [Model Context Protocol](https://modelcontextprotocol.io/) for the protocol specification
- [Google AI](https://ai.google.dev/) for Gemini AI
- [National Weather Service](https://weather.gov/) for weather data API

## Learn More

- [MCP Documentation](https://modelcontextprotocol.io/)
- [Google AI Documentation](https://ai.google.dev/docs)
- [FastMCP Documentation](https://github.com/jlowin/fastmcp)

---

**Happy coding! 🌟**

## What's New in Gemini 2.5 Flash

- 🚀 **Faster Processing**: Improved response times
- 🧠 **Better Reasoning**: Enhanced understanding of complex queries
- 📊 **Superior Formatting**: Better structured responses
- 🔧 **Improved Tool Usage**: More accurate tool selection and parameter handling
- 🌐 **Enhanced Context**: Better understanding of weather-related requests
- 🎯 **Smart Location Detection**: Automatically routes queries to appropriate tools