---
name: update
description: Use when the user invokes /update or asks to push the current changes and bring the checkout in sync with the remote. Applies in any git repository, and in a parent folder whose direct children are separate repositories.
---

# Update

Push the work that is actually in progress, then make the current branch match its remote. Stay on the branch you are already on. For this request, do not switch to `main`.

## Which repositories

If the current directory is inside a git repository, update that repository only. If it is not a repository, update each direct child directory that has its own `.git`. Do not search deeper. Do not create branches, worktrees, or pull requests.

## Per repository

Read status, diff, and recent commit messages first.

Commit the changes that belong to the work, including new files that are part of it. Leave out anything that should not be shared, and name each path you left out:

- secrets and local credentials, such as `.env`, keys, tokens, and credential files
- operating-system and editor junk, such as `.DS_Store` and swap files
- dependencies, build output, caches, and logs

When a file is ambiguous, leave it out and say so. One commit per repository. Write the message in that repository's style and say why the change exists. Do not combine repositories into one commit.

Then publish the branch:

1. `git pull --rebase` on the current branch. Skip the pull when the branch has no upstream yet.
2. `git push` the current branch. Set the upstream when it has none.

Do not change git config, force-push, or skip hooks. If a hook rejects the commit, fix the cause and make a new commit. If the rebase conflicts or the push is rejected, stop that repository, say why, and continue with the others.

If the repository's own instructions say to refresh installed skill copies after a skill change, and this commit changed skills, do that refresh after the push.

## Report

For each repository, say the branch, what was committed or that there was nothing to commit, what was left out, and whether pull and push succeeded.
