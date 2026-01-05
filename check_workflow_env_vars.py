#!/usr/bin/env python3
"""
Workflow Environment Variables Checker
Verifies that all Node.js scripts have required environment variables in workflows
"""

import yaml
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple

# Scripts that require SUPABASE credentials
SUPABASE_REQUIRED_SCRIPTS = {
    'telegram_alert_service.js': ['SUPABASE_URL', 'SUPABASE_SERVICE_KEY'],
    'supabase-sync.js': ['SUPABASE_URL', 'SUPABASE_SERVICE_KEY'],
    'supabase-sync-global.js': ['SUPABASE_URL', 'SUPABASE_SERVICE_KEY'],
    'telegram-alerts-global.js': ['SUPABASE_URL', 'SUPABASE_SERVICE_KEY'],
    'telegram-alerts.js': ['SUPABASE_URL', 'SUPABASE_SERVICE_KEY'],
    'telegram_broadcast.js': ['SUPABASE_URL', 'SUPABASE_SERVICE_ROLE_KEY'],
    'sendgrid_mailer.js': ['SUPABASE_URL', 'SUPABASE_SERVICE_KEY'],
    'weekly_report_generator.js': ['SUPABASE_URL', 'SUPABASE_SERVICE_KEY'],
    'click_tracker.js': ['SUPABASE_URL', 'SUPABASE_SERVICE_KEY'],
}

def find_node_script_calls(workflow_path: Path) -> List[Tuple[str, int, str]]:
    """Find all node script calls in a workflow"""
    with open(workflow_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    calls = []
    for i, line in enumerate(lines, 1):
        if 'node scripts/' in line:
            # Extract script name
            match = re.search(r'node scripts/([a-zA-Z0-9_\-]+\.js)', line)
            if match:
                script_name = match.group(1)
                calls.append((script_name, i, line.strip()))
    
    return calls

def get_step_env_vars(workflow_path: Path, line_number: int) -> Set[str]:
    """Get environment variables defined in the step containing this line"""
    try:
        with open(workflow_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        jobs = data.get('jobs', {})
        
        # Search through all jobs and steps
        for job_name, job_config in jobs.items():
            steps = job_config.get('steps', [])
            
            current_line = 1
            for step in steps:
                # Count lines in this step (approximate)
                step_str = str(step)
                step_lines = step_str.count('\n') + 3  # Rough estimate
                
                if current_line <= line_number <= current_line + step_lines:
                    # Found the step
                    env_vars = step.get('env', {})
                    return set(env_vars.keys())
                
                current_line += step_lines
        
        return set()
    except Exception:
        return set()

def check_workflow_env_vars(workflow_path: Path) -> List[str]:
    """Check if workflow has all required environment variables for its scripts"""
    issues = []
    
    script_calls = find_node_script_calls(workflow_path)
    
    for script_name, line_num, line_content in script_calls:
        if script_name in SUPABASE_REQUIRED_SCRIPTS:
            required_vars = SUPABASE_REQUIRED_SCRIPTS[script_name]
            step_env = get_step_env_vars(workflow_path, line_num)
            
            missing_vars = [var for var in required_vars if var not in step_env]
            
            if missing_vars:
                issues.append(
                    f"  ❌ Line {line_num}: {script_name} missing: {', '.join(missing_vars)}"
                )
    
    return issues

def main():
    workflows_dir = Path('.github/workflows')
    
    if not workflows_dir.exists():
        print("❌ ERROR: .github/workflows directory not found")
        return False
    
    print(f"\n{'='*80}")
    print(f"🔍 CHECKING NODE.JS SCRIPT ENVIRONMENT VARIABLES")
    print(f"{'='*80}\n")
    
    all_issues = []
    workflows_checked = 0
    
    for workflow_path in workflows_dir.glob('*.yml'):
        issues = check_workflow_env_vars(workflow_path)
        
        if issues:
            print(f"⚠️  {workflow_path.name}")
            for issue in issues:
                print(issue)
            print()
            all_issues.extend(issues)
        else:
            script_calls = find_node_script_calls(workflow_path)
            if script_calls:
                print(f"✅ {workflow_path.name}")
        
        workflows_checked += 1
    
    print(f"\n{'='*80}")
    print(f"SUMMARY")
    print(f"{'='*80}\n")
    
    print(f"Workflows checked: {workflows_checked}")
    print(f"Issues found: {len(all_issues)}")
    
    if all_issues:
        print(f"\n❌ ENVIRONMENT VARIABLE ISSUES DETECTED")
        print(f"\nTo fix these issues:")
        print(f"1. Add missing environment variables to the 'env' section of each step")
        print(f"2. Ensure secrets are configured in GitHub repository settings")
        print(f"3. Reference: GITHUB_SECRETS_SETUP_GUIDE.md")
        return False
    else:
        print(f"\n✅ ALL NODE.JS SCRIPTS HAVE REQUIRED ENVIRONMENT VARIABLES")
        return True

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
