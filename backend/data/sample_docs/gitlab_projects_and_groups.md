# GitLab Projects and Groups Documentation

Source URL: https://docs.gitlab.com/ee/user/project/

## Overview of GitLab Projects
In GitLab, a project is the central hub for hosting your git repository, managing source code files, tracking issues, planning work with boards, and running CI/CD pipelines. Every project belongs to a namespace (either a user namespace or a group namespace).

### How to Create a GitLab Project
To create a new project in GitLab via the web UI:
1. On the left sidebar, select **Create new** (`+`) and then select **New project/repository**.
2. Select **Create blank project**.
3. Enter the project details:
   - **Project name**: Enter the name of your project (e.g., `my-awesome-app`).
   - **Project URL**: Choose the namespace (your personal user account or a group).
   - **Project slug**: The URL-friendly identifier automatically generated from the project name.
   - **Visibility Level**: Choose Public, Internal, or Private.
4. Select **Initialize repository with a README** if you want an initial commit with a README file.
5. Select **Create project**.

To create a project via REST API:
```bash
curl --request POST --header "PRIVATE-TOKEN: <your_access_token>" \
  --url "https://gitlab.com/api/v4/projects?name=my-new-project&visibility=private"
```

## Visibility Levels
GitLab supports three distinct visibility levels for projects and groups:
- **Private**: Access must be explicitly granted for each user. Private projects and groups are not visible to anonymous visitors or unauthenticated users.
- **Internal**: Any authenticated user can view, clone, and read the project, except external users.
- **Public**: Anyone can view, clone, and read public projects without logging in or authenticating.

## Managing GitLab Groups and Subgroups
Groups allow you to organize multiple projects and manage user permissions across repositories simultaneously.
- **Subgroups**: You can nest groups up to 20 levels deep to mirror complex organizational structures.
- **Group Roles**: User permissions cascade down from the parent group to subgroups and child projects.
- **Transferring Projects**: Projects can be transferred between groups or user namespaces under **Project Settings > General > Advanced > Transfer project**.
- **Archiving Projects**: Archiving a project places it in read-only mode, keeping historical data intact while preventing new commits or pipeline runs.
