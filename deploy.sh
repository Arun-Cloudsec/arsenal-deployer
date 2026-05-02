#!/bin/bash
# =============================================================================
# ARSENAL DEPLOYER - One-Click Azure Deployment
# =============================================================================
set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "    ___    ____  ____  _________  ____________    __    __"
echo "   /   |  / __ \/ __ \/ ____/   |/_  __/  _/ /   / /   / /"
echo "  / /| | / /_/ / / / / __/ / /| | / /  / // /   / /   / / "
echo " / ___ |/ _, _/ /_/ / /___/ ___ |/ / _/ // /___/ /___/ /___"
echo "/_/  |_/_/ |_/_____/_____/_/  |_/_/ /___/_____/_____/_____/"
echo -e "${NC}"
echo -e "${GREEN}Multi-Category Azure Deployment Platform${NC}"
echo ""

# Check prerequisites
echo -e "${BLUE}🔍 Checking prerequisites...${NC}"

if ! command -v az &> /dev/null; then
    echo -e "${YELLOW}Azure CLI not found. Installing...${NC}"
    curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
fi

if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is required but not installed.${NC}"
    echo "Please install Docker first: https://docs.docker.com/get-docker/"
    exit 1
fi

# Azure login
echo -e "${BLUE}🔐 Checking Azure authentication...${NC}"
if ! az account show &> /dev/null; then
    echo -e "${YELLOW}Please login to Azure...${NC}"
    az login --use-device-code
fi

SUBSCRIPTION_ID=$(az account show --query id -o tsv)
TENANT_ID=$(az account show --query tenantId -o tsv)
echo -e "${GREEN}✅ Authenticated to Azure subscription: ${SUBSCRIPTION_ID}${NC}"

# Configuration
RG_NAME="arsenal-platform-rg"
LOCATION="eastus"
CONTAINER_NAME="arsenal-deployer"
DNS_LABEL="arsenal-$(date +%s)"

echo ""
echo -e "${BLUE}📦 Setting up Arsenal Platform...${NC}"

# Create resource group
echo "Creating resource group..."
az group create     --name $RG_NAME     --location $LOCATION     --tags "project=arsenal" "environment=platform"     --output none

# Deploy container instance
echo "Deploying Arsenal container..."
az container create     --resource-group $RG_NAME     --name $CONTAINER_NAME     --image arsenaldeployer/arsenal:latest     --dns-name-label $DNS_LABEL     --ports 8080     --environment-variables         AZURE_SUBSCRIPTION_ID=$SUBSCRIPTION_ID         AZURE_TENANT_ID=$TENANT_ID         ARSENAL_ENV=production     --cpu 2     --memory 4     --os-type Linux     --restart-policy Always     --output none

# Get public URL
FQDN=$(az container show     --resource-group $RG_NAME     --name $CONTAINER_NAME     --query ipAddress.fqdn     --output tsv)

URL="http://${FQDN}:8080"

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║           🚀 ARSENAL PLATFORM IS LIVE!                     ║${NC}"
echo -e "${GREEN}╠════════════════════════════════════════════════════════════╣${NC}"
echo -e "${GREEN}║  URL:    ${URL}${NC}"
echo -e "${GREEN}║  RG:     ${RG_NAME}${NC}"
echo -e "${GREEN}║  Region: ${LOCATION}${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}📋 Available Categories:${NC}"
echo "   💻 Technology    📊 Management    👥 HR"
echo "   💰 Finance       ⚖️ Legal         🎯 Strategy"
echo "   🔧 Engineering   ⚙️ Operations"
echo ""
echo -e "${BLUE}✨ Features:${NC}"
echo "   • 32+ pre-built deployment topics"
echo "   • Custom topic creation"
echo "   • Additional requirements input (JSON/Terraform)"
echo "   • Deploy to Azure in < 60 seconds"
echo "   • One-click destroy"
echo ""
echo -e "${YELLOW}💡 Tip: Bookmark this URL for quick access${NC}"
echo ""
