# VehicleIQ Branching Strategy

## Branch Structure

### `master` - Production Branch
- **Purpose:** Stable, production-ready code
- **Protection:** Only merge from `dev` when explicitly requested
- **Deployment:** Production deployments come from this branch
- **Direct commits:** ❌ Not allowed

### `dev` - Development Branch
- **Purpose:** Active development and testing
- **Protection:** All new features and fixes go here first
- **Testing:** Must pass all tests before merging to master
- **Direct commits:** ✅ Allowed during development

## Workflow

### Daily Development
```bash
# Always work on dev branch
git checkout dev
git pull origin dev

# Make changes, commit, and push
git add .
git commit -m "feat: your feature description"
git push origin dev
```

### Merging to Master (Only when requested)
```bash
# Switch to master
git checkout master
git pull origin master

# Merge dev into master
git merge dev

# Push to master
git push origin master

# Switch back to dev
git checkout dev
```

## Current Status

- ✅ `master` branch: Phase 1 complete, stable
- ✅ `dev` branch: Created from master, ready for Phase 2 development
- ✅ Both branches pushed to GitHub

## Quick Commands

```bash
# Check current branch
git branch

# Switch to dev (for development)
git checkout dev

# Switch to master (for releases)
git checkout master

# View all branches
git branch -a

# Check branch status
git status
```

## Rules

1. **All development happens on `dev`**
2. **Never commit directly to `master`**
3. **Merge to `master` only when explicitly requested**
4. **Always test on `dev` before merging to `master`**
5. **Keep `dev` up to date with regular commits**

## GitHub Repository

- Repository: https://github.com/mpk112/vehicle-iq
- Master branch: https://github.com/mpk112/vehicle-iq/tree/master
- Dev branch: https://github.com/mpk112/vehicle-iq/tree/dev

## Phase 2 Development

All Phase 2 work will be done on the `dev` branch:
- Image Intelligence features
- Fraud Detection implementation
- Price Prediction models
- Health Scoring system
- Benchmarking capabilities

When Phase 2 is complete and tested, we'll merge to `master`.
