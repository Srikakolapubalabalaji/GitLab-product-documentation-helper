# GitLab Issues, Epics, and Work Items Documentation

Source URL: https://docs.gitlab.com/ee/user/project/issues/

## GitLab Issues Overview
Issues are the fundamental building blocks for tracking work, bugs, enhancements, and tasks in GitLab projects.

### How to Create an Issue
1. On the left sidebar, select **Plan > Issues**.
2. Select **New issue**.
3. Fill in the required fields:
   - **Title**: A clear summary of the issue.
   - **Description**: Detailed description using Markdown, task lists (`- [ ] task`), and quick actions.
   - **Assignee**: Assign team members responsible for the work.
   - **Milestone**: Associate with a release or sprint.
   - **Labels**: Categorize the issue (e.g., `bug`, `feature`, `priority::high`).
4. Select **Create issue**.

## Epics and Roadmaps (GitLab Premium / Ultimate)
- **Epics**: Higher-level work containers that span multiple projects and subgroups. Epics track portfolio-level initiatives and contain child epics and issues.
- **Roadmaps**: Visual timeline graphs showing epics mapped across start and due dates.

## Comparison: Issues vs Epics vs Merge Requests
| Feature | Issues | Epics | Merge Requests |
| :--- | :--- | :--- | :--- |
| **Scope** | Single Project level | Group & Subgroup level | Single Project level |
| **Purpose** | Planning & tracking tasks/bugs | High-level portfolio initiatives | Proposing, reviewing, and merging code changes |
| **Hierarchy** | Can be child of an Epic | Can contain child Epics & Issues | Resolves Issues via `Closes #123` |
| **Availability** | All GitLab Tiers (Free+) | Premium & Ultimate Tiers | All GitLab Tiers (Free+) |

## Issue Boards & Milestones
- **Issue Boards**: Kanban-style boards organizing issues into workflow columns based on labels, assignees, or milestones.
- **Milestones**: Track issues and merge requests assigned to a specific target release date or sprint period.
- **Time Tracking**: Use quick actions `/estimate 2d` and `/spend 4h` in issue descriptions/comments to track effort.
