#!/bin/bash

echo "🔥 GOD-LIKE ATTACK VALIDATION SUITE"
echo "=================================="
echo ""
echo "This will thoroughly test your attack system for:"
echo "• Garbage vs strikes differentiation"
echo "• Formula accuracy"
echo "• Pattern consistency"
echo "• Edge cases and weird scenarios"
echo "• Performance and stability"
echo ""
echo "Starting validation..."

# Run the comprehensive validation suite
python3 tools/validation/comprehensive_attack_validation_suite.py

# Check exit code
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ VALIDATION COMPLETE - All tests passed!"
    echo "Your attack system is bulletproof! 🛡️"
else
    echo ""
    echo "❌ VALIDATION FAILED - Issues detected!"
    echo "Check build/reports/attack_validation_report.json for details"
    echo ""
    echo "🚨 CRITICAL ISSUES FOUND:"
    echo "• Review the failed tests above"
    echo "• Fix formula violations first"
    echo "• Address pattern mismatches"
    echo "• Check for delivery anomalies"
fi

# Move report to build/reports if it was generated at project root
if [ -f attack_validation_report.json ]; then
    mkdir -p build/reports
    mv -f attack_validation_report.json build/reports/
fi

echo ""
echo "📄 Full report: build/reports/attack_validation_report.json"
