#!/bin/bash

# Evolution API - Get QR Code (Bypass Browser Auth)
# Solves 401 Unauthorized issue

API_KEY="12345"
INSTANCE="dermacheck"
API_URL="http://localhost:8080"

echo "======================================================================"
echo "📱 DermaCheck AI - Get WhatsApp QR Code"
echo "======================================================================"
echo ""

# Check if instance exists
echo "🔍 Checking if instance exists..."
INSTANCES=$(curl -s -X GET "$API_URL/instance/fetchInstances" \
  -H "apikey: $API_KEY")

if echo "$INSTANCES" | grep -q "$INSTANCE"; then
    echo "✅ Instance '$INSTANCE' found"
else
    echo "⚠️ Instance '$INSTANCE' not found. Creating..."
    
    # Create instance
    curl -s -X POST "$API_URL/instance/create" \
      -H "apikey: $API_KEY" \
      -H "Content-Type: application/json" \
      -d "{
        \"instanceName\": \"$INSTANCE\",
        \"qrcode\": true,
        \"integration\": \"WHATSAPP-BAILEYS\"
      }" > /dev/null
    
    echo "✅ Instance created"
    sleep 3
fi

echo ""

# Get QR code
echo "📥 Fetching QR Code..."

QR_RESPONSE=$(curl -s -X GET "$API_URL/instance/qrcode/$INSTANCE" \
  -H "apikey: $API_KEY")

# Check if QR code received
if echo "$QR_RESPONSE" | grep -q "base64"; then
    echo "✅ QR Code received"
    
    # Extract and save QR code
    echo "$QR_RESPONSE" \
      | jq -r '.qrcode.base64' \
      | sed 's/data:image\/png;base64,//' \
      | base64 -d > qr_code.png
    
    echo "✅ QR Code saved: qr_code.png"
    echo ""
    
    # Try to open image
    echo "🖼️ Opening QR Code..."
    
    if command -v xdg-open &> /dev/null; then
        xdg-open qr_code.png &
    elif command -v eog &> /dev/null; then
        eog qr_code.png &
    elif command -v firefox &> /dev/null; then
        firefox qr_code.png &
    else
        echo "⚠️ Could not open image automatically"
        echo "Please open qr_code.png manually"
    fi
    
    echo ""
    echo "======================================================================"
    echo "📱 SCAN QR CODE WITH WHATSAPP"
    echo "======================================================================"
    echo ""
    echo "1. Open WhatsApp on your phone"
    echo "2. Settings → Linked Devices"
    echo "3. Link a Device"
    echo "4. Scan the QR code"
    echo ""
    echo "⏰ QR code expires in 30 seconds!"
    echo "   If expired, run this script again."
    echo ""
    echo "Press ENTER after scanning..."
    read
    
    # Check connection
    echo ""
    echo "🔍 Verifying connection..."
    sleep 2
    
    CONNECTION=$(curl -s -X GET "$API_URL/instance/connectionState/$INSTANCE" \
      -H "apikey: $API_KEY")
    
    if echo "$CONNECTION" | grep -q '"state":"open"'; then
        echo ""
        echo "======================================================================"
        echo "✅ SUCCESS! WhatsApp Connected!"
        echo "======================================================================"
        echo ""
        echo "You can now:"
        echo "• Start the Python bot: python whatsapp_bot_evolution.py"
        echo "• Send 'Halo' from another phone to test"
        echo "• Send a photo to test image analysis"
        echo ""
    else
        echo "⚠️ Not connected yet. Connection state:"
        echo "$CONNECTION" | jq '.'
        echo ""
        echo "Try scanning QR code again or check logs:"
        echo "docker logs evolution_api -f"
    fi
    
else
    echo "❌ Failed to get QR code"
    echo "Response: $QR_RESPONSE"
    echo ""
    echo "Possible issues:"
    echo "• Instance not ready (wait a few seconds)"
    echo "• API key mismatch"
    echo "• Evolution API not running"
    echo ""
    echo "Check logs: docker logs evolution_api -f"
fi

echo ""
echo "======================================================================"
