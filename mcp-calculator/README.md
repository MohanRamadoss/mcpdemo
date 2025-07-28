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

## 🏗️ Architecture Flow

### System Overview
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   User Input    │    │  Gemini 2.5      │    │  MCP Calculator │
│  (Natural Lang) │───▶│  Flash AI        │───▶│    Server       │
│                 │    │  (Tool Parser)   │    │  (Math Engine)  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         ▲                        │                       │
         │                        ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  Formatted      │    │   JSON Tool      │    │  Mathematical   │
│   Response      │◀───│   Call Request   │◀───│   Calculation   │
│                 │    │                  │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### Flow Breakdown

#### 1. **User Input Processing**
- User enters natural language query: *"What is 3 to the power of 4?"*
- Client captures input and prepares for AI processing

#### 2. **AI Intent Recognition** 
- **Gemini 2.5 Flash** analyzes the query
- Identifies mathematical operation: `power(3, 4)`
- Generates structured JSON tool call:
  ```json
  {"tool_call": {"name": "power", "arguments": {"a": 3, "b": 4}}}
  ```

#### 3. **MCP Server Communication**
- Client sends tool call to **MCP Calculator Server**
- Server validates parameters and executes calculation
- Returns result: `81.0`

#### 4. **Response Enhancement**
- **Gemini 2.5 Flash** receives calculation result
- Generates educational, formatted response
- Includes mathematical explanation and context

#### 5. **User Output**
- Client displays comprehensive result:
  ```
  🧮 Mathematical Result:
  
  The calculation 3 to the power of 4 equals 81.
  This means 3 × 3 × 3 × 3 = 81.
  ```

### Component Details

#### **Advanced Calculator Client** (`advanced_calculator_client.py`)
- **Role**: Orchestrator and AI Interface
- **Responsibilities**:
  - User interaction management
  - Gemini 2.5 Flash integration
  - MCP protocol communication
  - Response formatting and display
- **Key Features**:
  - Natural language processing
  - JSON tool call parsing
  - Error handling and validation
  - Interactive chat loop

#### **MCP Calculator Server** (`mcp_server.py`)
- **Role**: Mathematical Engine
- **Responsibilities**:
  - Mathematical function implementations
  - Parameter validation
  - Result computation
  - Error handling (division by zero, etc.)
- **Available Tools**: 13 mathematical functions
  - Basic: `add`, `subtract`, `multiply`, `divide`
  - Advanced: `power`, `sqrt`, `cbrt`, `factorial`
  - Trigonometric: `sin`, `cos`, `tan`
  - Other: `log`, `remainder`

#### **Gemini 2.5 Flash AI**
- **Role**: Natural Language Processor
- **Responsibilities**:
  - Query interpretation
  - Tool selection and parameter extraction
  - Response generation and formatting
  - Mathematical explanation
- **Configuration**:
  - Temperature: 0.1 (high precision)
  - Max tokens: 1500
  - Response format: Plain text

### Data Flow Example

```
Input: "What is the square root of 144?"
   ↓
Gemini Analysis: Identifies sqrt operation
   ↓
JSON Generation: {"tool_call": {"name": "sqrt", "arguments": {"a": 144}}}
   ↓
MCP Server Call: sqrt(144)
   ↓
Mathematical Result: 12.0
   ↓
AI Enhancement: "The square root of 144 is 12. This means 12 × 12 = 144."
   ↓
Formatted Output: Display with emoji and formatting
```

### Error Handling Flow

```
Invalid Input → AI Detection → Error Response
     ↓              ↓              ↓
Math Error   → Server Check → Graceful Message
     ↓              ↓              ↓
Network Issue → Connection → Retry/Fallback
```

### Integration Points

1. **MCP Protocol**: Standardized communication between client and server
2. **Google AI API**: Gemini 2.5 Flash model integration
3. **Python Math Library**: Core mathematical operations
4. **Environment Configuration**: API key and settings management

This architecture ensures:
- ✅ **Separation of Concerns**: AI, Math, and UI are separate
- ✅ **Scalability**: Easy to add new mathematical functions
- ✅ **Reliability**: Error handling at each layer
- ✅ **Maintainability**: Clear component boundaries
- ✅ **Extensibility**: Can integrate with other MCP servers

## 📊 Professional Flow Diagrams

### 🔄 MCP Client-Server Communication Flow

```
🟦 CLIENT SIDE                    🟩 SERVER SIDE                    🟨 AI LAYER
┌─────────────────┐              ┌─────────────────┐              ┌─────────────────┐
│                 │              │                 │              │                 │
│  User Interface │              │  MCP Server     │              │  Gemini 2.5     │
│                 │              │  (FastMCP)      │              │  Flash AI       │
│      INPUT      │              │                 │              │                 │
└─────────────────┘              └─────────────────┘              └─────────────────┘
         │                                │                                │
         │ ①                             │                                │
         ▼                                │                                │
┌─────────────────┐                      │                                │
│  Query Capture  │                      │                                │
│ "3 to power 4"  │                      │                                │
└─────────────────┘                      │                                │
         │                                │                                │
         │ ②                             │                                │
         ▼                                │                        ③      │
┌─────────────────┐              ┌─────────────────┐              ┌─────────────────┐
│   AI Request    │─────────────▶│                 │─────────────▶│   NLP Analysis  │
│   Formation     │              │                 │              │                 │
└─────────────────┘              │                 │              │ Intent:power(a,b)│
         ▲                        │                 │              └─────────────────┘
         │                        │                 │                        │
         │ ⑧                      │                 │                        │ ④
         │                        │                 │                        ▼
┌─────────────────┐              │                 │              ┌─────────────────┐
│ Response Format │              │                 │              │ JSON Generator  │
│   & Display     │              │                 │              │ {"tool_call":   │
└─────────────────┘              │                 │              │  {"name":"power"│
         ▲                        │                 │              │   "args":{...}}}│
         │                        │                 │              └─────────────────┘
         │ ⑦                      │                 │                        │
         │                        │                 │                        │ ⑤
┌─────────────────┐              │                 │              ┌─────────────────┐
│ Final Response  │◀─────────────│                 │◀─────────────│ JSON Tool Call  │
│   Generation    │              │                 │              │   Validation    │
└─────────────────┘              │                 │              └─────────────────┘
         ▲                        │                 │                        │
         │                        │                 │                        │ ⑥
         │                        │                 │                        ▼
         │                        │  Tool Executor  │              ┌─────────────────┐
         │                        │                 │              │   MCP Client    │
         │                        │   power(3,4)    │              │  Session.call   │
         │                        │      ↓          │              │    _tool()      │
         │                        │   Result: 81    │              └─────────────────┘
         │                        │                 │                        │
         │                        └─────────────────┘                        │
         │                                ▲                                   │
         │                                │                                   │
         └────────────────────────────────┼───────────────────────────────────┘
                                          │
                                    📊 Mathematical
                                       Engine
```

### 🔧 Detailed Component Flow

#### 🟦 **CLIENT RESPONSIBILITIES**
```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENT OPERATIONS                        │
├─────────────────────────────────────────────────────────────────┤
│ 🎯 USER INTERACTION                                             │
│   ├── Input Collection (natural language)                      │
│   ├── Command Parsing (quit, help, calculations)               │
│   └── Response Display (formatted output)                      │
│                                                                 │
│ 🤖 AI INTEGRATION                                               │
│   ├── Gemini 2.5 Flash Configuration                          │
│   ├── Prompt Engineering (system prompts)                      │
│   ├── Response Processing (JSON extraction)                    │
│   └── Error Handling (parsing failures)                        │
│                                                                 │
│ 🔗 MCP COMMUNICATION                                            │
│   ├── Server Connection (STDIO transport)                      │
│   ├── Session Management (initialization)                      │
│   ├── Tool Discovery (list_tools)                             │
│   └── Tool Execution (call_tool)                              │
└─────────────────────────────────────────────────────────────────┘
```

#### 🟩 **SERVER RESPONSIBILITIES**
```
┌─────────────────────────────────────────────────────────────────┐
│                       SERVER OPERATIONS                         │
├─────────────────────────────────────────────────────────────────┤
│ 🧮 MATHEMATICAL ENGINE                                          │
│   ├── Function Registry (13 mathematical operations)           │
│   ├── Parameter Validation (type checking)                     │
│   ├── Calculation Execution (math operations)                  │
│   └── Result Formatting (float/int conversion)                 │
│                                                                 │
│ 🛡️ ERROR HANDLING                                              │
│   ├── Division by Zero Protection                              │
│   ├── Domain Validation (sqrt, log constraints)               │
│   ├── Overflow Detection (large numbers)                       │
│   └── Type Safety (integer vs float)                          │
│                                                                 │
│ 📡 MCP PROTOCOL                                                 │
│   ├── Tool Registration (@mcp.tool decorators)                │
│   ├── Request Processing (FastMCP framework)                   │
│   ├── Response Serialization (JSON format)                    │
│   └── Transport Management (STDIO/SSE)                        │
└─────────────────────────────────────────────────────────────────┘
```

#### 🟨 **AI MANAGEMENT FLOW**
```
┌─────────────────────────────────────────────────────────────────┐
│                      AI ORCHESTRATION                          │
├─────────────────────────────────────────────────────────────────┤
│ 🧠 NATURAL LANGUAGE PROCESSING                                 │
│   ├── Query Analysis ("square root of 144")                   │
│   ├── Intent Recognition (mathematical operation)              │
│   ├── Parameter Extraction (numbers and operations)           │
│   └── Context Understanding (mathematical concepts)            │
│                                                                 │
│ 🔧 TOOL ORCHESTRATION                                          │
│   ├── Tool Selection (choosing correct function)              │
│   ├── JSON Generation (structured tool calls)                 │
│   ├── Parameter Mapping (natural language → function args)    │
│   └── Validation Logic (parameter constraints)                │
│                                                                 │
│ 📝 RESPONSE ENHANCEMENT                                         │
│   ├── Result Interpretation (mathematical meaning)            │
│   ├── Educational Content (step-by-step explanations)         │
│   ├── Formatting & Styling (emojis, structure)               │
│   └── Error Communication (user-friendly messages)           │
└─────────────────────────────────────────────────────────────────┘
```

### 🔄 Step-by-Step Communication Protocol

```
    CLIENT                          AI LAYER                        SERVER
      │                               │                               │
      │ ①─────────────────────────────▶│                               │
      │   "What is 3^4?"               │                               │
      │                               │                               │
      │                               │ ② Analyze Query               │
      │                               │    ↓                          │
      │                               │   Identify: power(3,4)        │
      │                               │    ↓                          │
      │                               │ ③ Generate JSON               │
      │                               │   {"tool_call":               │
      │                               │    {"name":"power",           │
      │                               │     "args":{"a":3,"b":4}}}    │
      │                               │                               │
      │ ④◀────────────────────────────│                               │
      │   JSON Tool Call              │                               │
      │                               │                               │
      │ ⑤─────────────────────────────────────────────────────────────▶│
      │   session.call_tool("power", {"a":3, "b":4})                 │
      │                               │                               │
      │                               │                               │ ⑥ Execute
      │                               │                               │   power(3,4)
      │                               │                               │   ↓
      │                               │                               │   Result: 81.0
      │                               │                               │
      │ ⑦◀────────────────────────────────────────────────────────────│
      │   Return: 81.0                │                               │
      │                               │                               │
      │ ⑧─────────────────────────────▶│                               │
      │   Raw Result + Context        │                               │
      │                               │                               │
      │                               │ ⑨ Enhance Response            │
      │                               │   "3 to the power of 4        │
      │                               │    equals 81. This means      │
      │                               │    3×3×3×3 = 81"              │
      │                               │                               │
      │ ⑩◀────────────────────────────│                               │
      │   Enhanced Response           │                               │
      │                               │                               │
      │ ⑪ Display to User             │                               │
      │   🧮 Mathematical Result:      │                               │
      │   3^4 = 81                    │                               │
```

### 🎨 Color Legend

- 🟦 **BLUE**: Client-side operations (User Interface, Session Management)
- 🟩 **GREEN**: Server-side operations (Mathematical Engine, Tool Registry)
- 🟨 **YELLOW**: AI Layer operations (NLP, Tool Orchestration, Response Generation)
- 🔄 **ARROWS**: Data flow direction and process sequence
- 📊 **SYMBOLS**: 
  - ① ② ③ Sequential steps
  - ▶ ◀ Data transmission direction
  - ↓ ↑ Internal processing flow

### 🏗️ Architecture Benefits

| Component | Responsibility | Benefits |
|-----------|---------------|----------|
| **Client** | UI + AI Integration | • Smooth user experience<br>• Intelligent query processing<br>• Error handling |
| **AI Layer** | Natural Language Processing | • Human-like interaction<br>• Context understanding<br>• Educational responses |
| **Server** | Mathematical Computing | • Precise calculations<br>• Function modularity<br>• Scalable operations |

This design ensures **loose coupling**, **high cohesion**, and **clear separation of concerns** for maintainable and extensible mathematical computing.

## 🔗 Deep Dive: MCP Client-Server Communication

### 🚀 How FastMCP Works

#### **Server Side: `mcp_server.py`**
```python
# FastMCP Framework Initialization
mcp = FastMCP(
    "Scientific Calculator",                    # Server name
    description="A scientific calculator providing mathematical operations",
    version="1.0.0"
)

# Tool Registration via Decorators
@mcp.tool()
def add(a: float, b: float) -> float:
    """Add two numbers"""
    return float(a + b)
```

**🔧 FastMCP Architecture:**
```
FastMCP Server Process
├── 📡 Transport Layer (STDIO/SSE)
├── 🛠️ Tool Registry (@mcp.tool decorators)
├── 📝 Schema Generator (automatic from function signatures)
├── 🔍 Request Parser (JSON-RPC protocol)
├── ⚡ Function Executor (direct Python calls)
└── 📤 Response Serializer (JSON format)
```

#### **Client Side: `advanced_calculator_client.py`**
```python
# MCP Client Session Setup
server_params = StdioServerParameters(
    command="python3",                          # Execute server
    args=[server_script_path],                 # Server file path
    env=None                                   # Environment variables
)

# Transport and Session Management
stdio_transport = await stdio_client(server_params)
self.stdio, self.write = stdio_transport
self.session = ClientSession(self.stdio, self.write)
await self.session.initialize()
```

### 🔄 Communication Protocol Flow

#### **1. Server Startup Process**
```
mcp_server.py Execution
         ↓
FastMCP Initialization
         ↓
Tool Registration Scan (@mcp.tool decorators)
         ↓
Schema Generation (function signatures → JSON schema)
         ↓
Transport Setup (STDIO for client communication)
         ↓
Ready for Requests (listening on stdin/stdout)
```

#### **2. Client Connection Process**
```
advanced_calculator_client.py
         ↓
StdioServerParameters Configuration
         ↓
Subprocess Launch (python3 mcp_server.py)
         ↓
STDIO Transport Establishment
         ↓
ClientSession Creation
         ↓
MCP Handshake (initialize())
         ↓
Tool Discovery (list_tools())
```

#### **3. Request-Response Cycle**
```
🟨 AI LAYER                    🟦 CLIENT                      🟩 SERVER
     │                             │                             │
     │ ① Generate JSON              │                             │
     │   Tool Call                  │                             │
     │                             │                             │
     │ {"tool_call":               │                             │
     │  {"name": "power",          │                             │
     │   "arguments":              │                             │
     │    {"a": 3, "b": 4}}}       │                             │
     │                             │                             │
     │ ②────────────────────────▶  │                             │
     │                             │                             │
     │                             │ ③ session.call_tool()       │
     │                             │   ────────────────────────▶ │
     │                             │                             │
     │                             │   JSON-RPC Request:         │
     │                             │   {                         │
     │                             │     "method": "tools/call", │
     │                             │     "params": {             │
     │                             │       "name": "power",      │
     │                             │       "arguments": {        │
     │                             │         "a": 3, "b": 4      │
     │                             │       }                     │
     │                             │     }                       │
     │                             │   }                         │
     │                             │                             │
     │                             │                             │ ④ FastMCP Processing
     │                             │                             │   ├─ Request Parse
     │                             │                             │   ├─ Tool Lookup
     │                             │                             │   ├─ Parameter Validation
     │                             │                             │   ├─ Function Execution
     │                             │                             │   │   power(3, 4) = 81.0
     │                             │                             │   └─ Response Format
     │                             │                             │
     │                             │   JSON-RPC Response:        │
     │                             │   {                         │
     │                             │     "content": [            │
     │                             │       {                     │
     │                             │         "type": "text",     │
     │                             │         "text": "81.0"      │
     │                             │       }                     │
     │                             │     ]                       │
     │                             │   }                         │
     │                             │                             │
     │                             │ ⑤ ◀────────────────────────  │
     │                             │                             │
     │ ⑥ ◀──────────────────────── │                             │
     │   Raw Result: "81.0"        │                             │
     │                             │                             │
     │ ⑦ AI Enhancement            │                             │
     │   "3 to the power of 4      │                             │
     │    equals 81. This means    │                             │
     │    3×3×3×3 = 81"            │                             │
     │                             │                             │
     │ ⑧ ────────────────────────▶ │                             │
     │   Enhanced Response         │                             │
```

### 🧠 AI Integration Deep Dive

#### **Gemini 2.5 Flash Role in Communication**

```python
# AI System Prompt Construction
system_prompt = f"""You are an advanced mathematical assistant with access to these calculator tools:

{tools_description}

When you need to use a tool, respond with ONLY a clean JSON object:
{{"tool_call": {{"name": "tool_name", "arguments": {{"param1": value1}}}}}}
"""

# AI Configuration for Mathematical Precision
generation_config = {
    "temperature": 0.1,          # Low temperature for accuracy
    "top_p": 0.9,               # Focused sampling
    "top_k": 50,                # Limited token selection
    "max_output_tokens": 1500,   # Response length limit
    "response_mime_type": "text/plain"
}
```

#### **AI Processing Pipeline**
```
User Query: "What is 3 to the power of 4?"
         ↓
🧠 Gemini 2.5 Flash Analysis
├── ① Natural Language Understanding
│   ├─ Parse: "3 to the power of 4"
│   ├─ Identify: Mathematical operation
│   └─ Extract: base=3, exponent=4
│
├── ② Tool Selection Logic
│   ├─ Available tools scan
│   ├─ Match operation: "power"
│   └─ Parameter mapping: a=3, b=4
│
├── ③ JSON Generation
│   ├─ Structure validation
│   ├─ Parameter type checking
│   └─ Format compliance
│
└── ④ Output: {"tool_call": {"name": "power", "arguments": {"a": 3, "b": 4}}}
```

### 📡 STDIO Transport Protocol

#### **How STDIO Communication Works**
```
Client Process                    Server Process
┌─────────────┐                  ┌─────────────┐
│             │                  │             │
│ Python      │    stdin/stdout  │ Python      │
│ Client      │ ◀──────────────▶ │ Server      │
│ Session     │                  │ FastMCP     │
│             │                  │             │
└─────────────┘                  └─────────────┘
      │                                │
      │ JSON-RPC Messages              │
      │ ───────────────────────────▶   │
      │                                │
      │ ◀─────────────────────────────  │
      │ JSON-RPC Responses             │
```

**Message Format:**
```json
// Client → Server (Tool Call)
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "power",
    "arguments": {
      "a": 3,
      "b": 4
    }
  }
}

// Server → Client (Result)
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "81.0"
      }
    ]
  }
}
```

### 🔧 FastMCP Tool Registry Mechanism

#### **Decorator Magic: `@mcp.tool()`**
```python
@mcp.tool()
def power(a: float, b: float) -> float:
    """Power of two numbers"""
    try:
        return float(a ** b)
    except OverflowError:
        raise ValueError("Result too large")
```

**What Happens Behind the Scenes:**
```
1. Decorator Registration
   ├── Function signature analysis
   ├── Parameter type extraction
   ├── Docstring processing
   └── Tool schema generation

2. Schema Creation
   {
     "name": "power",
     "description": "Power of two numbers",
     "inputSchema": {
       "type": "object",
       "properties": {
         "a": {"type": "number"},
         "b": {"type": "number"}
       },
       "required": ["a", "b"]
     }
   }

3. Runtime Registration
   ├── Tool registry update
   ├── Function pointer storage
   └── Ready for execution
```

### 🚦 Error Handling Flow

#### **Multi-Layer Error Management**
```
🟨 AI Layer Errors              🟦 Client Errors              🟩 Server Errors
├── JSON parsing failures       ├── Connection issues          ├── Mathematical errors
├── Tool selection errors       ├── Transport failures         ├── Parameter validation
├── Parameter validation        ├── Session management         ├── Function execution
└── Response generation         └── Timeout handling           └── Result serialization
         │                              │                              │
         ▼                              ▼                              ▼
    Graceful degradation     →    Retry mechanisms      →    Error propagation
         │                              │                              │
         ▼                              ▼                              ▼
    User-friendly messages   →    Fallback strategies   →    JSON error responses
```

### 🎯 Key Communication Benefits

| Layer | Benefit | Implementation |
|-------|---------|----------------|
| **AI Layer** | Natural Language → Structured Calls | Gemini 2.5 Flash with system prompts |
| **Client Layer** | Session Management + Error Handling | MCP ClientSession with async/await |
| **Transport** | Reliable Process Communication | STDIO with JSON-RPC protocol |
| **Server Layer** | Automatic Tool Discovery | FastMCP decorators + schema generation |
| **Math Engine** | Precise Calculations | Python math library with error handling |

This architecture enables **seamless natural language mathematical computing** through sophisticated AI orchestration and robust MCP protocol communication! 🧮✨

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
