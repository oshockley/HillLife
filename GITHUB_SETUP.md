# GitHub Repository Setup Guide for Hill Life 🏔️

## Step 1: Create GitHub Repository Online

1. **Go to GitHub**
   - Visit https://github.com
   - Log in to your account (or create one if needed)

2. **Create New Repository**
   - Click the "+" icon in top right
   - Select "New repository"
   
3. **Repository Settings**
   - **Repository name**: `hill-life` (or your preferred name)
   - **Description**: "Hill Life - A modern fitness tracking PWA to reach your pinnacle 🏔️"
   - **Visibility**: Choose Public or Private
   - **Initialize**: 
     - ❌ DON'T check "Add a README file" (we already have one)
     - ❌ DON'T add .gitignore (we created one)
     - ❌ DON'T choose a license yet
   - Click "Create repository"

## Step 2: Prepare Your Local Files

Open Command Prompt or Git Bash in your FitTracker folder:

```bash
cd "C:\Users\Shock\Desktop\FitTracker"
```

## Step 3: Initialize Git Repository

```bash
# Initialize git repository
git init

# Add all files to staging
git add .

# Make your first commit
git commit -m "Initial commit: Hill Life fitness tracking PWA with mobile support"
```

## Step 4: Connect to GitHub

Replace `YOUR_USERNAME` and `YOUR_REPO_NAME` with your actual GitHub info:

```bash
# Add GitHub repository as remote origin
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git

# Rename default branch to main (if needed)
git branch -M main

# Push code to GitHub
git push -u origin main
```

## Step 5: Verify Upload

1. Refresh your GitHub repository page
2. You should see all your Hill Life files uploaded
3. The README.md should display with the Hill Life branding

## Alternative Method: GitHub CLI

If you have GitHub CLI installed:

```bash
# Login to GitHub
gh auth login

# Create repository and push in one command
gh repo create hill-life --public --description "Hill Life - A modern fitness tracking PWA to reach your pinnacle 🏔️"

# Initialize and push
git init
git add .
git commit -m "Initial commit: Hill Life fitness tracking PWA"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/hill-life.git
git push -u origin main
```

## Step 6: Repository Setup

After uploading, consider:

1. **Add Topics/Tags**
   - Go to your repo on GitHub
   - Click gear icon next to "About"
   - Add topics: `fitness`, `pwa`, `flask`, `mobile-app`, `workout-tracker`

2. **Enable GitHub Pages** (optional)
   - Go to Settings → Pages
   - Select source branch (main)
   - Your app will be available at: `https://YOUR_USERNAME.github.io/hill-life`

3. **Add License**
   - Create new file: `LICENSE`
   - Choose MIT License or your preferred license

## Step 7: Future Updates

To update your repository:

```bash
# Make changes to your code
# Then:

git add .
git commit -m "Add new feature: [describe your changes]"
git push origin main
```

## Common Git Commands

```bash
# Check status
git status

# See commit history
git log --oneline

# Create new branch for feature
git checkout -b feature/new-feature

# Switch branches
git checkout main

# Merge branch
git merge feature/new-feature

# Pull latest changes
git pull origin main
```

## Troubleshooting

**Problem**: "Permission denied" when pushing
**Solution**: 
- Use Personal Access Token instead of password
- Generate token at: GitHub → Settings → Developer settings → Personal access tokens

**Problem**: Large file errors
**Solution**: 
- Check .gitignore includes database files
- Remove fitness_tracker.db: `git rm --cached fitness_tracker.db`

**Problem**: Repository already exists
**Solution**: 
- Either delete the GitHub repo and recreate
- Or force push: `git push -f origin main` (⚠️ dangerous)

## Sample Commands for Your Project

```bash
# Navigate to your project
cd "C:\Users\Shock\Desktop\FitTracker"

# Initialize git
git init

# Add all files
git add .

# First commit
git commit -m "🏔️ Initial commit: Hill Life PWA with animated gradients, mobile support, and social features"

# Connect to GitHub (replace with your info)
git remote add origin https://github.com/YOUR_USERNAME/hill-life.git

# Push to GitHub
git branch -M main
git push -u origin main
```

## Next Steps After Upload

1. **Share your repository** with friends and users
2. **Add collaborators** if working with a team
3. **Set up GitHub Actions** for automatic deployment
4. **Create issues** for feature requests and bugs
5. **Add a wiki** for detailed documentation

Your Hill Life app will now be safely stored on GitHub and ready for collaboration! 🚀
