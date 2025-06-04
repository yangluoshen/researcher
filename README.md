# DeepSeek Fullstack LangGraph Quickstart

This is a quickstart for building a fullstack conversational AI using LangGraph and DeepSeek models with real web search capabilities.

![DeepSeek Fullstack LangGraph](./app.png)

## Features

- 🎯 Multi-agent research workflow using LangGraph.
- 🔍 Dynamic search query generation using DeepSeek models.
- 🌐 **Real web research** with SearXNG integration and multiple fallback search engines.
- 🧠 Smart reflection to identify knowledge gaps.
- 📚 Source tracking and citation generation with real URLs.
- 🚀 Production-ready with Docker deployment.
- 💻 Beautiful React frontend with real-time streaming.
- 🔧 Configurable effort levels and model selection.

## Prerequisites

Before getting started, make sure you have the following:

1.  **Docker and Docker Compose**: For containerized deployment.
2.  **Node.js and npm**: For frontend development (if running outside Docker).
3.  **Python 3.11+**: For backend development (if running outside Docker).

## Environment Variables

The application requires the following environment variables:

-   **`DEEPSEEK_API_KEY`**: The backend agent requires a DeepSeek API key. [Get one here](https://platform.deepseek.com/api_keys)
-   **`LANGSMITH_API_KEY`** (optional): For LangSmith tracing and monitoring.

### Optional Search Configuration

-   **`SEARXNG_URL`** (optional): URL of your own SearXNG instance (e.g., `https://your-searxng.example.com`)
-   **`SEARCH_ENGINES`** (optional): Comma-separated list of search engines to use (default: `"google,bing,duckduckgo"`)

## Search Engine Integration

This application uses **real web search** powered by:

1. **SearXNG**: Privacy-respecting metasearch engine
   - Uses multiple public SearXNG instances as fallback
   - You can configure your own SearXNG instance with `SEARXNG_URL`
   - Aggregates results from Google, Bing, DuckDuckGo, and more

2. **DuckDuckGo API**: Fallback for instant answers
3. **Emergency Fallback**: Graceful degradation when all search engines are unavailable

## Quick Start with Docker

1.  Clone this repository: `git clone <repository-url>`
2.  Navigate to the project directory: `cd deepseek-fullstack-langgraph-quickstart`
3.  Create a `.env` file and add your DeepSeek API key:
    ```bash
    DEEPSEEK_API_KEY="YOUR_ACTUAL_API_KEY"
    # Optional: Configure search
    SEARXNG_URL="https://your-searxng.example.com"
    SEARCH_ENGINES="google,bing,duckduckgo"
    ```
4.  Build and run with Docker Compose: `make run`

The application will be available at:

-   **Frontend**: <http://localhost:3000>
-   **Backend API**: <http://localhost:8123>

## How It Works

The application implements a sophisticated multi-agent research workflow with **real web search**:

1.  **Generate Initial Queries:** Based on your input, it generates a set of initial search queries using a DeepSeek model.
2.  **Web Research:** For each query, it performs **real web searches** using SearXNG/search engines and then uses DeepSeek to analyze and synthesize the results.
3.  **Reflection:** After gathering initial information, the system reflects on whether there are knowledge gaps using a DeepSeek model.
4.  **Additional Research:** If gaps are identified, it generates follow-up queries and conducts additional web research.
5.  **Final Synthesis:** Finally, it synthesizes all the information into a comprehensive answer with **real citations** from web sources, using a DeepSeek model.

This workflow continues iteratively until the system determines it has sufficient information or reaches the maximum number of research loops.

## Manual Setup (Development)

If you prefer to run the application manually for development:

### Backend Setup

```bash
cd backend
pip install -e .
# or with uv:
# uv pip install -e .
```

### Environment Setup

Create a `.env` file in the backend directory:

```bash
DEEPSEEK_API_KEY="your_deepseek_api_key_here"
LANGSMITH_API_KEY="your_langsmith_api_key_here"  # Optional
SEARXNG_URL="https://your-searxng.example.com"   # Optional
SEARCH_ENGINES="google,bing,duckduckgo"          # Optional
```

### Running Development Servers

```bash
# Backend
cd backend && langgraph dev

# Frontend (in another terminal)
cd frontend && npm install && npm run dev
```

### Production Deployment

```bash
# Build the Docker image
docker build -t deepseek-fullstack-langgraph -f Dockerfile .

# Run with docker-compose
DEEPSEEK_API_KEY=<your_deepseek_api_key> LANGSMITH_API_KEY=<your_langsmith_api_key> docker-compose up
```

## Setting Up Your Own SearXNG Instance (Optional)

For better privacy and reliability, you can run your own SearXNG instance:

```bash
# Using Docker
docker run -d -p 8080:8080 \
  --name searxng \
  -v "${PWD}/searxng:/etc/searxng" \
  -e "BASE_URL=http://localhost:8080/" \
  searxng/searxng:latest

# Then set in your .env:
# SEARXNG_URL=http://localhost:8080
```

## Model Options

- **`deepseek-chat`**: Fast, general-purpose chat model (recommended for most tasks)
- **`deepseek-reasoner`**: Advanced reasoning model (better for complex analysis and final synthesis)

## Technologies Used

- [DeepSeek](https://api-docs.deepseek.com/) - LLM for query generation, reflection, and answer synthesis.
- [SearXNG](https://docs.searxng.org/) - Privacy-respecting metasearch engine for web research.
- [LangGraph](https://langchain-ai.github.io/langgraph/) - Multi-agent orchestration framework.
- [LangChain](https://python.langchain.com/) - LLM application framework.
- [React](https://react.dev/) - Frontend framework.
- [FastAPI](https://fastapi.tiangolo.com/) - Backend API framework.
- [Docker](https://www.docker.com/) - Containerization platform.

## License

This project is licensed under the Apache License 2.0. See the [LICENSE](LICENSE) file for details. 