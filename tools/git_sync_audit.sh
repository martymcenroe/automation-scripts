#!/bin/bash
# git_sync_audit.sh
# Purpose: Audit and Sync ~/dotfiles and all repos in ~/Projects

# Define targets: Explicit dotfiles + all folders in Projects
REPO_LIST=("$HOME/dotfiles" "$HOME/Projects"/*)

echo "--- 🚀 Starting Git Sync Audit ---"
printf "Targeting: ~/dotfiles + %d repos in ~/Projects\n\n" $((${#REPO_LIST[@]} - 1))

for repo in "${REPO_LIST[@]}"; do
    # Only process if it is a directory and has a .git folder
    if [ -d "$repo" ] && [ -d "$repo/.git" ]; then
        repo_name=$(basename "$repo")
        printf "%-25s : " "$repo_name"
        
        # Run checks in a subshell to avoid directory hopping issues
        (
            cd "$repo" || exit
            
            # 1. Fetch latest data
            git fetch -q origin
            
            # 2. Check Status
            STATUS=$(git status -s)
            LOCAL=$(git rev-parse @)
            REMOTE=$(git rev-parse @{u} 2>/dev/null)
            BASE=$(git merge-base @ @{u} 2>/dev/null)

            if [ -n "$STATUS" ]; then
                echo "🟡 SKIP (Dirty Workspace) - Commit or Stash first."
            elif [ "$LOCAL" = "$REMOTE" ]; then
                echo "✅ OK (Already Up-to-Date)"
            elif [ "$LOCAL" = "$BASE" ]; then
                # We are behind, but clean. Safe to pull.
                git pull -q
                echo "🟢 UPDATED (Fast-Forwarded)"
            elif [ "$REMOTE" = "$BASE" ]; then
                echo "⬆️  AHEAD (You have unpushed commits)"
            else
                echo "🔴 DIVERGED (Requires Manual Merge)"
            fi
        )
    fi
done

echo ""
echo "--- Sync Complete ---"
