#!/bin/bash

# DermaCheck AI - Quick Deploy Script for Evolution API
# Run this to quickly deploy and test the WhatsApp bot

set -e  # Exit on error

echo "======================================================================"
echo "🚀 DermaCheck AI - Evolution API Quick Deploy"
echo "======================================================================"
echo ""

# Step 1: Check Docker
echo "📋 Step 1: Checking Docker installation..."
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found!"
    echo "Please install Docker first: https://docs.docker.com/get-docker/"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose not found!"
    echo "Please install Docker Compose first"
    exit 1
fi

echo "✅ Docker found: $(docker --version)"
echo "✅ Docker Compose found: $(docker-compose --version)"
echo ""

# Step 2: Deploy Evolution API
echo "📋 Step 2: Deploying Evolution API containers..."
docker-compose up -d

echo "⏳ Waiting 10 seconds for containers to start..."
sleep 10

# Check if containers are running
if docker ps | grep -q "evolution_api"; then
    echo "✅ Evolution API container running"
else
    echo "❌ Evolution API container failed to start"
    echo "Check logs: docker logs evolution_api"
    exit 1
fi

if docker ps | grep -q "evolution_postgres"; then
    echo "✅ PostgreSQL container running"
else
    echo "❌ PostgreSQL container failed to start"
    echo "Check logs: docker logs evolution_postgres"
    exit 1
fi

echo ""

# Step 3: Create WhatsApp instance
echo "📋 Step 3: Creating WhatsApp instance..."

RESPONSE=$(curl -s -X POST http://localhost:8080/instance/create \
  -H "apikey: dermacheck_ai_secret_key_2026" \
  -H "Content-Type: application/json" \
  -d '{
    "instanceName": "dermacheck",
    "qrcode": true,
    "integration": "WHATSAPP-BAILEYS"
  }')

if echo "$RESPONSE" | grep -q "instanceName"; then
    echo "✅ Instance created successfully!"
else
    echo "⚠️ Instance may already exist or error occurred"
    echo "Response: $RESPONSE"
fi

echo ""

# Step 4: Display QR code instructions
echo "======================================================================"
echo "📱 Step 4: Connect WhatsApp"
echo "======================================================================"
echo ""
echo "Open this URL in your browser to see QR code:"
echo ""
echo "   🔗 http://localhost:8080/instance/connect/dermacheck"
echo ""
echo "Then:"
echo "1. Open WhatsApp on your phone"
echo "2. Go to Settings → Linked Devices"
echo "3. Tap 'Link a Device'"
echo "4. Scan the QR code"
echo ""
echo "Press ENTER after scanning QR code..."
read

# Step 5: Check connection
echo ""
echo "📋 Step 5: Checking WhatsApp connection..."
sleep 3

CONNECTION=$(curl -s -X GET http://localhost:8080/instance/connectionState/dermacheck \
  -H "apikey: dermacheck_ai_secret_key_2026")

if echo "$CONNECTION" | grep -q '"state":"open"'; then
    echo "✅ WhatsApp connected successfully!"
else
    echo "⚠️ WhatsApp not connected yet"
    echo "Response: $CONNECTION"
    echo "Try scanning QR again or check Evolution API logs"
fi

echo ""

# Step 6: Start Python bot
echo "======================================================================"
echo "📋 Step 6: Starting Python Bot"
echo "======================================================================"
echo ""
echo "The bot will start in a new terminal. Keep it running!"
echo ""
echo "If not started automatically, run:"
echo "   python whatsapp_bot_evolution.py"
echo ""

# Try to start bot in background
if command -v gnome-terminal &> /dev/null; then
    gnome-terminal -- bash -c "cd $(pwd) && python whatsapp_bot_evolution.py; exec bash"
elif command -v xterm &> /dev/null; then
    xterm -e "cd $(pwd) && python whatsapp_bot_evolution.py" &
else
    echo "⚠️ Could not open new terminal automatically"
    echo "Please run manually: python whatsapp_bot_evolution.py"
fi

echo ""
echo "======================================================================"
echo "✅ DEPLOYMENT COMPLETE!"
echo "======================================================================"
echo ""
echo "🎯 Next Steps:"
echo "1. Make sure Python bot is running (check terminal)"
echo "2. Send 'Halo' from another phone to test"
echo "3. Send a photo to test image analysis"
echo ""
echo "📊 Management Commands:"
echo "• View logs: docker-compose logs -f"
echo "• Stop: docker-compose down"
echo "• Restart: docker-compose restart"
echo ""
echo "🔗 Useful URLs:"
echo "• Evolution API: http://localhost:8080"
echo "• QR Code: http://localhost:8080/instance/connect/dermacheck"
echo "• Bot Webhook: http://localhost:5000/webhook"
echo ""
echo "Happy testing! 🚀"
echo "======================================================================"
