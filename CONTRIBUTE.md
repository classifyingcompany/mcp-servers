# Contributing to MCP Servers Collection

🙏 **Terima kasih** for your interest in contributing to the MCP Servers Collection! This project is built by the community, for the community, with a special focus on empowering Indonesian businesses and developers.

## 📋 Table of Contents

- [Code of Conduct](#-code-of-conduct)
- [Getting Started](#-getting-started)
- [Development Setup](#️-development-setup)
- [Contributing Guidelines](#-contributing-guidelines)
- [Types of Contributions](#-types-of-contributions)
- [Indonesian Market Focus](#-indonesian-market-focus)
- [Pull Request Process](#-pull-request-process)
- [Issue Guidelines](#-issue-guidelines)
- [Coding Standards](#-coding-standards)
- [Testing Requirements](#-testing-requirements)
- [Documentation](#-documentation)
- [Community](#-community)

## 📜 Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). By participating, you agree to uphold this code. Please report unacceptable behavior to [conduct@campshure.com](mailto:conduct@campshure.com).

### Our Values
- **🤝 Inclusivity**: Welcome developers from all backgrounds
- **🌏 Indonesian Focus**: Prioritize Indonesian market needs
- **🎓 Learning**: Support newcomers and knowledge sharing
- **💼 Professional**: Maintain enterprise-grade quality
- **🚀 Innovation**: Embrace new ideas and technologies

## 🚀 Getting Started

### Prerequisites

```bash
# Required tools
- Python 3.11+
- Git 2.30+
- Docker 20.10+
- Docker Compose 2.0+

# Recommended tools
- VS Code with Python extension
- GitHub CLI
- Postman (for API testing)
```

### Quick Start

```bash
# 1. Fork the repository on GitHub
# 2. Clone your fork
git clone https://github.com/classifyingcompany/mcp-servers.git
cd mcp-servers

# 3. Add upstream remote
git remote add upstream https://github.com/classifyingcompany/mcp-servers.git

# 4. Create development environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate     # Windows

# 5. Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 6. Run tests to ensure everything works
python -m pytest tests/ -v

# 7. Start coding! 🎉
```

## 🛠️ Development Setup

### Environment Configuration

Create a local development environment:

```bash
# Copy environment template
cp .env.example .env.dev

# Edit with your development settings
nano .env.dev
```

```bash
# Development Environment (.env.dev)
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=debug

# Indonesian Development Settings
DEFAULT_TIMEZONE=Asia/Jakarta
DEFAULT_LANGUAGE=id
BABEL_LOCALE=id_ID

# Test API Keys (use test/sandbox keys)
GMAIL_CLIENT_ID=your-test-client-id
SLACK_BOT_TOKEN=xoxb-test-token
GITHUB_TOKEN=ghp_test_token
PERPLEXITY_API_KEY=test-api-key
```

### Development Tools

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Pre-commit hooks for code quality
pre-commit install

# Code formatting
black .
isort .

# Linting
flake8 .
mypy .

# Security check
bandit -r .
```

## 🤝 Contributing Guidelines

### What We're Looking For

**🔥 High Priority Contributions:**
- New MCP server integrations (especially Indonesian services)
- Indonesian language support improvements
- Performance optimizations
- Security enhancements
- Documentation improvements
- Test coverage expansion

**🌟 Indonesian Market Contributions:**
- Integration with Indonesian payment gateways (GoPay, OVO, DANA)
- Indonesian banking API integrations
- Local business directory APIs
- Indonesian government API integrations
- Bahasa Indonesia NLP improvements
- Indonesian timezone and calendar optimizations

**💡 Innovation Areas:**
- AI/ML model integrations
- Microservices architecture improvements
- Monitoring and observability
- Mobile-first optimizations
- Cloud-native enhancements

### Contribution Types Welcome

- 🐛 **Bug Fixes**: Fix existing issues
- ✨ **New Features**: Add new MCP servers or functionality
- 📚 **Documentation**: Improve docs, tutorials, examples
- 🧪 **Tests**: Add or improve test coverage
- 🎨 **UI/UX**: Improve user experience (especially for Indonesian users)
- 🔧 **DevOps**: CI/CD, deployment, monitoring improvements
- 🌐 **Localization**: Indonesian language support
- 📈 **Performance**: Optimization and scaling improvements

## 🇮🇩 Indonesian Market Focus

This project prioritizes Indonesian business needs. When contributing, consider:

### **Business Context**
- **UMKM Support**: Small and medium enterprises (Usaha Mikro Kecil Menengah)
- **Digital Transformation**: Help traditional businesses adopt AI
- **Local Regulations**: Comply with Indonesian data protection laws
- **Cost Efficiency**: Optimize for Indonesian infrastructure costs

### **Technical Considerations**
- **Timezone**: Default to `Asia/Jakarta` (WIB)
- **Language**: Support Indonesian (`id`) and English (`en`)
- **Currency**: IDR handling in financial features
- **Mobile-First**: Optimize for mobile usage patterns
- **Connectivity**: Handle slower internet connections gracefully

### **Cultural Sensitivity**
- Use Indonesian examples in documentation when relevant
- Respect local business practices and customs
- Consider Islamic calendar for scheduling features
- Support Indonesian number/date formatting

## 📝 Pull Request Process

### Branch Naming

```bash
# Feature branches
feature/indonesian-payment-integration
feature/gmail-bahasa-indonesia-support

# Bug fixes
bugfix/filesystem-permission-issue
bugfix/calendar-timezone-jakarta

# Documentation
docs/contributing-guide-indonesian
docs/api-documentation-update

# Hotfixes
hotfix/security-vulnerability-patch
```

### PR Template

When creating a PR, include:

```markdown
## Description
Brief description of changes (in English, Indonesian examples welcome)

## Type of Change
- [ ] 🐛 Bug fix
- [ ] ✨ New feature
- [ ] 📚 Documentation update
- [ ] 🇮🇩 Indonesian market enhancement
- [ ] 🔧 DevOps/Infrastructure
- [ ] ⚡ Performance improvement

## Indonesian Market Impact
- [ ] Improves Indonesian business workflows
- [ ] Adds Indonesian language support
- [ ] Integrates with Indonesian services
- [ ] Optimizes for Indonesian infrastructure
- [ ] N/A - Not Indonesia-specific

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests pass
- [ ] Manual testing completed
- [ ] Indonesian timezone testing (if applicable)

## Documentation
- [ ] Code comments added
- [ ] API documentation updated
- [ ] README updated if needed
- [ ] Indonesian examples provided (if applicable)

## Breaking Changes
List any breaking changes and migration steps

## Screenshots/Examples
Add screenshots or code examples, especially for Indonesian features
```

### Review Process

1. **Automated Checks**: All CI/CD checks must pass
2. **Code Review**: At least one maintainer approval required
3. **Indonesian Focus Review**: Indonesian-specific features get additional review
4. **Documentation Review**: Ensure docs are clear for both English and Indonesian developers
5. **Security Review**: Security-sensitive changes get extra scrutiny

## 🐛 Issue Guidelines

### Issue Templates

We provide templates for:
- 🐛 **Bug Reports**: Reproducible issues
- ✨ **Feature Requests**: New functionality proposals
- 🇮🇩 **Indonesian Enhancement**: Indonesia-specific improvements
- 📚 **Documentation**: Documentation improvements
- ❓ **Questions**: General questions and support

### Good Issue Examples

**Bug Report:**
```markdown
## Bug: Gmail Server Tidak Support Indonesian Characters

**Environment:**
- OS: Ubuntu 22.04
- Python: 3.11.5
- Timezone: Asia/Jakarta

**Description:**
Email dengan karakter Indonesia (ñ, ç) tidak ter-encode dengan benar.

**Steps to Reproduce:**
1. Send email with subject: "Selamat pagi, apa kabar?"
2. Check received email
3. Characters appear as �

**Expected:** Indonesian characters display correctly
**Actual:** Characters show as �
```

**Feature Request:**
```markdown
## Feature: Integrasi dengan API Bank Indonesia

**Problem:**
Indonesian businesses need real-time exchange rates from Bank Indonesia.

**Proposed Solution:**
New MCP server for Bank Indonesia API integration:
- Real-time IDR exchange rates
- Economic indicators
- Inflation data
- Indonesian market holidays

**Indonesian Business Value:**
- UMKM can get accurate exchange rates
- Fintech apps can integrate easily
- Economic analysis for Indonesian market
```

## 💻 Coding Standards

### Python Style Guide

```python
# Follow PEP 8 with these additions:

# 1. Indonesian-friendly variable names (when appropriate)
waktu_jakarta = datetime.now(timezone('Asia/Jakarta'))
mata_uang_idr = 'IDR'
alamat_indonesia = get_indonesian_address()

# 2. Comprehensive docstrings with Indonesian examples
async def kirim_email(penerima: List[str], subjek: str, isi: str) -> str:
    """Send email through Gmail integration.
    
    Optimized for Indonesian business communication patterns.
    
    Args:
        penerima: List of recipient emails
        subjek: Email subject (supports Indonesian characters)
        isi: Email body (HTML supported, Indonesian formatting)
    
    Returns:
        Message ID or error description
        
    Example:
        >>> await kirim_email(
        ...     penerima=["partner@perusahaan.co.id"],
        ...     subjek="Proposal Kerjasama UMKM",
        ...     isi="<p>Selamat pagi,<br>Berikut proposal...</p>"
        ... )
        'msg_12345'
    """

# 3. Error handling with Indonesian context
try:
    result = await process_indonesian_business_data()
except IndonesianAPIException as e:
    logger.error(f"Gagal memproses data bisnis Indonesia: {e}")
    return "Maaf, terjadi kesalahan saat memproses data"

# 4. Configuration with Indonesian defaults
INDONESIAN_BUSINESS_HOURS = {
    'start': 9,  # 09:00 WIB
    'end': 17,   # 17:00 WIB
    'timezone': 'Asia/Jakarta',
    'weekend': ['saturday', 'sunday'],
    'holidays': INDONESIAN_NATIONAL_HOLIDAYS
}
```

### Code Quality Requirements

```bash
# All code must pass these checks:
black --check .                 # Code formatting
isort --check-only .            # Import sorting  
flake8 .                       # Linting
mypy .                         # Type checking
bandit -r .                    # Security scanning
pytest tests/ --cov=.          # Test coverage > 80%
```

### API Design Standards

```python
# RESTful API design for Indonesian market
@mcp.tool()
async def get_indonesian_holidays(
    year: int = None,
    include_religious: bool = True,
    include_regional: bool = False,
    format: str = "iso"  # iso, indonesian, custom
) -> str:
    """Get Indonesian national and religious holidays.
    
    Includes both national holidays and major religious observances
    relevant to Indonesian business operations.
    """
```

## 🧪 Testing Requirements

### Test Coverage Standards

- **Minimum Coverage**: 80% overall
- **New Features**: 90% coverage required
- **Critical Paths**: 100% coverage (authentication, security, data handling)
- **Indonesian Features**: Include cultural and timezone edge cases

### Test Categories

```python
# 1. Unit Tests
class TestIndonesianCalendarServer:
    """Test Indonesian-specific calendar functionality."""
    
    @pytest.mark.asyncio
    async def test_jakarta_timezone_handling(self):
        """Test proper Jakarta timezone handling."""
        
    @pytest.mark.asyncio  
    async def test_indonesian_holidays_integration(self):
        """Test Indonesian national holidays are respected."""

# 2. Integration Tests
class TestIndonesianBusinessWorkflows:
    """Test complete Indonesian business workflows."""
    
    @pytest.mark.asyncio
    async def test_umkm_automation_flow(self):
        """Test end-to-end UMKM business automation."""

# 3. Performance Tests
class TestIndonesianInfrastructure:
    """Test performance on Indonesian infrastructure."""
    
    @pytest.mark.asyncio
    async def test_slow_connection_handling(self):
        """Test graceful degradation on slow connections."""
```

### Running Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run Indonesian-specific tests
python -m pytest tests/ -k "indonesian" -v

# Run with coverage
python -m pytest tests/ --cov=. --cov-report=html

# Run performance tests
python -m pytest tests/test_performance.py --benchmark-only

# Run integration tests
python -m pytest tests/test_integration/ -v
```

## 📚 Documentation

### Documentation Standards

1. **Code Documentation**: Every function/class has comprehensive docstrings
2. **API Documentation**: OpenAPI/Swagger specs for all endpoints
3. **User Guides**: Step-by-step guides for Indonesian business use cases
4. **Developer Guides**: Technical documentation for contributors
5. **Indonesian Examples**: Local business scenarios in documentation

### Documentation Structure

```
docs/
├── api/                    # API documentation
├── guides/                 # User guides
│   ├── english/           # English documentation
│   └── indonesian/        # Indonesian documentation
├── developers/            # Developer documentation
├── examples/              # Code examples
│   ├── umkm/             # UMKM business examples
│   ├── fintech/          # Indonesian fintech examples
│   └── ecommerce/        # E-commerce examples
└── deployment/           # Deployment guides
```

### Writing Guidelines

```markdown
# Good Documentation Example

## Gmail Server - Indonesian Business Usage

### Kirim Email Otomatis untuk UMKM

This example shows how to automate email sending for Indonesian small businesses:

```python
# Send payment reminder in Indonesian
await gmail_server.send_email(
    to=["customer@perusahaan.co.id"],
    subject="Pengingat Pembayaran - Invoice #INV-001",
    body="""
    <p>Yth. Bapak/Ibu,</p>
    <p>Kami ingin mengingatkan bahwa pembayaran invoice #INV-001 
    telah jatuh tempo pada tanggal 15 Januari 2024.</p>
    <p>Silakan melakukan pembayaran melalui:</p>
    <ul>
        <li>Transfer Bank: BCA 1234567890</li>
        <li>E-Wallet: GoPay/OVO 081234567890</li>
    </ul>
    <p>Terima kasih atas perhatiannya.</p>
    """
)
\```

**Benefits for Indonesian Businesses:**
- Automated Indonesian language communication
- Support for local payment methods
- Jakarta timezone handling
- Cultural appropriate formatting
\```
```

## 👥 Community

### Communication Channels

- **🐛 Issues**: [GitHub Issues](https://github.com/classifyingcompany/mcp-servers/issues)
- **💬 Discussions**: [GitHub Discussions](https://github.com/classifyingcompany/mcp-servers/discussions)
- **📧 Email**: [contribute@campshure.com](mailto:wan@campshure.com)
- **🌐 Website**: [CampShure.com](https://campshure.com)
- **📱 Telegram**: [@MCPServersID](https://t.me/MCPServersID) (Indonesian community)

### Indonesian Developer Community

**🇮🇩 Indonesian Contributors Welcome!**

We especially encourage contributions from Indonesian developers who understand local business needs:

- **Startup Founders**: Share your automation pain points
- **Enterprise Developers**: Contribute enterprise-grade features
- **UMKM Supporters**: Help small businesses with automation
- **Students**: Learn by contributing to real-world projects
- **Freelancers**: Build your portfolio with impactful contributions

### Recognition

**🏆 Contributor Recognition:**
- Monthly contributor highlights
- Indonesian developer spotlights
- CampShure platform credits for significant contributions
- Recommendation letters for outstanding contributors
- Speaking opportunities at Indonesian tech events

### Mentorship Program

**🎓 For New Contributors:**
- Paired with experienced Indonesian developers
- Monthly virtual meetups
- Code review guidance
- Career development support

**🚀 For Experienced Contributors:**
- Mentor new Indonesian developers
- Lead feature development
- Technical writing opportunities
- Conference speaking invitations

## 🤝 Getting Help

### First-Time Contributors

1. **Start Small**: Look for `good-first-issue` labels
2. **Ask Questions**: Use GitHub Discussions for questions
3. **Indonesian Support**: Get help in Bahasa Indonesia on our Telegram
4. **Pair Programming**: Available for complex features

### Code Review Support

- **English/Indonesian**: Reviews available in both languages
- **Technical Guidance**: Architecture and design help
- **Indonesian Context**: Business logic validation for local market
- **Performance Tips**: Optimization for Indonesian infrastructure

### Resources for Indonesian Developers

- **[Indonesian API Directory](docs/indonesian-apis.md)**: List of Indonesian business APIs
- **[UMKM Automation Guide](docs/umkm-guide.md)**: Small business automation patterns
- **[Indonesian Compliance Guide](docs/compliance-id.md)**: Local regulation compliance
- **[Performance Guide](docs/performance-indonesia.md)**: Optimization for Indonesian infrastructure

---

## 🙏 Thank You!

Your contributions make this project better for the entire Indonesian developer community. Whether you're fixing a small bug, adding Indonesian language support, or building the next game-changing MCP server integration, every contribution matters.

**Terima kasih sudah berkontribusi untuk kemajuan teknologi Indonesia!** 🇮🇩

---

**Questions?** Reach out to us at [wan@campshure.com](mailto:wan@campshure.com) or join our [Telegram community](https://t.me/MCPServersID).

**Happy Coding!** 🚀