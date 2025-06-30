.PHONY: help install build up down logs test prefect clean

help:  ## Show this help
	@echo "🚀 SaaS Analytics API with Prefect Orchestration"
	@echo "Available commands:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install:  ## Install Python dependencies
	@echo "📦 Installing dependencies..."
	pip install -r requirements.txt

build:  ## Build Docker images
	@echo "🔧 Building Docker images..."
	docker compose build

up:  ## Start all services (API + DB + Redis)
	@echo "🚀 Starting all services..."
	docker compose up -d
	@echo "✅ Services started!"
	@echo "📊 API: http://localhost:8000"
	@echo "📋 Swagger: http://localhost:8000/docs"

down:  ## Stop all services
	@echo "🛑 Stopping all services..."
	docker compose down

logs:  ## Show logs from all services
	docker compose logs -f

test:  ## Run tests
	@echo "🧪 Running tests..."
	pytest tests/ -v

prefect-install:  ## Install Prefect dependencies
	@echo "📦 Installing Prefect..."
	pip install prefect==2.14.0 prefect-sqlalchemy==0.4.1

prefect-server:  ## Start Prefect server
	@echo "🔄 Starting Prefect server..."
	prefect server start --host 0.0.0.0 &
	@echo "📊 Prefect UI: http://localhost:4200"

prefect-setup:  ## Setup Prefect workflows and deployments
	@echo "⚙️ Setting up Prefect workflows..."
	python scripts/setup_prefect.py

prefect-worker:  ## Start Prefect worker
	@echo "👷 Starting Prefect worker..."
	prefect worker start --pool analytics-pool

prefect-full:  ## Complete Prefect setup (install + server + setup + worker)
	@echo "🚀 Complete Prefect setup..."
	make prefect-install
	sleep 2
	make prefect-server
	sleep 5
	make prefect-setup
	@echo "💡 Now run 'make prefect-worker' in a separate terminal"

dev:  ## Start development environment with Prefect
	@echo "🔧 Starting development environment..."
	make up
	sleep 10
	make prefect-full
	@echo "✅ Development environment ready!"
	@echo ""
	@echo "🔗 Quick Links:"
	@echo "  📊 API Swagger: http://localhost:8000/docs"
	@echo "  🔄 Prefect UI: http://localhost:4200"
	@echo "  📈 Analytics: http://localhost:8000/analytics/summary"
	@echo "  🔧 Prefect Flows: http://localhost:8000/prefect/flows/status"

clean:  ## Clean up containers and volumes
	@echo "🧹 Cleaning up..."
	docker compose down -v
	docker system prune -f

demo:  ## Run demo scenarios
	@echo "🎬 Running demo scenarios..."
	@echo "1. Generating fake data..."
	curl -X POST "http://localhost:8000/sales-data/generate-fake?count=100"
	@echo ""
	@echo "2. Running Prefect ETL pipeline..."
	curl -X POST "http://localhost:8000/prefect/flows/daily-etl/run" \
		-H "Authorization: Bearer YOUR_TOKEN"
	@echo ""
	@echo "3. Checking cached analytics..."
	curl "http://localhost:8000/prefect/analytics/cached"

status:  ## Check status of all services
	@echo "📊 Service Status:"
	@echo "Docker containers:"
	docker compose ps
	@echo ""
	@echo "Prefect server status:"
	curl -s http://localhost:4200/api/health || echo "❌ Prefect server not running"
	@echo ""
	@echo "API health:"
	curl -s http://localhost:8000/health/ || echo "❌ API not running"

# Development shortcuts
db-shell:  ## Connect to PostgreSQL shell
	docker compose exec db psql -U admin -d saas_db

redis-cli:  ## Connect to Redis CLI
	docker compose exec redis redis-cli

api-logs:  ## Show API logs only
	docker compose logs -f app

requirements:  ## Generate requirements.txt from current environment
	pip freeze > requirements.txt

backup-db:  ## Backup database
	docker compose exec db pg_dump -U admin saas_db > backup_$(shell date +%Y%m%d_%H%M%S).sql

restore-db:  ## Restore database from backup (usage: make restore-db BACKUP=backup_file.sql)
	cat $(BACKUP) | docker compose exec -T db psql -U admin -d saas_db