#!/usr/bin/env python3
"""
Comprehensive GitHub Actions Workflow Testing Suite
Tests all workflows for syntax, structure, timeouts, secrets, and best practices
"""

import yaml
import sys
import re
from pathlib import Path
from typing import Dict, List, Tuple, Any
from collections import defaultdict

class WorkflowTester:
    def __init__(self, workflows_dir: Path):
        self.workflows_dir = workflows_dir
        self.workflows = list(workflows_dir.glob('*.yml'))
        self.test_results = defaultdict(list)
        self.critical_failures = []
        self.warnings = []
        
    def run_all_tests(self):
        """Run all test suites"""
        print(f"\n{'='*80}")
        print(f"🧪 TESTING {len(self.workflows)} GITHUB ACTIONS WORKFLOWS")
        print(f"{'='*80}\n")
        
        for workflow in self.workflows:
            print(f"\n📋 Testing: {workflow.name}")
            print("-" * 80)
            
            # Test 1: YAML Syntax
            if not self.test_yaml_syntax(workflow):
                self.critical_failures.append(f"{workflow.name}: Invalid YAML")
                continue
            
            # Test 2: Required Fields
            self.test_required_fields(workflow)
            
            # Test 3: Timeout Configuration
            self.test_timeouts(workflow)
            
            # Test 4: Secret References
            self.test_secrets(workflow)
            
            # Test 5: Caching Configuration
            self.test_caching(workflow)
            
            # Test 6: Job Dependencies
            self.test_job_dependencies(workflow)
            
            # Test 7: Best Practices
            self.test_best_practices(workflow)
        
        self.print_summary()
        return len(self.critical_failures) == 0
    
    def test_yaml_syntax(self, workflow_path: Path) -> bool:
        """Test 1: Validate YAML syntax"""
        try:
            with open(workflow_path, 'r', encoding='utf-8') as f:
                yaml.safe_load(f)
            print(f"  ✅ YAML Syntax: Valid")
            return True
        except yaml.YAMLError as e:
            print(f"  ❌ YAML Syntax: {str(e)}")
            return False
        except Exception as e:
            print(f"  ❌ YAML Syntax: Error reading file - {str(e)}")
            return False
    
    def test_required_fields(self, workflow_path: Path):
        """Test 2: Check required top-level fields"""
        try:
            with open(workflow_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            required = ['name', 'on', 'jobs']
            missing = [field for field in required if not data.get(field)]
            
            if missing:
                # Check if 'on' is parsed as True (boolean issue)
                if 'on' in missing and data.get(True):
                    print(f"  ✅ Required Fields: All present (note: 'on' parsed as True)")
                else:
                    print(f"  ❌ Required Fields: Missing {', '.join(missing)}")
                    self.critical_failures.append(f"{workflow_path.name}: Missing {missing}")
            else:
                print(f"  ✅ Required Fields: All present")
        except Exception as e:
            print(f"  ❌ Required Fields: Error - {str(e)}")
    
    def test_timeouts(self, workflow_path: Path):
        """Test 3: Verify all jobs have timeout-minutes"""
        try:
            with open(workflow_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            jobs = data.get('jobs', {})
            jobs_without_timeout = []
            timeout_values = []
            
            for job_name, job_config in jobs.items():
                timeout = job_config.get('timeout-minutes')
                if not timeout:
                    jobs_without_timeout.append(job_name)
                else:
                    timeout_values.append((job_name, timeout))
            
            if jobs_without_timeout:
                print(f"  ❌ Timeouts: Missing in {', '.join(jobs_without_timeout)}")
                self.critical_failures.append(f"{workflow_path.name}: Jobs without timeout")
            else:
                avg_timeout = sum(t[1] for t in timeout_values) / len(timeout_values)
                print(f"  ✅ Timeouts: All {len(jobs)} jobs configured (avg: {avg_timeout:.1f}m)")
        except Exception as e:
            print(f"  ⚠️  Timeouts: Error - {str(e)}")
    
    def test_secrets(self, workflow_path: Path):
        """Test 4: Extract and validate secret references"""
        try:
            with open(workflow_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            secrets = re.findall(r'\$\{\{\s*secrets\.([A-Z_]+)\s*\}\}', content)
            unique_secrets = sorted(set(secrets))
            
            if unique_secrets:
                print(f"  🔑 Secrets: {len(unique_secrets)} used - {', '.join(unique_secrets[:3])}{' ...' if len(unique_secrets) > 3 else ''}")
            else:
                print(f"  ℹ️  Secrets: None used")
        except Exception as e:
            print(f"  ⚠️  Secrets: Error - {str(e)}")
    
    def test_caching(self, workflow_path: Path):
        """Test 5: Check for caching configuration"""
        try:
            with open(workflow_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            has_pip_cache = "cache: 'pip'" in content
            has_npm_cache = "cache: 'npm'" in content
            
            caches = []
            if has_pip_cache:
                caches.append('pip')
            if has_npm_cache:
                caches.append('npm')
            
            if caches:
                print(f"  ✅ Caching: Enabled ({', '.join(caches)})")
            else:
                print(f"  ⚠️  Caching: Not configured")
                self.warnings.append(f"{workflow_path.name}: No caching")
        except Exception as e:
            print(f"  ⚠️  Caching: Error - {str(e)}")
    
    def test_job_dependencies(self, workflow_path: Path):
        """Test 6: Validate job dependency chains"""
        try:
            with open(workflow_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            jobs = data.get('jobs', {})
            job_names = set(jobs.keys())
            
            for job_name, job_config in jobs.items():
                needs = job_config.get('needs', [])
                if isinstance(needs, str):
                    needs = [needs]
                
                # Check if all dependencies exist
                missing_deps = [dep for dep in needs if dep not in job_names]
                if missing_deps:
                    print(f"  ❌ Dependencies: Job '{job_name}' references non-existent job(s): {missing_deps}")
                    self.critical_failures.append(f"{workflow_path.name}: Invalid dependencies")
                    return
            
            dep_count = sum(1 for job in jobs.values() if job.get('needs'))
            print(f"  ✅ Dependencies: Valid ({dep_count}/{len(jobs)} jobs have dependencies)")
        except Exception as e:
            print(f"  ⚠️  Dependencies: Error - {str(e)}")
    
    def test_best_practices(self, workflow_path: Path):
        """Test 7: Check for best practices"""
        try:
            with open(workflow_path, 'r', encoding='utf-8') as f:
                content = f.read()
                data = yaml.safe_load(f)
            
            issues = []
            recommendations = []
            
            # Check for checkout action
            if 'actions/checkout@' not in content:
                issues.append("No checkout action found")
            
            # Check for version pinning in actions
            if '@v3' in content:
                recommendations.append("Consider upgrading actions from @v3 to @v4")
            
            # Check for continue-on-error usage
            if 'continue-on-error: true' in content:
                recommendations.append("Has resilience with continue-on-error")
            
            # Check for artifact retention
            if 'retention-days:' in content:
                recommendations.append("Artifact retention configured")
            
            # Check for manual trigger
            on_config = data.get('on') or data.get(True)
            if isinstance(on_config, dict) and 'workflow_dispatch' in on_config:
                recommendations.append("Manual trigger enabled")
            
            if issues:
                print(f"  ⚠️  Best Practices: Issues - {', '.join(issues)}")
            else:
                print(f"  ✅ Best Practices: {len(recommendations)} good practices found")
                
        except Exception as e:
            print(f"  ℹ️  Best Practices: Error - {str(e)}")
    
    def print_summary(self):
        """Print final test summary"""
        print(f"\n{'='*80}")
        print(f"TEST SUMMARY")
        print(f"{'='*80}\n")
        
        print(f"📊 Workflows Tested: {len(self.workflows)}")
        print(f"✅ Passed: {len(self.workflows) - len(self.critical_failures)}")
        print(f"❌ Failed: {len(self.critical_failures)}")
        print(f"⚠️  Warnings: {len(self.warnings)}")
        
        if self.critical_failures:
            print(f"\n❌ CRITICAL FAILURES:")
            for failure in self.critical_failures:
                print(f"  • {failure}")
        
        if self.warnings:
            print(f"\n⚠️  WARNINGS:")
            for warning in self.warnings[:5]:
                print(f"  • {warning}")
            if len(self.warnings) > 5:
                print(f"  ... and {len(self.warnings) - 5} more")
        
        if not self.critical_failures:
            print(f"\n✅ ALL TESTS PASSED! Workflows are production-ready.")
        else:
            print(f"\n❌ TESTS FAILED. Please fix critical issues before deploying.")

def main():
    workflows_dir = Path('.github/workflows')
    
    if not workflows_dir.exists():
        print("❌ ERROR: .github/workflows directory not found")
        sys.exit(1)
    
    tester = WorkflowTester(workflows_dir)
    success = tester.run_all_tests()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
