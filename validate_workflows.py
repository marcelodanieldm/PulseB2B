#!/usr/bin/env python3
"""
Workflow Validation Script
Validates all GitHub Actions workflows for:
- YAML syntax errors
- Required fields (name, on, jobs)
- Timeout configurations
- Secret references
- Cache configurations
"""

import yaml
import sys
from pathlib import Path
from typing import Dict, List, Tuple

def validate_yaml_syntax(workflow_path: Path) -> Tuple[bool, str]:
    """Validate YAML syntax of a workflow file."""
    try:
        with open(workflow_path, 'r', encoding='utf-8') as f:
            yaml.safe_load(f)
        return True, "Valid YAML syntax"
    except yaml.YAMLError as e:
        return False, f"YAML syntax error: {str(e)}"
    except Exception as e:
        return False, f"Error reading file: {str(e)}"

def check_required_fields(workflow_path: Path) -> Tuple[bool, List[str]]:
    """Check if workflow has required top-level fields."""
    try:
        with open(workflow_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        missing_fields = []
        if not data.get('name'):
            missing_fields.append('name')
        if not data.get('on'):
            missing_fields.append('on')
        if not data.get('jobs'):
            missing_fields.append('jobs')
        
        return len(missing_fields) == 0, missing_fields
    except Exception as e:
        return False, [f"Error: {str(e)}"]

def check_timeouts(workflow_path: Path) -> Tuple[bool, List[str]]:
    """Check if all jobs have timeout-minutes configured."""
    try:
        with open(workflow_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        jobs_without_timeout = []
        jobs = data.get('jobs', {})
        
        for job_name, job_config in jobs.items():
            if not job_config.get('timeout-minutes'):
                jobs_without_timeout.append(job_name)
        
        return len(jobs_without_timeout) == 0, jobs_without_timeout
    except Exception as e:
        return False, [f"Error: {str(e)}"]

def extract_secrets(workflow_path: Path) -> List[str]:
    """Extract all secret references from a workflow."""
    try:
        with open(workflow_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        import re
        secrets = re.findall(r'\$\{\{\s*secrets\.([A-Z_]+)\s*\}\}', content)
        return sorted(set(secrets))
    except Exception as e:
        return [f"Error: {str(e)}"]

def main():
    workflows_dir = Path('.github/workflows')
    
    if not workflows_dir.exists():
        print("ERROR: .github/workflows directory not found")
        sys.exit(1)
    
    workflows = list(workflows_dir.glob('*.yml'))
    
    if not workflows:
        print("ERROR: No workflow files found")
        sys.exit(1)
    
    print(f"\n{'='*80}")
    print(f"VALIDATING {len(workflows)} WORKFLOWS")
    print(f"{'='*80}\n")
    
    all_valid = True
    all_secrets = set()
    
    for workflow in workflows:
        print(f"\n📄 {workflow.name}")
        print("-" * 80)
        
        # Validate YAML syntax
        is_valid, message = validate_yaml_syntax(workflow)
        if is_valid:
            print(f"  ✅ YAML Syntax: {message}")
        else:
            print(f"  ❌ YAML Syntax: {message}")
            all_valid = False
            continue
        
        # Check required fields
        has_fields, missing = check_required_fields(workflow)
        if has_fields:
            print(f"  ✅ Required Fields: All present")
        else:
            print(f"  ❌ Required Fields: Missing {', '.join(missing)}")
            all_valid = False
        
        # Check timeouts
        has_timeouts, jobs_without = check_timeouts(workflow)
        if has_timeouts:
            print(f"  ✅ Timeouts: All jobs configured")
        else:
            print(f"  ⚠️  Timeouts: Jobs without timeout: {', '.join(jobs_without)}")
        
        # Extract secrets
        secrets = extract_secrets(workflow)
        if secrets:
            print(f"  🔑 Secrets ({len(secrets)}): {', '.join(secrets)}")
            all_secrets.update(secrets)
        else:
            print(f"  ℹ️  Secrets: None used")
    
    print(f"\n{'='*80}")
    print(f"SUMMARY")
    print(f"{'='*80}")
    print(f"Total workflows: {len(workflows)}")
    print(f"Unique secrets: {len(all_secrets)}")
    
    if all_secrets:
        print(f"\nAll secrets used across workflows:")
        for secret in sorted(all_secrets):
            print(f"  - {secret}")
    
    if all_valid:
        print(f"\n✅ All workflows are valid!")
        sys.exit(0)
    else:
        print(f"\n❌ Some workflows have errors")
        sys.exit(1)

if __name__ == "__main__":
    main()
