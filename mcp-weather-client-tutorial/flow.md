# MCP Weather Server Flow Documentation

This document provides comprehensive flow diagrams showing how the MCP Weather Server operates, from client connection to weather data delivery.

## 🏗️ Overall System Architecture

```mermaid
graph TB
    User[👤 User] --> Client[🖥️ MCP Client<br/>Gemini 2.5 Flash]
    Client --> Server[🌤️ Weather Server<br/>FastMCP]
    Server --> NWS[🌐 National Weather Service API]
    Server --> Coords[📍 Coordinates Database]
    
    subgraph "Client Features"
        Client --> AI[🤖 AI Processing]
        Client --> JSON[📋 JSON Tool Calls]
        Client --> Format[📊 Response Formatting]
    end
    
    subgraph "Server Tools"
        Server --> Alerts[🚨 get_alerts]
        Server --> Forecast[🌡️ get_forecast]
        Server --> Help[❓ get_help]
        Server --> International[🌍 get_international_weather_info]
        Server --> GetCoords[📍 get_coordinates]
    end
    
    subgraph "External APIs"
        NWS --> AlertsAPI[Alerts API]
        NWS --> ForecastAPI[Forecast API]
        NWS --> PointsAPI[Points API]
    end
```

## 🔄 Complete User Interaction Flow

```mermaid
sequenceDiagram
    participant U as 👤 User
    participant C as 🖥️ Client
    participant G as 🤖 Gemini 2.5 Flash
    participant S as 🌤️ Weather Server
    participant N as 🌐 NWS API
    
    U->>C: Start Client
    C->>S: Connect via STDIO
    S-->>C: Connection Established
    C->>S: List Available Tools
    S-->>C: Tools: [get_alerts, get_forecast, get_help, etc.]
    
    loop Interactive Chat
        U->>C: Enter Weather Query
        C->>C: Check for Help Keywords
        C->>C: Check for International Cities
        C->>G: Send Query + System Prompt
        G-->>C: AI Response (Text or JSON Tool Call)
        
        alt Tool Call Required
            C->>S: Execute Tool Call
            S->>N: Fetch Weather Data
            N-->>S: Weather Response
            S-->>C: Formatted Weather Data
            C->>G: Generate Final Response
            G-->>C: Natural Language Response
        else Direct Response
            C-->>U: Display AI Response
        end
        
        C-->>U: Display Final Response
    end
```

## 🛠️ Tool-Specific Flows

### 🚨 Weather Alerts Flow (US States)

```mermaid
flowchart TD
    Start([User asks for alerts]) --> Parse[Parse State Name]
    Parse --> Convert{State in<br/>full name?}
    Convert -->|Yes| StateCode[Convert to 2-letter code]
    Convert -->|No| UseCode[Use provided code]
    StateCode --> BuildURL[Build NWS Alerts URL]
    UseCode --> BuildURL
    
    BuildURL --> APICall[Call NWS API]
    APICall --> CheckResponse{Response<br/>successful?}
    CheckResponse -->|No| Error[Return error message]
    CheckResponse -->|Yes| CheckAlerts{Any alerts<br/>found?}
    
    CheckAlerts -->|No| NoAlerts[✅ No active alerts]
    CheckAlerts -->|Yes| FormatAlerts[📋 Format alerts with emojis]
    FormatAlerts --> Return[Return formatted response]
    NoAlerts --> Return
    Error --> Return
    Return --> End([Display to user])
```

### 🌡️ Weather Forecast Flow (US Coordinates)

```mermaid
flowchart TD
    Start([User provides coordinates]) --> Validate[Validate lat/lng format]
    Validate --> Points[Call NWS Points API]
    Points --> CheckPoints{Points API<br/>successful?}
    CheckPoints -->|No| ErrorCoords[❌ Invalid coordinates<br/>or outside US]
    CheckPoints -->|Yes| ExtractInfo[Extract location info<br/>and forecast URL]
    
    ExtractInfo --> ForecastCall[Call NWS Forecast API]
    ForecastCall --> CheckForecast{Forecast API<br/>successful?}
    CheckForecast -->|No| ErrorForecast[❌ Cannot fetch forecast]
    CheckForecast -->|Yes| ParsePeriods[Parse forecast periods]
    
    ParsePeriods --> Limit[Limit to 5 periods]
    Limit --> FormatPeriods[📅 Format with emojis:<br/>🌡️ Temperature<br/>💨 Wind<br/>🌤️ Conditions]
    FormatPeriods --> Return[Return formatted forecast]
    
    ErrorCoords --> Return
    ErrorForecast --> Return
    Return --> End([Display to user])
```

### 🌍 International Weather Flow

```mermaid
flowchart TD
    Start([User asks about international weather]) --> DetectCity[Detect international city]
    DetectCity --> CheckDatabase{City in<br/>coordinates DB?}
    
    CheckDatabase -->|Yes| ShowCoords[📍 Display coordinates<br/>with usage instructions]
    CheckDatabase -->|No| ShowAlternatives[🌍 Show available cities<br/>and alternatives]
    
    ShowCoords --> ExplainLimitation[⚠️ Explain US-only limitation]
    ShowAlternatives --> ExplainLimitation
    
    ExplainLimitation --> Suggest[💡 Suggest external weather services:<br/>• Weather.com<br/>• AccuWeather<br/>• OpenWeatherMap]
    Suggest --> Return[Return helpful response]
    Return --> End([Display to user])
```

## 🤖 AI Processing Flow

```mermaid
flowchart TD
    Query[User Query Received] --> Keywords{Contains help<br/>keywords?}
    Keywords -->|Yes| HelpTool[Use get_help tool]
    Keywords -->|No| International{International city<br/>detected?}
    
    International -->|Yes| WeatherKeywords{Contains weather<br/>keywords?}
    WeatherKeywords -->|Yes| IntlTool[Use international_weather_info tool]
    WeatherKeywords -->|No| CoordsTool[Use get_coordinates tool]
    
    International -->|No| GeminiPrompt[Send to Gemini 2.5 Flash]
    GeminiPrompt --> GeminiResponse[Receive AI response]
    GeminiResponse --> CheckJSON{Response contains<br/>tool_call JSON?}
    
    CheckJSON -->|Yes| ParseJSON[Parse JSON tool call]
    CheckJSON -->|No| DirectResponse[Return direct response]
    
    ParseJSON --> ExecuteTool[Execute specified tool]
    ExecuteTool --> ToolResult[Get tool result]
    ToolResult --> FinalPrompt[Generate final response prompt]
    FinalPrompt --> FinalAI[Get final AI response]
    
    HelpTool --> ExtractContent[Extract text content]
    IntlTool --> ExtractContent
    CoordsTool --> ExtractContent
    FinalAI --> ExtractContent
    DirectResponse --> ExtractContent
    
    ExtractContent --> Display[Display formatted response]
    Display --> End([User sees result])
```

## 📊 Data Flow Architecture

```mermaid
graph LR
    subgraph "Input Layer"
        UI[User Input]
        Natural[Natural Language]
        Direct[Direct Tool Calls]
    end
    
    subgraph "Processing Layer"
        Client[MCP Client]
        AI[Gemini 2.5 Flash]
        Parser[Query Parser]
        Validator[Input Validator]
    end
    
    subgraph "Service Layer"
        MCP[MCP Server]
        Tools[Weather Tools]
        Router[Request Router]
    end
    
    subgraph "Data Layer"
        NWS[NWS API]
        Coords[Coordinates DB]
        States[State Codes DB]
    end
    
    subgraph "Output Layer"
        Format[Response Formatter]
        Display[User Display]
        Emojis[Emoji Enhancement]
    end
    
    UI --> Client
    Natural --> AI
    Direct --> Parser
    
    Client --> MCP
    AI --> MCP
    Parser --> Validator
    Validator --> MCP
    
    MCP --> Tools
    Tools --> Router
    Router --> NWS
    Router --> Coords
    Router --> States
    
    NWS --> Format
    Coords --> Format
    States --> Format
    Format --> Emojis
    Emojis --> Display
```

## 🔧 Error Handling Flow

```mermaid
flowchart TD
    Start([Request Received]) --> TryProcess{Try to process}
    TryProcess -->|Success| Success[Return successful response]
    TryProcess -->|Error| ErrorType{Error type?}
    
    ErrorType -->|Network| NetworkError[🌐 Network connectivity issue]
    ErrorType -->|API| APIError[⚠️ External API error]
    ErrorType -->|Parsing| ParseError[📋 JSON parsing error]
    ErrorType -->|Validation| ValidationError[❌ Input validation error]
    ErrorType -->|Unknown| UnknownError[🔧 Unknown error]
    
    NetworkError --> LogError[Log error details]
    APIError --> LogError
    ParseError --> LogError
    ValidationError --> LogError
    UnknownError --> LogError
    
    LogError --> UserFriendly[Generate user-friendly message]
    UserFriendly --> Suggest[Suggest alternative actions]
    Suggest --> Return[Return error response]
    
    Success --> Return
    Return --> End([Response delivered])
```

## 🚀 Performance Optimization Flow

```mermaid
graph TB
    Request[Incoming Request] --> Cache{Check cache}
    Cache -->|Hit| CacheReturn[Return cached data]
    Cache -->|Miss| Process[Process request]
    
    Process --> Parallel{Can parallelize?}
    Parallel -->|Yes| ParallelCall[Make parallel API calls]
    Parallel -->|No| Sequential[Sequential processing]
    
    ParallelCall --> Combine[Combine results]
    Sequential --> Combine
    Combine --> Validate[Validate response]
    Validate --> CacheStore[Store in cache]
    CacheStore --> Format[Format response]
    Format --> Compress[Compress if large]
    Compress --> Return[Return to client]
    
    CacheReturn --> Return
    Return --> Monitor[Monitor performance]
    Monitor --> Metrics[Update metrics]
```

## 📈 System Monitoring Flow

```mermaid
flowchart LR
    subgraph "Metrics Collection"
        Requests[Request Count]
        Latency[Response Time]
        Errors[Error Rate]
        Memory[Memory Usage]
    end
    
    subgraph "Health Checks"
        API[NWS API Status]
        Server[Server Health]
        Client[Client Connections]
    end
    
    subgraph "Alerts"
        Threshold[Threshold Monitoring]
        Notification[Alert Notifications]
        Recovery[Auto Recovery]
    end
    
    Requests --> Threshold
    Latency --> Threshold
    Errors --> Threshold
    Memory --> Threshold
    
    API --> Threshold
    Server --> Threshold
    Client --> Threshold
    
    Threshold --> Notification
    Notification --> Recovery
    Recovery --> Requests
```

## 🎯 Key Features Summary

| Feature | Description | Implementation |
|---------|-------------|----------------|
| 🤖 **AI Integration** | Gemini 2.5 Flash for natural language processing | Advanced prompt engineering with tool calling |
| 🌍 **International Support** | Coordinates and guidance for global locations | Built-in city database with 30+ major cities |
| 🚨 **Real-time Alerts** | Live weather alerts for all US states | Direct NWS API integration |
| 📍 **Precise Forecasts** | Coordinate-based weather forecasts | NWS Points → Forecast API chain |
| 🔧 **Error Resilience** | Comprehensive error handling | Multiple fallback strategies |
| 📱 **User-Friendly** | Intuitive emoji-rich responses | Enhanced formatting and clear guidance |

---

*This flow documentation provides a complete overview of the MCP Weather Server architecture, helping developers understand the system's operation and extend its capabilities.*
