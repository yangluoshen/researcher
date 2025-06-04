.PHONY: help dev-frontend dev-backend dev run build

help:
	@echo "Available commands:"
	@echo "  make dev-frontend    - Starts the frontend development server (Vite)"
	@echo "  make dev-backend     - Starts the backend development server (LangGraph)"
	@echo "  make dev             - Starts both frontend and backend development servers"
	@echo "  make build           - Builds the Docker image"
	@echo "  make run             - Builds and runs the application with docker-compose"
	@echo ""
	@echo "Prerequisites:"
	@echo "  - Set DEEPSEEK_API_KEY in .env file"
	@echo "  - Optional: Set SEARXNG_URL for custom search instance"
	@echo "  - Optional: Set SEARCH_ENGINES for custom search engine selection"

dev-frontend:
	@echo "Starting frontend development server..."
	@cd frontend && npm run dev

dev-backend:
	@echo "Starting backend development server..."
	@cd backend && langgraph dev

# Run frontend and backend concurrently
dev:
	@echo "Starting both frontend and backend development servers..."
	@make dev-frontend & make dev-backend

build:
	@echo "Building Docker image..."
	@docker build -t deepseek-fullstack-langgraph -f Dockerfile .

run: build
	@echo "Starting application with docker-compose..."
	@if [ ! -f .env ]; then \
		echo "Warning: .env file not found. Please create one with DEEPSEEK_API_KEY"; \
		echo "Example: echo 'DEEPSEEK_API_KEY=your_key_here' > .env"; \
	fi
	@docker-compose up 