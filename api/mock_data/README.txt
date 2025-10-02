Mock datasets for AI Metrics Dashboard

Files:
- openai_metrics_mock.json -> /metrics/openai
- claude_metrics_mock.json -> /metrics/claude
- copilot_metrics_mock.json -> /metrics/copilot
- cursor_metrics_mock.json -> /metrics/cursor
- dashboard_stats_mock.json -> /metrics/stats

Each metrics file provides: ApiResponse<MetricData[]> with required fields:
- id, applicationId, timestamp (ISO), responseTime (ms), requestCount, errorRate (%), successRate (%), averageTokens, cost (USD), uptime (%)
Optional fields per app:
- chatgpt/claude: model, promptTokens, completionTokens, totalTokens
- copilot: totalSuggestions, acceptedSuggestions, totalUsers, linesSuggested, linesAccepted
- cursor: totalSeats, activeUsers, monthlyActiveUsers, weeklyActiveUsers, dailyActiveUsers, tokenBreakdown, eventBreakdown, modelBreakdown

Dashboard stats file provides: ApiResponse<DashboardStats> with keys:
- totalRequests, averageResponseTime, overallSuccessRate, totalCost, activeApplications
Plus backend-style details object with per-app breakdowns.