import subprocess
import sys
import argparse

def run_gh_command(repo_name, visibility):
    """Wraps the gh repo edit command."""
    print(f"Processing: {repo_name} -> {visibility}")
    # Added --accept-visibility-change-consequences to bypass the safety prompt
    command = f"gh repo edit {repo_name} --visibility {visibility} --accept-visibility-change-consequences"
    
    try:
        # We run without 'check=True' first to catch specific gh errors gracefully
        result = subprocess.run(command, shell=True, text=True, capture_output=True)
        if result.returncode == 0:
            print(f"✅ Success: {repo_name} is now {visibility}")
        else:
            print(f"❌ Error on {repo_name}: {result.stderr.strip()}")
    except Exception as e:
        print(f"❌ System Error: {e}")

def main():
    parser = argparse.ArgumentParser(description="Bulk toggle repository visibility.")
    parser.add_argument("repos", nargs="+", help="List of repositories to modify")
    parser.add_argument("--public", action="store_true", help="Set to PUBLIC")
    parser.add_argument("--private", action="store_true", help="Set to PRIVATE")
    
    args = parser.parse_args()

    # Validation
    if args.public and args.private:
        print("Error: Cannot set both --public and --private")
        sys.exit(1)
    
    if not args.public and not args.private:
        print("Error: Must specify either --public or --private")
        sys.exit(1)

    target_visibility = "public" if args.public else "private"

    print(f"--- Bulk Setting Visibility to: {target_visibility.upper()} ---")
    print(f"Targets: {', '.join(args.repos)}")
    
    confirm = input("Are you sure? (y/n): ")
    if confirm.lower() != 'y':
        print("Aborted.")
        sys.exit(0)

    for repo in args.repos:
        run_gh_command(repo, target_visibility)

if __name__ == "__main__":
    main()
