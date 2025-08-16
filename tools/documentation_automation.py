#!/usr/bin/env python3
"""
Documentation Automation Tool for BladeFighters Project

This script provides automated documentation validation, generation, and reporting
for the CI/CD pipeline and development workflow.
"""

import os
import json
import re
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional


class DocumentationValidator:
    """Validates documentation quality and completeness."""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.modules_dir = self.project_root / "modules"
        self.docs_dir = self.project_root / "docs"
        
    def check_module_documentation(self) -> Dict[str, Any]:
        """Check documentation coverage for all modules."""
        results = {
            "modules_with_readme": 0,
            "modules_with_migration_guides": 0,
            "modules_with_integration_guides": 0,
            "modules_with_tests": 0,
            "total_modules": 0,
            "missing_documentation": [],
            "module_details": {}
        }
        
        if not self.modules_dir.exists():
            return results
            
        for module_dir in self.modules_dir.iterdir():
            if module_dir.is_dir() and not module_dir.name.startswith('.'):
                module_name = module_dir.name
                results["total_modules"] += 1
                results["module_details"][module_name] = {
                    "has_readme": False,
                    "has_migration_guide": False,
                    "has_integration_guide": False,
                    "has_tests": False,
                    "missing_files": []
                }
                
                # Check README.md
                if (module_dir / "README.md").exists():
                    results["modules_with_readme"] += 1
                    results["module_details"][module_name]["has_readme"] = True
                else:
                    results["module_details"][module_name]["missing_files"].append("README.md")
                
                # Check migration guide
                if (module_dir / "MIGRATION_GUIDE.md").exists():
                    results["modules_with_migration_guides"] += 1
                    results["module_details"][module_name]["has_migration_guide"] = True
                
                # Check integration guide
                if (module_dir / "INTEGRATION_GUIDE.md").exists():
                    results["modules_with_integration_guides"] += 1
                    results["module_details"][module_name]["has_integration_guide"] = True
                
                # Check tests directory
                if (module_dir / "tests").exists():
                    results["modules_with_tests"] += 1
                    results["module_details"][module_name]["has_tests"] = True
                
                if results["module_details"][module_name]["missing_files"]:
                    results["missing_documentation"].append(module_name)
        
        return results
    
    def validate_readme_template_compliance(self) -> Dict[str, Any]:
        """Validate that module READMEs follow the template structure."""
        template_sections = [
            "## Overview",
            "## 🎯 Key Features",
            "## 📁 Module Structure", 
            "## 🚀 Quick Start",
            "## 📋 API Reference"
        ]
        
        results = {
            "compliant_modules": [],
            "non_compliant_modules": [],
            "missing_sections": {}
        }
        
        for module_dir in self.modules_dir.iterdir():
            if module_dir.is_dir() and not module_dir.name.startswith('.'):
                readme_path = module_dir / "README.md"
                if readme_path.exists():
                    with open(readme_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    missing_sections = []
                    for section in template_sections:
                        if section not in content:
                            missing_sections.append(section)
                    
                    if missing_sections:
                        results["non_compliant_modules"].append(module_dir.name)
                        results["missing_sections"][module_dir.name] = missing_sections
                    else:
                        results["compliant_modules"].append(module_dir.name)
        
        return results
    
    def check_developer_logs_freshness(self) -> Dict[str, Any]:
        """Check if developer logs are being updated regularly."""
        logs_dir = self.docs_dir / "developer_logs"
        results = {
            "total_logs": 0,
            "recent_logs": 0,
            "stale_logs": [],
            "missing_logs": []
        }
        
        if not logs_dir.exists():
            return results
        
        cutoff_date = datetime.now() - timedelta(days=7)
        
        for log_file in logs_dir.glob("*.md"):
            if log_file.name != "README.md":
                results["total_logs"] += 1
                mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
                
                if mtime > cutoff_date:
                    results["recent_logs"] += 1
                else:
                    results["stale_logs"].append({
                        "file": log_file.name,
                        "last_modified": mtime.isoformat(),
                        "days_old": (datetime.now() - mtime).days
                    })
        
        return results
    
    def generate_coverage_report(self) -> Dict[str, Any]:
        """Generate comprehensive documentation coverage report."""
        module_coverage = self.check_module_documentation()
        template_compliance = self.validate_readme_template_compliance()
        log_freshness = self.check_developer_logs_freshness()
        
        coverage_percentage = 0
        if module_coverage["total_modules"] > 0:
            coverage_percentage = (module_coverage["modules_with_readme"] / module_coverage["total_modules"]) * 100
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "coverage_percentage": round(coverage_percentage, 1),
            "module_coverage": module_coverage,
            "template_compliance": template_compliance,
            "log_freshness": log_freshness,
            "summary": {
                "status": "good" if coverage_percentage >= 80 else "needs_attention",
                "priority_actions": []
            }
        }
        
        # Generate priority actions
        if module_coverage["missing_documentation"]:
            report["summary"]["priority_actions"].append(
                f"Create README.md for {len(module_coverage['missing_documentation'])} modules"
            )
        
        if template_compliance["non_compliant_modules"]:
            report["summary"]["priority_actions"].append(
                f"Update {len(template_compliance['non_compliant_modules'])} modules to follow template"
            )
        
        if log_freshness["stale_logs"]:
            report["summary"]["priority_actions"].append(
                f"Update {len(log_freshness['stale_logs'])} stale developer logs"
            )
        
        return report


class DocumentationGenerator:
    """Generates documentation files and reports."""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.modules_dir = self.project_root / "modules"
        self.docs_dir = self.project_root / "docs"
    
    def create_module_readme_template(self, module_name: str) -> str:
        """Generate a README.md template for a module."""
        template = f"""# {module_name.replace('_', ' ').title()} Module

## Overview

[Brief description of the {module_name} module's purpose, functionality, and role in the overall system. 2-3 sentences that explain what this module does and why it exists.]

## 🎯 Key Features

- **[Feature 1]** - Brief description of key functionality
- **[Feature 2]** - Brief description of key functionality  
- **[Feature 3]** - Brief description of key functionality
- **[Feature 4]** - Brief description of key functionality

## 📁 Module Structure

```
modules/{module_name}/
├── __init__.py                    # Module initialization and exports
├── README.md                      # This documentation file
├── [main_file].py                 # Primary module implementation
├── [supporting_file].py           # Supporting functionality
├── [integration_file].py          # Integration layer (if applicable)
├── MIGRATION_GUIDE.md            # Migration from old system (if applicable)
├── INTEGRATION_GUIDE.md          # Integration instructions (if applicable)
├── tests/
│   ├── test_[main_file].py       # Main test suite
│   ├── test_[supporting_file].py # Supporting tests
│   └── test_integration.py       # Integration tests (if applicable)
└── [other_files]                 # Additional module files
```

## 🚀 Quick Start

### Basic Usage

```python
from modules.{module_name}.[main_file] import [MainClass]

# Initialize the module
[instance] = [MainClass]()

# Basic operation
result = [instance].[basic_method]()
print(f"Result: {{result}}")
```

### Advanced Usage

```python
from modules.{module_name}.[main_file] import [MainClass]
from modules.{module_name}.[supporting_file] import [SupportClass]

# Initialize with configuration
config = {{
    "setting1": "value1",
    "setting2": "value2"
}}
[instance] = [MainClass](config)

# Advanced operations
[instance].[advanced_method](param1, param2)
```

## 📋 API Reference

### [MainClass]

The primary class for {module_name} functionality.

#### Constructor

```python
[MainClass](config=None, **kwargs)
```

**Parameters:**
- `config` (dict, optional): Configuration dictionary
- `**kwargs`: Additional configuration parameters

**Returns:**
- `[MainClass]`: Initialized instance

#### Methods

##### `[method_name](param1, param2=None)`

[Description of what this method does and when to use it.]

**Parameters:**
- `param1` (type): Description of parameter
- `param2` (type, optional): Description of optional parameter

**Returns:**
- `return_type`: Description of return value

**Raises:**
- `ExceptionType`: When and why this exception is raised

**Example:**
```python
# Example usage code here
```

## 🔗 Integration

### Dependencies

[List other modules this module depends on]

### Integration Points

[Describe how this module integrates with other parts of the system]

## 🧪 Testing

### Running Tests

```bash
# Run module-specific tests
pytest modules/{module_name}/tests/

# Run all tests
pytest
```

### Test Coverage

[Describe test coverage and testing strategy]

## 📝 Migration Notes

[If applicable, describe migration from previous versions or systems]

## 🤝 Contributing

[Guidelines for contributing to this module]

---
*Last updated: {datetime.now().strftime('%Y-%m-%d')}*
"""
        return template
    
    def generate_missing_readmes(self) -> List[str]:
        """Generate README.md files for modules that don't have them."""
        generated_files = []
        
        for module_dir in self.modules_dir.iterdir():
            if module_dir.is_dir() and not module_dir.name.startswith('.'):
                readme_path = module_dir / "README.md"
                if not readme_path.exists():
                    template_content = self.create_module_readme_template(module_dir.name)
                    with open(readme_path, 'w', encoding='utf-8') as f:
                        f.write(template_content)
                    generated_files.append(str(readme_path))
        
        return generated_files


def main():
    """Main CLI interface for documentation automation."""
    if len(sys.argv) < 2:
        print("Usage: python documentation_automation.py <command> [options]")
        print("\nCommands:")
        print("  validate     - Validate documentation quality")
        print("  generate     - Generate missing documentation")
        print("  report       - Generate coverage report")
        print("  all          - Run all checks and generate report")
        return
    
    command = sys.argv[1]
    validator = DocumentationValidator()
    generator = DocumentationGenerator()
    
    if command == "validate":
        print("🔍 Validating documentation...")
        coverage = validator.check_module_documentation()
        compliance = validator.validate_readme_template_compliance()
        
        print(f"📊 Documentation Coverage: {coverage['modules_with_readme']}/{coverage['total_modules']} modules")
        print(f"📋 Template Compliance: {len(compliance['compliant_modules'])}/{coverage['total_modules']} modules")
        
        if coverage['missing_documentation']:
            print(f"❌ Missing README.md in: {', '.join(coverage['missing_documentation'])}")
        
        if compliance['non_compliant_modules']:
            print(f"⚠️  Non-compliant modules: {', '.join(compliance['non_compliant_modules'])}")
    
    elif command == "generate":
        print("📝 Generating missing documentation...")
        generated = generator.generate_missing_readmes()
        if generated:
            print(f"✅ Generated {len(generated)} README.md files:")
            for file in generated:
                print(f"  - {file}")
        else:
            print("✅ All modules already have README.md files")
    
    elif command == "report":
        print("📊 Generating comprehensive report...")
        report = validator.generate_coverage_report()
        
        # Save report
        build_dir = Path("build/docs")
        build_dir.mkdir(parents=True, exist_ok=True)
        
        report_path = build_dir / "coverage_report.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        
        print(f"📄 Report saved to: {report_path}")
        print(f"📈 Coverage: {report['coverage_percentage']}%")
        print(f"📋 Status: {report['summary']['status']}")
        
        if report['summary']['priority_actions']:
            print("🎯 Priority Actions:")
            for action in report['summary']['priority_actions']:
                print(f"  - {action}")
    
    elif command == "all":
        print("🚀 Running complete documentation automation...")
        
        # Generate missing docs
        generated = generator.generate_missing_readmes()
        if generated:
            print(f"✅ Generated {len(generated)} README.md files")
        
        # Generate report
        report = validator.generate_coverage_report()
        build_dir = Path("build/docs")
        build_dir.mkdir(parents=True, exist_ok=True)
        
        report_path = build_dir / "coverage_report.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        
        print(f"📊 Final Coverage: {report['coverage_percentage']}%")
        print(f"📄 Report saved to: {report_path}")
    
    else:
        print(f"❌ Unknown command: {command}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
