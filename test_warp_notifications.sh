#!/bin/bash

# Test Warp Notifications with AI Workspace Integration
echo "🧪 Testing Warp Notifications with AI Generation"
echo "================================================"

# Test basic notification
echo "1. Basic notification test..."
notify-send "🎨 AI Workspace" "Warp notifications are working!" --urgency=normal
sleep 2

# Test with AI generation completion simulation
echo "2. AI generation notification test..."
notify-send "✅ Image Generated" "flux_kontext_turbo_00020_.png completed in 47.3s" --icon=dialog-information --urgency=normal
sleep 2

# Test batch completion notification
echo "3. Batch completion notification..."
notify-send "🎉 Batch Complete" "3/3 portraits generated successfully! Total time: 2m 15s" --icon=dialog-information --urgency=normal
sleep 2

# Test error notification
echo "4. Error notification test..."
notify-send "⚠️ ComfyUI Warning" "GPU memory low - consider reducing batch size" --icon=dialog-warning --urgency=critical
sleep 2

# Test with custom Warp helper
echo "5. Warp helper test..."
warp-notify "🚀 System Ready" "All AI services operational - RTX 4060 Ti ready" --urgency=normal

echo ""
echo "✅ All notification tests completed!"
echo "If you saw 5 notifications, Warp notifications are working properly."
echo ""
echo "💡 Usage in your AI scripts:"
echo "   notify-send \"Title\" \"Message\" --urgency=normal"
echo "   warp-notify \"Title\" \"Message\"  # Custom helper"
echo ""
echo "🎯 Integration examples:"
echo "   # After image generation:"
echo "   notify-send \"🎨 Generated\" \"Portrait completed!\" --icon=dialog-information"
echo "   # After batch completion:"
echo "   notify-send \"🎉 Batch Done\" \"5 images ready\" --urgency=normal"