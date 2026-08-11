# GitLab Access Control, Roles, and Authentication Tokens

Source URL: https://docs.gitlab.com/ee/user/permissions.html

## GitLab User Roles & Permissions Matrix
GitLab enforces Role-Based Access Control (RBAC) across groups and projects. Each role grants cumulative permissions:

| Role | Key Capabilities & Permissions | Clone / Push Code | CI/CD Variable Access | Add Members |
| :--- | :--- | :--- | :--- | :--- |
| **Guest** | View public/private projects, create issues, leave comments. | No | No | No |
| **Reporter** | View code, clone repository, download artifacts, manage issue labels. | Read Only | No | No |
| **Developer** | Create feature branches, push code, create merge requests, trigger CI/CD pipelines. | Read & Push | No Masked/Protected Edit | No |
| **Maintainer** | Protect/unprotect branches, manage settings, set CI/CD variables, add members. | Read & Push (Protected) | Full Access | Yes |
| **Owner** | Full administrative rights over group/project, manage billing, delete project, transfer ownership. | Full Access | Full Access | Yes |

## Comprehensive Token Types Comparison

| Token Type | Scope | Lifetime | Primary Use Case | How Created / Managed |
| :--- | :--- | :--- | :--- | :--- |
| **Personal Access Token (PAT)** | User Account level | 1-365 Days | User API scripts, Git over HTTPS, CLI access on behalf of a user. | **User Profile > Access Tokens** |
| **Project Access Token** | Single Project level | 1-365 Days | Bot accounts, project-level automated scripts without user account. | **Project Settings > Access Tokens** |
| **Group Access Token** | Group & Subgroups level | 1-365 Days | Automation across multiple repositories within an organization. | **Group Settings > Access Tokens** |
| **Deploy Token** | Read-Only Repository/Registry | Custom / No Expiry | Kubernetes clusters, production servers pulling images/packages. | **Project Settings > Repository > Deploy Tokens** |
| **CI_JOB_TOKEN** | Single Job execution | Short-lived (Job duration) | Pulling dependent project artifacts or container images within CI/CD. | Predefined `$CI_JOB_TOKEN` in CI pipeline |

## Setting up SSH Keys for Git Authentication
SSH keys provide secure, passwordless authentication for Git command-line operations (`git clone`, `git push`):
1. Generate SSH key pair locally: `ssh-keygen -t ed25519 -C "user@example.com"`.
2. Copy public key: `cat ~/.ssh/id_ed25519.pub`.
3. Go to GitLab UI: **User Profile Icon > Edit Profile > SSH Keys**.
4. Paste key content, enter a descriptive title, set expiration, and select **Add key**.
