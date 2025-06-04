#!/bin/bash
# Script to deploy to GitHub Pages

echo "🚀 Deploying to GitHub Pages..."

# Clean and build
echo "📦 Building the project..."
npm run build

# Deploy to gh-pages branch
echo "🌐 Deploying to gh-pages branch..."
npx gh-pages -d build -f

echo "✅ Deployment complete!"
echo ""
echo "📝 IMPORTANT: You need to configure GitHub Pages in your repository settings:"
echo "   1. Go to: https://github.com/jaimegarcia/colombia-salary-viz-2025/settings/pages"
echo "   2. Under 'Source', select 'Deploy from a branch'"
echo "   3. Choose 'gh-pages' branch and '/ (root)' folder"
echo "   4. Click 'Save'"
echo ""
echo "🔗 Your site will be available at: https://jaimegarcia.github.io/colombia-salary-viz-2025/"
echo "   (It may take a few minutes to become available after configuration)"
