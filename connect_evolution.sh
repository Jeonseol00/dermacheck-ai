#!/bin/bash

# Evolution API - Quick Connect Script (No UI!)
# Bypasses dashboard timeout issues

set -e

API_URL="http://localhost:8080"
API_KEY="dermacheck_ai_secret_key_2026"
INSTANCE="dermacheck"

echo "======================================================================"
echo "🚀 Evolution API - Quick Connect (Curl Method)"
echo "======================================================================"
echo ""

# Step 1: Clean up old instance
echo "📋 Step 1: Cleaning up old instance..."
curl -s -X DELETE "$API_URL/instance/logout/$INSTANCE" \
  -H "apikey: $API_KEY" > /dev/null 2>&1 || true
echo "✅ Clean slate ready"
echo ""

# Step 2: Create new instance
echo "📋 Step 2: Creating WhatsApp instance..."
RESPONSE=$(curl -s -X POST "$API_URL/instance/create" \
  -H "apikey: $API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"instanceName\": \"$INSTANCE\",
    \"qrcode\": true,
    \"integration\": \"WHATSAPP-BAILEYS\"
  }")

if echo "$RESPONSE" | grep -q "instanceName"; then
    echo "✅ Instance created successfully!"
else
    echo "❌ Failed to create instance"
    echo "Response: $RESPONSE"
    exit 1
fi

echo ""

# Step 3: Get QR Code
echo "======================================================================"
echo "📱 Step 3: Get QR Code"
echo "======================================================================"
echo ""
echo "Opening QR code in browser in 3 seconds..."
sleep 3

# Try to open in browser
QR_URL="$API_URL/instance/connect/$INSTANCE"

if command -v xdg-open &> /dev/null; then
    xdg-open "$QR_URL" &
elif command -v firefox &> /dev/null; then
    firefox "$QR_URL" &
elif command -v google-chrome &> /dev/null; then
    google-chrome "$QR_URL" &
else
    echo "⚠️ Could not open browser automatically"
    echo ""
    echo "Please open this URL manually:"
    echo "   $QR_URL"
fi

echo ""
echo "======================================================================"
echo "📱 SCAN QR CODE WITH WHATSAPP"
echo "======================================================================"
echo ""
echo "1. Open WhatsApp on your phone"
echo "2. Go to Settings → Linked Devices"  
echo "3. Tap 'Link a Device'"
echo "4. Scan the QR code from the browser"
echo ""
echo "Press ENTER after scanning..."
read

# Step 4: Check connection
echo ""
echo "📋 Step 4: Verifying connection..."
sleep 3

for i in {1..5}; do
    CONNECTION=$(curl -s -X GET "$API_URL/instance/connectionState/$INSTANCE" \
      -H "apikey: $API_KEY")
    
    if echo "$CONNECTION" | grep -q '"state":"open"'; then
        echo "✅ WhatsApp connected successfully!"
        CONNECTED=true
        break
    else
        echo "⏳ Waiting for connection... (attempt $i/5)"
        sleep 2
    fi
done

if [ -z "$CONNECTED" ]; then
    echo "⚠️ WhatsApp not connected yet"
    echo "Connection state: $CONNECTION"
    echo ""
    echo "Try scanning QR again or check logs:"
    echo "   docker logs evolution_api -f"
    exit 1
fi

echo ""

# Step 5: Test send message
echo "======================================================================"
echo "📋 Step 5: Testing message send"
echo "======================================================================"
echo ""
read -p "Enter phone number to test (e.g., 6289699280299): " PHONE_NUMBER

if [ -n "$PHONE_NUMBER" ]; then
    curl -s -X POST "$API_URL/message/sendText/$INSTANCE" \
      -H "apikey: $API_KEY" \
      -H "Content-Type: application/json" \
      -d "{
        \"number\": \"$PHONE_NUMBER\",
        \"text\": \"🎉 DermaCheck AI Connected via Evolution API!\"
      }" > /dev/null
    
    echo "✅ Test message sent to $PHONE_NUMBER"
    echo "Check your phone!"
else
    echo "⚠️ Skipping test message"
fi

echo ""
echo "======================================================================"
echo "✅ SETUP COMPLETE!"
echo "======================================================================"
echo ""
echo "🎯 Next Steps:"
echo "1. Make sure Python bot is running:"
echo "   python whatsapp_bot_evolution.py"
echo ""
echo "2. Test bot by sending 'Halo' from another phone"
echo ""
echo "3. Send a photo to test image analysis"
echo ""
echo "📊 Useful Commands:"
echo "• Check connection:"
echo "  curl -X GET $API_URL/instance/connectionState/$INSTANCE \\"
echo "    -H 'apikey: $API_KEY'"
echo ""
echo "• Get new QR (if expired):"
echo "  Open: $API_URL/instance/connect/$INSTANCE"
echo ""
echo "• View logs:"
echo "  docker logs evolution_api -f"
echo ""
echo "Happy testing! 🚀"
echo "======================================================================"
