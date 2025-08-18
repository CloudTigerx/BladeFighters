#!/bin/bash

echo "🗑️ COMPREHENSIVE GARBAGE VALIDATION SUITE"
echo "========================================="
echo ""
echo "This will thoroughly test your garbage system for:"
echo "• Garbage formula accuracy"
echo "• Garbage delivery mechanics"
echo "• Garbage vs strikes differentiation"
echo "• Garbage placement patterns"
echo "• Garbage transformation issues"
echo "• Edge cases and weird scenarios"
echo ""
echo "Starting garbage validation..."

# Run the comprehensive garbage validation suite
python3 tools/validation/comprehensive_garbage_validation_suite.py

# Check exit code
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ GARBAGE VALIDATION COMPLETE - All tests passed!"
    echo "Your garbage system is bulletproof! 🛡️🗑️"
else
    echo ""
    echo "❌ GARBAGE VALIDATION FAILED - Issues detected!"
    echo "Check build/reports/garbage_validation_report.json for details"
    echo ""
    echo "🚨 CRITICAL GARBAGE ISSUES FOUND:"
    echo "• Review the failed tests above"
    echo "• Fix garbage formula violations first"
    echo "• Address garbage delivery anomalies"
    echo "• Check for garbage transformation issues"
fi

# Move report to build/reports if it was generated at project root
if [ -f garbage_validation_report.json ]; then
    mkdir -p build/reports
    mv -f garbage_validation_report.json build/reports/
fi

echo ""
echo "📄 Full report: build/reports/garbage_validation_report.json"
