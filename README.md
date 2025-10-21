# GitHub Repository Migration Tool

A Python script to migrate your forked GitHub repositories from one account to another, automatically excluding repositories that exist locally on your machine.

## Features

- Recursively scans local directories to identify GitHub repositories
- Lists all forked repositories from your source GitHub account
- Intelligently excludes local repositories from migration
- Safely migrates remaining forks to your target account
- Includes dry-run mode for safe previewing
- Supports both SSH and HTTPS Git URLs
- Color-coded terminal output for easy monitoring

## Quick Start

See [QUICKSTART.md](QUICKSTART.md) for a 5-minute setup guide.

## Documentation

- **[QUICKSTART.md](QUICKSTART.md)** - Get up and running quickly
- **[MIGRATION_README.md](MIGRATION_README.md)** - Complete documentation
- **[example_migration.sh](example_migration.sh)** - Example usage script

## Basic Usage

```bash
# Dry run (recommended first)
./migrate_github_repos.py \
  --local-path ~/projects \
  --source-user old-username \
  --target-user new-username \
  --dry-run

# Actual migration
./migrate_github_repos.py \
  --local-path ~/projects \
  --source-user old-username \
  --target-user new-username
```

## Requirements

- Python 3.6+
- Git command line tool
- GitHub CLI (`gh`) - [Install here](https://cli.github.com/)
- GitHub Personal Access Tokens for both accounts

## How It Works

1. **Scan**: Traverses your local directory tree to find all GitHub repositories
2. **Identify**: Extracts repository metadata (owner, name, URL) from Git remotes
3. **List**: Fetches all forked repositories from your source GitHub account
4. **Filter**: Excludes any repositories found locally from the migration list
5. **Migrate**: Forks the remaining repositories to your target account

## Why Use This Tool?

When migrating between GitHub accounts, you typically want to:
- Keep repositories you're actively working on locally (don't duplicate them)
- Migrate your forks that you're not actively developing
- Maintain the fork relationship with upstream repositories

This tool automates that decision-making process by excluding any repository that exists in your local development environment.

## License

This project is provided as-is for your use.

## Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.
