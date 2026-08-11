# GitLab Runners and Executors Documentation

Source URL: https://docs.gitlab.com/ee/ci/runners/

## Overview of GitLab Runner
GitLab Runner is an open-source application written in Go that processes and executes CI/CD jobs defined in `.gitlab-ci.yml`. It runs on local machines, virtual machines, Docker containers, or Kubernetes clusters.

## Runner Types Comparison
GitLab categorizes runners into three distinct scope levels based on availability:

| Runner Type | Scope | Management & Access | Use Cases |
| :--- | :--- | :--- | :--- |
| **Shared Runners** | System-wide / All projects | Managed by GitLab Administrators | General-purpose builds across all projects in instance/SaaS. |
| **Group Runners** | Group & Subgroup level | Managed by Group Owners | Organization-wide shared build pipelines and custom environments. |
| **Specific / Project Runners** | Single Project level | Managed by Project Maintainers/Owners | Specialized hardware (GPUs), sensitive production deployments, custom OS requirements. |

## Executor Architecture
The runner executor determines the isolated runtime environment in which job commands are run:
1. **Docker Executor**: Runs each job inside a clean Docker container image. Best for isolated, reproducible builds.
2. **Kubernetes Executor**: Dynamically provisions Kubernetes pods for job execution. Scales automatically for high-concurrency environments.
3. **Shell Executor**: Runs jobs directly on the host machine OS where GitLab Runner is installed. Fast, but lacks job isolation.
4. **VirtualBox / Parallels / SSH Executors**: Executes job scripts inside target virtual machines or via SSH connections to remote servers.

## Registering a GitLab Runner
To register a runner using the `gitlab-runner` binary CLI:
```bash
sudo gitlab-runner register \
  --non-interactive \
  --url "https://gitlab.com/" \
  --token "glrt-YOUR_RUNNER_AUTHENTICATION_TOKEN" \
  --executor "docker" \
  --docker-image "alpine:latest" \
  --description "production-docker-runner" \
  --tag-list "docker,linux,production"
```

## `config.toml` Configuration File
Runner behavior and concurrency limits are governed by the `config.toml` file located at `/etc/gitlab-runner/config.toml` (Linux) or `C:\ProgramData\gitlab-runner\config.toml` (Windows):
```toml
concurrent = 10
check_interval = 3

[session_server]
  session_timeout = 1800

[[runners]]
  name = "production-docker-runner"
  url = "https://gitlab.com/"
  id = 123456
  token = "glrt-YOUR_RUNNER_TOKEN"
  token_obtained_at = 2026-01-01T00:00:00Z
  token_expires_at = 0001-01-01T00:00:00Z
  executor = "docker"
  [runners.custom_build_dir]
  [runners.cache]
    MaxUploadedArchiveSize = 0
  [runners.docker]
    tls_verify = false
    image = "alpine:latest"
    privileged = false
    disable_entrypoint_overwrite = false
    oom_kill_disable = false
    disable_cache = false
    volumes = ["/cache"]
    shm_size = 0
```
