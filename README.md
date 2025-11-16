# MCP Servers Collection - Production Ready AI Automation Platform

[![Deploy to Production](https://github.com/your-username/mcp-servers/actions/workflows/deploy.yml/badge.svg)](https://github.com/your-username/mcp-servers/actions/workflows/deploy.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

A comprehensive collection of Model Context Protocol (MCP) servers for AI automation, specifically designed for enterprise use and optimized for the Indonesian market. Built by [CampShure](https://campshure.com) for scalable business automation.

## 🌟 Features

### **Complete MCP Server Collection**
- **📅 Calendar Server**: Google Calendar integration for scheduling automation
- **📁 Filesystem Server**: Secure file management with workspace isolation  
- **🐙 GitHub Server**: Repository management and automation
- **📧 Gmail Server**: Email automation and management
- **🔍 Perplexity Server**: AI-powered search and knowledge retrieval
- **💬 Slack Server**: Team communication automation
- **🌤️ Weather Server**: Weather data and alerts from National Weather Service

### **Production Ready Infrastructure**
- **🚀 Full CI/CD Pipeline**: Automated testing, building, and deployment
- **🐳 Docker Containerization**: Scalable container-based architecture
- **🔒 Security First**: User isolation, rate limiting, comprehensive security
- **📊 Monitoring**: Health checks, logging, and performance metrics
- **🌏 Indonesian Market Ready**: Timezone, language, and business optimizations

## 📋 Prerequisites

- **Docker & Docker Compose**: Container runtime
- **Python 3.11+**: Programming language
- **Git**: Version control
- **Nginx** (optional): Reverse proxy
- **Valid API Keys**: For external services (Gmail, Slack, GitHub, Perplexity)

## 🚀 Quick Start

### **1. Clone Repository**

```bash
git clone https://github.com/your-username/mcp-servers.git
cd mcp-servers
```

### **2. Local Development**

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Run status check
python check_status.py

# Start development server
python main.py
```

### **3. Production Deployment**

```bash
# Run automated deployment script
./deploy.sh

# Configure environment
cp .env.example .env
nano .env  # Edit with your configuration

# Start all services
sudo systemctl start mcp-servers

# Check status
docker-compose ps
```

## 🔧 Configuration

### **Environment Setup**

```bash
# Essential Configuration (.env)
ENVIRONMENT=production
SECRET_KEY=your-super-secret-key
API_KEY=your-mcp-api-key

# Indonesian Market Settings
DEFAULT_TIMEZONE=Asia/Jakarta
DEFAULT_LANGUAGE=id
BABEL_LOCALE=id_ID

# API Keys
GMAIL_CLIENT_ID=your-gmail-client-id
GMAIL_CLIENT_SECRET=your-gmail-client-secret
SLACK_BOT_TOKEN=xoxb-your-slack-token
GITHUB_TOKEN=your-github-token
PERPLEXITY_API_KEY=your-perplexity-key
```

### **GitHub Secrets (CI/CD)**

Required secrets for automated deployment:

```yaml
PRODUCTION_HOST: your-server.com
PRODUCTION_USER: deploy-user
SSH_PRIVATE_KEY: |
  -----BEGIN OPENSSH PRIVATE KEY-----
  your-ssh-private-key-here
  -----END OPENSSH PRIVATE KEY-----
SSH_PORT: 22
SLACK_WEBHOOK_URL: https://hooks.slack.com/services/...
```

## 🏗️ Architecture

```mermaid
graph TB
    A[GitHub Repository] --> B[GitHub Actions CI/CD]
    B --> C[Docker Build]
    C --> D[Production Server]
    D --> E[Docker Compose Stack]
    
    E --> F[MCP Servers Container]
    E --> G[Redis Cache]
    E --> H[PostgreSQL Database]
    E --> I[Nginx Reverse Proxy]
    E --> J[Monitoring Stack]
    
    F --> K[Calendar Server]
    F --> L[Gmail Server]
    F --> M[Slack Server]
    F --> N[GitHub Server]
    F --> O[Filesystem Server]
    F --> P[Perplexity Server]
    F --> Q[Weather Server]
```

## 🔄 CI/CD Pipeline

### **Automated Deployment Flow**

1. **Code Push**: Developer pushes to main branch
2. **Testing**: Automated pytest, linting, security scans
3. **Building**: Docker image creation with optimization
4. **Deployment**: SSH deployment to production server
5. **Health Checks**: Verify all services are healthy
6. **Notifications**: Slack notification of deployment status

### **Manual Deployment**

```bash
# Deploy via GitHub Actions
gh workflow run deploy.yml

# Or deploy locally
docker-compose up -d --build

# Check deployment status
./health_check.sh
```

## 📊 Monitoring & Management

### **Health Monitoring**

```bash
# Overall health check
python check_status.py

# Service status
sudo systemctl status mcp-servers

# Container logs
docker-compose logs -f mcp-servers

# Individual server health
curl http://localhost:8000/health
```

### **Performance Monitoring**

- **Grafana Dashboard**: `http://your-server:3000`
- **Prometheus Metrics**: `http://your-server:9090`
- **Log Analysis**: `/opt/mcp-servers/logs/`

### **Backup & Recovery**

```bash
# Manual backup
/usr/local/bin/backup-mcp-servers

# Automated daily backups (configured via cron)
# View backup status
ls -la /var/backups/mcp-servers/
```

## 🧪 Testing

### **Run Test Suite**

```bash
# All tests
python -m pytest tests/ -v

# Specific server tests
python -m pytest tests/test_all_servers.py::TestWeatherServer -v

# Coverage report
python -m pytest tests/ --cov=. --cov-report=html
```

### **Indonesian Market Tests**

```bash
# Test Indonesian-specific features
python -m pytest tests/test_all_servers.py::TestIndonesianMarketFeatures -v
```

## 🔌 API Usage Examples

### **Weather Server**
```python
# Get Indonesian weather alerts
await get_alerts("ID")  # Indonesia weather alerts

# Jakarta weather forecast
await get_forecast(-6.2088, 106.8456)  # Jakarta coordinates
```

### **Calendar Server**
```python
# Create meeting in Jakarta timezone
await create_event(
    title="Team Standup",
    start_datetime="2024-01-15T09:00:00+07:00",  # WIB timezone
    end_datetime="2024-01-15T09:30:00+07:00"
)
```

### **Perplexity Server**
```python
# Indonesian market research
await research_indonesian_market(
    topic="fintech Indonesia 2024",
    focus_areas=["regulations", "digital banking", "investment"]
)

# Competitor analysis
await analyze_competitors(
    company_or_industry="ride-sharing Indonesia",
    include_financials=True
)
```

## 🛠️ Development

### **Adding New Servers**

1. **Create server file**: `your_server.py`
2. **Follow MCP pattern**:
```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("your-server")

@mcp.tool()
async def your_function(param: str) -> str:
    """Your function description."""
    return "result"

def main():
    mcp.run(transport='stdio')
```
3. **Update configuration**: Add to `main.py` and `check_status.py`
4. **Add tests**: Create tests in `tests/`
5. **Update documentation**

### **Indonesian Market Customizations**

- **Timezone**: Default to `Asia/Jakarta`
- **Language**: Support Indonesian (`id`) and English (`en`)
- **Business Hours**: 09:00-17:00 WIB
- **Local Holidays**: Indonesian national and religious holidays
- **Currency**: IDR support in financial calculations

## 📁 Project Structure

```
mcp-servers/
├── .github/
│   ├── workflows/          # CI/CD pipeline
│   ├── ISSUE_TEMPLATE/     # Issue templates
│   └── PULL_REQUEST_TEMPLATE.md
├── tests/                  # Test suite
├── monitoring/             # Prometheus & Grafana configs
├── logs/                   # Application logs
├── user-workspaces/        # User file isolation
├── ssl/                    # SSL certificates
│
├── calendar_server.py      # 📅 Google Calendar integration
├── filesystem_server.py    # 📁 File management
├── github_server.py        # 🐙 GitHub automation
├── gmail_server.py         # 📧 Email automation  
├── perplexity_server.py    # 🔍 AI search
├── slack_server.py         # 💬 Team communication
├── weather_server.py       # 🌤️ Weather data
│
├── main.py                 # Main application entry
├── check_status.py         # Health monitoring
├── requirements.txt        # Dependencies
├── Dockerfile             # Container definition
├── docker-compose.yml     # Multi-service setup
├── nginx.conf             # Reverse proxy
├── deploy.sh              # Deployment script
├── .env.example           # Environment template
└── README.md              # This documentation
```

## 🤝 Contributing

### **Development Workflow**

1. **Fork** the repository
2. **Create** feature branch: `git checkout -b feature/amazing-feature`
3. **Follow** Indonesian coding standards and documentation
4. **Add** tests for new functionality
5. **Commit** changes: `git commit -m 'Add amazing Indonesian feature'`
6. **Push** to branch: `git push origin feature/amazing-feature`
7. **Open** Pull Request with detailed description

### **Code Standards**

- **Python**: Follow PEP 8 with Indonesian comments where helpful
- **Documentation**: English primary, Indonesian examples
- **Testing**: Comprehensive test coverage required
- **Security**: Security-first approach for enterprise use

## 🌏 Indonesian Market Focus

This MCP servers collection is specifically optimized for Indonesian businesses:

- **🏢 Enterprise Ready**: Tested with Indonesian corporations
- **🌐 Local Integration**: Support for Indonesian banking, payment systems
- **📱 Mobile Optimized**: Mobile-first approach for Indonesian users
- **🔒 Compliance**: Aligned with Indonesian data protection regulations
- **💰 Cost Effective**: Optimized for Indonesian cloud infrastructure costs

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support & Community

- **🐛 Issues**: [GitHub Issues](https://github.com/your-username/mcp-servers/issues)
- **💬 Discussions**: [GitHub Discussions](https://github.com/your-username/mcp-servers/discussions)
- **📧 Email**: [contact@campshure.com](mailto:contact@campshure.com)
- **🌐 Website**: [CampShure.com](https://campshure.com)

## 🌟 Acknowledgments

- **[FastMCP](https://github.com/jlowin/fastmcp)**: Excellent MCP framework
- **[National Weather Service](https://weather.gov)**: Reliable weather data
- **Indonesian Developer Community**: Feedback and contributions
- **CampShure Team**: Indonesian AI automation platform

---

**Built with ❤️ for Indonesian businesses by the CampShure team**

*Democratizing AI automation for Indonesian enterprises*