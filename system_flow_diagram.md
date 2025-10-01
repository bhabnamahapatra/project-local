# AI Organization Dashboard - End-to-End System Flow Diagram

## 🎯 **System Overview Flow**

```mermaid
flowchart TD
    subgraph "User Entry Points"
        A1[👤 Developer/User] --> A2{Choose Action}
        A2 -->|Deploy System| A3[Run docker-compose up]
        A2 -->|Access Dashboard| A4[Open Browser: localhost:3000]
        A2 -->|Test APIs| A5[Run API Tests]
        A2 -->|Backup Data| A6[Run Backup Script]
    end

    subgraph "System Initialization"
        A3 --> B1[PostgreSQL Container]
        A3 --> B2[API Container]
        A3 --> B3[Collector Container]
        A3 --> B4[Dashboard Container]
        
        B1 --> B1a[Initialize Database Schema]
        B1 --> B1b[Create Tables & Indexes]
        B1 --> B1c[Setup Unified Metrics View]
        
        B2 --> B2a[Start FastAPI Server]
        B2 --> B2b[Connect to Database]
        B2 --> B2c[Setup CORS & Routes]
        
        B3 --> B3a[Load Environment Variables]
        B3 --> B3b[Schedule Collection Jobs]
        B3 --> B3c[Connect to Database]
        
        B4 --> B4a[Build React App]
        B4 --> B4b[Start Nginx Server]
        B4 --> B4c[Configure API Proxy]
    end

    subgraph "Data Collection Flow"
        C1[Scheduled Collection Job] --> C2{Check API Keys}
        C2 -->|Keys Valid| C3[Collect OpenAI Metrics]
        C2 -->|Keys Valid| C4[Collect GitHub Copilot Metrics]
        C2 -->|Keys Valid| C5[Collect Anthropic Claude Metrics]
        C2 -->|Keys Valid| C6[Collect Cursor Metrics]
        C2 -->|Keys Missing| C7[Log Error & Skip]
        
        C3 --> C8[Parse API Responses]
        C4 --> C8
        C5 --> C8
        C6 --> C8
        
        C8 --> C9[Transform Data Format]
        C9 --> C10[Insert into Database]
        C10 --> C11[Update Unified Metrics View]
    end

    subgraph "API Request Flow"
        D1[Client Request] --> D2{API Endpoint}
        
        D2 -->|GET /| D3[Return System Status]
        D2 -->|GET /health| D4[Return Health Check]
        D2 -->|GET /stats| D5[Return System Stats]
        
        D2 -->|POST /auth/login| D6{Validate Credentials}
        D6 -->|Valid| D7[Generate JWT Token]
        D6 -->|Invalid| D8[Return 401 Error]
        
        D2 -->|GET /metrics| D9[Query Database]
        D2 -->|GET /metrics/{app}| D10[Query Specific App]
        D2 -->|GET /metrics/{app}/stats| D11[Calculate Statistics]
        
        D9 --> D12[Format Response]
        D10 --> D12
        D11 --> D12
        D3 --> D12
        D4 --> D12
        D5 --> D12
        D7 --> D12
        D8 --> D12
        
        D12 --> D13[Return JSON Response]
    end

    subgraph "Dashboard Flow"
        E1[User Opens Dashboard] --> E2[Load Dashboard UI]
        E2 --> E3[Fetch System Status]
        E3 --> E4{Status OK?}
        
        E4 -->|Yes| E5[Fetch Metrics Data]
        E4 -->|No| E6[Show Error Message]
        
        E5 --> E7[Process & Format Data]
        E7 --> E8[Render Charts & Tables]
        E8 --> E9[Display KPIs]
        
        E9 --> E10{User Interaction}
        E10 -->|Filter by Date| E11[Update Charts]
        E10 -->|Select App| E12[Show App Details]
        E10 -->|Export Data| E13[Download CSV/JSON]
        E10 -->|Refresh| E5
    end

    subgraph "Data Storage"
        F1[PostgreSQL Database] --> F2[openai_metrics Table]
        F1 --> F3[copilot_metrics Table]
        F1 --> F4[claude_metrics Table]
        F1 --> F5[cursor_metrics Table]
        
        F2 --> F6[unified_metrics View]
        F3 --> F6
        F4 --> F6
        F5 --> F6
        
        F6 --> F7[Aggregated Reports]
    end

    subgraph "Backup & Recovery"
        G1[Backup Trigger] --> G2{Backup Type}
        G2 -->|Full Backup| G3[Export Complete Database]
        G2 -->|Table Export| G4[Export Specific Table]
        G2 -->|CSV Export| G5[Export as CSV]
        
        G3 --> G6[Save Backup File]
        G4 --> G6
        G5 --> G6
        
        G7[Restore Trigger] --> G8{Restore Type}
        G8 -->|Full Restore| G9[Import Complete Database]
        G8 -->|Table Import| G10[Import Specific Table]
        G8 -->|CSV Import| G11[Import from CSV]
        
        G9 --> G12[Verify Data Integrity]
        G10 --> G12
        G11 --> G12
    end

    subgraph "Testing Flow"
        H1[Test Suite Start] --> H2{Test Type}
        
        H2 -->|Health Tests| H3[Test Health Endpoints]
        H2 -->|Auth Tests| H4[Test Login/Logout]
        H2 -->|Metrics Tests| H5[Test All Metric Endpoints]
        H2 -->|Error Tests| H6[Test Error Handling]
        H2 -->|Performance Tests| H7[Test Response Times]
        
        H3 --> H8{Tests Pass?}
        H4 --> H8
        H5 --> H8
        H6 --> H8
        H7 --> H8
        
        H8 -->|Yes| H9[Generate Success Report]
        H8 -->|No| H10[Generate Failure Report]
        
        H9 --> H11[Show Coverage Stats]
        H10 --> H11
    end

    %% Connections between flows
    B1 -.->|Data Storage| F1
    C10 -.->|Store Data| F1
    D9 -.->|Query Data| F1
    E5 -.->|Fetch Data| D9
    G3 -.->|Backup| F1
    G9 -.->|Restore| F1
    H5 -.->|Test| D9

    style A1 fill:#e1f5fe
    style A2 fill:#fff3e0
    style B1 fill:#f3e5f5
    style F1 fill:#e8f5e9
    style G1 fill:#ffebee
    style H1 fill:#fce4ec
```

## 📋 **Flowchart Symbol Legend**

| Symbol | Meaning | Example |
|--------|---------|---------|
| 🔷 Rectangle | Process/Action | `Start API Server` |
| 🔶 Diamond | Decision Point | `{Keys Valid?}` |
| 🔵 Rounded Rectangle | Start/End Point | `[User Entry]` |
| 📄 Rectangle with Dashed Lines | Data Storage | `PostgreSQL Database` |
| 🔄 Circle | Connector | `C1` |
| → Arrow | Flow Direction | `A → B` |
| -.-> Dotted Arrow | Data Flow | `Query → Database` |

## 🎯 **Key Decision Points**

1. **API Key Validation**: Determines if data collection proceeds
2. **Health Status Check**: Controls dashboard accessibility
3. **Authentication**: Gatekeeps API access
4. **Test Results**: Determines deployment success

## 🔄 **Data Flow Patterns**

- **Collection Flow**: External APIs → Collectors → Database → Unified View
- **API Flow**: Client → FastAPI → Database → JSON Response
- **Dashboard Flow**: Browser → API Calls → Data Processing → UI Rendering
- **Backup Flow**: Database → Export → File System → Transfer

## ⚡ **Critical Paths**

- **Successful Deployment**: All services healthy → Data collection active → Dashboard accessible
- **Failed Deployment**: Any service down → Error handling → Recovery procedures
- **Data Pipeline**: Scheduled collection → API calls → Database storage → Dashboard display

---

*This flowchart provides a complete visual representation of the AI Organization Dashboard system, showing all major processes, decision points, and data flows from user entry to final output.*