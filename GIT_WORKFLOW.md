# Git Workflow Quick Reference

## Current Branch Status

```bash
# Check which branch you're on
git branch
# * dev          <- You should see this (active development)
#   master       <- Production branch
```

## Daily Development Workflow

### 1. Start Your Day
```bash
# Make sure you're on dev branch
git checkout dev

# Get latest changes
git pull origin dev
```

### 2. Make Changes
```bash
# Edit files, write code...

# Check what changed
git status

# See detailed changes
git diff
```

### 3. Commit Changes
```bash
# Stage all changes
git add .

# Or stage specific files
git add backend/app/services/fraud.py

# Commit with descriptive message
git commit -m "feat: implement fraud detection service"

# Push to dev branch
git push origin dev
```

## Commit Message Conventions

Use these prefixes:
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `test:` - Adding or updating tests
- `refactor:` - Code refactoring
- `chore:` - Maintenance tasks

Examples:
```bash
git commit -m "feat: add OCR extraction endpoint"
git commit -m "fix: resolve database connection timeout"
git commit -m "docs: update API documentation"
git commit -m "test: add unit tests for fraud detection"
```

## Checking Status

```bash
# See current branch and changes
git status

# See commit history
git log --oneline -10

# See branch graph
git log --oneline --graph --all -10

# See what's on remote
git remote -v
```

## Merging to Master (Only When Requested)

**⚠️ DO NOT do this unless explicitly requested!**

```bash
# 1. Make sure dev is clean and pushed
git checkout dev
git status  # Should be clean
git push origin dev

# 2. Switch to master
git checkout master
git pull origin master

# 3. Merge dev into master
git merge dev

# 4. Push to master
git push origin master

# 5. Switch back to dev
git checkout dev
```

## Useful Commands

```bash
# Undo last commit (keep changes)
git reset --soft HEAD~1

# Discard all local changes
git reset --hard HEAD

# See differences between branches
git diff master..dev

# List all branches (local and remote)
git branch -a

# Delete local branch (if needed)
git branch -d branch-name
```

## Branch Protection Rules

- ✅ **dev**: Active development, commit freely
- ❌ **master**: Production only, merge only when requested

## GitHub Links

- Repository: https://github.com/mpk112/vehicle-iq
- Dev branch: https://github.com/mpk112/vehicle-iq/tree/dev
- Master branch: https://github.com/mpk112/vehicle-iq/tree/master

## Current Setup

- ✅ `dev` branch created from `master`
- ✅ Both branches pushed to GitHub
- ✅ Currently on `dev` branch
- ✅ Ready for Phase 2 development

## Remember

1. Always work on `dev` branch
2. Commit and push regularly
3. Use descriptive commit messages
4. Only merge to `master` when requested
5. Test before pushing
