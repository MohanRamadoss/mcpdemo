# 🧮 MCP Scientific Calculator with Gemini 2.5 Flash

A powerful scientific calculator that combines MCP (Model Context Protocol) with Google's Gemini 2.5 Flash AI for natural language mathematical queries.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Google AI API key (already configured)

### Setup with Existing Virtual Environment
```bash
# Activate the existing weather venv
cd /home/mohan/terraform/MCP/mcp-weather-client-tutorial
source venv/bin/activate

# Navigate to Calculator MCP directory
cd ../mcp-calculator

# Install dependencies (they should already be available from weather venv)
pip install -r requirements.txt
```

### Usage
```bash
# Start the interactive calculator
python3 advanced_calculator_client.py mcp_server.py
```

## 🧮 Available Mathematical Operations

### Basic Operations
- **Addition**: "What is 5 plus 3?" → `8`
- **Subtraction**: "Subtract 7 from 15" → `8`
- **Multiplication**: "Multiply 4 by 9" → `36`
- **Division**: "Divide 24 by 3" → `8`

### Advanced Operations
- **Power**: "2 to the power of 8" → `256`
- **Square Root**: "Square root of 64" → `8`
- **Cube Root**: "Cube root of 27" → `3`
- **Factorial**: "5 factorial" → `120`

### Trigonometric Functions
- **Sine**: "Sin of 30 degrees" → `0.5`
- **Cosine**: "Cos of 60 degrees" → `0.5`
- **Tangent**: "Tan of 45 degrees" → `1`

### Other Functions
- **Logarithm**: "Log of 100" → `4.605...`
- **Remainder**: "17 mod 5" → `2`

## 💡 Example Queries

```
🧮 Math Query: What is 15 + 27?
🧮 Math Query: Calculate the square root of 144
🧮 Math Query: What is 2 to the power of 10?
🧮 Math Query: Find the sine of 30 degrees
🧮 Math Query: What is 7 factorial?
🧮 Math Query: Divide 156 by 12
🧮 Math Query: Calculate 25 squared
🧮 Math Query: What's the remainder when 23 is divided by 7?
🧮 Math Query: Find the cube root of 125
🧮 Math Query: What is the natural log of 50?
```

## 🛠️ Available Tools

| Function | Description | Example Usage |
|----------|-------------|---------------|
| `add` | Addition | "Add 15 and 27" |
| `subtract` | Subtraction | "Subtract 8 from 20" |
| `multiply` | Multiplication | "Multiply 6 by 7" |
| `divide` | Division | "Divide 100 by 4" |
| `power` | Exponentiation | "2 to the power of 8" |
| `sqrt` | Square root | "Square root of 64" |
| `cbrt` | Cube root | "Cube root of 27" |
| `factorial` | Factorial | "5 factorial" |
| `log` | Natural logarithm | "Log of 100" |
| `remainder` | Modulo operation | "17 mod 5" |
| `sin` | Sine (degrees) | "Sin of 30 degrees" |
| `cos` | Cosine (degrees) | "Cos of 60 degrees" |
| `tan` | Tangent (degrees) | "Tan of 45 degrees" |

## 🎯 Features

✅ **Natural Language Processing**: Ask math questions conversationally  
✅ **Gemini 2.5 Flash Integration**: Advanced AI understanding  
✅ **Comprehensive Operations**: 13 mathematical functions  
✅ **Error Handling**: Graceful handling of mathematical errors  
✅ **Interactive Interface**: Real-time mathematical assistance  
✅ **Scientific Calculations**: Trigonometry, logarithms, factorials  
✅ **Precision Computing**: Accurate floating-point calculations  
✅ **Educational Tool**: Perfect for students and professionals  

## 🔧 Running Different Modes

### Interactive Client (Default)
```bash
python3 advanced_calculator_client.py mcp_server.py
```

### Web Server Mode (Optional)
```bash
python3 mcp_server.py --sse
# Then access via SSE at http://localhost:3001
```

## 🎓 Educational Examples

### Basic Math
```
🧮 Math Query: What is 123 + 456?
🧮 Math Query: Calculate 789 - 234
🧮 Math Query: Multiply 12 by 15
🧮 Math Query: Divide 144 by 12
```

### Scientific Calculations
```
🧮 Math Query: What is 3 to the power of 4?
🧮 Math Query: Find the square root of 169
🧮 Math Query: Calculate 6 factorial
🧮 Math Query: What is the natural log of 2.718?
```

### Trigonometry
```
🧮 Math Query: Sin of 45 degrees
🧮 Math Query: Cosine of 90 degrees
🧮 Math Query: Tangent of 60 degrees
```

## 📊 Mathematical Accuracy

- **Floating Point**: All calculations use Python's float precision
- **Integer Operations**: Factorial returns exact integer results
- **Error Handling**: Division by zero and invalid operations handled gracefully
- **Range Limits**: Overflow protection for very large numbers

## 🚀 Integration with Other MCP Servers

This calculator can run alongside other MCP servers using the same virtual environment:

```bash
# Terminal 1: Weather MCP
cd /home/mohan/terraform/MCP/mcp-weather-client-tutorial
source venv/bin/activate
python3 advanced_client.py weather_server.py

# Terminal 2: Calculator MCP (same venv)
cd ../mcp-calculator
python3 advanced_calculator_client.py mcp_server.py

# Terminal 3: Linux MCP (same venv)
cd ../mcp-for-linux
python3 advanced_linux_client.py main.py
```

## 🌟 Powered by Gemini 2.5 Flash

This calculator leverages Google's most advanced AI model for:
- **Natural language understanding** of mathematical expressions
- **Intelligent operation parsing** from conversational queries
- **Context-aware calculations** with step-by-step reasoning
- **Clear result formatting** with explanations

## 🔍 Key Differences from Other MCP Servers

### Calculator vs Weather Server
| Feature | Calculator | Weather Server |
|---------|------------|----------------|
| **Domain** | Mathematics | Weather Data |
| **Operations** | 13 math functions | 5 weather tools |
| **Data Source** | Built-in calculations | National Weather Service API |
| **Complexity** | Synchronous operations | Async API calls |
| **Error Types** | Math errors (div by zero) | Network/API errors |

### Calculator vs Linux Server
| Feature | Calculator | Linux Server |
|---------|------------|--------------|
| **Domain** | Mathematics | System Administration |
| **Structure** | Single file | Modular (tools/ + resources/) |
| **Tools Count** | 13 functions | 25+ tools across categories |
| **Permissions** | None required | Often requires sudo |
| **Safety** | Math-only operations | System-changing operations |

## 📁 Project Structure

```
mcp-calculator/
├── mcp_server.py                    # Main calculator server
├── advanced_calculator_client.py    # Gemini-powered client
├── requirements.txt                 # Dependencies
├── .env                            # API configuration
└── README.md                       # This documentation
```

## ⚠️ Usage Notes

- **Angle Units**: Trigonometric functions use degrees (not radians)
- **Factorial Input**: Requires non-negative integers only
- **Division Safety**: Division by zero returns error message
- **Logarithm Domain**: Only positive numbers accepted
- **Large Numbers**: Very large results may overflow

---

**Happy calculating! 🧮✨**

## 🔧 Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies are installed in venv
2. **API Connection**: Check Google AI API key configuration
3. **Math Errors**: Review input validity (positive numbers for sqrt, etc.)
4. **Server Connection**: Verify server script path is correct

### Getting Help

```
🧮 Math Query: help
🧮 Math Query: what can I calculate?
🧮 Math Query: show examples
```
