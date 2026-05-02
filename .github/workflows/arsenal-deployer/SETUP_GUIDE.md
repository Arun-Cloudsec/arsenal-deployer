# 🚀 Arsenal Deployer — Complete Setup Guide

## Step-by-Step: From Zero to Live in 10 Minutes

---

## 📁 Step 1: Prepare Your Repository

### Option A: Use the Downloaded Files

1. **Create a new GitHub repository** (e.g., `your-username/arsenal-deployer`)
2. **Download all files** from the provided output folder
3. **Upload to your repo**:

```bash
# Clone your new empty repo
git clone https://github.com/YOUR_USERNAME/arsenal-deployer.git
cd arsenal-deployer

# Copy all downloaded files here
cp -r /path/to/downloaded/arsenal-deployer/* .

# Push to GitHub
git add .
git commit -m "🚀 Initial Arsenal Deployer setup"
git push origin main
```

### Option B: Fork & Customize (Recommended)

1. Fork this template repository
2. Clone your fork:
```bash
git clone https://github.com/YOUR_USERNAME/arsenal-deployer.git
cd arsenal-deployer
```

---

## 🔐 Step 2: Azure Setup (5 minutes)

### 2.1 Install Azure CLI

```bash
# macOS
brew install azure-cli

# Windows
winget install Microsoft.AzureCLI

# Linux
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
```

### 2.2 Login to Azure

```bash
az login
# This opens a browser for authentication
```

### 2.3 Get Your Subscription Info

```bash
# Get subscription ID
az account show --query id -o tsv
# Save this value!

# Get tenant ID
az account show --query tenantId -o tsv
# Save this value too!
```

### 2.4 Create Service Principal (for GitHub Actions)

```bash
# Replace YOUR_SUBSCRIPTION_ID with your actual ID
az ad sp create-for-rbac \
  --name "arsenal-deployer-sp" \
  --role Contributor \
  --scopes /subscriptions/YOUR_SUBSCRIPTION_ID \
  --sdk-auth
```

**Save the ENTIRE JSON output** — this becomes your `AZURE_CREDENTIALS` secret.

Example output:
```json
{
  "clientId": "12345678-1234-1234-1234-123456789012",
  "clientSecret": "abc123...",
  "subscriptionId": "your-sub-id",
  "tenantId": "your-tenant-id",
  ...
}
```

### 2.5 Create Azure Container Registry (ACR)

```bash
# Create resource group
az group create \
  --name arsenal-platform-rg \
  --location eastus \
  --tags project=arsenal

# Create ACR (must be globally unique, 5-50 chars, alphanumeric)
az acr create \
  --name arsenaldeployer \
  --resource-group arsenal-platform-rg \
  --sku Standard \
  --location eastus \
  --admin-enabled true

# Get ACR credentials
az acr credential show \
  --name arsenaldeployer \
  --query "{username:username, password:passwords[0].value}"
```

Save the **username** and **password**.

---

## 🔑 Step 3: Configure GitHub Secrets

Go to your GitHub repo → **Settings → Secrets and variables → Actions → New repository secret**

Add these 5 secrets:

| Secret Name | Value | Where You Got It |
|-------------|-------|-------------------|
| `AZURE_CREDENTIALS` | Full JSON from Step 2.4 | Service Principal creation |
| `AZURE_SUBSCRIPTION_ID` | Your Azure subscription ID | `az account show --query id` |
| `AZURE_TENANT_ID` | Your Azure tenant ID | `az account show --query tenantId` |
| `ACR_USERNAME` | ACR admin username | Step 2.5 output |
| `ACR_PASSWORD` | ACR admin password | Step 2.5 output |

---

## 🚀 Step 4: Trigger Deployment

### Method 1: Push to Main (Automatic)

```bash
# Make any small change
echo "# Arsenal Deployer" >> README.md
git add .
git commit -m "🚀 Trigger deployment"
git push origin main
```

Go to **Actions** tab in GitHub — you'll see the workflow running!

### Method 2: Manual Trigger

1. Go to **Actions** tab
2. Select **"🚀 Arsenal Deployer - Build & Deploy to Azure"**
3. Click **"Run workflow"**
4. Select environment (development/staging/production)
5. Click **"Run workflow"**

---

## ✅ Step 5: Verify Deployment

### Check Workflow Status

1. Go to **Actions** tab in GitHub
2. Click on the latest workflow run
3. Wait for all jobs to complete (green checkmarks)

### Get Your App URL

```bash
# Get the public URL
az container show \
  --resource-group arsenal-platform-rg \
  --name arsenal-deployer \
  --query ipAddress.fqdn \
  -o tsv
```

Your app will be at: `http://<fqdn>:8080`

### Test the Deployment

1. Open the URL in browser
2. You should see the Arsenal Deployer UI
3. Select a category → Choose a topic → Configure → Deploy!

---

## 🔄 Step 6: Continuous Deployment (Optional)

The workflow is already configured for auto-deploy on every push to `main`.

To trigger a new deployment:

```bash
# Make any code change
git add .
git commit -m "Update: new feature"
git push origin main
# → GitHub Actions auto-deploys!
```

---

## 🛠️ Troubleshooting

### Issue: "Azure credentials not found"
**Fix**: Double-check `AZURE_CREDENTIALS` secret is complete JSON (not just clientId)

### Issue: "ACR access denied"
**Fix**: Verify ACR admin is enabled: `az acr update -n arsenaldeployer --admin-enabled true`

### Issue: "Container stays in Creating state"
**Fix**: Check Azure Container Instance quotas in your region

### Issue: "Health check fails"
**Fix**: Container may need more time. Check logs:
```bash
az container logs \
  --resource-group arsenal-platform-rg \
  --name arsenal-deployer
```

---

## 📂 Repository Structure Explained

```
arsenal-deployer/
│
├── 📄 app.py                          ← Main Flask app (8 categories, 32+ topics)
├── 📁 templates/
│   └── index.html                     ← Web UI (dark theme, responsive)
│
├── 🐳 Dockerfile                      ← Container definition
├── 📦 requirements.txt                ← Python dependencies
├── 🚀 deploy.sh                       ← One-click Azure deploy script
├── 🐳 docker-compose.yml            ← Local development setup
├── 📝 Makefile                        ← Common commands
│
├── 📁 .github/workflows/
│   └── deploy.yml                     ← GitHub Actions CI/CD pipeline
│
├── 📁 arm-templates/
│   └── ai-ml-platform.json            ← Sample ARM template
│
├── 📁 terraform-modules/
│   ├── main.tf                        ← Terraform infrastructure
│   └── terraform.tfvars.example       ← Terraform variables template
│
├── 📖 README.md                       ← Full documentation
├── 📄 LICENSE                         ← MIT License
├── 🚫 .gitignore                      ← Git ignore rules
└── 🚫 .dockerignore                   ← Docker ignore rules
```

---

## 🎯 What Happens When You Push?

```
Git Push to main
    │
    ▼
┌─────────────────┐
│ GitHub Actions  │
│  Triggered      │
└────────┬────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌──────┐  ┌────────┐
│Build │  │  Test  │
│Image │  │  Code  │
└──┬───┘  └───┬────┘
   │          │
   └────┬─────┘
        ▼
   ┌────────┐
   │ Push   │
   │ to ACR │
   └───┬────┘
       │
       ▼
  ┌─────────┐
  │ Deploy  │
  │ to ACI  │
  └───┬─────┘
      │
      ▼
  ┌─────────┐
  │ Health  │
  │ Check   │
  └───┬─────┘
      │
      ▼
   🎉 LIVE!
```

---

## 🌟 Next Steps

1. **Customize categories** in `app.py` → `ARSENAL_CATEGORIES`
2. **Add ARM templates** in `arm-templates/` folder
3. **Add Terraform modules** in `terraform-modules/`
4. **Configure monitoring** with Azure Monitor
5. **Set up custom domain** with Azure DNS

---

## 💬 Support

- Open an issue in the GitHub repo
- Check Azure Container Instance logs: `az container logs --resource-group arsenal-platform-rg --name arsenal-deployer`
- Review GitHub Actions logs in the Actions tab

---

<div align="center">

**🚀 You're now ready to deploy anything to Azure in under 60 seconds!**

</div>
