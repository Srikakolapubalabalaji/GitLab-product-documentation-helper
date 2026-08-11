# GitLab Merge Requests (MR) Documentation

Source URL: https://docs.gitlab.com/ee/user/project/merge_requests/

## Overview of Merge Requests
A Merge Request (MR) is the core method of proposing, discussing, reviewing, and merging code changes into a branch within a GitLab project or across forks.

### How to Create a Merge Request
1. Push your branch to GitLab (`git push origin feature-branch`).
2. Go to your project in GitLab UI and select **Code > Merge requests**.
3. Select **New merge request**.
4. Select the **Source branch** (your feature branch) and **Target branch** (e.g., `main` or `master`).
5. Select **Compare branches and continue**.
6. Fill in title, description (mention `Closes #123` to auto-close issues), assignees, reviewers, and approval rules.
7. Select **Create merge request**.

## Draft Merge Requests
Mark an MR as a work-in-progress by prefixing the title with `Draft:` or `WIP:` (e.g., `Draft: Add user authentication`). Draft MRs cannot be merged until marked as ready by selecting **Mark as ready** in the UI.

## Merge Request Approvals & CODEOWNERS
- **Approval Rules**: Specify minimum required approvals from designated code owners, security teams, or project maintainers before merging.
- **CODEOWNERS File**: Define users or groups responsible for specific files/directories (e.g., `/docs/ @tech-writers`). Requiring approval from CODEOWNERS ensures critical files are reviewed by experts.

## Merge Strategies Comparison
GitLab supports four main merge strategies configured under **Project Settings > Merge requests**:
1. **Merge Commit**: Creates a merge commit combining source into target branch (preserves complete history tree).
2. **Fast-Forward Merge**: Linear history without merge commits. Target branch head is simply updated to source branch tip. Requires source branch to be up to date with target branch.
3. **Rebase Merge**: Rebases source branch commits onto target branch head before fast-forwarding.
4. **Squash Merging**: Combines all commits from the MR branch into a single clean commit before merging into the target branch.
