# GCP Cloud Management MCP Server ☁️

A comprehensive Google Cloud Platform management agent built with the Model Context Protocol (MCP) and powered by Gemini 2.5 Flash AI.

## Features

✅ **Compute Engine**: Instance management across zones  
✅ **Cloud Storage**: Bucket and object operations  
✅ **Cloud Functions**: Serverless function management and invocation  
✅ **Cloud Monitoring**: Metrics and performance data  
✅ **Billing Information**: Cost tracking and analysis  
✅ **Multi-Zone Support**: Work across all GCP zones and regions  
✅ **Natural Language Interface**: Powered by Gemini 2.5 Flash  

## Architecture Overview

### MCP Protocol & AI Integration Flow

```mermaid
sequenceDiagram
    participant User
    participant GeminiAI as Gemini 2.5 Flash AI
    participant MCPClient as MCP Client
    participant MCPServer as GCP MCP Server
    participant GCPAPIs as Google Cloud APIs
    
    User->>GeminiAI: "List my compute instances in us-central1-a"
    
    Note over GeminiAI: AI processes natural language<br/>and understands intent
    
    GeminiAI->>MCPClient: Generate tool call JSON<br/>{"tool_call": {"name": "list_compute_instances", "arguments": {"zone": "us-central1-a"}}}
    
    MCPClient->>MCPServer: Execute MCP tool call via STDIO
    
    Note over MCPServer: MCP Server validates<br/>parameters and permissions
    
    MCPServer->>GCPAPIs: Call Compute Engine API<br/>compute_v1.InstancesClient.list()
    GCPAPIs-->>MCPServer: Return instance data
    
    MCPServer-->>MCPClient: Return formatted GCP data<br/>via MCP protocol
    
    MCPClient->>GeminiAI: Process raw data with context<br/>for user-friendly response
    
    Note over GeminiAI: AI enhances raw data with<br/>intelligent formatting and insights
    
    GeminiAI-->>User: "☁️ Found 3 instances in us-central1-a:<br/>• web-server-1 (running)<br/>• api-server-2 (stopped)<br/>• db-server-3 (running)"
```

### System Architecture

```mermaid
graph TB
    subgraph "User Interface Layer"
        A[User Query<br/>Natural Language] --> B[Gemini 2.5 Flash AI<br/>Language Understanding]
    end
    
    subgraph "AI Processing Layer"
        B --> C[Intent Analysis]
        C --> D[Tool Selection Logic]
        D --> E[Parameter Extraction]
    end
    
    subgraph "MCP Protocol Layer"
        E --> F[MCP Client<br/>Protocol Handler]
        F --> G[STDIO Transport]
        G --> H[MCP Server<br/>Tool Executor]
    end
    
    subgraph "GCP Integration Layer"
        H --> I[Authentication<br/>Service Account/OAuth]
        I --> J[GCP API Gateway]
    end
    
    subgraph "Google Cloud Services"
        J --> K[Compute Engine]
        J --> L[Cloud Storage]
        J --> M[Cloud Functions]
        J --> N[Cloud Monitoring]
        J --> O[Cloud Billing]
    end
    
    subgraph "Response Processing"
        K --> P[Data Aggregation]
        L --> P
        M --> P
        N --> P
        O --> P
        P --> Q[MCP Response Format]
        Q --> R[AI Enhancement<br/>Gemini 2.5 Flash]
        R --> S[User-Friendly Output]
    end
    
    style A fill:#e1f5fe
    style B fill:#f3e5f5
    style H fill:#e8f5e8
    style R fill:#fff3e0
```

### MCP Protocol Communication Flow

```mermaid
flowchart TD
    A[User Input<br/>'Start instance web-server-1'] --> B{Gemini 2.5 Flash<br/>Analysis}
    
    B -->|Intent: Control GCP| C[Tool Call Generation<br/>JSON Format]
    
    C --> D[MCP Client<br/>Protocol Handler]
    
    D -->|STDIO Transport| E[MCP Server<br/>Receives Tool Call]
    
    E --> F{Tool Validation}
    F -->|Valid| G[Execute GCP API Call]
    F -->|Invalid| H[Return Error Response]
    
    G --> I[Google Cloud APIs<br/>Compute Engine]
    I --> J[Operation Success/Failure]
    
    J --> K[Format MCP Response]
    K -->|STDIO Transport| L[MCP Client Receives Data]
    
    L --> M[Gemini 2.5 Flash<br/>Response Enhancement]
    M --> N[Formatted User Response]
    
    H --> L
    
    style A fill:#e1f5fe
    style B fill:#f3e5f5
    style E fill:#e8f5e8
    style I fill:#fff3e0
    style M fill:#f3e5f5
```

### Tool Calling Architecture

```mermaid
classDiagram
    class GeminiAI {
        +processQuery(userInput)
        +generateToolCall(intent)
        +enhanceResponse(rawData)
        +model: gemini-2.5-flash
    }
    
    class MCPClient {
        +connectToServer(serverPath)
        +executeToolCall(toolName, args)
        +processResponse(mcpResponse)
        +session: ClientSession
    }
    
    class MCPServer {
        +registerTools()
        +validateRequest(toolCall)
        +executeGCPOperation(params)
        +formatResponse(gcpData)
    }
    
    class GCPTool {
        +name: string
        +description: string
        +parameters: schema
        +execute(args)
    }
    
    class GCPService {
        +authenticate()
        +callAPI(endpoint, params)
        +handleResponse(apiResponse)
        +credentials: ServiceAccount
    }
    
    GeminiAI --> MCPClient : "Intelligent tool selection"
    MCPClient --> MCPServer : "MCP Protocol (STDIO)"
    MCPServer --> GCPTool : "Tool execution"
    GCPTool --> GCPService : "API calls"
    GCPService --> GCPTool : "Cloud data"
    GCPTool --> MCPServer : "Formatted results"
    MCPServer --> MCPClient : "MCP response"
    MCPClient --> GeminiAI : "Raw data for enhancement"
```

## Prerequisites

- Python 3.8+
- GCP credentials configured (gcloud CLI or service account)
- Google AI API key for Gemini 2.5 Flash
- Required IAM permissions for GCP services

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Configure GCP credentials (choose one method)
gcloud auth application-default login  # gcloud CLI
# OR set service account key
export GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account.json

# Run the server
python3 gcp_client.py gcp_server.py
```

## Usage Examples

**Compute Engine:**
- "List compute instances in us-central1-a"
- "Start instance web-server-1"
- "Stop instance web-server-1"

**Cloud Storage:**
- "List all storage buckets"
- "Show objects in bucket my-data-bucket"

**Cloud Functions:**
- "List Cloud Functions in us-central1"
- "Invoke function my-function"

**Cloud Monitoring:**
- "Get CPU metrics for the last 2 hours"
- "Show memory utilization metrics"

## How MCP Enables Intelligent Cloud Management

### 1. **Protocol Standardization**
MCP provides a standardized interface between AI models and cloud tools, enabling:
- Consistent tool discovery and registration
- Type-safe parameter passing
- Reliable error handling
- Transport-agnostic communication

### 2. **AI-Driven Tool Selection**
Gemini 2.5 Flash analyzes user queries and automatically:
- Identifies the appropriate GCP service
- Selects the correct tool from available options
- Extracts and formats required parameters
- Handles complex multi-step operations

### 3. **Seamless Integration**
The MCP protocol bridges the gap between:
- Natural language user interface
- Structured API calls to Google Cloud
- Rich, contextual response generation

## Available Tools

| Category | Tools | Description |
|----------|-------|-------------|
| **Compute Engine** | `list_compute_instances`, `start_compute_instance`, `stop_compute_instance` | VM management |
| **Cloud Storage** | `list_storage_buckets`, `get_storage_bucket_objects` | Storage management |
| **Cloud Functions** | `list_cloud_functions`, `invoke_cloud_function` | Serverless functions |
| **Cloud Monitoring** | `get_monitoring_metrics` | Performance metrics |
| **Billing** | `get_gcp_billing_info` | Cost information |

## Security Best Practices

- Use service accounts with minimal permissions
- Enable audit logging
- Regularly review IAM permissions
- Use VPC security controls

## Sample Queries

- "What Compute instances are running in us-west1-a?"
- "Start instance my-vm in us-central1-a"
- "How many storage buckets do I have?"
- "List my Cloud Functions and their runtimes"
- "Show CPU usage for the last hour"

## Technical Benefits of MCP

### For Developers
- **Rapid Prototyping**: Build cloud management tools quickly
- **Type Safety**: Schema-validated tool parameters
- **Error Handling**: Consistent error responses across tools
- **Extensibility**: Easy to add new cloud services

### For Users
- **Natural Language**: No need to learn complex CLI commands
- **Intelligent Assistance**: AI understands context and intent
- **Consistent Experience**: Same interface across all cloud services
- **Real-time Feedback**: Immediate responses to cloud operations

### For Operations
- **Audit Trail**: Complete logging of all operations
- **Permission Control**: Fine-grained access control
- **Monitoring**: Built-in performance and error monitoring
- **Scalability**: Handle multiple concurrent operations
