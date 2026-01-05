#!/usr/bin/env python3
"""
Workflow Execution Simulation Tests
Validates workflow structure, environment variables, and execution paths
"""

import yaml
import sys
import re
from pathlib import Path
from typing import Dict, List, Set

class WorkflowExecutionTester:
    def __init__(self, workflows_dir: Path):
        self.workflows_dir = workflows_dir
        self.workflows = list(workflows_dir.glob('*.yml'))
        self.all_secrets = set()
        self.all_envs = set()
        self.issues = []
        
    def test_execution_paths(self):
        """Test all execution paths and configurations"""
        print(f"\n{'='*80}")
        print(f"🔬 WORKFLOW EXECUTION PATH ANALYSIS")
        print(f"{'='*80}\n")
        
        for workflow in self.workflows:
            try:
                with open(workflow, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                    content = f.read()
                
                print(f"\n📋 {workflow.name}")
                print("-" * 80)
                
                # Test schedule configuration
                self.check_schedule(workflow.name, data)
                
                # Test environment variables
                self.check_environment_vars(workflow.name, data, content)
                
                # Test action versions
                self.check_action_versions(workflow.name, content)
                
                # Test script references
                self.check_script_references(workflow.name, content)
                
                # Test Python/Node setup
                self.check_runtime_setup(workflow.name, content)
                
            except Exception as e:
                print(f"  ❌ Error analyzing: {str(e)}")
                self.issues.append(f"{workflow.name}: Analysis error")
        
        self.print_execution_summary()
        
    def check_schedule(self, name: str, data: Dict):
        """Check schedule configuration"""
        on_config = data.get('on') or data.get(True)
        
        if not on_config:
            print(f"  ⚠️  Schedule: No trigger configured")
            return
        
        if isinstance(on_config, dict):
            triggers = []
            if 'schedule' in on_config:
                cron_jobs = on_config['schedule']
                if isinstance(cron_jobs, list):
                    triggers.append(f"cron ({len(cron_jobs)} schedules)")
            if 'workflow_dispatch' in on_config:
                triggers.append("manual")
            if 'push' in on_config:
                triggers.append("push")
            if 'pull_request' in on_config:
                triggers.append("PR")
            
            print(f"  ✅ Triggers: {', '.join(triggers) if triggers else 'configured'}")
        else:
            print(f"  ✅ Triggers: Configured")
    
    def check_environment_vars(self, name: str, data: Dict, content: str):
        """Check environment variable usage"""
        # Global env vars
        global_env = data.get('env', {})
        
        # Extract all env references
        env_refs = re.findall(r'\$\{\{\s*env\.([A-Z_]+)\s*\}\}', content)
        secrets_refs = re.findall(r'\$\{\{\s*secrets\.([A-Z_]+)\s*\}\}', content)
        
        self.all_secrets.update(secrets_refs)
        
        total_env = len(set(env_refs)) + len(global_env)
        total_secrets = len(set(secrets_refs))
        
        if total_env > 0 or total_secrets > 0:
            print(f"  ✅ Variables: {total_env} env, {total_secrets} secrets")
        else:
            print(f"  ℹ️  Variables: None defined")
    
    def check_action_versions(self, name: str, content: str):
        """Check GitHub Actions versions"""
        actions = re.findall(r'uses:\s+([^\s]+@v\d+)', content)
        
        if not actions:
            print(f"  ⚠️  Actions: No versioned actions found")
            return
        
        # Count by version
        v3_count = sum(1 for a in actions if '@v3' in a)
        v4_count = sum(1 for a in actions if '@v4' in a)
        v5_count = sum(1 for a in actions if '@v5' in a)
        
        versions = []
        if v5_count:
            versions.append(f"v5({v5_count})")
        if v4_count:
            versions.append(f"v4({v4_count})")
        if v3_count:
            versions.append(f"v3({v3_count})")
        
        status = "✅" if v3_count == 0 else "⚠️ "
        print(f"  {status} Actions: {', '.join(versions)}")
        
        if v3_count > 0:
            self.issues.append(f"{name}: Using deprecated @v3 actions")
    
    def check_script_references(self, name: str, content: str):
        """Check script file references"""
        # Find Python scripts
        python_scripts = re.findall(r'python\s+([^\s]+\.py)', content)
        # Find Node scripts
        node_scripts = re.findall(r'node\s+([^\s]+\.js)', content)
        
        all_scripts = set(python_scripts + node_scripts)
        
        if all_scripts:
            print(f"  ✅ Scripts: {len(all_scripts)} referenced")
            
            # Check if scripts exist
            missing = []
            for script in all_scripts:
                script_path = Path(script)
                if not script_path.exists():
                    missing.append(script_path.name)
            
            if missing:
                print(f"     ⚠️  Missing: {', '.join(missing[:3])}")
                self.issues.append(f"{name}: Missing scripts")
        else:
            print(f"  ℹ️  Scripts: None referenced")
    
    def check_runtime_setup(self, name: str, content: str):
        """Check Python/Node.js runtime setup"""
        has_python = 'setup-python@' in content
        has_node = 'setup-node@' in content
        
        runtimes = []
        if has_python:
            # Extract Python version
            py_version = re.search(r'python-version:\s*[\'"]?([0-9.]+)', content)
            if py_version:
                runtimes.append(f"Python {py_version.group(1)}")
            else:
                runtimes.append("Python")
        
        if has_node:
            # Extract Node version
            node_version = re.search(r'node-version:\s*[\'"]?([0-9.]+)', content)
            if node_version:
                runtimes.append(f"Node {node_version.group(1)}")
            else:
                runtimes.append("Node")
        
        if runtimes:
            print(f"  ✅ Runtimes: {', '.join(runtimes)}")
        else:
            print(f"  ℹ️  Runtimes: None configured")
    
    def print_execution_summary(self):
        """Print execution test summary"""
        print(f"\n{'='*80}")
        print(f"EXECUTION TEST SUMMARY")
        print(f"{'='*80}\n")
        
        print(f"📊 Workflows Analyzed: {len(self.workflows)}")
        print(f"🔑 Unique Secrets: {len(self.all_secrets)}")
        print(f"⚠️  Issues Found: {len(self.issues)}")
        
        if self.issues:
            print(f"\n⚠️  ISSUES DETECTED:")
            for issue in self.issues[:10]:
                print(f"  • {issue}")
        else:
            print(f"\n✅ NO CRITICAL ISSUES DETECTED")
        
        print(f"\n{'='*80}")
        print(f"SECRET INVENTORY ({len(self.all_secrets)} total)")
        print(f"{'='*80}")
        
        # Group secrets by category
        supabase = [s for s in self.all_secrets if 'SUPABASE' in s]
        telegram = [s for s in self.all_secrets if 'TELEGRAM' in s]
        google = [s for s in self.all_secrets if 'GOOGLE' in s]
        other = [s for s in self.all_secrets if s not in supabase + telegram + google]
        
        if supabase:
            print(f"\n📊 Supabase ({len(supabase)}):")
            for s in sorted(supabase):
                print(f"  • {s}")
        
        if telegram:
            print(f"\n📱 Telegram ({len(telegram)}):")
            for s in sorted(telegram):
                print(f"  • {s}")
        
        if google:
            print(f"\n🔍 Google ({len(google)}):")
            for s in sorted(google):
                print(f"  • {s}")
        
        if other:
            print(f"\n🔧 Other ({len(other)}):")
            for s in sorted(other):
                print(f"  • {s}")

def main():
    workflows_dir = Path('.github/workflows')
    
    if not workflows_dir.exists():
        print("❌ ERROR: .github/workflows directory not found")
        sys.exit(1)
    
    tester = WorkflowExecutionTester(workflows_dir)
    tester.test_execution_paths()
    
    sys.exit(0 if len(tester.issues) == 0 else 1)

if __name__ == "__main__":
    main()
