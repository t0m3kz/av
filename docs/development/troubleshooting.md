# CI/CD Troubleshooting Guide

## Quick Diagnostics

### Pipeline Status Check
```bash
# Check current workflow status
gh workflow list

# View recent runs
gh run list --limit 10

# Get details of a specific run
gh run view <run-id>
```

### Local Pipeline Simulation
```bash
# Install act to run GitHub Actions locally
# https://github.com/nektos/act
curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash

# Run CI workflow locally
act push

# Run specific job
act -j test

# Run with specific event
act pull_request
```

## Common Issues and Solutions

### 1. Test Failures

#### Symptom: Tests fail in CI but pass locally
**Possible Causes:**
- Environment differences
- Missing dependencies
- Timing issues
- Platform-specific behavior

**Solutions:**
```bash
# Reproduce locally with same Python version
pyenv install 3.10.0
pyenv local 3.10.0

# Install exact dependencies from lockfile
uv sync --frozen

# Run tests with same parameters as CI
uv run pytest tests/ -v --tb=short --cov=spatium --timeout=60
```

#### Symptom: Intermittent test failures
**Possible Causes:**
- Race conditions
- Network dependencies
- Resource constraints

**Solutions:**
```bash
# Run tests multiple times to identify flaky tests
for i in {1..10}; do uv run pytest tests/; done

# Run with increased timeout
uv run pytest tests/ --timeout=120

# Run tests in parallel to stress test
uv run pytest tests/ -n auto
```

### 2. Build Failures

#### Symptom: Package build fails
**Possible Causes:**
- Missing build dependencies
- Invalid package configuration
- File permission issues

**Solutions:**
```bash
# Check package configuration
python -m build --check

# Validate pyproject.toml
uv run python -c "import tomllib; tomllib.load(open('pyproject.toml', 'rb'))"

# Build locally
python -m build
twine check dist/*
```

#### Symptom: Docker build fails
**Possible Causes:**
- Missing Docker context files
- Base image issues
- Layer size problems

**Solutions:**
```bash
# Build Docker image locally
docker build -t spatium:test .

# Check Dockerfile syntax
docker run --rm -i hadolint/hadolint < Dockerfile

# Analyze image size
docker images spatium:test
docker history spatium:test
```

### 3. Security Scan Issues

#### Symptom: Security vulnerabilities detected
**Investigation:**
```bash
# Run security scan locally
uv add --dev safety bandit

# Check for known vulnerabilities
uv run safety check --json > security-report.json

# Analyze code for security issues
uv run bandit -r spatium/ -f json > bandit-report.json

# Review specific issues
cat security-report.json | jq '.[] | select(.vulnerability.severity == "high")'
```

**Resolution:**
1. Update vulnerable dependencies
2. Add security exceptions if false positives
3. Implement secure coding practices

### 4. Coverage Issues

#### Symptom: Coverage below threshold
**Investigation:**
```bash
# Generate detailed coverage report
uv run pytest tests/ --cov=spatium --cov-report=html

# Open coverage report
open htmlcov/index.html

# Find uncovered lines
uv run pytest tests/ --cov=spatium --cov-report=term-missing
```

**Resolution:**
1. Add tests for uncovered code
2. Remove dead code
3. Add coverage pragmas for unreachable code

### 5. Dependency Issues

#### Symptom: Dependency conflicts
**Investigation:**
```bash
# Check dependency tree
uv add --dev pipdeptree
uv run pipdeptree

# Identify conflicts
uv run pipdeptree --warn conflict

# Check for outdated packages
uv pip list --outdated
```

**Resolution:**
```bash
# Update dependencies
uv lock --upgrade

# Resolve specific conflicts
uv add package==specific-version

# Pin problematic dependencies
echo "problematic-package==1.0.0" >> pyproject.toml
```

## Workflow-Specific Troubleshooting

### CI Workflow Issues

#### Lint failures
```bash
# Fix formatting issues
uv run ruff format .

# Fix linting issues automatically
uv run ruff check . --fix

# Check specific files
uv run ruff check spatium/main.py
```

#### Type checking failures
```bash
# Run mypy locally
uv run mypy spatium/

# Fix specific type issues
uv run mypy spatium/main.py --show-error-codes

# Add type ignores if needed
# type: ignore[error-code]
```

### Release Workflow Issues

#### Version conflicts
```bash
# Check existing tags
git tag -l

# Delete problematic tag (if safe)
git tag -d v1.0.0
git push origin :refs/tags/v1.0.0

# Create new tag
git tag v1.0.1
git push origin v1.0.1
```

#### Build artifacts issues
```bash
# Clean previous builds
rm -rf dist/ build/ *.egg-info/

# Rebuild from scratch
python -m build

# Verify package contents
tar -tzf dist/*.tar.gz
```

### Nightly Build Issues

#### Performance regression
```bash
# Run benchmarks locally
uv add --dev pytest-benchmark
uv run pytest tests/performance/ --benchmark-only

# Compare with previous results
uv run pytest tests/performance/ --benchmark-compare=previous_results.json
```

#### External service failures
```bash
# Check service availability
curl -I https://api.example.com/health

# Mock external services in tests
# Use @patch decorators for network calls
```

## Advanced Debugging

### GitHub Actions Debugging

#### Enable debug logging
```yaml
env:
  ACTIONS_STEP_DEBUG: true
  ACTIONS_RUNNER_DEBUG: true
```

#### SSH into runner
```yaml
- name: Setup tmate session
  uses: mxschmitt/action-tmate@v3
  if: failure()
```

### Local Environment Setup

#### Exact CI environment
```bash
# Use same Ubuntu version
docker run -it ubuntu:22.04 bash

# Install same Python version
apt-get update && apt-get install -y python3.10 python3-pip

# Install uv
pip install uv

# Clone and test
git clone <repo>
cd <repo>
uv sync
uv run pytest tests/
```

### Log Analysis

#### Parse workflow logs
```bash
# Download logs using GitHub CLI
gh run download <run-id>

# Extract specific job logs
unzip <run-id>.zip
cat "job-name/step-name.txt"

# Search for errors
grep -i error *.txt
grep -i failed *.txt
```

### Performance Analysis

#### Workflow timing
```bash
# Analyze workflow duration
gh run list --json | jq '.[] | {workflow: .name, duration: .updated_at, status: .conclusion}'

# Compare job times
gh run view <run-id> --json | jq '.jobs[] | {name: .name, duration: .conclusion}'
```

#### Resource usage
```yaml
# Add resource monitoring to workflows
- name: Monitor resources
  run: |
    echo "CPU info:"
    nproc
    cat /proc/cpuinfo | grep "model name" | head -1
    echo "Memory info:"
    free -h
    echo "Disk space:"
    df -h
```

## Prevention Strategies

### Pre-commit Hooks
```bash
# Install pre-commit
pip install pre-commit

# Set up hooks
pre-commit install

# Run on all files
pre-commit run --all-files
```

### Regular Maintenance

#### Weekly tasks
```bash
# Update dependencies
uv lock --upgrade

# Run security audit
uv run safety check

# Clean up old artifacts
gh run list --status completed --limit 100 | grep -v "success" | xargs -I {} gh run delete {}
```

#### Monthly tasks
```bash
# Review pipeline performance
gh workflow list --json | jq '.[] | {name: .name, state: .state}'

# Update GitHub Actions
# Check .github/workflows/*.yml for version updates

# Review security policies
# Update .github/dependabot.yml
```

## Emergency Procedures

### Critical Pipeline Failure

1. **Immediate Actions:**
   ```bash
   # Disable failing workflow
   gh workflow disable <workflow-name>

   # Create hotfix branch
   git checkout -b hotfix/pipeline-fix
   ```

2. **Investigation:**
   ```bash
   # Get recent logs
   gh run list --limit 5
   gh run view <failed-run-id> --log
   ```

3. **Quick Fix:**
   ```bash
   # Skip problematic step temporarily
   if: false  # Add to problematic step

   # Or reduce test scope
   uv run pytest tests/unit/  # Skip integration tests
   ```

4. **Recovery:**
   ```bash
   # Re-enable workflow
   gh workflow enable <workflow-name>

   # Test fix
   git push origin hotfix/pipeline-fix
   ```

### Security Incident

1. **Immediate Response:**
   ```bash
   # Disable all workflows
   gh workflow disable-all

   # Revoke tokens if compromised
   # Go to Settings > Secrets and variables > Actions
   ```

2. **Investigation:**
   ```bash
   # Check workflow logs for suspicious activity
   gh run list --limit 50 | grep -E "(failed|cancelled)"

   # Review recent commits
   git log --oneline -10
   ```

3. **Recovery:**
   ```bash
   # Update all secrets
   # Regenerate API tokens
   # Re-enable workflows one by one
   ```

## Getting Help

### Internal Resources
- CI/CD documentation: `docs/development/cicd.md`
- Team chat: #dev-ops channel
- Issue tracker: GitHub Issues with `ci/cd` label

### External Resources
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [GitHub Community Forum](https://github.community/)
- [uv Documentation](https://docs.astral.sh/uv/)

### Support Contacts
- **Infrastructure Issues**: DevOps team
- **Security Issues**: Security team
- **Emergency**: On-call rotation
