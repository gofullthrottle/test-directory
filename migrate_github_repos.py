#!/usr/bin/env python3
"""
GitHub Repository Migration Script

This script helps migrate forked GitHub repositories from one account to another,
excluding repositories that exist locally.

Features:
- Scans local directories to identify GitHub repositories
- Lists all forked repositories from source GitHub account
- Filters out repositories that exist locally
- Migrates remaining forked repositories to target account
- Supports dry-run mode for safety
"""

import os
import subprocess
import json
import argparse
import re
from pathlib import Path
from typing import List, Dict, Set, Optional
from urllib.parse import urlparse
import sys


class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class GitHubRepoScanner:
    """Scans local directories for GitHub repositories"""

    def __init__(self, base_path: str):
        self.base_path = Path(base_path).resolve()
        self.local_repos: Dict[str, Dict[str, str]] = {}

    def is_git_repository(self, path: Path) -> bool:
        """Check if a directory is a git repository"""
        return (path / '.git').exists()

    def get_remote_url(self, repo_path: Path, remote_name: str = 'origin') -> Optional[str]:
        """Get the remote URL for a git repository"""
        try:
            result = subprocess.run(
                ['git', '-C', str(repo_path), 'remote', 'get-url', remote_name],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return None

    def parse_github_url(self, url: str) -> Optional[Dict[str, str]]:
        """
        Parse a GitHub URL to extract owner and repo name
        Supports both HTTPS and SSH URLs
        """
        if not url:
            return None

        # SSH format: git@github.com:owner/repo.git
        ssh_pattern = r'git@github\.com:([^/]+)/(.+?)(?:\.git)?$'
        # HTTPS format: https://github.com/owner/repo.git
        https_pattern = r'https://github\.com/([^/]+)/(.+?)(?:\.git)?$'

        for pattern in [ssh_pattern, https_pattern]:
            match = re.match(pattern, url)
            if match:
                owner, repo = match.groups()
                return {
                    'owner': owner,
                    'repo': repo,
                    'full_name': f"{owner}/{repo}"
                }

        return None

    def scan_directory(self) -> Dict[str, Dict[str, str]]:
        """Scan the base directory for all GitHub repositories"""
        print(f"{Colors.HEADER}Scanning {self.base_path} for GitHub repositories...{Colors.ENDC}")

        for root, dirs, _ in os.walk(self.base_path):
            # Skip hidden directories except .git
            dirs[:] = [d for d in dirs if not d.startswith('.') or d == '.git']

            root_path = Path(root)

            if self.is_git_repository(root_path):
                remote_url = self.get_remote_url(root_path)
                if remote_url:
                    repo_info = self.parse_github_url(remote_url)
                    if repo_info:
                        full_name = repo_info['full_name']
                        self.local_repos[full_name] = {
                            'path': str(root_path),
                            'owner': repo_info['owner'],
                            'repo': repo_info['repo'],
                            'url': remote_url
                        }
                        print(f"  {Colors.OKGREEN}✓{Colors.ENDC} Found: {full_name} at {root_path}")

                # Don't traverse into git repositories
                dirs.clear()

        print(f"\n{Colors.OKBLUE}Found {len(self.local_repos)} GitHub repositories locally{Colors.ENDC}\n")
        return self.local_repos


class GitHubRepoMigrator:
    """Handles migration of GitHub repositories using GitHub API"""

    def __init__(self, source_token: str, target_token: str, source_username: str, target_username: str):
        self.source_token = source_token
        self.target_token = target_token
        self.source_username = source_username
        self.target_username = target_username

    def run_gh_command(self, args: List[str], token: str) -> Optional[str]:
        """Run a GitHub CLI command with authentication"""
        env = os.environ.copy()
        env['GH_TOKEN'] = token

        try:
            result = subprocess.run(
                ['gh'] + args,
                capture_output=True,
                text=True,
                check=True,
                env=env
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            print(f"{Colors.FAIL}Error running gh command: {e.stderr}{Colors.ENDC}")
            return None

    def get_forked_repositories(self) -> List[Dict[str, any]]:
        """Get all forked repositories from the source account"""
        print(f"{Colors.HEADER}Fetching forked repositories from {self.source_username}...{Colors.ENDC}")

        # Use GitHub CLI to list repositories
        output = self.run_gh_command(
            ['repo', 'list', self.source_username, '--fork', '--json',
             'name,nameWithOwner,isFork,parent,url', '--limit', '1000'],
            self.source_token
        )

        if not output:
            return []

        repos = json.loads(output)
        print(f"{Colors.OKBLUE}Found {len(repos)} forked repositories{Colors.ENDC}\n")
        return repos

    def fork_repository(self, repo_full_name: str, dry_run: bool = False) -> bool:
        """Fork a repository to the target account"""
        if dry_run:
            print(f"  {Colors.WARNING}[DRY RUN]{Colors.ENDC} Would fork: {repo_full_name}")
            return True

        print(f"  {Colors.OKCYAN}Forking:{Colors.ENDC} {repo_full_name}...")

        # Fork the repository using gh CLI
        output = self.run_gh_command(
            ['repo', 'fork', repo_full_name, '--fork-name', repo_full_name.split('/')[-1]],
            self.target_token
        )

        if output:
            print(f"  {Colors.OKGREEN}✓{Colors.ENDC} Successfully forked to {self.target_username}")
            return True
        else:
            print(f"  {Colors.FAIL}✗{Colors.ENDC} Failed to fork")
            return False

    def migrate_repositories(self, local_repos: Dict[str, Dict[str, str]], dry_run: bool = False):
        """Migrate forked repositories, excluding local ones"""
        forked_repos = self.get_forked_repositories()

        if not forked_repos:
            print(f"{Colors.WARNING}No forked repositories found{Colors.ENDC}")
            return

        # Get set of local repository names
        local_repo_names = set(local_repos.keys())

        # Filter repositories to migrate
        repos_to_migrate = []
        repos_skipped = []

        for repo in forked_repos:
            repo_name = repo['nameWithOwner']
            if repo_name in local_repo_names:
                repos_skipped.append(repo_name)
            else:
                repos_to_migrate.append(repo)

        # Display summary
        print(f"{Colors.HEADER}Migration Summary:{Colors.ENDC}")
        print(f"  Total forked repositories: {len(forked_repos)}")
        print(f"  Repositories to migrate: {Colors.OKGREEN}{len(repos_to_migrate)}{Colors.ENDC}")
        print(f"  Repositories skipped (local): {Colors.WARNING}{len(repos_skipped)}{Colors.ENDC}\n")

        if repos_skipped:
            print(f"{Colors.WARNING}Skipping local repositories:{Colors.ENDC}")
            for repo_name in repos_skipped:
                local_path = local_repos[repo_name]['path']
                print(f"  - {repo_name} (at {local_path})")
            print()

        if not repos_to_migrate:
            print(f"{Colors.OKGREEN}No repositories to migrate!{Colors.ENDC}")
            return

        # Confirm migration
        if not dry_run:
            print(f"{Colors.WARNING}About to migrate {len(repos_to_migrate)} repositories to {self.target_username}{Colors.ENDC}")
            confirm = input("Continue? [y/N]: ")
            if confirm.lower() != 'y':
                print("Migration cancelled.")
                return

        # Perform migration
        print(f"\n{Colors.HEADER}Starting migration...{Colors.ENDC}\n")
        successful = 0
        failed = 0

        for repo in repos_to_migrate:
            # Get the parent repository (original) to fork from
            parent_repo = repo.get('parent', {}).get('nameWithOwner')
            if parent_repo:
                if self.fork_repository(parent_repo, dry_run):
                    successful += 1
                else:
                    failed += 1
            else:
                print(f"  {Colors.WARNING}⚠{Colors.ENDC} Skipping {repo['nameWithOwner']}: No parent found")

        # Final summary
        print(f"\n{Colors.HEADER}Migration Complete!{Colors.ENDC}")
        print(f"  {Colors.OKGREEN}Successful: {successful}{Colors.ENDC}")
        if failed > 0:
            print(f"  {Colors.FAIL}Failed: {failed}{Colors.ENDC}")


def main():
    parser = argparse.ArgumentParser(
        description='Migrate forked GitHub repositories, excluding local ones',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Dry run to see what would be migrated
  %(prog)s --local-path ~/projects --source-user alice --target-user bob --dry-run

  # Actual migration
  %(prog)s --local-path ~/projects --source-user alice --target-user bob

Environment Variables:
  GITHUB_SOURCE_TOKEN: GitHub token for source account (required)
  GITHUB_TARGET_TOKEN: GitHub token for target account (required)
        """
    )

    parser.add_argument(
        '--local-path',
        required=True,
        help='Path to scan for local GitHub repositories'
    )
    parser.add_argument(
        '--source-user',
        required=True,
        help='Source GitHub username'
    )
    parser.add_argument(
        '--target-user',
        required=True,
        help='Target GitHub username'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be migrated without actually doing it'
    )
    parser.add_argument(
        '--source-token',
        help='GitHub token for source account (or set GITHUB_SOURCE_TOKEN env var)'
    )
    parser.add_argument(
        '--target-token',
        help='GitHub token for target account (or set GITHUB_TARGET_TOKEN env var)'
    )

    args = parser.parse_args()

    # Get tokens from arguments or environment
    source_token = args.source_token or os.environ.get('GITHUB_SOURCE_TOKEN')
    target_token = args.target_token or os.environ.get('GITHUB_TARGET_TOKEN')

    if not source_token:
        print(f"{Colors.FAIL}Error: Source GitHub token not provided{Colors.ENDC}")
        print("Set GITHUB_SOURCE_TOKEN environment variable or use --source-token")
        sys.exit(1)

    if not target_token:
        print(f"{Colors.FAIL}Error: Target GitHub token not provided{Colors.ENDC}")
        print("Set GITHUB_TARGET_TOKEN environment variable or use --target-token")
        sys.exit(1)

    # Check if local path exists
    if not os.path.exists(args.local_path):
        print(f"{Colors.FAIL}Error: Local path does not exist: {args.local_path}{Colors.ENDC}")
        sys.exit(1)

    # Step 1: Scan local repositories
    scanner = GitHubRepoScanner(args.local_path)
    local_repos = scanner.scan_directory()

    # Step 2: Migrate repositories
    migrator = GitHubRepoMigrator(
        source_token=source_token,
        target_token=target_token,
        source_username=args.source_user,
        target_username=args.target_user
    )
    migrator.migrate_repositories(local_repos, dry_run=args.dry_run)


if __name__ == '__main__':
    main()
