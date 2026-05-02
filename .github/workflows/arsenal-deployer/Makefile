.PHONY: help build run test deploy clean

# Default target
help:
	@echo "Arsenal Deployer - Available Commands"
	@echo "======================================"
	@echo "make build      - Build Docker image"
	@echo "make run        - Run locally with Docker Compose"
	@echo "make test       - Run tests"
	@echo "make deploy     - Deploy to Azure (requires Azure CLI)"
	@echo "make clean      - Clean up containers and images"
	@echo "make push       - Push image to Docker Hub/ACR"
	@echo "make logs       - View application logs"
	@echo "make shell      - Open shell in container"

build:
	docker build -t arsenaldeployer/arsenal:latest .

run:
	docker-compose up --build

run-detached:
	docker-compose up -d --build

test:
	pytest tests/ -v

deploy:
	chmod +x deploy.sh
	./deploy.sh

clean:
	docker-compose down -v
	docker rmi arsenaldeployer/arsenal:latest || true
	@echo "Cleanup complete"

push:
	docker push arsenaldeployer/arsenal:latest

logs:
	docker-compose logs -f arsenal

shell:
	docker-compose exec arsenal /bin/bash

# Azure specific targets
azure-login:
	az login

azure-deploy-aci:
	az container create \
		--resource-group arsenal-platform-rg \
		--name arsenal-deployer \
		--image arsenaldeployer/arsenal:latest \
		--dns-name-label arsenal-deployer \
		--ports 8080 \
		--cpu 2 \
		--memory 4

azure-destroy:
	az group delete --name arsenal-platform-rg --yes --no-wait
