#!/bin/bash

# 7-Eleven AI Preventive Maintenance - Deployment Script

echo "🚀 Starting deployment process..."

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "❌ Git is not installed. Please install Git first."
    exit 1
fi

# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "❌ Not in a git repository. Please initialize git first:"
    echo "   git init"
    echo "   git remote add origin <your-repo-url>"
    exit 1
fi

# Add all files
echo "📁 Adding files to git..."
git add .

# Commit changes
echo "💾 Committing changes..."
git commit -m "Deploy to Streamlit Cloud - $(date)"

# Push to remote repository
echo "📤 Pushing to remote repository..."
git push origin main

echo "✅ Deployment script completed!"
echo ""
echo "🌐 Next steps:"
echo "1. Go to https://share.streamlit.io"
echo "2. Sign in with your GitHub account"
echo "3. Click 'New app'"
echo "4. Select your repository"
echo "5. Set main file path to: maincai.py"
echo "6. Click 'Deploy'"
echo ""
echo "🎉 Your app will be deployed in a few minutes!" 