# GitLab Security, Governance, and Compliance Documentation

Source URL: https://docs.gitlab.com/ee/user/application_security/

## Application Security Scanners Overview
GitLab provides comprehensive built-in security analyzers integrated directly into CI/CD pipelines to detect vulnerabilities early in the software development lifecycle (DevSecOps).

### Security Scanning Tools Comparison
| Scanner | Full Name | Purpose & Detection Focus | When Executed |
| :--- | :--- | :--- | :--- |
| **SAST** | Static Application Security Testing | Analyzes source code for known security vulnerabilities and coding flaws without running the code. | Build / Test stage |
| **DAST** | Dynamic Application Security Testing | Analyzes running web applications by simulating real-world attacks to identify runtime vulnerabilities. | Review / Staging stage |
| **Secret Detection** | Secret Detection | Scans commit history and code for hardcoded credentials, API tokens, passwords, and private keys. | Commit / Test stage |
| **Container Scanning** | Container Image Scanning | Scans Docker/OCI container images for known OS and application package vulnerabilities (CVEs). | Package / Build stage |
| **Dependency Scanning** | Dependency Scanning | Scans project dependencies (e.g. npm, PyPI, Maven, Cargo) for known security vulnerabilities. | Test stage |
| **License Compliance** | License Compliance | Searches project dependencies for open-source licenses and flags non-compliant software licenses. | Test stage |

## Enabling SAST in `.gitlab-ci.yml`
To enable Static Application Security Testing (SAST), include the official CI template:
```yaml
include:
  - template: Security/SAST.gitlab-ci.yml
  - template: Security/Secret-Detection.gitlab-ci.yml
  - template: Security/Container-Scanning.gitlab-ci.yml
```

## Vulnerability Reports & Security Dashboards
- **Merge Request Security Widget**: Shows newly introduced security vulnerabilities directly in the Merge Request UI before code is merged.
- **Vulnerability Report**: Centralized dashboard listing all active vulnerabilities across the project or group. Security teams can dismiss, create issues for, or confirm vulnerabilities.
- **Scan Execution Policies**: Enforce security scan execution across all projects in a group regardless of individual `.gitlab-ci.yml` configurations.
