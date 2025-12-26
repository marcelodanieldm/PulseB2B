#!/usr/bin/env python3
"""Trigger all GitHub Actions workflows that support workflow_dispatch."""

import os
import sys
import json
import subprocess
from pathlib import Path

# Get the repository info
repo_path = Path(__file__).parent
os.chdir(repo_path)

# Get repo name from git remote
try:
    result = subprocess.run(
        ["git", "config", "--get", "remote.origin.url"],
        capture_output=True,
        text=True,
        check=True
    )
    remote_url = result.stdout.strip()
    # Parse GitHub owner/repo from URL
    if "github.com" in remote_url:
        if remote_url.endswith(".git"):
            remote_url = remote_url[:-4]
        if ":" in remote_url and "@" in remote_url:  # SSH format
            repo_info = remote_url.split(":")[-1]
        else:  # HTTPS format
            parts = remote_url.split("/")
            owner = parts[-2]
            repo = parts[-1]
    else:
        print("❌ Not a GitHub repository")
        sys.exit(1)
except Exception as e:
    print(f"❌ Failed to get repository info: {e}")
    sys.exit(1)

# List of workflows to trigger
workflows = [
    "serverless-ghost-pipeline.yml",
    "test-and-report-telegram.yml",
    "oracle-ghost-automation.yml",
    "critical-funding-alert.yml",
    "regional-arbitrage-alert.yml",
    "high-value-lead-alert.yml",
    "pulse-90-alert.yml",
    "weekly-digest.yml",
    "weekly_lead_digest.yml",
    "weekly_email_reports.yml",
    "telegram_daily_broadcast.yml",
    "multi_region_pipeline.yml",
    "lead-scraping.yml",
    "generate_daily_teaser.yml",
    "daily_scrape.yml"
]

print(f"📦 Repository: {owner}/{repo}")
print(f"🚀 Triggering {len(workflows)} workflows...\n")

# Check if GITHUB_TOKEN is set
github_token = os.environ.get("GITHUB_TOKEN")
if not github_token:
    print("⚠️  GITHUB_TOKEN environment variable not set")
    print("Please set it with: $env:GITHUB_TOKEN='your_token_here' (PowerShell)")
    print("Or create a Personal Access Token at: https://github.com/settings/tokens")
    sys.exit(1)

# Trigger each workflow
success_count = 0
failed_count = 0

for workflow in workflows:
    workflow_name = workflow.replace(".yml", "").replace("_", " ").replace("-", " ").title()
    print(f"⚡ Triggering: {workflow_name}")
    
    try:
        # Use curl to trigger the workflow via GitHub API
        cmd = [
            "curl",
            "-X", "POST",
            "-H", "Accept: application/vnd.github.v3+json",
            "-H", f"Authorization: token {github_token}",
            f"https://api.github.com/repos/{owner}/{repo}/actions/workflows/{workflow}/dispatches",
            "-d", '{"ref":"main"}'
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.returncode == 0:
            print(f"  ✅ Triggered successfully")
            success_count += 1
        else:
            print(f"  ❌ Failed: {result.stderr}")
            failed_count += 1
            
    except Exception as e:
        print(f"  ❌ Error: {e}")
        failed_count += 1
    
    print()

print("\n" + "="*50)
print(f"📊 Summary:")
print(f"  ✅ Success: {success_count}")
print(f"  ❌ Failed: {failed_count}")
print(f"  📈 Total: {len(workflows)}")
print("="*50)

if success_count > 0:
    print(f"\n🌐 Check workflow runs at:")
    print(f"   https://github.com/{owner}/{repo}/actions")
