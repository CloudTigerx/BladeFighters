# DevOps & CI/CD Guide - BladeFighters Project

## 🚀 Overview

This guide covers the complete DevOps infrastructure, CI/CD pipeline, and development workflow for the BladeFighters project. Our system ensures code quality, comprehensive testing, and automated documentation management.

## 📋 CI/CD Pipeline Overview

### GitHub Actions Workflows

#### 1. **Main CI Pipeline** (`.github/workflows/ci.yml`)
- **Triggers**: Push to any branch, Pull Requests
- **Purpose**: Core code quality and testing
- **Checks**:
  - Reactor boundary protection
  - Ruff linting
  - Black formatting
  - MyPy type checking
  - Pytest test suite
  - Documentation quality check

#### 2. **Documentation Quality Check** (`.github/workflows/documentation-check.yml`)
- **Triggers**: Changes to documentation files
- **Purpose**: Documentation validation and quality assurance
- **Checks**:
  - Required documentation files presence
  - Markdown formatting validation
  - Broken link detection
  - Template compliance validation
  - Developer logs freshness
  - Coverage reporting

#### 3. **Cleanup CI** (`.github/workflows/cleanup-check.yml`)
- **Triggers**: Pull requests to `cleanup/**` branches
- **Purpose**: Maintenance and cleanup validation
- **Checks**:
  - All standard CI checks
  - Cleanup report generation
  - Artifact upload

## 🛠️ Development Workflow

### Prerequisites
```bash
# Install development dependencies
make dev-install

# Set up pre-commit hooks
make dev-setup
```

### Daily Development Commands

#### Code Quality
```bash
# Run all quality checks
make lint

# Auto-format code
make format

# Type checking
mypy .

# Linting only
ruff check .
```

#### Testing
```bash
# Quick tests
make test-quick

# Comprehensive test suite
make test-all

# Module-specific tests
make test-audio
make test-screen
make test-input

# Performance tests
make test-performance

# Coverage report
make test-coverage
```

#### Documentation
```bash
# Validate documentation
make docs-validate

# Generate missing documentation
make docs-generate

# Generate coverage report
make docs-report

# Run all documentation tasks
make docs-all
```

## 📚 Documentation Automation

### Documentation Structure

```
docs/
├── MODULE_TEMPLATE.md          # Standard module documentation template
├── README.md                   # Main project documentation
├── DEVELOPER_NOTES.md          # Developer guidelines
├── DEVELOPMENT.md              # Development workflow
├── DEVOPS_GUIDE.md            # This file
├── developer_logs/             # Daily developer logs
│   ├── README.md              # Logging guidelines
│   ├── [DEV_NAME]_log.md      # Individual developer logs
└── technical_notes/           # Technical decisions and architecture
    ├── README.md              # Notes guidelines
    └── [MODULE]_notes.md      # Module-specific technical notes
```

### Module Documentation Requirements

Each module must have:
- `README.md` - Following the standard template
- `MIGRATION_GUIDE.md` - If migrating from old systems
- `INTEGRATION_GUIDE.md` - Integration instructions
- `tests/` directory - Test suite

### Documentation Automation Tool

The `tools/documentation_automation.py` script provides:

```bash
# Validate documentation quality
python tools/documentation_automation.py validate

# Generate missing README files
python tools/documentation_automation.py generate

# Generate coverage report
python tools/documentation_automation.py report

# Run all documentation tasks
python tools/documentation_automation.py all
```

## 🔧 Configuration Files

### Markdown Link Check Configuration (`.markdown-link-check.json`)
- Ignores localhost and internal links
- Configures retry behavior for external links
- Sets appropriate timeouts

### PyProject Configuration (`pyproject.toml`)
- Black formatting settings (100 char line length)
- Ruff linting configuration
- MyPy type checking settings
- Excludes reactor files from type checking

## 🚨 Quality Gates

### Code Quality Gates
- **Linting**: All Ruff checks must pass
- **Formatting**: Black formatting check must pass
- **Type Checking**: MyPy must pass (excluding reactor files)
- **Tests**: All tests must pass
- **Reactor Protection**: Critical game logic files cannot be modified

### Documentation Quality Gates
- **Coverage**: 80%+ of modules must have README.md
- **Template Compliance**: All READMEs must follow template structure
- **Link Validation**: No broken links in documentation
- **Formatting**: All markdown files properly formatted
- **Freshness**: Developer logs updated within 7 days

## 📊 Monitoring and Reporting

### Test Results
- Test results stored in `test_results/`
- Coverage reports in `htmlcov/`
- Performance metrics in `build/`

### Documentation Reports
- Coverage reports in `build/docs/coverage_report.json`
- Missing documentation lists
- Template compliance status
- Priority action items

### CI/CD Artifacts
- Documentation coverage reports
- Cleanup analysis reports
- Test coverage reports

## 🔄 Release Process

### Pre-Release Checklist
```bash
# 1. Run comprehensive tests
make test-all

# 2. Validate documentation
make docs-validate

# 3. Check code quality
make lint

# 4. Generate coverage report
make test-coverage

# 5. Prepare release
make release-prep
```

### Release Steps
1. **Create Release Branch**: `git checkout -b release/v1.x.x`
2. **Update Version**: Update version in relevant files
3. **Run Full CI**: Ensure all checks pass
4. **Generate Documentation**: `make docs-all`
5. **Create Pull Request**: Merge to main
6. **Tag Release**: Create GitHub release with artifacts

## 🛡️ Security and Compliance

### Reactor Protection
- Critical game logic files are protected from modification
- CI pipeline enforces reactor boundary checks
- Only authorized changes allowed through specific processes

### Dependency Management
- Pinned dependency versions in `requirements-dev.txt`
- Regular security updates through Dependabot
- Vulnerability scanning in CI pipeline

## 🚀 Performance Optimization

### CI/CD Performance
- Dependency caching for faster builds
- Parallel job execution where possible
- Selective workflow triggers based on file changes
- Optimized test execution order

### Development Performance
- Fast test commands for development
- Watch mode for continuous testing
- Incremental documentation generation
- Local validation before CI

## 📞 Troubleshooting

### Common Issues

#### CI Failures
```bash
# Check local linting
make lint

# Check local tests
make test-quick

# Validate documentation
make docs-validate
```

#### Documentation Issues
```bash
# Generate missing documentation
make docs-generate

# Check template compliance
python tools/documentation_automation.py validate
```

#### Performance Issues
```bash
# Profile tests
make test-profile

# Memory profiling
make test-memory

# Performance monitoring
make perf-monitor
```

### Emergency Procedures
```bash
# Emergency cleanup
make emergency-clean

# Reset development environment
make dev-setup
```

## 📈 Metrics and KPIs

### Code Quality Metrics
- Test coverage percentage
- Linting error count
- Type checking coverage
- Documentation coverage

### Performance Metrics
- Test execution time
- Build duration
- Documentation generation time
- CI pipeline efficiency

### Team Productivity Metrics
- Documentation freshness
- Module completion status
- Integration guide coverage
- Developer log activity

## 🔮 Future Enhancements

### Planned Improvements
- Automated dependency updates
- Enhanced security scanning
- Performance regression detection
- Advanced documentation analytics
- Automated release notes generation

### Monitoring Enhancements
- Real-time CI/CD metrics dashboard
- Automated performance regression alerts
- Documentation quality scoring
- Team productivity insights

---

## 📞 Support and Resources

### Documentation Specialist
- **GitHub Issues**: For documentation gaps and suggestions
- **GitHub Discussions**: For questions and clarifications
- **Developer Logs**: For ongoing progress updates

### DevOps Team
- **CI/CD Issues**: Report pipeline problems
- **Performance Issues**: Report slow builds or tests
- **Security Concerns**: Report security vulnerabilities

### Quick Reference
- **Make Commands**: See `make help` for all available commands
- **CI Status**: Check GitHub Actions tab
- **Documentation**: Check `docs/` directory
- **Module Status**: Run `make docs-report` for current status

---

*Last updated: 2024-01-15*
*Maintained by: DevOps Team*
