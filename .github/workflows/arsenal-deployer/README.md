# 🚀 Arsenal Deployer

> **Multi-Category Azure Deployment Platform** — Choose your stack, customize inputs, deploy to Azure in under 60 seconds.

[![Build & Deploy](https://github.com/YOUR_USERNAME/arsenal-deployer/actions/workflows/deploy.yml/badge.svg)](https://github.com/YOUR_USERNAME/arsenal-deployer/actions/workflows/deploy.yml)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://hub.docker.com/r/arsenaldeployer/arsenal)
[![Azure](https://img.shields.io/badge/azure-container--instance-blue.svg)](https://azure.microsoft.com)

---

## 📋 Table of Contents

- [Features](#-features)
- [Quick Start](#-quick-start)
- [Categories & Topics](#-categories--topics)
- [GitHub Actions Setup](#-github-actions-setup)
- [Architecture](#-architecture)
- [API Reference](#-api-reference)
- [Contributing](#-contributing)

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| **8 Categories** | Technology, Management, HR, Finance, Legal, Strategy, Engineering, Operations |
| **32+ Topics** | Pre-built deployment stacks with optimized Azure configurations |
| **Custom Topics** | Add your own deployment topics dynamically via UI |
| **Dynamic Inputs** | Per-topic configuration (checkboxes, selects, numbers, multi-select) |
| **Additional Requirements** | Free-form JSON/Terraform input for advanced customization |
| **Live Timer** | Real-time deployment progress with step-by-step status |
| **One-Click Destroy** | Clean up resources instantly |
| **Cost Estimates** | Displayed before deployment |
| **< 60s Deploy** | Most stacks deploy in 30-60 seconds |

---

## 🚀 Quick Start

### Option 1: One-Line Install (Recommended)

```bash
curl -sL https://raw.githubusercontent.com/YOUR_USERNAME/arsenal-deployer/main/deploy.sh | bash
```

### Option 2: GitHub Actions Auto-Deploy

1. **Fork this repository**
2. **Add GitHub Secrets** (see [setup below](#-github-actions-setup))
3. **Push to `main` branch** → Auto-deploys to Azure

### Option 3: Manual Docker Build

```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/arsenal-deployer.git
cd arsenal-deployer

# Build and push Docker image
docker build -t arsenaldeployer/arsenal:latest .
docker push arsenaldeployer/arsenal:latest

# Run deploy script
chmod +x deploy.sh
./deploy.sh
```

### Option 4: Azure Container Apps

```bash
az containerapp create   --name arsenal-deployer   --resource-group arsenal-rg   --environment arsenal-env   --image arsenaldeployer/arsenal:latest   --target-port 8080   --ingress external   --cpu 2   --memory 4Gi
```

---

## 📂 Categories & Topics

### 💻 Technology
| Topic | Description | Cost | Time |
|-------|-------------|------|------|
| AI/ML Platform | GPU clusters, JupyterHub, MLflow, Vector DBs | $800-2500/mo | 45-60s |
| Kubernetes Cluster | AKS with ingress, monitoring, cert-manager | $300-1200/mo | 50-60s |
| Serverless Architecture | Functions, Logic Apps, Event Grid, Cosmos DB | $50-400/mo | 30-45s |
| Data Platform | Synapse, Databricks, Data Factory, ADLS | $1000-5000/mo | 55-60s |
| CI/CD Pipeline | DevOps, GitHub Actions runners, artifact repos | $200-800/mo | 40-50s |
| Observability Stack | Monitoring, logging, tracing, alerting | $150-600/mo | 35-45s |

### 📊 Management
| Topic | Description | Cost | Time |
|-------|-------------|------|------|
| PMO Dashboard | Project Online, Power BI, Planner integration | $100-500/mo | 25-35s |
| Portfolio Analytics | Investment tracking, ROI analysis, risk scoring | $300-1000/mo | 40-50s |
| Resource Management | Capacity planning, skill mapping, allocation | $200-800/mo | 45-55s |
| Change Management | ITIL processes, CAB workflow, risk assessment | $150-600/mo | 30-40s |

### 👥 HR
| Topic | Description | Cost | Time |
|-------|-------------|------|------|
| Talent Acquisition Suite | ATS, interview scheduling, candidate scoring | $200-800/mo | 35-45s |
| HR Analytics Platform | People analytics, retention prediction, DEI metrics | $400-1500/mo | 45-55s |
| Payroll Automation | Multi-country payroll, compliance, tax engine | $300-1200/mo | 40-50s |
| Employee Engagement | Pulse surveys, sentiment analysis, recognition | $150-600/mo | 30-40s |

### 💰 Finance
| Topic | Description | Cost | Time |
|-------|-------------|------|------|
| FP&A Platform | Budgeting, forecasting, variance analysis | $500-2000/mo | 50-60s |
| Treasury Management | Cash flow, FX risk, hedging, bank integration | $400-1500/mo | 45-55s |
| Audit & Compliance | SOX, GDPR, automated controls, evidence collection | $300-1200/mo | 40-50s |
| Global Tax Engine | Transfer pricing, tax reporting, e-invoicing | $600-2500/mo | 50-60s |

### ⚖️ Legal
| Topic | Description | Cost | Time |
|-------|-------------|------|------|
| Contract Lifecycle Management | Drafting, negotiation, execution, renewal | $400-1500/mo | 35-45s |
| IP Portfolio Management | Patents, trademarks, licensing, renewals | $300-1000/mo | 40-50s |
| Litigation Support | eDiscovery, case management, document review | $500-2000/mo | 45-55s |
| Regulatory Tracking | Regulation monitoring, impact analysis, reporting | $200-800/mo | 30-40s |

### 🎯 Strategy
| Topic | Description | Cost | Time |
|-------|-------------|------|------|
| Market Intelligence Platform | Competitive analysis, trend detection, forecasting | $600-2500/mo | 50-60s |
| M&A Diligence Suite | Target screening, valuation, integration planning | $800-3000/mo | 55-60s |
| Innovation Lab | Ideation, prototyping, portfolio, metrics | $300-1200/mo | 40-50s |
| OKR & Strategy Execution | Goal setting, alignment, tracking, retrospectives | $200-800/mo | 30-40s |

### 🔧 Engineering
| Topic | Description | Cost | Time |
|-------|-------------|------|------|
| Developer Environment | IDE cloud, pair programming, code spaces | $200-1000/mo/dev | 40-50s |
| Test Automation Grid | Selenium, Playwright, mobile, performance | $300-1500/mo | 35-45s |
| Release Management | Feature flags, canary, blue-green, rollback | $250-1000/mo | 40-50s |
| Documentation Platform | Tech docs, API refs, wikis, search | $100-500/mo | 25-35s |

### ⚙️ Operations
| Topic | Description | Cost | Time |
|-------|-------------|------|------|
| Supply Chain Control Tower | End-to-end visibility, demand planning, optimization | $800-3000/mo | 55-60s |
| Manufacturing Execution | MES, OEE, quality gates, traceability | $1000-4000/mo | 55-60s |
| Warehouse Automation | WMS, robotics integration, picking optimization | $600-2500/mo | 50-60s |
| Predictive Maintenance | Condition monitoring, failure prediction, scheduling | $500-2000/mo | 50-60s |

---

## 🔧 GitHub Actions Setup

### 1. Create Azure Service Principal

```bash
# Login to Azure
az login

# Create service principal with Contributor role
az ad sp create-for-rbac   --name "arsenal-deployer-sp"   --role Contributor   --scopes /subscriptions/$(az account show --query id -o tsv)   --sdk-auth
```

Save the JSON output — you'll need it for the `AZURE_CREDENTIALS` secret.

### 2. Create Azure Container Registry (ACR)

```bash
# Create ACR
az acr create   --name arsenaldeployer   --resource-group arsenal-platform-rg   --sku Standard   --location eastus   --admin-enabled true

# Get ACR credentials
az acr credential show --name arsenaldeployer --query "{username:username, password:passwords[0].value}"
```

### 3. Add GitHub Secrets

Go to **Settings → Secrets and variables → Actions** and add:

| Secret | Value | Description |
|--------|-------|-------------|
| `AZURE_CREDENTIALS` | JSON from step 1 | Azure Service Principal |
| `AZURE_SUBSCRIPTION_ID` | Your subscription ID | Azure Subscription |
| `AZURE_TENANT_ID` | Your tenant ID | Azure Tenant |
| `ACR_USERNAME` | ACR admin username | Container Registry Login |
| `ACR_PASSWORD` | ACR admin password | Container Registry Password |

### 4. Push to Main Branch

```bash
git add .
git commit -m "Initial deployment"
git push origin main
```

GitHub Actions will automatically:
1. Build the Docker image
2. Push to ACR
3. Deploy to Azure Container Instance
4. Run health checks

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        GitHub Repo                           │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  app.py  │  │templates │  │Dockerfile│  │deploy.sh │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
│       └──────────────┴──────────────┴──────────────┘         │
│                         │                                   │
│              ┌──────────▼──────────┐                        │
│              │   GitHub Actions    │                        │
│              │  (Build & Deploy)   │                        │
│              └──────────┬──────────┘                        │
└─────────────────────────┼───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│              Azure Container Registry (ACR)                  │
│              arsenaldeployer.azurecr.io/arsenal:latest       │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│              Azure Container Instance (ACI)                  │
│              ┌─────────────────────────────┐                 │
│              │   Arsenal Deployer App      │                 │
│              │   Port: 8080                │                 │
│              │   CPU: 2 | Memory: 4GB      │                 │
│              │                             │                 │
│              │   ┌─────────────────────┐ │                 │
│              │   │  Web UI (index.html)  │ │                 │
│              │   │  - Category Selection │ │                 │
│              │   │  - Topic Cards        │ │                 │
│              │   │  - Config Panel       │ │                 │
│              │   └─────────────────────┘ │                 │
│              │                             │                 │
│              │   ┌─────────────────────┐ │                 │
│              │   │  Flask API (app.py)   │ │                 │
│              │   │  - /api/deploy        │ │                 │
│              │   │  - /api/custom-topic│ │                 │
│              │   │  - /api/status        │ │                 │
│              │   │  - /api/destroy       │ │                 │
│              │   └─────────────────────┘ │                 │
│              │                             │                 │
│              │   ┌─────────────────────┐ │                 │
│              │   │  Azure CLI Engine     │ │                 │
│              │   │  - ARM Template Gen   │ │                 │
│              │   │  - Resource Deploy    │ │                 │
│              │   │  - Status Monitoring  │ │                 │
│              │   └─────────────────────┘ │                 │
│              └─────────────────────────────┘                 │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│              Deployed Azure Resources                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  AKS     │  │  VMs     │  │  Databases│  │  Storage │   │
│  │  ML WS   │  │  Functions│  │  Synapse  │  │  IoT Hub │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## 📡 API Reference

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Web UI |
| `GET` | `/api/categories` | List all categories & topics |
| `POST` | `/api/deploy` | Deploy a stack |
| `POST` | `/api/custom-topic` | Add custom topic |
| `GET` | `/api/status/<deploy_id>` | Check deployment status |
| `POST` | `/api/destroy/<deploy_id>` | Destroy deployment |

### Deploy Request

```json
POST /api/deploy
{
  "category": "technology",
  "topic": "ai_ml_platform",
  "custom_inputs": {
    "projectName": "my-ai-project",
    "adminUsername": "azureuser",
    "adminPassword": "SecurePass123!",
    "environment": "production",
    "gpu_count": 4,
    "enable_openai": true,
    "model_version": "gpt-4"
  },
  "additional_requirements": "{
    "customTags": {"team": "ai-research"},
    "enableBackup": true
  }"
}
```

### Deploy Response

```json
{
  "status": "success",
  "deploy_id": "a1b2c3d4",
  "category": "technology",
  "topic": "ai_ml_platform",
  "resource_group": "arsenal-technology-ai_ml_platform-a1b2c3d4",
  "deployment_name": "arsenal-a1b2c3d4",
  "portal_url": "https://portal.azure.com/#@/resource/...",
  "estimated_cost": "$800-2500/mo",
  "deploy_time": "45-60s",
  "message": "🎉 AI/ML Platform deployed successfully!",
  "outputs": {}
}
```

---

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Adding New Topics

Topics are defined in `app.py` in the `ARSENAL_CATEGORIES` dictionary. To add a new topic:

1. Add to existing category or create new category
2. Define topic metadata (name, description, cost, resources)
3. Specify input schema (types: text, number, select, checkbox, multi_select)
4. Update ARM template generator if needed

---

## 📄 License

MIT License — see [LICENSE](LICENSE) file.

---

## 🙏 Acknowledgments

- Built with [Flask](https://flask.palletsprojects.com/)
- Deployed on [Azure Container Instances](https://azure.microsoft.com/services/container-instances/)
- CI/CD via [GitHub Actions](https://github.com/features/actions)
- Inspired by [Kiwi Claw](https://kiwiclaw.com/) deployment patterns

---

<div align="center">
  <h3>🚀 Deploy Anything. Anytime. Under 60 Seconds.</h3>
  <p>Made with ❤️ for the Azure community</p>
</div>
