# 🚀 Deploy to GitHub Pages - Like Your Colleague!

## Quick Setup (5 minutes)

### Step 1: Create GitHub Repository

```bash
cd /Users/nsenthil/AI_TOOL/openshift-upgrade-advisor

# Initialize git (if not already)
git init

# Create .gitignore
cat > .gitignore <<EOF
__pycache__/
*.pyc
.DS_Store
*.log
test-*.json
node_modules/
EOF

# Add files
git add .
git commit -m "Initial commit: OpenShift Operator Upgrade Advisor"

# Create repo on GitHub (via web or CLI)
gh repo create openshift-upgrade-advisor --public --source=. --remote=origin

# Push
git push -u origin main
```

### Step 2: Enable GitHub Pages

**Option A: Via GitHub Web Interface**
1. Go to repo settings
2. Click "Pages" in sidebar
3. Source: Deploy from branch
4. Branch: `main` / `docs` folder
5. Save

**Option B: Via GitHub CLI**
```bash
gh repo edit --enable-pages --pages-branch main
```

### Step 3: Create GitHub Actions Workflow

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to GitHub Pages

on:
  push:
    branches: [ main ]
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Pages
        uses: actions/configure-pages@v3
      
      - name: Upload artifact
        uses: actions/upload-pages-artifact@v2
        with:
          path: '.'
      
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v2
```

### Step 4: Share!

Your tool is now live at:
```
https://yourusername.github.io/openshift-upgrade-advisor/
```

Share this link just like your colleague did! 🎉
