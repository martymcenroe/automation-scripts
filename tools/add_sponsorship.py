import os
import subprocess
import sys
import time

# Configuration
FUNDING_CONTENT = "github: martymcenroe\n"

def run_command(command):
    """Executes a shell command and handles errors."""
    print(f"> {command}")
    try:
        subprocess.run(command, check=True, shell=True, text=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {command}")
        sys.exit(1)

def main():
    print("--- Automating GitHub Sponsorship Setup ---")

    # 1. Check if .github directory exists
    if not os.path.exists(".github"):
        os.makedirs(".github")
        print("Created .github directory")

    # 2. Check/Create FUNDING.yml
    funding_path = os.path.join(".github", "FUNDING.yml")
    if os.path.exists(funding_path):
        print("FUNDING.yml already exists. Aborting to prevent overwrite.")
        return

    with open(funding_path, "w") as f:
        f.write(FUNDING_CONTENT)
    print("Created .github/FUNDING.yml")

    # 3. Git Operations
    timestamp = int(time.time())
    branch_name = f"feat/sponsor-{timestamp}"

    print(f"\n--- Starting Git Workflow ({branch_name}) ---")
    
    # Create Branch
    run_command(f"git checkout -b {branch_name}")

    # Stage and Commit
    run_command("git add .github/FUNDING.yml")
    run_command('git commit -m "feat: Enable GitHub Sponsorship"')

    # Push
    run_command(f"git push origin {branch_name}")

    # PR and Merge
    print("\n--- Creating and Merging Pull Request ---")
    run_command('gh pr create --title "feat: Enable GitHub Sponsorship" --body "Adds the .github/FUNDING.yml configuration to enable the Sponsor button."')
    run_command("gh pr merge --squash --delete-branch")

    print("\n--- Success! Sponsorship enabled for this repo. ---")

if __name__ == "__main__":
    main()
