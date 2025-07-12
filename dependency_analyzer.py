#!/usr/bin/env python3
"""
Dependency Analyzer for Blade Fighters Refactoring
Analyzes imports, function calls, and data dependencies between modules
"""

import ast
import os
import re
from collections import defaultdict, Counter
from typing import Dict, List, Set, Tuple
import json

class DependencyAnalyzer:
    def __init__(self, root_dir: str = "."):
        self.root_dir = root_dir
        self.python_files = []
        self.dependencies = defaultdict(set)
        self.reverse_dependencies = defaultdict(set)
        self.function_calls = defaultdict(set)
        self.class_usage = defaultdict(set)
        self.data_flow = defaultdict(set)
        
    def find_python_files(self):
        """Find all Python files in the project."""
        for root, dirs, files in os.walk(self.root_dir):
            # Skip common directories that shouldn't be analyzed
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'venv', 'env']]
            
            for file in files:
                if file.endswith('.py'):
                    self.python_files.append(os.path.join(root, file))
    
    def analyze_file(self, file_path: str) -> Dict:
        """Analyze a single Python file for dependencies."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            analyzer = FileAnalyzer(file_path)
            analyzer.visit(tree)
            
            return {
                'imports': analyzer.imports,
                'function_calls': analyzer.function_calls,
                'class_usage': analyzer.class_usage,
                'attributes': analyzer.attributes,
                'lines_of_code': len(content.splitlines())
            }
        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")
            return {}
    
    def analyze_all_files(self):
        """Analyze all Python files in the project."""
        self.find_python_files()
        
        for file_path in self.python_files:
            module_name = os.path.splitext(os.path.basename(file_path))[0]
            analysis = self.analyze_file(file_path)
            
            if analysis:
                # Record imports
                for imported_module in analysis['imports']:
                    self.dependencies[module_name].add(imported_module)
                    self.reverse_dependencies[imported_module].add(module_name)
                
                # Record function calls
                for func_call in analysis['function_calls']:
                    self.function_calls[module_name].add(func_call)
                
                # Record class usage
                for class_name in analysis['class_usage']:
                    self.class_usage[module_name].add(class_name)
    
    def generate_dependency_report(self) -> Dict:
        """Generate a comprehensive dependency report."""
        report = {
            'summary': {
                'total_files': len(self.python_files),
                'total_dependencies': sum(len(deps) for deps in self.dependencies.values()),
                'most_dependent_modules': self.get_most_dependent_modules(),
                'most_used_modules': self.get_most_used_modules()
            },
            'module_analysis': {},
            'coupling_analysis': {},
            'extraction_recommendations': []
        }
        
        # Analyze each module
        for module in self.dependencies:
            report['module_analysis'][module] = {
                'dependencies': list(self.dependencies[module]),
                'dependents': list(self.reverse_dependencies[module]),
                'function_calls': list(self.function_calls[module]),
                'class_usage': list(self.class_usage[module]),
                'coupling_score': self.calculate_coupling_score(module)
            }
        
        # Generate coupling analysis
        report['coupling_analysis'] = self.analyze_coupling()
        
        # Generate extraction recommendations
        report['extraction_recommendations'] = self.generate_extraction_recommendations()
        
        return report
    
    def calculate_coupling_score(self, module: str) -> float:
        """Calculate coupling score for a module (0-1, higher = more coupled)."""
        dependencies = len(self.dependencies[module])
        dependents = len(self.reverse_dependencies[module])
        function_calls = len(self.function_calls[module])
        
        # Normalize scores
        max_deps = max(len(deps) for deps in self.dependencies.values()) if self.dependencies else 1
        max_funcs = max(len(funcs) for funcs in self.function_calls.values()) if self.function_calls else 1
        
        dep_score = dependencies / max_deps
        func_score = function_calls / max_funcs
        
        # Weighted average
        return (dep_score * 0.4 + func_score * 0.6)
    
    def get_most_dependent_modules(self) -> List[Tuple[str, int]]:
        """Get modules with the most dependencies."""
        return sorted(
            [(module, len(deps)) for module, deps in self.dependencies.items()],
            key=lambda x: x[1],
            reverse=True
        )[:5]
    
    def get_most_used_modules(self) -> List[Tuple[str, int]]:
        """Get modules that are imported by the most other modules."""
        return sorted(
            [(module, len(dependents)) for module, dependents in self.reverse_dependencies.items()],
            key=lambda x: x[1],
            reverse=True
        )[:5]
    
    def analyze_coupling(self) -> Dict:
        """Analyze coupling patterns in the codebase."""
        coupling_groups = defaultdict(list)
        
        for module in self.dependencies:
            coupling_score = self.calculate_coupling_score(module)
            
            if coupling_score > 0.7:
                coupling_groups['highly_coupled'].append(module)
            elif coupling_score > 0.4:
                coupling_groups['moderately_coupled'].append(module)
            else:
                coupling_groups['loosely_coupled'].append(module)
        
        return {
            'highly_coupled': coupling_groups['highly_coupled'],
            'moderately_coupled': coupling_groups['moderately_coupled'],
            'loosely_coupled': coupling_groups['loosely_coupled']
        }
    
    def generate_extraction_recommendations(self) -> List[Dict]:
        """Generate recommendations for module extraction order."""
        recommendations = []
        
        # Start with loosely coupled modules
        for module in self.analyze_coupling()['loosely_coupled']:
            recommendations.append({
                'module': module,
                'priority': 'low',
                'reason': 'Loosely coupled, easy to extract',
                'estimated_effort': '1-2 hours'
            })
        
        # Then moderately coupled modules
        for module in self.analyze_coupling()['moderately_coupled']:
            recommendations.append({
                'module': module,
                'priority': 'medium',
                'reason': 'Moderate coupling, requires interface design',
                'estimated_effort': '4-8 hours'
            })
        
        # Finally highly coupled modules
        for module in self.analyze_coupling()['highly_coupled']:
            recommendations.append({
                'module': module,
                'priority': 'high',
                'reason': 'Highly coupled, requires careful planning',
                'estimated_effort': '8-16 hours'
            })
        
        return recommendations
    
    def save_report(self, filename: str = 'dependency_report.json'):
        """Save the dependency report to a JSON file."""
        report = self.generate_dependency_report()
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"Dependency report saved to {filename}")
    
    def print_summary(self):
        """Print a summary of the dependency analysis."""
        report = self.generate_dependency_report()
        
        print("\n" + "="*60)
        print("BLADE FIGHTERS DEPENDENCY ANALYSIS SUMMARY")
        print("="*60)
        
        print(f"\n📊 OVERVIEW:")
        print(f"   Total Python files: {report['summary']['total_files']}")
        print(f"   Total dependencies: {report['summary']['total_dependencies']}")
        
        print(f"\n🔗 MOST DEPENDENT MODULES:")
        for module, count in report['summary']['most_dependent_modules']:
            print(f"   {module}: {count} dependencies")
        
        print(f"\n📈 MOST USED MODULES:")
        for module, count in report['summary']['most_used_modules']:
            print(f"   {module}: {count} dependents")
        
        print(f"\n🔧 COUPLING ANALYSIS:")
        coupling = report['coupling_analysis']
        print(f"   Highly coupled: {len(coupling['highly_coupled'])} modules")
        print(f"   Moderately coupled: {len(coupling['moderately_coupled'])} modules")
        print(f"   Loosely coupled: {len(coupling['loosely_coupled'])} modules")
        
        print(f"\n🎯 EXTRACTION RECOMMENDATIONS:")
        for rec in report['extraction_recommendations'][:5]:  # Top 5
            print(f"   {rec['module']} ({rec['priority']} priority): {rec['reason']}")


class FileAnalyzer(ast.NodeVisitor):
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.imports = set()
        self.function_calls = set()
        self.class_usage = set()
        self.attributes = set()
    
    def visit_Import(self, node):
        for alias in node.names:
            module_name = alias.name.split('.')[0]  # Get base module name
            self.imports.add(module_name)
        self.generic_visit(node)
    
    def visit_ImportFrom(self, node):
        if node.module:
            module_name = node.module.split('.')[0]  # Get base module name
            self.imports.add(module_name)
        self.generic_visit(node)
    
    def visit_Call(self, node):
        if isinstance(node.func, ast.Name):
            self.function_calls.add(node.func.id)
        elif isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Name):
                self.class_usage.add(node.func.value.id)
        self.generic_visit(node)
    
    def visit_Attribute(self, node):
        if isinstance(node.value, ast.Name):
            self.attributes.add(f"{node.value.id}.{node.attr}")
        self.generic_visit(node)


def main():
    """Main function to run the dependency analysis."""
    analyzer = DependencyAnalyzer()
    
    print("🔍 Analyzing Blade Fighters codebase dependencies...")
    analyzer.analyze_all_files()
    
    print("📋 Generating dependency report...")
    analyzer.print_summary()
    
    print("\n💾 Saving detailed report...")
    analyzer.save_report()
    
    print("\n✅ Analysis complete! Check dependency_report.json for detailed results.")


if __name__ == "__main__":
    main() 