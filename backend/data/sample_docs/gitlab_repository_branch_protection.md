# GitLab Repository Branch Protection and CODEOWNERS Documentation

Source URL: https://docs.gitlab.com/ee/user/project/protected_branches.html

## Protected Branches Overview
Protected branches restrict who can push code to, merge into, or delete critical branches (such as `main` or `release/*`).

### Configuring Protected Branches
To protect a branch in GitLab UI:
1. Go to **Settings > Repository**.
2. Expand **Protected branches**.
3. Select **Protect a branch**.
4. Configure options:
   - **Branch**: Select branch name or wildcard pattern (e.g., `main` or `stable-*`).
   - **Allowed to merge**: Choose roles allowed to merge MRs into the branch (Developers, Maintainers, or specific users).
   - **Allowed to push**: Choose roles allowed to push directly (Maintainers, No one, etc.).
   - **Require approval from Code Owners**: Toggle ON to mandate CODEOWNERS review.
5. Select **Protect**.

## CODEOWNERS Syntax & File Rules
The `CODEOWNERS` file specifies developers or teams responsible for reviewing changes to specific files in the repository.

### Placement Locations
GitLab checks for CODEOWNERS files in three valid repository locations:
1. `CODEOWNERS` (root directory)
2. `docs/CODEOWNERS`
3. `.gitlab/CODEOWNERS`

### CODEOWNERS Syntax Example
```gitignore
# Default owner for everything in repository
* @default-maintainer-user

# JavaScript frontend files owned by frontend team
*.js @org/frontend-team
*.tsx @org/frontend-team

# Documentation files owned by docs team
/docs/ @docs-team-lead @tech-writer

# Infrastructure code requires security team review
/terraform/ @security-lead
```

## Push Rules and Git LFS
- **Push Rules**: System rules restricting commit patterns, restricting commit author emails to company domain, or blocking files larger than specified size limits.
- **Git LFS (Large File Storage)**: Replaces large files (video, audio, datasets, zip archives) with pointer text files in Git while storing binary payloads on GitLab server (`git lfs track "*.zip"`).
