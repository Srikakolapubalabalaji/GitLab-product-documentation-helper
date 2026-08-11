# GitLab Administration and Infrastructure Troubleshooting Documentation

Source URL: https://docs.gitlab.com/ee/administration/troubleshooting/

## GitLab Omnibus & Architecture Components
Omnibus GitLab packages all necessary services for running self-managed GitLab:
- **GitLab Rails (Puma / Sidekiq)**: Application server handling UI requests, background job workers.
- **Gitaly**: High-performance RPC service providing disk access to Git repositories.
- **Nginx**: Web server reverse proxy.
- **PostgreSQL**: Relational database storing metadata, users, issues, MRs.
- **Redis**: In-memory cache and background job queue manager.

## Key Admin CLI Commands (`gitlab-ctl`)
```bash
# Check status of all system services
sudo gitlab-ctl status

# Reconfigure GitLab after changing /etc/gitlab/gitlab.rb
sudo gitlab-ctl reconfigure

# Restart all services (or specific service e.g. sudo gitlab-ctl restart gitaly)
sudo gitlab-ctl restart

# Tail log output across all services
sudo gitlab-ctl tail
```

## System Log Locations
When troubleshooting administrative issues, inspect logs in `/var/log/gitlab/`:
- **Gitaly RPC Logs**: `/var/log/gitlab/gitaly/current`
- **GitLab Rails Production Logs**: `/var/log/gitlab/gitlab-rails/production.log`
- **Nginx Error Logs**: `/var/log/gitlab/nginx/gitlab_error.log`
- **Sidekiq Background Logs**: `/var/log/gitlab/gitlab-rails/sidekiq.log`

## Backup and Restore Operations
- **Create Full Backup**:
  ```bash
  sudo gitlab-backup create
  ```
  Backups are saved to `/var/opt/gitlab/backups/` as TAR archives.
- **Restore Backup**:
  ```bash
  sudo gitlab-ctl stop puma
  sudo gitlab-ctl stop sidekiq
  sudo gitlab-backup restore BACKUP=1700000000_2026_01_01_16.0.0
  sudo gitlab-ctl reconfigure
  sudo gitlab-ctl restart
  ```
