# GitLab CI/CD Pipelines and Workflows Documentation

Source URL: https://docs.gitlab.com/ee/ci/pipelines/

## Overview of GitLab CI/CD
GitLab CI/CD is a built-in continuous integration, continuous delivery, and continuous deployment engine configured via a single YAML configuration file named `.gitlab-ci.yml` placed in the root of the repository.

### Essential `.gitlab-ci.yml` Structure
```yaml
stages:
  - build
  - test
  - deploy

default:
  image: node:18-alpine

build_job:
  stage: build
  script:
    - npm ci
    - npm run build
  artifacts:
    paths:
      - dist/
    expire_in: 1 week

test_job:
  stage: test
  script:
    - npm run test
  rules:
    - if: '$CI_COMMIT_BRANCH == "main"'
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'

deploy_job:
  stage: deploy
  script:
    - echo "Deploying to production server..."
  environment:
    name: production
    url: https://example.com
  rules:
    - if: '$CI_COMMIT_BRANCH == "main"'
      when: manual
```

## Controlling Job Execution with `rules`
The `rules` keyword determines whether a job runs or is skipped:
- `if`: Evaluates logical conditional expressions (e.g. `$CI_COMMIT_BRANCH == "main"`).
- `changes`: Checks if specific paths/files changed in the commit/MR (e.g. `changes: ["src/**/*"]`).
- `exists`: Checks if specific files exist in the repository (e.g. `exists: ["Dockerfile"]`).
- `when`: Specifies execution condition (`always`, `never`, `on_success`, `on_failure`, `manual`).

## CI/CD Pipeline Architectures
1. **Basic Sequential Pipelines**: Jobs run sequentially stage by stage (`build` -> `test` -> `deploy`).
2. **Directed Acyclic Graph (DAG) Pipelines**: Uses the `needs:` keyword to allow jobs to start immediately after their dependencies complete without waiting for the entire stage to finish.
   ```yaml
   test_backend:
     stage: test
     needs: ["build_backend"]
     script: pytest
   ```
3. **Parent-Child Pipelines**: Allows a parent `.gitlab-ci.yml` to trigger downstream child pipeline configurations (`trigger: include: child-pipeline.yml`).
4. **Multi-Project Pipelines**: Triggers pipelines in external downstream projects (`trigger: project: my-group/other-project`).
5. **Matrix Builds**: Runs a job multiple times with different variable combinations using `parallel: matrix`.
   ```yaml
   test_matrix:
     script: npm test
     parallel:
       matrix:
         - NODE_VERSION: ["16", "18", "20"]
   ```

## Predefined CI/CD Variables
GitLab automatically injects predefined environment variables into every job execution context:
- `$CI_COMMIT_SHA`: Full commit hash being tested.
- `$CI_COMMIT_BRANCH`: Branch name for branch pipelines.
- `$CI_JOB_TOKEN`: Short-lived authentication token for pulling containers or calling GitLab APIs within the job.
- `$CI_PIPELINE_SOURCE`: Source trigger (`push`, `merge_request_event`, `schedule`, `web`, `trigger`).
