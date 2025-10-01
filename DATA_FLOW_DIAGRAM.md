# AI Organization Dashboard - Comprehensive Data Flow Diagram

## Overview

This document provides a detailed, step-by-step data flow diagram illustrating the complete data lifecycle within the AI Organization Dashboard system, from data ingestion to visualization.

## Data Flow Architecture

```mermaid
graph TB
    %% Define subgraphs for different system layers
    subgraph "External Data Sources"
        OAPI["OpenAI API<br/>REST API<br/>JSON Format"]
        COAPI["GitHub Copilot API<br/>REST API<br/>JSON Format"]
        CLAPI["Claude API<br/>REST API<br/>JSON Format"]
        CUAPI["Cursor API<br/>REST API<br/>JSON Format"]
    end

    subgraph "Data Collection Layer"
        COLLECTOR["Collector Service<br/>Python Application<br/>Port: N/A"]
        OPENAI_COLLECTOR["openai.py<br/>OpenAI Collector Module"]
        COPILOT_COLLECTOR["copilot.py<br/>Copilot Collector Module"]
        CLAUDE_COLLECTOR["claude.py<br/>Claude Collector Module"]
        CURSOR_COLLECTOR["cursor.py<br/>Cursor Collector Module"]
        SCHEDULER["Collection Scheduler<br/>Cron/Interval Based"]
    end

    subgraph "Data Processing & Transformation"
        TRANSFORM["Data Transformer<br/>Format Normalization"]
        VALIDATE["Data Validator<br/>Schema Validation"]
        ENRICH["Data Enricher<br/>Add Metadata/Timestamps"]
        AGGREGATE["Data Aggregator<br/>Statistical Calculations"]
    end

    subgraph "Data Storage Layer"
        POSTGRES[("PostgreSQL Database<br/>Port: 5432<br/>Tables: openai_metrics, copilot_metrics,<br/>claude_metrics, cursor_metrics")]
        CACHE["In-Memory Cache<br/>FastAPI Caching"]
        INDEXES["Database Indexes<br/>Performance Optimization"]
    end

    subgraph "API Service Layer"
        FASTAPI["FastAPI Service<br/>Port: 5000<br/>REST API"]
        METRICS_ROUTER["/metrics/* Endpoints<br/>Data Retrieval APIs"]
        AUTH_ROUTER["/auth/* Endpoints<br/>Authentication APIs"]
        HEALTH_ROUTER["/health Endpoint<br/>System Health Check"]
        MIDDLEWARE["CORS Middleware<br/>Security Layer"]
    end

    subgraph "Frontend Application"
        REACT["React Application<br/>Port: 3000<br/>TypeScript"]
        DASHBOARD["DashboardPage Component<br/>Main Dashboard View"]
        CHARTS["MetricsChart Component<br/>Data Visualization"]
        TABLES["MetricsTable Component<br/>Tabular Data Display"]
        FILTERS["FilterPanel Component<br/>Data Filtering"]
        AUTH["AuthContext<br/>Authentication State"]
    end

    subgraph "Data Output & Visualization"
        CHART_VIZ["Interactive Charts<br/>Line/Bar Charts<br/>Recharts Library"]
        TABLE_VIZ["Data Tables<br/>Sortable/Filterable<br/>Material-UI"]
        STATS["KPI Cards<br/>Aggregated Statistics<br/>Real-time Updates"]
        EXPORT["Data Export<br/>JSON/CSV Formats<br/>Future Feature"]
    end

    %% Data Collection Flow
    OAPI -->|"HTTPS Request<br/>API Keys<br/>Rate Limited"| OPENAI_COLLECTOR
    COAPI -->|"HTTPS Request<br/>OAuth Tokens<br/>Rate Limited"| COPILOT_COLLECTOR
    CLAPI -->|"HTTPS Request<br/>API Keys<br/>Rate Limited"| CLAUDE_COLLECTOR
    CUAPI -->|"HTTPS Request<br/>API Keys<br/>Rate Limited"| CURSOR_COLLECTOR

    OPENAI_COLLECTOR -->|"Raw JSON Data<br/>Timestamp: ISO 8601<br/>Model Performance"| COLLECTOR
    COPILOT_COLLECTOR -->|"Raw JSON Data<br/>Usage Statistics<br/>Suggestion Metrics"| COLLECTOR
    CLAUDE_COLLECTOR -->|"Raw JSON Data<br/>Response Metrics<br/>Token Usage"| COLLECTOR
    CURSOR_COLLECTOR -->|"Raw JSON Data<br/>User Activity<br/>Interaction Data"| COLLECTOR

    SCHEDULER -->|"Trigger Collection<br/>Configurable Interval<br/>Default: 30min"| COLLECTOR

    %% Data Processing Flow
    COLLECTOR -->|"Raw Metrics Data<br/>Provider-Specific Format<br/>With Timestamps"| TRANSFORM
    
    TRANSFORM -->|"Normalized JSON<br/>Unified Schema<br/>Field Mapping"| VALIDATE
    
    VALIDATE -->|"Validated Data<br/>Schema Compliant<br/>Error Handling"| ENRICH
    
    ENRICH -->|"Enriched Data<br/>Added Metadata<br/>Calculated Fields"| AGGREGATE

    %% Data Storage Flow
    AGGREGATE -->|"Processed Metrics<br/>Aggregated Statistics<br/>Ready for Storage"| POSTGRES
    
    POSTGRES -->|"Indexed Data<br/>B-Tree Indexes<br/>Query Optimization"| INDEXES
    
    POSTGRES -.->|"Cached Results<br/>Frequently Accessed<br/>TTL: Configurable"| CACHE

    %% API Request Flow
    REACT -->|"HTTP Request<br/>JWT Token<br/>REST API Call"| FASTAPI
    
    FASTAPI -->|"Route Processing<br/>Authentication Check<br/>Authorization"| MIDDLEWARE
    
    MIDDLEWARE -->|"CORS Validation<br/>Security Headers<br/>Rate Limiting"| METRICS_ROUTER

    %% Data Retrieval Flow
    METRICS_ROUTER -->|"SQL Query<br/>Parameterized<br/>With Filters"| POSTGRES
    
    POSTGRES -->|"Query Results<br/>JSON Format<br/>Paginated"| METRICS_ROUTER
    
    METRICS_ROUTER -->|"API Response<br/>JSON Payload<br/>Success/Error"| REACT

    %% Frontend Processing Flow
    REACT -->|"State Management<br/>React Hooks<br/>Context API"| DASHBOARD
    
    DASHBOARD -->|"Component Props<br/>Filtered Data<br/>User Selections"| CHARTS
    
    DASHBOARD -->|"Tabular Data<br/>Sort Parameters<br/>Pagination"| TABLES

    %% Visualization Flow
    CHARTS -->|"Chart Configuration<br/>Line/Bar Types<br/>Color Schemes"| CHART_VIZ
    
    TABLES -->|"Table Configuration<br/>Column Definitions<br/>Sorting Logic"| TABLE_VIZ
    
    DASHBOARD -->|"KPI Calculations<br/>Aggregated Values<br/>Real-time Updates"| STATS

    %% Authentication Flow
    AUTH_ROUTER -->|"Login Request<br/>Credentials<br/>POST /auth/login"| POSTGRES
    
    POSTGRES -->|"User Validation<br/>Password Check<br/>Role Verification"| AUTH_ROUTER
    
    AUTH_ROUTER -->|"JWT Token<br/>Access Token<br/>Refresh Token"| REACT
    
    REACT -->|"Token Storage<br/>localStorage<br/>Auth Context"| AUTH

    %% Health Check Flow
    HEALTH_ROUTER -->|"Health Request<br/>GET /health<br/>System Status"| POSTGRES
    
    POSTGRES -->|"Connection Test<br/>Table Counts<br/>Performance Metrics"| HEALTH_ROUTER

    style OAPI fill:#e1f5fe
    style COAPI fill:#e1f5fe
    style CLAPI fill:#e1f5fe
    style CUAPI fill:#e1f5fe
    style COLLECTOR fill:#fff3e0
    style POSTGRES fill:#f3e5f5
    style FASTAPI fill:#e8f5e9
    style REACT fill:#e3f2fd
    style CHART_VIZ fill:#fce4ec
    style TABLE_VIZ fill:#fce4ec
    style STATS fill:#fce4ec
```

## Detailed Data Flow Stages

### 1. Data Sources and Entry Points

**External APIs:**
- **OpenAI API**: Provides GPT model usage metrics, token consumption, and cost data
- **GitHub Copilot API**: Delivers code suggestion metrics, acceptance rates, and user activity
- **Claude API**: Supplies response metrics, model performance, and usage statistics
- **Cursor API**: Offers editor interaction data, user engagement, and feature usage metrics

**Data Formats:**
- All external APIs return JSON-formatted data
- Timestamps follow ISO 8601 standard
- Rate limiting enforced by API providers
- Authentication via API keys or OAuth tokens

### 2. Data Processing Stages with Transformations

**Collection Phase:**
```
External API → Collector Module → Raw JSON Data
```

**Transformation Phase:**
```
Raw Data → Field Mapping → Schema Normalization → Unified Format
```

**Validation Phase:**
```
Transformed Data → Schema Validation → Type Checking → Error Handling
```

**Enrichment Phase:**
```
Validated Data → Metadata Addition → Calculated Fields → Timestamps
```

**Aggregation Phase:**
```
Enriched Data → Statistical Calculations → Summary Metrics → Ready for Storage
```

### 3. Storage Locations and Data Persistence

**Primary Storage:**
- **PostgreSQL Database** with separate tables for each AI service
- **Indexed columns** for optimal query performance (timestamp, application_id)
- **JSONB fields** for flexible metadata storage
- **Unified view** for cross-platform reporting

**Caching Layer:**
- **In-memory caching** for frequently accessed data
- **Configurable TTL** for cache expiration
- **Cache invalidation** on data updates

### 4. Data Outputs and Destinations

**API Responses:**
- **JSON format** with consistent response structure
- **Paginated results** for large datasets
- **Filtering and sorting** capabilities
- **Error handling** with descriptive messages

**Frontend Visualizations:**
- **Interactive charts** using Recharts library
- **Sortable tables** with Material-UI components
- **Real-time updates** via React state management
- **Responsive design** for multiple screen sizes

### 5. Key Decision Points and Conditional Flows

**Collection Decision Tree:**
```
Schedule Trigger → Check API Availability → Validate Credentials → Collect Data → Handle Errors → Retry Logic
```

**Authentication Flow:**
```
User Login → Credential Validation → Role Check → Generate JWT → Store Token → Authorize Requests
```

**Data Validation Flow:**
```
Incoming Data → Schema Check → Type Validation → Range Check → Error Logging → Reject/Accept
```

**Error Handling Flow:**
```
API Error → Log Error → Return Error Response → Display User-Friendly Message → Suggest Resolution
```

## Critical Paths and Potential Bottlenecks

### Critical Paths:
1. **Real-time Data Collection**: External API calls must complete within scheduled intervals
2. **Database Queries**: Optimized indexes ensure fast data retrieval
3. **Authentication**: JWT validation must be performant for every API request
4. **Frontend Rendering**: Chart and table components must handle large datasets efficiently

### Potential Bottlenecks:
1. **External API Rate Limits**: May delay data collection if limits are exceeded
2. **Database Connection Pool**: Could become saturated under high load
3. **Large Dataset Processing**: Unfiltered queries returning thousands of records
4. **Memory Usage**: Frontend caching of large datasets in browser memory

## Data Formats and Protocols

### API Communication:
- **Protocol**: HTTPS (TLS 1.3)
- **Format**: JSON (application/json)
- **Authentication**: JWT Bearer tokens
- **CORS**: Configured for cross-origin requests

### Database Communication:
- **Protocol**: PostgreSQL wire protocol
- **Connection Pooling**: Managed by connection pooler
- **Query Format**: Parameterized SQL queries
- **Transaction Management**: ACID compliance

### External API Integration:
- **Rate Limiting**: Respects provider limits
- **Retry Logic**: Exponential backoff on failures
- **Timeout Configuration**: 30-second default timeout
- **Error Handling**: Graceful degradation on failures

## Performance Optimization Strategies

1. **Database Indexing**: Strategic indexes on frequently queried columns
2. **Query Optimization**: Efficient SQL queries with proper JOINs and filters
3. **Caching Strategy**: Multi-level caching (database, API, frontend)
4. **Pagination**: Limited result sets for large queries
5. **Async Processing**: Non-blocking data collection and processing
6. **Connection Pooling**: Efficient database connection management

This comprehensive data flow diagram ensures clear understanding of how data moves through the AI Organization Dashboard system, enabling effective monitoring, optimization, and troubleshooting of the entire data pipeline.