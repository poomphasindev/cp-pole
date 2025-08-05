#!/bin/bash

# Switch to Demo Version Script
echo "🔄 Switching to Demo Version..."

# Backup original main file
if [ -f "maincai.py" ]; then
    echo "📁 Backing up original maincai.py..."
    cp maincai.py maincai_original.py
fi

# Copy demo version to main
echo "📝 Copying demo version..."
cp maincai_demo.py maincai.py

# Update requirements to minimal version
echo "📦 Updating requirements.txt..."
cat > requirements.txt << EOF
streamlit>=1.28.0
numpy>=1.24.0,<2.0.0
Pillow>=10.0.0
pandas>=2.0.0
openpyxl>=3.1.0
EOF

echo "✅ Demo version ready!"
echo ""
echo "🚀 Next steps:"
echo "1. git add ."
echo "2. git commit -m 'Switch to demo version'"
echo "3. git push origin main"
echo ""
echo "🌐 Your app will automatically redeploy on Streamlit Cloud" 