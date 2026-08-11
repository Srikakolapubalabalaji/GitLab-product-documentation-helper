# GitLab REST API and GraphQL API Documentation

Source URL: https://docs.gitlab.com/ee/api/rest/

## Overview of GitLab API
GitLab provides a comprehensive REST API (Version 4) and GraphQL API for automating project creation, issue management, pipeline triggers, user management, and administrative tasks.

## REST API Authentication Methods
All REST API requests to `https://gitlab.com/api/v4/` require authentication via HTTP Headers or query parameters:

1. **Personal / Project / Group Access Tokens**:
   Header: `PRIVATE-TOKEN: <your_access_token>`
   ```bash
   curl --header "PRIVATE-TOKEN: glpat-abcdef123456" "https://gitlab.com/api/v4/projects"
   ```
2. **OAuth 2.0 Tokens**:
   Header: `Authorization: Bearer <oauth_access_token>`
   ```bash
   curl --header "Authorization: Bearer oauth_token_value" "https://gitlab.com/api/v4/user"
   ```
3. **CI/CD Job Token (`CI_JOB_TOKEN`)**:
   Header: `JOB-TOKEN: <ci_job_token>`
   ```bash
   curl --header "JOB-TOKEN: $CI_JOB_TOKEN" "https://gitlab.com/api/v4/projects/$CI_PROJECT_ID/pipelines"
   ```

## Common REST API Endpoints

### 1. List Projects
`GET /api/v4/projects`
Query params: `per_page=20`, `page=1`, `membership=true`, `search=keyword`.

### 2. Create Project
`POST /api/v4/projects`
Request body (JSON):
```json
{
  "name": "new-project",
  "visibility": "private",
  "initialize_with_readme": true
}
```

### 3. Trigger a Pipeline
`POST /api/v4/projects/:id/pipeline`
Query params / body: `ref=main`.

### 4. Create an Issue
`POST /api/v4/projects/:id/issues`
Body: `{"title": "Bug in login page", "description": "Details..."}`.

## API Pagination & Rate Limits
- **Pagination Headers**: GitLab REST API uses standard headers `X-Page`, `X-Next-Page`, `X-Prev-Page`, `X-Total`, `X-Total-Pages`.
- **Keyset Pagination**: For large datasets, use keyset pagination with `pagination=keyset&order_by=id&sort=asc`.
- **Rate Limiting**: Exceeding rate limits returns `HTTP 429 Too Many Requests` with `Retry-After` header indicating wait duration in seconds.

## GraphQL API Endpoint
- **URL**: `https://gitlab.com/api/graphql`
- **Method**: `POST`
- **Header**: `Authorization: Bearer <access_token>` or `PRIVATE-TOKEN: <pat>`
- Example Query:
```graphql
query {
  project(fullPath: "gitlab-org/gitlab") {
    name
    description
    pipelines(first: 5) {
      nodes {
        id
        status
        ref
      }
    }
  }
}
```
