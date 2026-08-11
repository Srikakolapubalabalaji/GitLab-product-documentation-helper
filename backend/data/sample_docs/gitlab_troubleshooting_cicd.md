# GitLab CI/CD Troubleshooting and Error Resolution Guide

Source URL: https://docs.gitlab.com/ee/ci/troubleshooting.html

## Common CI/CD Errors, Root Causes, and Solutions

### 1. Job stuck! "This job is stuck because the project doesn't have any runners online assigned to it."
- **Root Cause**: No active runner is available that matches the `tags:` specified in the job, or shared runners are disabled for the project.
- **Resolution**:
  1. Check **Settings > CI/CD > Runners** to ensure runners are enabled and online.
  2. Verify that the job `tags:` in `.gitlab-ci.yml` match the runner tags (e.g. `tags: [docker, linux]`).
  3. If using untagged runners, ensure the runner setting **"Run untagged jobs"** is enabled in runner config.

### 2. Docker in Docker (dind) Connection Refused (`Cannot connect to the Docker daemon`)
- **Root Cause**: The runner container cannot communicate with the Docker daemon background service.
- **Resolution**: Ensure `privileged = true` is enabled in `config.toml` and `DOCKER_TLS_CERTDIR: ""` or Docker TLS environment variables are set in `.gitlab-ci.yml`:
  ```yaml
  variables:
    DOCKER_HOST: tcp://docker:2375
    DOCKER_TLS_CERTDIR: ""
  services:
    - docker:24.0.5-dind
  ```

### 3. Masked CI/CD Variable Failure (`Variable is invalid: value must be base64`)
- **Root Cause**: Masked variables must meet strict regex requirements (must be at least 8 characters long, contain only alphanumeric characters or `+`, `/`, `=`, `@`, `:`, `.`, `-`, `_`).
- **Resolution**: Base64 encode complex secret strings before saving in **Settings > CI/CD > Variables**, and decode them inside the job script (`echo "$MY_SECRET" | base64 -d`).

### 4. `CI_JOB_TOKEN` Unauthorized / Permission Denied across Projects
- **Root Cause**: Job token scope restrictions prevent one project pipeline from accessing another project's API or container registry.
- **Resolution**: In target project settings, navigate to **Settings > CI/CD > Job Token Permissions** and authorize access for the calling project.
