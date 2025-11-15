#!/usr/bin/env python3
"""
Audit non-forked repos for LICENSE files and create PRs for missing licenses.

Usage:
    python license_audit.py --dry-run    # List repos without LICENSE
    python license_audit.py              # Create PRs for missing licenses
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path

def run_command(cmd, cwd=None, capture=True):
    """Run shell command and return output."""
    try:
        if capture:
            result = subprocess.run(
                cmd, 
                shell=True, 
                cwd=cwd, 
                capture_output=True, 
                text=True,
                check=True
            )
            return result.stdout.strip()
        else:
            subprocess.run(cmd, shell=True, cwd=cwd, check=True)
            return None
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {cmd}")
        print(f"Error: {e.stderr}")
        return None

def is_git_repo(path):
    """Check if directory is a git repository."""
    return (path / ".git").exists()

def is_forked_repo(repo_path):
    """Check if repo is a fork using gh CLI."""
    result = run_command("gh repo view --json isFork --jq .isFork", cwd=repo_path)
    return result == "true" if result else False

def has_license_file(repo_path):
    """Check for LICENSE file (exact name, not LICENSE.md)."""
    return (repo_path / "LICENSE").exists()

def get_repo_name(repo_path):
    """Get repository name from gh CLI."""
    result = run_command("gh repo view --json nameWithOwner --jq .nameWithOwner", cwd=repo_path)
    return result if result else repo_path.name

def create_license_pr(repo_path, source_license, dry_run=False):
    """Create PR to add LICENSE file to repo."""
    repo_name = get_repo_name(repo_path)
    branch_name = "add-license"
    
    print(f"\n{'[DRY RUN] ' if dry_run else ''}Processing: {repo_name}")
    
    if dry_run:
        print(f"  Would create PR to add LICENSE file")
        return True
    
    # Store current branch
    current_branch = run_command("git branch --show-current", cwd=repo_path)
    
    try:
        # Create and checkout new branch
        print(f"  Creating branch: {branch_name}")
        run_command(f"git checkout -b {branch_name}", cwd=repo_path)
        
        # Copy LICENSE file
        print(f"  Copying LICENSE file")
        dest_license = repo_path / "LICENSE"
        with open(source_license, 'r') as src:
            with open(dest_license, 'w') as dst:
                dst.write(src.read())
        
        # Stage and commit
        print(f"  Committing LICENSE file")
        run_command("git add LICENSE", cwd=repo_path)
        run_command('git commit -m "Add MIT LICENSE"', cwd=repo_path)
        
        # Push branch
        print(f"  Pushing branch to remote")
        run_command(f"git push -u origin {branch_name}", cwd=repo_path)
        
        # Create PR
        print(f"  Creating pull request")
        pr_result = run_command(
            'gh pr create --title "Add MIT LICENSE" --body "Adding MIT license to repository"',
            cwd=repo_path
        )
        
        if pr_result:
            print(f"  PR created: {pr_result}")
            
            # Auto-merge the PR
            print(f"  Merging PR")
            run_command("gh pr merge --merge --delete-branch", cwd=repo_path)
            
            # Switch back to original branch
            run_command(f"git checkout {current_branch}", cwd=repo_path)
            run_command("git pull", cwd=repo_path)
            
            print(f"  ✓ LICENSE added and PR merged")
            return True
        else:
            print(f"  ✗ Failed to create PR")
            run_command(f"git checkout {current_branch}", cwd=repo_path)
            return False
            
    except Exception as e:
        print(f"  ✗ Error: {e}")
        # Try to return to original branch
        run_command(f"git checkout {current_branch}", cwd=repo_path, capture=False)
        return False

def main():
    parser = argparse.ArgumentParser(description="Audit repos for LICENSE files")
    parser.add_argument(
        "--dry-run", 
        action="store_true",
        help="List repos without LICENSE but don't create PRs"
    )
    args = parser.parse_args()
    
    # Get Projects directory
    projects_dir = Path.home() / "Projects"
    if not projects_dir.exists():
        print(f"Error: Projects directory not found at {projects_dir}")
        sys.exit(1)
    
    # Source LICENSE file
    source_license = projects_dir / "LICENSE"
    if not source_license.exists():
        print(f"Error: Source LICENSE file not found at {source_license}")
        sys.exit(1)
    
    print(f"{'=' * 60}")
    print(f"LICENSE Audit - {'DRY RUN MODE' if args.dry_run else 'EXECUTION MODE'}")
    print(f"{'=' * 60}")
    print(f"Projects directory: {projects_dir}")
    print(f"Source LICENSE: {source_license}")
    print()
    
    # Find all repos
    repos_checked = 0
    repos_skipped = 0
    repos_missing_license = []
    repos_processed = []
    
    for item in sorted(projects_dir.iterdir()):
        if not item.is_dir() or item.name.startswith('.'):
            continue
        
        if not is_git_repo(item):
            continue
        
        repos_checked += 1
        
        # Skip forked repos
        if is_forked_repo(item):
            print(f"Skipping forked repo: {item.name}")
            repos_skipped += 1
            continue
        
        # Check for LICENSE
        if not has_license_file(item):
            repos_missing_license.append(item)
            
            if args.dry_run:
                print(f"Missing LICENSE: {item.name}")
            else:
                if create_license_pr(item, source_license, dry_run=False):
                    repos_processed.append(item.name)
    
    # Summary
    print(f"\n{'=' * 60}")
    print(f"SUMMARY")
    print(f"{'=' * 60}")
    print(f"Total repos checked: {repos_checked}")
    # print(f"Forked repos skipped: {repos_skipped}")
    print(f"Repos missing LICENSE: {len(repos_missing_license)}")
    
    if args.dry_run:
        print(f"\nRepos that would get PRs:")
        for repo in repos_missing_license:
            print(f"  - {repo.name}")
        print(f"\nRun without --dry-run to create PRs")
    else:
        print(f"Repos processed successfully: {len(repos_processed)}")
        if repos_processed:
            for name in repos_processed:
                print(f"  ✓ {name}")
        
        failed = len(repos_missing_license) - len(repos_processed)
        if failed > 0:
            print(f"\nFailed to process: {failed} repos")

if __name__ == "__main__":
    main()