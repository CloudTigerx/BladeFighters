#!/usr/bin/env python3
"""
Dependency Validator for BladeFighters Modules

This tool validates cross-module dependencies and integration points with GameStateManager,
ensuring proper module integration and detecting potential conflicts.
"""

import argparse
import json
import sys
import ast
from pathlib import Path
from typing import Dict, List, Any, Set, Optional
from datetime import datetime
import importlib.util

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class DependencyValidator:
    """Validates module dependencies and integration points."""
    
    def __init__(self, module_name: str):
        self.module_name = module_name
        self.module_path = Path(f"modules/{module_name}")
        self.results = {
            "module": module_name,
            "timestamp": datetime.now().isoformat(),
            "dependencies": {},
            "integration_points": {},
            "conflicts": [],
            "validation_score": 0.0
        }
    
    def analyze_module_dependencies(self) -> Dict[str, Any]:
        """Analyze module dependencies by parsing Python files."""
        print(f"🔍 Analyzing dependencies for {self.module_name}")
        
        dependencies = {
            "internal_deps": [],
            "external_deps": [],
            "game_state_deps": [],
            "cross_module_deps": [],
            "file_dependencies": {}
        }
        
        if not self.module_path.exists():
            return {"error": f"Module path {self.module_path} does not exist"}
        
        # Analyze all Python files in the module
        for py_file in self.module_path.rglob("*.py"):
            if py_file.name.startswith("__"):
                continue
            
            file_deps = self.analyze_file_dependencies(py_file)
            dependencies["file_dependencies"][str(py_file.relative_to(self.module_path))] = file_deps
            
            # Collect all dependencies
            for dep_type, deps in file_deps.items():
                if dep_type in dependencies:
                    dependencies[dep_type].extend(deps)
        
        # Remove duplicates
        for key in dependencies:
            if isinstance(dependencies[key], list):
                dependencies[key] = list(set(dependencies[key]))
        
        return dependencies
    
    def analyze_file_dependencies(self, file_path: Path) -> Dict[str, List[str]]:
        """Analyze dependencies in a single Python file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            imports = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    for alias in node.names:
                        if module:
                            imports.append(f"{module}.{alias.name}")
                        else:
                            imports.append(alias.name)
            
            # Categorize dependencies
            internal_deps = []
            external_deps = []
            game_state_deps = []
            cross_module_deps = []
            
            for imp in imports:
                if imp.startswith("modules.game_state_module"):
                    game_state_deps.append(imp)
                elif imp.startswith("modules."):
                    cross_module_deps.append(imp)
                elif imp.startswith("core."):
                    internal_deps.append(imp)
                else:
                    external_deps.append(imp)
            
            return {
                "internal_deps": internal_deps,
                "external_deps": external_deps,
                "game_state_deps": game_state_deps,
                "cross_module_deps": cross_module_deps
            }
            
        except Exception as e:
            return {"error": f"Failed to parse {file_path}: {e}"}
    
    def validate_game_state_integration(self) -> Dict[str, Any]:
        """Validate integration with GameStateManager."""
        print(f"🔗 Validating GameStateManager integration for {self.module_name}")
        
        integration_points = {
            "state_operations": [],
            "state_schema_compliance": False,
            "state_validation": False,
            "state_persistence": False,
            "integration_score": 0.0
        }
        
        try:
            # Check if module has GameStateManager integration
            module_files = list(self.module_path.rglob("*.py"))
            
            for file_path in module_files:
                if file_path.name.startswith("__"):
                    continue
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for GameStateManager usage
                if "GameStateManager" in content:
                    integration_points["state_operations"].append(str(file_path.relative_to(self.module_path)))
                
                # Check for state schema compliance
                if "state_schema" in content or "StateSchema" in content:
                    integration_points["state_schema_compliance"] = True
                
                # Check for state validation
                if "validate_state" in content or "state_validator" in content:
                    integration_points["state_validation"] = True
                
                # Check for state persistence
                if "save_state" in content or "load_state" in content or "persist" in content:
                    integration_points["state_persistence"] = True
            
            # Calculate integration score
            score = 0.0
            if integration_points["state_operations"]:
                score += 30.0
            if integration_points["state_schema_compliance"]:
                score += 25.0
            if integration_points["state_validation"]:
                score += 25.0
            if integration_points["state_persistence"]:
                score += 20.0
            
            integration_points["integration_score"] = score
            
            return integration_points
            
        except Exception as e:
            return {"error": f"Failed to validate GameStateManager integration: {e}"}
    
    def detect_cross_module_conflicts(self) -> List[Dict[str, Any]]:
        """Detect potential conflicts with other modules."""
        print(f"⚠️ Detecting cross-module conflicts for {self.module_name}")
        
        conflicts = []
        
        try:
            # Check for naming conflicts
            module_files = list(self.module_path.rglob("*.py"))
            module_classes = []
            module_functions = []
            
            for file_path in module_files:
                if file_path.name.startswith("__"):
                    continue
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    tree = ast.parse(content)
                    
                    for node in ast.walk(tree):
                        if isinstance(node, ast.ClassDef):
                            module_classes.append(node.name)
                        elif isinstance(node, ast.FunctionDef):
                            module_functions.append(node.name)
                
                except Exception:
                    continue
            
            # Check for conflicts with other modules
            other_modules = ['audio_module', 'screen_module', 'input_module', 'settings_module']
            
            for other_module in other_modules:
                if other_module == self.module_name:
                    continue
                
                other_module_path = Path(f"modules/{other_module}")
                if not other_module_path.exists():
                    continue
                
                other_classes = []
                other_functions = []
                
                for py_file in other_module_path.rglob("*.py"):
                    if py_file.name.startswith("__"):
                        continue
                    
                    try:
                        with open(py_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        tree = ast.parse(content)
                        
                        for node in ast.walk(tree):
                            if isinstance(node, ast.ClassDef):
                                other_classes.append(node.name)
                            elif isinstance(node, ast.FunctionDef):
                                other_functions.append(node.name)
                    
                    except Exception:
                        continue
                
                # Check for class name conflicts
                class_conflicts = set(module_classes) & set(other_classes)
                if class_conflicts:
                    conflicts.append({
                        "type": "class_name_conflict",
                        "module": other_module,
                        "conflicts": list(class_conflicts),
                        "severity": "high"
                    })
                
                # Check for function name conflicts
                function_conflicts = set(module_functions) & set(other_functions)
                if function_conflicts:
                    conflicts.append({
                        "type": "function_name_conflict",
                        "module": other_module,
                        "conflicts": list(function_conflicts),
                        "severity": "medium"
                    })
            
            return conflicts
            
        except Exception as e:
            return [{"error": f"Failed to detect conflicts: {e}"}]
    
    def validate_module_structure(self) -> Dict[str, Any]:
        """Validate module structure and organization."""
        print(f"📁 Validating module structure for {self.module_name}")
        
        structure = {
            "has_init": False,
            "has_tests": False,
            "has_docs": False,
            "has_migration_guide": False,
            "has_integration_guide": False,
            "structure_score": 0.0
        }
        
        # Check for __init__.py
        if (self.module_path / "__init__.py").exists():
            structure["has_init"] = True
            structure["structure_score"] += 20.0
        
        # Check for tests directory
        if (self.module_path / "tests").exists():
            structure["has_tests"] = True
            structure["structure_score"] += 25.0
        
        # Check for documentation
        if (self.module_path / "README.md").exists():
            structure["has_docs"] = True
            structure["structure_score"] += 20.0
        
        # Check for migration guide
        if (self.module_path / "MIGRATION_GUIDE.md").exists():
            structure["has_migration_guide"] = True
            structure["structure_score"] += 15.0
        
        # Check for integration guide
        if (self.module_path / "INTEGRATION_GUIDE.md").exists():
            structure["has_integration_guide"] = True
            structure["structure_score"] += 20.0
        
        return structure
    
    def run_validation(self) -> Dict[str, Any]:
        """Run complete dependency validation."""
        print(f"🚀 Running complete validation for {self.module_name}")
        
        # Analyze dependencies
        self.results["dependencies"] = self.analyze_module_dependencies()
        
        # Validate GameStateManager integration
        self.results["integration_points"] = self.validate_game_state_integration()
        
        # Detect conflicts
        self.results["conflicts"] = self.detect_cross_module_conflicts()
        
        # Validate structure
        self.results["structure"] = self.validate_module_structure()
        
        # Calculate overall validation score
        self.results["validation_score"] = self.calculate_validation_score()
        
        return self.results
    
    def calculate_validation_score(self) -> float:
        """Calculate overall validation score (0-100)."""
        score = 0.0
        
        # Structure score (max 30 points)
        if "structure" in self.results:
            score += min(30, self.results["structure"]["structure_score"])
        
        # Integration score (max 40 points)
        if "integration_points" in self.results and "integration_score" in self.results["integration_points"]:
            score += min(40, self.results["integration_points"]["integration_score"])
        
        # Dependency health (max 20 points)
        if "dependencies" in self.results:
            deps = self.results["dependencies"]
            if "game_state_deps" in deps and deps["game_state_deps"]:
                score += 10
            if "cross_module_deps" in deps and len(deps["cross_module_deps"]) <= 5:
                score += 10
        
        # Conflict penalty (max -10 points)
        if "conflicts" in self.results:
            conflict_penalty = len(self.results["conflicts"]) * 2
            score -= min(10, conflict_penalty)
        
        return max(0, round(score, 1))


def main():
    """Main CLI interface for dependency validation."""
    parser = argparse.ArgumentParser(description="Dependency validation for BladeFighters modules")
    parser.add_argument("--module", required=True, help="Module name to validate")
    parser.add_argument("--output", required=True, help="Output JSON file path")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    if args.verbose:
        print(f"🔧 Starting dependency validation for module: {args.module}")
    
    # Run validation
    validator = DependencyValidator(args.module)
    results = validator.run_validation()
    
    # Save results
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    if args.verbose:
        print(f"📊 Validation Score: {results.get('validation_score', 'N/A')}")
        print(f"⚠️ Conflicts Found: {len(results.get('conflicts', []))}")
        print(f"💾 Results saved to: {output_path}")
    
    # Exit with error code if validation score is low or conflicts exist
    validation_score = results.get('validation_score', 100)
    conflicts = results.get('conflicts', [])
    
    if validation_score < 70:
        print(f"⚠️ Warning: Low validation score ({validation_score})")
        sys.exit(1)
    
    if conflicts:
        print(f"⚠️ Warning: {len(conflicts)} conflicts detected")
        sys.exit(1)
    
    print(f"✅ Dependency validation completed for {args.module}")


if __name__ == "__main__":
    main()
