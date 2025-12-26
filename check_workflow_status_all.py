#!/usr/bin/env python3
"""Check the status of all GitHub Actions workflow runs."""

import os
import sys
import json
import subprocess
import time
from pathlib import Path
from datetime import datetime, timedelta

# Get the repository info
repo_path = Path(__file__).parent
os.chdir(repo_path)

try:
    result = subprocess.run(
        ["git", "config", "--get", "remote.origin.url"],
        capture_output=True,
        text=True,
        check=True
    )
    remote_url = result.stdout.strip()
    if "github.com" in remote_url:
        if remote_url.endswith(".git"):
            remote_url = remote_url[:-4]
        parts = remote_url.split("/")
        owner = parts[-2]
        repo = parts[-1]
    else:
        print("❌ Not a GitHub repository")
        sys.exit(1)
except Exception as e:
    print(f"❌ Failed to get repository info: {e}")
    sys.exit(1)

github_token = os.environ.get("GITHUB_TOKEN")
if not github_token:
    print("⚠️  GITHUB_TOKEN environment variable not set")
    sys.exit(1)

print(f"📦 Repository: {owner}/{repo}")
print(f"🔍 Checking workflow runs (last 5 minutes)...\n")

# Get workflow runs from the last 5 minutes
try:
    cmd = [
        "curl",
        "-s",
        "-H", "Accept: application/vnd.github.v3+json",
        "-H", f"Authorization: token {github_token}",
        f"https://api.github.com/repos/{owner}/{repo}/actions/runs?per_page=100"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    data = json.loads(result.stdout)
    
    if "workflow_runs" not in data:
        print("❌ Failed to fetch workflow runs")
        sys.exit(1)
    
    # Filter runs from the last 5 minutes
    five_min_ago = datetime.utcnow() - timedelta(minutes=5)
    recent_runs = []
    
    for run in data["workflow_runs"]:
        created_at = datetime.strptime(run["created_at"], "%Y-%m-%dT%H:%M:%SZ")
        if created_at > five_min_ago:
            recent_runs.append(run)
    
    if not recent_runs:
        print("ℹ️  No recent workflow runs found")
        sys.exit(0)
    
    # Status symbols
    status_icons = {
        "completed": "✅" if "success" else "❌",
        "in_progress": "⏳",
        "queued": "⏸️",
        "waiting": "⏸️"
    }
    
    conclusion_icons = {
        "success": "✅",
        "failure": "❌",
        "cancelled": "⚠️",
        "skipped": "⏭️",
        "timed_out": "⏱️",
        None: "⏳"
    }
    
    # Group by workflow name
    workflows = {}
    for run in recent_runs:
        workflow_name = run["name"]
        if workflow_name not in workflows:
            workflows[workflow_name] = []
        workflows[workflow_name].append(run)
    
    # Display results
    print("=" * 70)
    total = 0
    success = 0
    failed = 0
    in_progress = 0
    queued = 0
    
    for workflow_name, runs in sorted(workflows.items()):
        latest_run = runs[0]  # Most recent run
        status = latest_run["status"]
        conclusion = latest_run.get("conclusion")
        
        total += 1
        
        if status == "completed":
            if conclusion == "success":
                icon = "✅"
                success += 1
            elif conclusion == "failure":
                icon = "❌"
                failed += 1
            elif conclusion == "cancelled":
                icon = "⚠️"
            else:
                icon = "❓"
        elif status == "in_progress":
            icon = "⏳"
            in_progress += 1
        else:
            icon = "⏸️"
            queued += 1
        
        duration = ""
        if status == "completed" and "run_started_at" in latest_run:
            start = datetime.strptime(latest_run["run_started_at"], "%Y-%m-%dT%H:%M:%SZ")
            end = datetime.strptime(latest_run["updated_at"], "%Y-%m-%dT%H:%M:%SZ")
            duration_sec = (end - start).total_seconds()
            duration = f" ({int(duration_sec)}s)"
        
        print(f"{icon} {workflow_name:<40} {status:<15} {conclusion or '':<10}{duration}")
        print(f"   🔗 {latest_run['html_url']}")
        print()
    
    print("=" * 70)
    print(f"\n📊 Summary:")
    print(f"  ✅ Success:     {success}")
    print(f"  ❌ Failed:      {failed}")
    print(f"  ⏳ In Progress: {in_progress}")
    print(f"  ⏸️  Queued:      {queued}")
    print(f"  📈 Total:       {total}")
    print("=" * 70)
    
    if in_progress > 0 or queued > 0:
        print("\n💡 Tip: Run this script again in a few minutes to see final results")
    
    if failed > 0:
        print("\n⚠️  Some workflows failed. Check the links above for details.")
        sys.exit(1)
    
except json.JSONDecodeError as e:
    print(f"❌ Failed to parse API response: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
