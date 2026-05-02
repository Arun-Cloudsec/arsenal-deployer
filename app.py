from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import json
import os
import subprocess
import uuid
import threading
import secrets as _secrets
from functools import wraps

import bcrypt

app = Flask(__name__)

# Session signing key. In production, set SECRET_KEY as an env var so sessions
# survive container restarts. The fallback only protects local dev.
app.secret_key = os.getenv("SECRET_KEY") or _secrets.token_hex(32)

# Auth config — set these as env vars in the workflow.
ARSENAL_USERNAME = os.getenv("ARSENAL_USERNAME", "admin")
ARSENAL_PASSWORD_HASH = os.getenv("ARSENAL_PASSWORD_HASH", "")  # bcrypt hash


def require_auth(f):
    """Gate a route behind a logged-in session.
    HTML routes redirect to /login. API routes return 401 JSON.
    """
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get("authenticated"):
            if request.path.startswith("/api/"):
                return jsonify({"error": "authentication required"}), 401
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return wrapper


# =============================================================================
# AZURE CLI AUTHENTICATION
# Uses the container's system-assigned managed identity. The identity is
# attached when the container is created (see deploy.yml). After login, the
# az CLI caches credentials inside the container, so subsequent calls work.
# =============================================================================

_az_login_lock = threading.Lock()
_az_logged_in = False


def ensure_az_login():
    """Idempotent: log in via managed identity once per container lifetime."""
    global _az_logged_in
    if _az_logged_in:
        return

    with _az_login_lock:
        if _az_logged_in:
            return

        result = subprocess.run(
            ["az", "login", "--identity", "--output", "none"],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode != 0:
            raise RuntimeError(
                f"az login --identity failed (is a managed identity attached "
                f"and granted Contributor?): {result.stderr.strip()}"
            )

        sub_id = os.getenv("AZURE_SUBSCRIPTION_ID")
        if sub_id:
            sub_result = subprocess.run(
                ["az", "account", "set", "--subscription", sub_id, "--output", "none"],
                capture_output=True, text=True, timeout=15
            )
            if sub_result.returncode != 0:
                raise RuntimeError(
                    f"az account set failed: {sub_result.stderr.strip()}"
                )

        _az_logged_in = True


# =============================================================================
# ARSENAL KNOWLEDGE BASE: 8 Categories with Expandable Topics
# =============================================================================

ARSENAL_CATEGORIES = {
    "technology": {
        "icon": "💻",
        "name": "Technology",
        "description": "Cloud, AI, Infrastructure, DevTools",
        "color": "#3b82f6",
        "topics": {
            "ai_ml_platform": {
                "name": "AI/ML Platform",
                "description": "GPU clusters, JupyterHub, MLflow, Vector DBs",
                "template_type": "arm",
                "estimated_cost": "$800-2500/mo",
                "resources": ["Azure ML Workspace", "AKS with GPU nodes", "Azure OpenAI", "Cosmos DB Vector", "Azure Blob Storage"],
                "deploy_time": "45-60s",
                "inputs": {
                    "gpu_count": {"type": "number", "default": 2, "label": "GPU Nodes"},
                    "enable_openai": {"type": "checkbox", "default": True, "label": "Enable Azure OpenAI"},
                    "model_version": {"type": "select", "options": ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"], "default": "gpt-4", "label": "Default Model"}
                }
            },
            "kubernetes_cluster": {
                "name": "Kubernetes Cluster",
                "description": "AKS with ingress, monitoring, cert-manager",
                "template_type": "arm",
                "estimated_cost": "$300-1200/mo",
                "resources": ["AKS Cluster", "Application Gateway", "Azure Container Registry", "Azure Monitor", "Key Vault"],
                "deploy_time": "50-60s",
                "inputs": {
                    "node_count": {"type": "number", "default": 3, "label": "Node Count"},
                    "node_size": {"type": "select", "options": ["Standard_D4s_v3", "Standard_D8s_v3", "Standard_F4s_v2"], "default": "Standard_D4s_v3", "label": "Node Size"},
                    "enable_istio": {"type": "checkbox", "default": False, "label": "Install Istio Service Mesh"}
                }
            },
            "serverless_architecture": {
                "name": "Serverless Architecture",
                "description": "Functions, Logic Apps, Event Grid, Cosmos DB",
                "template_type": "arm",
                "estimated_cost": "$50-400/mo",
                "resources": ["Azure Functions Premium", "Logic Apps", "Event Grid", "Cosmos DB Serverless", "API Management"],
                "deploy_time": "30-45s",
                "inputs": {
                    "function_runtime": {"type": "select", "options": ["python", "node", "dotnet", "java"], "default": "python", "label": "Runtime"},
                    "concurrency": {"type": "number", "default": 100, "label": "Max Concurrency"}
                }
            },
            "data_platform": {
                "name": "Data Platform",
                "description": "Synapse, Databricks, Data Factory, ADLS",
                "template_type": "arm",
                "estimated_cost": "$1000-5000/mo",
                "resources": ["Azure Synapse Analytics", "Azure Databricks", "Data Factory", "Data Lake Storage Gen2", "Purview"],
                "deploy_time": "55-60s",
                "inputs": {
                    "sql_pool_size": {"type": "select", "options": ["DW100c", "DW500c", "DW1000c", "DW2000c"], "default": "DW500c", "label": "SQL Pool Size"},
                    "enable_purview": {"type": "checkbox", "default": True, "label": "Enable Data Governance (Purview)"}
                }
            },
            "cicd_pipeline": {
                "name": "CI/CD Pipeline Hub",
                "description": "DevOps, GitHub Actions runners, artifact repos",
                "template_type": "arm",
                "estimated_cost": "$200-800/mo",
                "resources": ["Azure DevOps Organization", "Self-hosted Runners VMSS", "Azure Artifacts", "SonarCloud", "Snyk"],
                "deploy_time": "40-50s",
                "inputs": {
                    "runner_count": {"type": "number", "default": 4, "label": "Self-hosted Runners"},
                    "enable_security_scan": {"type": "checkbox", "default": True, "label": "Auto Security Scanning"}
                }
            },
            "observability_stack": {
                "name": "Observability Stack",
                "description": "Monitoring, logging, tracing, alerting",
                "template_type": "arm",
                "estimated_cost": "$150-600/mo",
                "resources": ["Azure Monitor", "Log Analytics", "Application Insights", "Grafana", "Prometheus"],
                "deploy_time": "35-45s",
                "inputs": {
                    "retention_days": {"type": "number", "default": 90, "label": "Log Retention (days)"},
                    "enable_aiops": {"type": "checkbox", "default": True, "label": "Enable AIOps Anomaly Detection"}
                }
            }
        }
    },

    "management": {
        "icon": "📊",
        "name": "Management",
        "description": "PMO, Portfolio, Resource, Change Management",
        "color": "#8b5cf6",
        "topics": {
            "project_management_office": {
                "name": "PMO Dashboard",
                "description": "Project Online, Power BI, Planner integration",
                "template_type": "arm",
                "estimated_cost": "$100-500/mo",
                "resources": ["Project Online", "Power BI Premium", "SharePoint Online", "Power Automate", "Teams"],
                "deploy_time": "25-35s",
                "inputs": {
                    "project_count": {"type": "number", "default": 50, "label": "Max Projects"},
                    "methodology": {"type": "select", "options": ["agile", "waterfall", "hybrid", "safe"], "default": "hybrid", "label": "Methodology"}
                }
            },
            "portfolio_analytics": {
                "name": "Portfolio Analytics",
                "description": "Investment tracking, ROI analysis, risk scoring",
                "template_type": "arm",
                "estimated_cost": "$300-1000/mo",
                "resources": ["Power BI Embedded", "Azure SQL Database", "Azure Analysis Services", "Data Factory", "Azure Functions"],
                "deploy_time": "40-50s",
                "inputs": {
                    "kpi_count": {"type": "number", "default": 20, "label": "KPI Metrics"},
                    "refresh_frequency": {"type": "select", "options": ["real-time", "hourly", "daily"], "default": "hourly", "label": "Data Refresh"}
                }
            },
            "resource_management": {
                "name": "Resource Management",
                "description": "Capacity planning, skill mapping, allocation",
                "template_type": "arm",
                "estimated_cost": "$200-800/mo",
                "resources": ["Dynamics 365 Project Operations", "Azure AD", "Power Apps", "Azure SQL", "Logic Apps"],
                "deploy_time": "45-55s",
                "inputs": {
                    "team_size": {"type": "number", "default": 100, "label": "Team Size"},
                    "skill_framework": {"type": "select", "options": ["sfdc", "custom", "sfia"], "default": "sfia", "label": "Skills Framework"}
                }
            },
            "change_management": {
                "name": "Change Management",
                "description": "ITIL processes, CAB workflow, risk assessment",
                "template_type": "arm",
                "estimated_cost": "$150-600/mo",
                "resources": ["ServiceNow Integration", "Azure Logic Apps", "Power Automate", "SharePoint", "Teams"],
                "deploy_time": "30-40s",
                "inputs": {
                    "approval_levels": {"type": "number", "default": 3, "label": "Approval Levels"},
                    "auto_rollback": {"type": "checkbox", "default": True, "label": "Enable Auto-Rollback"}
                }
            }
        }
    },

    "hr": {
        "icon": "👥",
        "name": "HR",
        "description": "Recruitment, Payroll, Performance, Culture",
        "color": "#ec4899",
        "topics": {
            "talent_acquisition": {
                "name": "Talent Acquisition Suite",
                "description": "ATS, interview scheduling, candidate scoring",
                "template_type": "arm",
                "estimated_cost": "$200-800/mo",
                "resources": ["Dynamics 365 Talent", "Azure AI Language", "Power Apps", "Azure Blob", "Logic Apps"],
                "deploy_time": "35-45s",
                "inputs": {
                    "hiring_volume": {"type": "number", "default": 500, "label": "Annual Hiring Volume"},
                    "ai_screening": {"type": "checkbox", "default": True, "label": "AI Resume Screening"}
                }
            },
            "hr_analytics": {
                "name": "HR Analytics Platform",
                "description": "People analytics, retention prediction, DEI metrics",
                "template_type": "arm",
                "estimated_cost": "$400-1500/mo",
                "resources": ["Azure Synapse", "Power BI", "Azure ML", "Azure SQL", "Purview"],
                "deploy_time": "45-55s",
                "inputs": {
                    "workforce_size": {"type": "number", "default": 1000, "label": "Workforce Size"},
                    "predictive_models": {"type": "multi_select", "options": ["retention", "performance", "diversity", "compensation"], "default": ["retention"], "label": "Predictive Models"}
                }
            },
            "payroll_automation": {
                "name": "Payroll Automation",
                "description": "Multi-country payroll, compliance, tax engine",
                "template_type": "arm",
                "estimated_cost": "$300-1200/mo",
                "resources": ["Dynamics 365 Finance", "Azure Functions", "Logic Apps", "Azure SQL", "Key Vault"],
                "deploy_time": "40-50s",
                "inputs": {
                    "countries": {"type": "number", "default": 5, "label": "Countries"},
                    "payroll_frequency": {"type": "select", "options": ["monthly", "bi-weekly", "weekly"], "default": "monthly", "label": "Frequency"}
                }
            },
            "employee_engagement": {
                "name": "Employee Engagement",
                "description": "Pulse surveys, sentiment analysis, recognition",
                "template_type": "arm",
                "estimated_cost": "$150-600/mo",
                "resources": ["Viva Insights", "Azure AI Text Analytics", "Power Apps", "Teams Apps", "Azure Cosmos DB"],
                "deploy_time": "30-40s",
                "inputs": {
                    "survey_frequency": {"type": "select", "options": ["weekly", "monthly", "quarterly"], "default": "monthly", "label": "Pulse Frequency"},
                    "anonymity_level": {"type": "select", "options": ["fully_anonymous", "department_only", "manager_visible"], "default": "department_only", "label": "Anonymity"}
                }
            }
        }
    },

    "finance": {
        "icon": "💰",
        "name": "Finance",
        "description": "Accounting, FP&A, Treasury, Compliance",
        "color": "#10b981",
        "topics": {
            "financial_planning": {
                "name": "FP&A Platform",
                "description": "Budgeting, forecasting, variance analysis",
                "template_type": "arm",
                "estimated_cost": "$500-2000/mo",
                "resources": ["Dynamics 365 Finance", "Power BI Premium", "Azure Analysis Services", "Azure SQL", "Data Factory"],
                "deploy_time": "50-60s",
                "inputs": {
                    "planning_horizon": {"type": "select", "options": ["12_months", "24_months", "36_months", "60_months"], "default": "24_months", "label": "Planning Horizon"},
                    "scenario_count": {"type": "number", "default": 5, "label": "What-if Scenarios"}
                }
            },
            "treasury_management": {
                "name": "Treasury Management",
                "description": "Cash flow, FX risk, hedging, bank integration",
                "template_type": "arm",
                "estimated_cost": "$400-1500/mo",
                "resources": ["Dynamics 365 Finance", "Azure API Management", "Logic Apps", "Azure SQL", "Key Vault"],
                "deploy_time": "45-55s",
                "inputs": {
                    "bank_connections": {"type": "number", "default": 10, "label": "Bank Connections"},
                    "fx_hedging": {"type": "checkbox", "default": True, "label": "Enable FX Hedging"}
                }
            },
            "audit_compliance": {
                "name": "Audit & Compliance",
                "description": "SOX, GDPR, automated controls, evidence collection",
                "template_type": "arm",
                "estimated_cost": "$300-1200/mo",
                "resources": ["Microsoft Purview", "Azure Policy", "Azure Monitor", "SharePoint", "Power Automate"],
                "deploy_time": "40-50s",
                "inputs": {
                    "frameworks": {"type": "multi_select", "options": ["SOX", "GDPR", "HIPAA", "ISO27001", "SOC2"], "default": ["SOX"], "label": "Compliance Frameworks"},
                    "audit_frequency": {"type": "select", "options": ["continuous", "monthly", "quarterly"], "default": "continuous", "label": "Audit Frequency"}
                }
            },
            "tax_engine": {
                "name": "Global Tax Engine",
                "description": "Transfer pricing, tax reporting, e-invoicing",
                "template_type": "arm",
                "estimated_cost": "$600-2500/mo",
                "resources": ["Dynamics 365 Finance", "Azure Functions", "Logic Apps", "Azure SQL", "Blob Storage"],
                "deploy_time": "50-60s",
                "inputs": {
                    "tax_jurisdictions": {"type": "number", "default": 15, "label": "Tax Jurisdictions"},
                    "e_invoicing": {"type": "checkbox", "default": True, "label": "Enable E-Invoicing"}
                }
            }
        }
    },

    "legal": {
        "icon": "⚖️",
        "name": "Legal",
        "description": "Contract, IP, Litigation, Compliance",
        "color": "#f59e0b",
        "topics": {
            "contract_lifecycle": {
                "name": "Contract Lifecycle Management",
                "description": "Drafting, negotiation, execution, renewal",
                "template_type": "arm",
                "estimated_cost": "$400-1500/mo",
                "resources": ["SharePoint Premium", "Azure AI Language", "Power Automate", "Azure AD", "Azure Blob"],
                "deploy_time": "35-45s",
                "inputs": {
                    "contract_volume": {"type": "number", "default": 1000, "label": "Annual Contracts"},
                    "ai_clause_detection": {"type": "checkbox", "default": True, "label": "AI Clause Detection"}
                }
            },
            "ip_management": {
                "name": "IP Portfolio Management",
                "description": "Patents, trademarks, licensing, renewals",
                "template_type": "arm",
                "estimated_cost": "$300-1000/mo",
                "resources": ["Dynamics 365", "Azure SQL", "Power Apps", "Logic Apps", "Azure Search"],
                "deploy_time": "40-50s",
                "inputs": {
                    "ip_types": {"type": "multi_select", "options": ["patents", "trademarks", "copyrights", "trade_secrets"], "default": ["patents"], "label": "IP Types"},
                    "jurisdictions": {"type": "number", "default": 20, "label": "Jurisdictions"}
                }
            },
            "litigation_support": {
                "name": "Litigation Support",
                "description": "eDiscovery, case management, document review",
                "template_type": "arm",
                "estimated_cost": "$500-2000/mo",
                "resources": ["Microsoft Purview eDiscovery", "Azure Cognitive Search", "Azure Blob", "Power BI", "Azure SQL"],
                "deploy_time": "45-55s",
                "inputs": {
                    "case_capacity": {"type": "number", "default": 50, "label": "Active Cases"},
                    "data_volume_tb": {"type": "number", "default": 10, "label": "Data Volume (TB)"}
                }
            },
            "regulatory_tracking": {
                "name": "Regulatory Tracking",
                "description": "Regulation monitoring, impact analysis, reporting",
                "template_type": "arm",
                "estimated_cost": "$200-800/mo",
                "resources": ["Azure Functions", "Cosmos DB", "Power Apps", "Logic Apps", "Azure AI Language"],
                "deploy_time": "30-40s",
                "inputs": {
                    "industries": {"type": "multi_select", "options": ["financial", "healthcare", "energy", "tech", "retail"], "default": ["financial"], "label": "Industries"},
                    "alert_frequency": {"type": "select", "options": ["real-time", "daily", "weekly"], "default": "daily", "label": "Alert Frequency"}
                }
            }
        }
    },

    "strategy": {
        "icon": "🎯",
        "name": "Strategy",
        "description": "Market Intelligence, M&A, Innovation, OKRs",
        "color": "#6366f1",
        "topics": {
            "market_intelligence": {
                "name": "Market Intelligence Platform",
                "description": "Competitive analysis, trend detection, forecasting",
                "template_type": "arm",
                "estimated_cost": "$600-2500/mo",
                "resources": ["Azure Synapse", "Power BI", "Azure AI Language", "Azure OpenAI", "Cosmos DB"],
                "deploy_time": "50-60s",
                "inputs": {
                    "data_sources": {"type": "number", "default": 50, "label": "Data Sources"},
                    "ai_insights": {"type": "checkbox", "default": True, "label": "AI-Generated Insights"}
                }
            },
            "ma_diligence": {
                "name": "M&A Diligence Suite",
                "description": "Target screening, valuation, integration planning",
                "template_type": "arm",
                "estimated_cost": "$800-3000/mo",
                "resources": ["Dynamics 365", "Power BI Premium", "Azure ML", "Azure SQL", "SharePoint"],
                "deploy_time": "55-60s",
                "inputs": {
                    "pipeline_size": {"type": "number", "default": 20, "label": "Deal Pipeline Size"},
                    "valuation_models": {"type": "multi_select", "options": ["dcf", "comparable", "precedent", "lbo"], "default": ["dcf"], "label": "Valuation Models"}
                }
            },
            "innovation_lab": {
                "name": "Innovation Lab",
                "description": "Ideation, prototyping, portfolio, metrics",
                "template_type": "arm",
                "estimated_cost": "$300-1200/mo",
                "resources": ["Azure DevOps", "Power Apps", "Azure OpenAI", "Azure Container Instances", "Cosmos DB"],
                "deploy_time": "40-50s",
                "inputs": {
                    "lab_type": {"type": "select", "options": ["digital", "product", "process", "business_model"], "default": "digital", "label": "Lab Type"},
                    "prototype_budget": {"type": "number", "default": 500000, "label": "Annual Budget ($)"}
                }
            },
            "okr_platform": {
                "name": "OKR & Strategy Execution",
                "description": "Goal setting, alignment, tracking, retrospectives",
                "template_type": "arm",
                "estimated_cost": "$200-800/mo",
                "resources": ["Power Apps", "Power BI", "Azure SQL", "Teams Apps", "Azure Functions"],
                "deploy_time": "30-40s",
                "inputs": {
                    "org_levels": {"type": "number", "default": 5, "label": "Organization Levels"},
                    "check_in_frequency": {"type": "select", "options": ["weekly", "bi-weekly", "monthly"], "default": "weekly", "label": "Check-in Frequency"}
                }
            }
        }
    },

    "engineering": {
        "icon": "🔧",
        "name": "Engineering",
        "description": "R&D, Product Dev, QA, Release",
        "color": "#06b6d4",
        "topics": {
            "dev_environment": {
                "name": "Developer Environment",
                "description": "IDE cloud, pair programming, code spaces",
                "template_type": "arm",
                "estimated_cost": "$200-1000/mo per dev",
                "resources": ["Azure Virtual Desktop", "GitHub Codespaces", "Azure Container Instances", "Azure Files", "Azure Bastion"],
                "deploy_time": "40-50s",
                "inputs": {
                    "developer_count": {"type": "number", "default": 50, "label": "Developer Count"},
                    "ide_type": {"type": "select", "options": ["vscode", "jetbrains", "eclipse", "custom"], "default": "vscode", "label": "IDE Type"}
                }
            },
            "test_automation": {
                "name": "Test Automation Grid",
                "description": "Selenium, Playwright, mobile, performance",
                "template_type": "arm",
                "estimated_cost": "$300-1500/mo",
                "resources": ["Azure Container Instances", "Azure DevOps", "Azure Load Testing", "Azure Files", "Azure Monitor"],
                "deploy_time": "35-45s",
                "inputs": {
                    "parallel_tests": {"type": "number", "default": 100, "label": "Max Parallel Tests"},
                    "browser_matrix": {"type": "multi_select", "options": ["chrome", "firefox", "safari", "edge", "mobile_chrome", "mobile_safari"], "default": ["chrome"], "label": "Browser Matrix"}
                }
            },
            "release_management": {
                "name": "Release Management",
                "description": "Feature flags, canary, blue-green, rollback",
                "template_type": "arm",
                "estimated_cost": "$250-1000/mo",
                "resources": ["Azure DevOps", "AKS", "Azure App Configuration", "Azure Monitor", "Azure Traffic Manager"],
                "deploy_time": "40-50s",
                "inputs": {
                    "deployment_strategy": {"type": "select", "options": ["blue_green", "canary", "rolling", "a_b"], "default": "blue_green", "label": "Strategy"},
                    "rollback_time_sla": {"type": "number", "default": 300, "label": "Rollback SLA (seconds)"}
                }
            },
            "documentation_platform": {
                "name": "Documentation Platform",
                "description": "Tech docs, API refs, wikis, search",
                "template_type": "arm",
                "estimated_cost": "$100-500/mo",
                "resources": ["Azure Static Web Apps", "Azure Search", "Azure Functions", "Cosmos DB", "Azure CDN"],
                "deploy_time": "25-35s",
                "inputs": {
                    "doc_format": {"type": "select", "options": ["markdown", "asciidoc", "restructured", "openapi"], "default": "markdown", "label": "Doc Format"},
                    "search_type": {"type": "select", "options": ["semantic", "keyword", "hybrid"], "default": "semantic", "label": "Search Type"}
                }
            }
        }
    },

    "operations": {
        "icon": "⚙️",
        "name": "Operations",
        "description": "Supply Chain, Manufacturing, Logistics, Quality",
        "color": "#84cc16",
        "topics": {
            "supply_chain": {
                "name": "Supply Chain Control Tower",
                "description": "End-to-end visibility, demand planning, optimization",
                "template_type": "arm",
                "estimated_cost": "$800-3000/mo",
                "resources": ["Dynamics 365 Supply Chain", "Azure IoT Hub", "Azure Digital Twins", "Azure Synapse", "Power BI"],
                "deploy_time": "55-60s",
                "inputs": {
                    "supplier_count": {"type": "number", "default": 500, "label": "Supplier Count"},
                    "iot_sensors": {"type": "number", "default": 10000, "label": "IoT Sensors"},
                    "optimization_engine": {"type": "checkbox", "default": True, "label": "AI Optimization Engine"}
                }
            },
            "manufacturing_execution": {
                "name": "Manufacturing Execution",
                "description": "MES, OEE, quality gates, traceability",
                "template_type": "arm",
                "estimated_cost": "$1000-4000/mo",
                "resources": ["Azure IoT Edge", "Azure Digital Twins", "Azure SQL", "Power Apps", "Azure Stream Analytics"],
                "deploy_time": "55-60s",
                "inputs": {
                    "production_lines": {"type": "number", "default": 20, "label": "Production Lines"},
                    "quality_checkpoints": {"type": "number", "default": 50, "label": "Quality Checkpoints"}
                }
            },
            "warehouse_automation": {
                "name": "Warehouse Automation",
                "description": "WMS, robotics integration, picking optimization",
                "template_type": "arm",
                "estimated_cost": "$600-2500/mo",
                "resources": ["Dynamics 365 SCM", "Azure IoT Hub", "Azure Functions", "Azure Maps", "Azure SQL"],
                "deploy_time": "50-60s",
                "inputs": {
                    "warehouse_count": {"type": "number", "default": 10, "label": "Warehouse Count"},
                    "robotics_integration": {"type": "checkbox", "default": True, "label": "Robotics Integration"}
                }
            },
            "predictive_maintenance": {
                "name": "Predictive Maintenance",
                "description": "Condition monitoring, failure prediction, scheduling",
                "template_type": "arm",
                "estimated_cost": "$500-2000/mo",
                "resources": ["Azure IoT Hub", "Azure ML", "Azure Digital Twins", "Azure Functions", "Power BI"],
                "deploy_time": "50-60s",
                "inputs": {
                    "asset_count": {"type": "number", "default": 1000, "label": "Asset Count"},
                    "prediction_horizon": {"type": "select", "options": ["7_days", "30_days", "90_days"], "default": "30_days", "label": "Prediction Horizon"}
                }
            }
        }
    }
}


# =============================================================================
# DYNAMIC TEMPLATE GENERATOR
# =============================================================================

def generate_arm_template(category, topic_key, topic_data, custom_inputs):
    """Generate a complete ARM template based on topic configuration and user inputs.

    Lookup order:
      1. arm-templates/{category}/{topic_key}.json on disk — used as-is. The file's
         own parameters block defines what user inputs flow through. This is how
         "real" topics are wired up (see observability_stack.json, talent_acquisition.json).
      2. Generic 'marker' template — a tagged storage account, used as a placeholder
         for topics that don't yet have a real template. Lets every topic's deploy
         button succeed while we incrementally fill in real infra per topic.
    """
    deploy_id = str(uuid.uuid4())[:8]
    base_name = f"{category}-{topic_key}-{deploy_id}"

    # --- Path 1: load from disk if a real template exists ---
    templates_dir = os.getenv(
        'ARM_TEMPLATES_DIR',
        os.path.join(os.path.dirname(os.path.abspath(__file__)), 'arm-templates')
    )
    template_path = os.path.join(templates_dir, category, f'{topic_key}.json')
    if os.path.isfile(template_path):
        try:
            with open(template_path) as f:
                template = json.load(f)
            return template, base_name, deploy_id
        except (OSError, json.JSONDecodeError) as e:
            # Don't crash the deploy on a malformed file — log and fall through
            # to the marker template so the user still gets a working deployment.
            app.logger.warning(
                "Failed to load %s, falling back to marker template: %s",
                template_path, e
            )

    # --- Path 2: marker storage template (default for all unwired topics) ---
    template = {
        "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
        "contentVersion": "1.0.0.0",
        "parameters": {
            "location": {
                "type": "string",
                "defaultValue": "[resourceGroup().location]"
            },
            "environmentName": {
                "type": "string",
                "defaultValue": custom_inputs.get('environment', 'production')
            }
        },
        "variables": {
            "uniqueSuffix": deploy_id,
            "baseName": base_name,
            "storageAccountName": "[concat('arsenal', uniqueString(resourceGroup().id, variables('uniqueSuffix')))]"
        },
        "resources": [
            {
                "type": "Microsoft.Storage/storageAccounts",
                "apiVersion": "2023-01-01",
                "name": "[variables('storageAccountName')]",
                "location": "[parameters('location')]",
                "kind": "StorageV2",
                "sku": {"name": "Standard_LRS"},
                "properties": {
                    "minimumTlsVersion": "TLS1_2",
                    "allowBlobPublicAccess": False,
                    "supportsHttpsTrafficOnly": True
                },
                "tags": {
                    "arsenal": "true",
                    "category": category,
                    "topic": topic_key,
                    "topicName": topic_data.get('name', topic_key),
                    "deployId": deploy_id,
                    "environment": "[parameters('environmentName')]"
                }
            }
        ],
        "outputs": {
            "deploymentId": {
                "type": "string",
                "value": deploy_id
            },
            "resourceGroupName": {
                "type": "string",
                "value": "[resourceGroup().name]"
            },
            "storageAccountName": {
                "type": "string",
                "value": "[variables('storageAccountName')]"
            },
            "topicDeployed": {
                "type": "string",
                "value": topic_data.get('name', topic_key)
            }
        }
    }

    for input_key, input_config in topic_data.get('inputs', {}).items():
        param_type = "string"
        input_type = input_config.get('type')
        if input_type == 'number':
            param_type = "int"
        elif input_type == 'checkbox':
            param_type = "bool"
        elif input_type == 'multi_select':
            param_type = "array"

        default_value = input_config.get('default')
        if default_value is None:
            if param_type == 'int':
                default_value = 0
            elif param_type == 'bool':
                default_value = False
            elif param_type == 'array':
                default_value = []
            else:
                default_value = ''

        param_spec = {"type": param_type, "defaultValue": default_value}
        if 'options' in input_config and input_type == 'select':
            param_spec["allowedValues"] = input_config['options']

        template['parameters'][input_key] = param_spec

    return template, base_name, deploy_id


# =============================================================================
# FLASK ROUTES
# =============================================================================

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page. POST validates credentials against env-configured user."""
    if session.get("authenticated"):
        return redirect(url_for("index"))

    error = None
    if request.method == 'POST':
        username = (request.form.get('username') or '').strip()
        password = request.form.get('password') or ''

        valid = False
        if ARSENAL_PASSWORD_HASH and username == ARSENAL_USERNAME:
            try:
                valid = bcrypt.checkpw(
                    password.encode('utf-8'),
                    ARSENAL_PASSWORD_HASH.encode('utf-8')
                )
            except (ValueError, TypeError):
                valid = False

        if valid:
            session.clear()
            session['authenticated'] = True
            session['username'] = username
            return redirect(url_for('index'))

        error = 'Invalid username or password'

    return render_template('login.html', error=error), (401 if error else 200)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/auth/whoami')
def whoami():
    if not session.get('authenticated'):
        return jsonify({'authenticated': False})
    return jsonify({
        'authenticated': True,
        'username': session.get('username')
    })


@app.route('/')
@require_auth
def index():
    return render_template('index.html', categories=ARSENAL_CATEGORIES)


@app.route('/dashboard')
@require_auth
def dashboard_page():
    return render_template('dashboard.html', categories=ARSENAL_CATEGORIES)


@app.route('/api/deployments')
@require_auth
def list_deployments():
    """Return every resource group tagged arsenal=true with its resources.

    Used by /dashboard. Reads from Azure live (no local persistence) so the
    dashboard always reflects truth even if someone deleted a RG out-of-band.
    """
    try:
        ensure_az_login()

        rg_result = subprocess.run([
            "az", "group", "list",
            "--query", "[?tags.arsenal=='true']",
            "--output", "json"
        ], capture_output=True, text=True, timeout=30)

        if rg_result.returncode != 0:
            return jsonify({
                "error": "Failed to list resource groups",
                "details": rg_result.stderr.strip()
            }), 500

        groups = json.loads(rg_result.stdout or "[]")
        deployments = []

        for g in groups:
            tags = g.get('tags') or {}
            category = tags.get('category', 'unknown')
            topic = tags.get('topic', 'unknown')
            deploy_id = tags.get('deploy_id', '')

            # Fetch resources for this RG. Cap timeout per-RG so a single slow
            # group doesn't stall the whole dashboard.
            resources = []
            res_result = subprocess.run([
                "az", "resource", "list",
                "--resource-group", g['name'],
                "--query", "[].{type:type, name:name, location:location}",
                "--output", "json"
            ], capture_output=True, text=True, timeout=15)
            if res_result.returncode == 0:
                try:
                    resources = json.loads(res_result.stdout or "[]")
                except json.JSONDecodeError:
                    resources = []

            # Look up topic metadata for friendly name + cost estimate.
            cat_data = ARSENAL_CATEGORIES.get(category, {})
            topic_data = cat_data.get('topics', {}).get(topic, {})

            deployments.append({
                "deploy_id": deploy_id,
                "resource_group": g.get('name'),
                "location": g.get('location'),
                "category": category,
                "category_name": cat_data.get('name', category.title()),
                "category_icon": cat_data.get('icon', '📦'),
                "category_color": cat_data.get('color', '#06B6D4'),
                "topic": topic,
                "topic_name": topic_data.get('name', topic.replace('_', ' ').title()),
                "estimated_cost": topic_data.get('estimated_cost', 'Unknown'),
                "deploy_time": topic_data.get('deploy_time', '—'),
                "resource_count": len(resources),
                "resources": resources,
                "provisioning_state": (g.get('properties') or {}).get('provisioningState', 'Unknown'),
                "portal_url": (
                    f"https://portal.azure.com/#@/resource/subscriptions/"
                    f"{os.getenv('AZURE_SUBSCRIPTION_ID', '')}/resourceGroups/{g.get('name')}"
                ),
            })

        # Sort newest-first by deploy_id (UUIDs aren't temporal but the alpha
        # order is deterministic which is good enough for a small list).
        deployments.sort(key=lambda d: d['resource_group'], reverse=True)

        # Build summary roll-up.
        by_category = {}
        for d in deployments:
            by_category.setdefault(d['category'], 0)
            by_category[d['category']] += 1

        return jsonify({
            "deployments": deployments,
            "summary": {
                "total": len(deployments),
                "categories_used": len(by_category),
                "total_resources": sum(d['resource_count'] for d in deployments),
                "by_category": by_category,
            }
        })

    except subprocess.TimeoutExpired:
        return jsonify({"error": "Azure CLI timed out listing deployments"}), 504
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/categories')
@require_auth
def get_categories():
    return jsonify(ARSENAL_CATEGORIES)


@app.route('/api/deploy', methods=['POST'])
@require_auth
def deploy():
    data = request.json
    category = data.get('category')
    topic = data.get('topic')
    custom_inputs = data.get('custom_inputs', {})
    additional_requirements = data.get('additional_requirements', '')

    if category not in ARSENAL_CATEGORIES:
        return jsonify({"error": "Invalid category"}), 400

    if topic not in ARSENAL_CATEGORIES[category]['topics']:
        return jsonify({"error": "Invalid topic"}), 400

    topic_data = ARSENAL_CATEGORIES[category]['topics'][topic]

    # Generate template
    template, base_name, deploy_id = generate_arm_template(
        category, topic, topic_data, custom_inputs
    )

    # Save template
    template_file = f"/tmp/arsenal-{deploy_id}.json"
    with open(template_file, 'w') as f:
        json.dump(template, f, indent=2)

    # Create resource group and deploy
    rg_name = f"arsenal-{base_name}"
    deployment_name = f"arsenal-{deploy_id}"

    try:
        # Make sure the CLI inside this container is authenticated.
        ensure_az_login()

        # Create resource group
        rg_result = subprocess.run([
            "az", "group", "create",
            "--name", rg_name,
            "--location", "eastus",
            "--tags", f"arsenal=true category={category} topic={topic} deploy_id={deploy_id}",
            "--output", "none"
        ], capture_output=True, text=True, timeout=30)
        if rg_result.returncode != 0:
            raise Exception(f"az group create failed: {rg_result.stderr.strip()}")

        # Build the --parameters list dynamically from the parameters the
        # generated template actually declares. This prevents "unrecognized
        # parameter" errors regardless of which topic the user picked.
        declared_params = template.get('parameters', {})
        parameter_args = []
        for param_name, param_spec in declared_params.items():
            if param_name not in custom_inputs:
                # No user value — let ARM use the template's defaultValue.
                continue
            value = custom_inputs[param_name]
            # Coerce Python types to CLI-friendly strings.
            if isinstance(value, bool):
                value_str = 'true' if value else 'false'
            elif isinstance(value, (list, dict)):
                value_str = json.dumps(value)
            elif value is None:
                continue
            else:
                value_str = str(value)
            parameter_args.extend(['--parameters', f"{param_name}={value_str}"])

        # Deploy ARM template
        deploy_result = subprocess.run([
            "az", "deployment", "group", "create",
            "--resource-group", rg_name,
            "--name", deployment_name,
            "--template-file", template_file,
            *parameter_args,
            "--output", "json"
        ], capture_output=True, text=True, timeout=300)

        if deploy_result.returncode != 0:
            raise Exception(deploy_result.stderr)

        deployment_output = json.loads(deploy_result.stdout)
        outputs = deployment_output.get('properties', {}).get('outputs', {})

        return jsonify({
            "status": "success",
            "deploy_id": deploy_id,
            "category": category,
            "topic": topic,
            "resource_group": rg_name,
            "deployment_name": deployment_name,
            "portal_url": f"https://portal.azure.com/#@/resource/subscriptions/{os.getenv('AZURE_SUBSCRIPTION_ID', '')}/resourceGroups/{rg_name}",
            "estimated_cost": topic_data.get('estimated_cost', 'Variable'),
            "deploy_time": topic_data.get('deploy_time', '45-60s'),
            "message": f"🎉 {topic_data['name']} deployed successfully!",
            "outputs": outputs,
            "additional_requirements_processed": bool(additional_requirements)
        })

    except subprocess.TimeoutExpired:
        return jsonify({
            "status": "timeout",
            "deploy_id": deploy_id,
            "message": "Deployment is taking longer than expected. Check Azure Portal for status."
        }), 202

    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e),
            "deploy_id": deploy_id
        }), 500


@app.route('/api/custom-topic', methods=['POST'])
@require_auth
def add_custom_topic():
    """Allow users to add custom topics to any category."""
    data = request.json
    category = data.get('category')
    topic_key = data.get('topic_key')
    topic_data = data.get('topic_data')

    if category not in ARSENAL_CATEGORIES:
        return jsonify({"error": "Category not found"}), 400

    ARSENAL_CATEGORIES[category]['topics'][topic_key] = topic_data

    return jsonify({
        "status": "success",
        "message": f"Custom topic '{topic_data.get('name')}' added to {ARSENAL_CATEGORIES[category]['name']}"
    })


@app.route('/api/status/<deploy_id>')
@require_auth
def check_status(deploy_id):
    """Check deployment status."""
    try:
        ensure_az_login()
        result = subprocess.run([
            "az", "deployment", "group", "list",
            "--resource-group", f"arsenal-*-{deploy_id}",
            "--query", f"[?contains(name, 'arsenal-{deploy_id}')]",
            "--output", "json"
        ], capture_output=True, text=True, timeout=30)

        if result.returncode == 0:
            deployments = json.loads(result.stdout)
            status = deployments[0].get('properties', {}).get('provisioningState', 'Unknown') if deployments else 'Not Found'
            return jsonify({"deploy_id": deploy_id, "status": status})
    except Exception:
        pass

    return jsonify({"deploy_id": deploy_id, "status": "Unknown"})


@app.route('/api/destroy/<deploy_id>', methods=['POST'])
@require_auth
def destroy(deploy_id):
    """Destroy a deployment."""
    try:
        ensure_az_login()
        result = subprocess.run([
            "az", "group", "list",
            "--query", f"[?contains(name, 'arsenal-') && contains(name, '{deploy_id}')].name",
            "--output", "tsv"
        ], capture_output=True, text=True, timeout=30)

        if result.returncode == 0 and result.stdout.strip():
            rg_name = result.stdout.strip().splitlines()[0]
            subprocess.run([
                "az", "group", "delete",
                "--name", rg_name,
                "--yes",
                "--no-wait",
                "--output", "none"
            ], check=True, timeout=30)

            return jsonify({
                "status": "success",
                "message": f"Resource group {rg_name} is being deleted"
            })

    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500

    return jsonify({"status": "error", "message": "Deployment not found"}), 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
