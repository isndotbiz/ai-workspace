#!/bin/bash
# GitHub Sync Script for AI Workspace
# ===================================
# This script syncs your workspace to GitHub while excluding large model files

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}📤 Syncing AI Workspace to GitHub...${NC}"

# Get the directory where this script is located
WORKSPACE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$WORKSPACE_DIR"

# Check if this is a git repository
if [ ! -d ".git" ]; then
    echo -e "${RED}❌ Not a git repository. Run 'git init' first.${NC}"
    exit 1
fi

# Check if remote origin exists
if ! git remote get-url origin >/dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  No GitHub remote found.${NC}"
    echo -e "${BLUE}Please add your GitHub repository as origin:${NC}"
    echo -e "${YELLOW}git remote add origin https://github.com/yourusername/your-repo.git${NC}"
    exit 1
fi

# Show current status
echo -e "${BLUE}📊 Current git status:${NC}"
git status --short

# Add all files (but .gitignore will exclude large model files)
echo -e "${YELLOW}📝 Adding files to git...${NC}"
git add .

# Show what will be committed
echo -e "${BLUE}📋 Files to be committed:${NC}"
git status --short --cached

# Prompt for commit message if not provided
if [ -z "$1" ]; then
    echo -e "${YELLOW}💬 Enter commit message (or press Enter for default):${NC}"
    read -r COMMIT_MSG
    if [ -z "$COMMIT_MSG" ]; then
        COMMIT_MSG="Update workspace: $(date '+%Y-%m-%d %H:%M:%S')"
    fi
else
    COMMIT_MSG="$1"
fi

# Commit changes
echo -e "${YELLOW}💾 Committing changes...${NC}"
if git commit -m "$COMMIT_MSG"; then
    echo -e "${GREEN}✅ Changes committed successfully!${NC}"
else
    echo -e "${YELLOW}ℹ️  No changes to commit.${NC}"
fi

# Push to GitHub
echo -e "${YELLOW}🚀 Pushing to GitHub...${NC}"
if git push origin main 2>/dev/null || git push origin master 2>/dev/null; then
    echo -e "${GREEN}✅ Successfully pushed to GitHub!${NC}"
else
    echo -e "${RED}❌ Failed to push. Trying to set upstream...${NC}"
    CURRENT_BRANCH=$(git branch --show-current)
    if git push -u origin "$CURRENT_BRANCH"; then
        echo -e "${GREEN}✅ Successfully pushed to GitHub with upstream set!${NC}"
    else
        echo -e "${RED}❌ Failed to push to GitHub. Please check your remote configuration.${NC}"
        exit 1
    fi
fi

# Show final status
echo -e "${BLUE}📊 Final repository status:${NC}"
git log --oneline -5

# Check for large files that were ignored
echo -e "${BLUE}🔍 Checking for large files (excluded by .gitignore):${NC}"
LARGE_FILES=$(find ComfyUI/models -name "*.safetensors" -o -name "*.ckpt" -o -name "*.pt" -o -name "*.pth" 2>/dev/null | head -5)
if [ -n "$LARGE_FILES" ]; then
    echo -e "${YELLOW}📁 Large model files found (correctly excluded):${NC}"
    echo "$LARGE_FILES" | while read -r file; do
        if [ -f "$file" ]; then
            SIZE=$(du -h "$file" | cut -f1)
            echo -e "  🚫 $file (${SIZE})"
        fi
    done
    echo -e "${GREEN}✅ These files are properly excluded from GitHub sync.${NC}"
else
    echo -e "${YELLOW}📁 No large model files found in ComfyUI/models${NC}"
fi

echo -e "${GREEN}🎉 GitHub sync completed!${NC}"
echo -e "${BLUE}🌐 Repository URL: $(git remote get-url origin)${NC}"