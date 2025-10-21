# GitHub Repository Migration Script

This script helps you migrate your forked GitHub repositories from one account to another, while automatically excluding any repositories you have stored locally.

## Features

- **Local Repository Scanner**: Recursively scans a directory tree to find all GitHub repositories
- **Smart Filtering**: Automatically excludes repositories found locally from migration
- **Safe Migration**: Uses GitHub API to fork repositories to your new account
- **Dry Run Mode**: Preview what will be migrated before making changes
- **Comprehensive Logging**: Color-coded output showing progress and results
- **Support for Both URL Formats**: Works with SSH and HTTPS Git URLs

## Prerequisites

1. **Python 3.6+** installed on your system
2. **GitHub CLI (`gh`)** installed and available in PATH
   - Install from: https://cli.github.com/
3. **GitHub Personal Access Tokens** for both source and target accounts
   - Create tokens at: https://github.com/settings/tokens
   - Required scopes: `repo`, `read:org`

## Installation

1. Download the script:
   ```bash
   chmod +x migrate_github_repos.py
   ```

2. Install GitHub CLI if not already installed:
   ```bash
   # On macOS
   brew install gh

   # On Linux
   curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
   echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
   sudo apt update
   sudo apt install gh
   ```

## Usage

### Basic Usage

```bash
# Dry run (recommended first step)
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

### Using Environment Variables for Tokens

```bash
# Set tokens as environment variables
export GITHUB_SOURCE_TOKEN="ghp_your_source_token_here"
export GITHUB_TARGET_TOKEN="ghp_your_target_token_here"

# Run the script
./migrate_github_repos.py \
  --local-path ~/projects \
  --source-user old-username \
  --target-user new-username
```

### Using Command Line Arguments for Tokens

```bash
./migrate_github_repos.py \
  --local-path ~/projects \
  --source-user old-username \
  --target-user new-username \
  --source-token "ghp_your_source_token" \
  --target-token "ghp_your_target_token"
```

## How It Works

### Step 1: Scan Local Repositories

The script recursively traverses the specified directory (`--local-path`) and:
- Identifies all Git repositories (directories with `.git` folder)
- Extracts the remote URL for each repository
- Parses GitHub URLs to extract owner and repository name
- Builds a list of all local GitHub repositories

Example output:
```
Scanning /home/user/projects for GitHub repositories...
  ✓ Found: user/repo1 at /home/user/projects/repo1
  ✓ Found: user/repo2 at /home/user/projects/subfolder/repo2

Found 2 GitHub repositories locally
```

### Step 2: Fetch Forked Repositories

The script uses GitHub CLI to:
- List all forked repositories from your source account
- Extract repository metadata including parent repository information

### Step 3: Filter and Migrate

The script:
- Compares forked repositories with local repositories
- Excludes any repositories found locally
- Shows a summary of what will be migrated
- Asks for confirmation (unless in dry-run mode)
- Forks the remaining repositories to the target account

Example output:
```
Migration Summary:
  Total forked repositories: 10
  Repositories to migrate: 7
  Repositories skipped (local): 3

Skipping local repositories:
  - user/repo1 (at /home/user/projects/repo1)
  - user/repo2 (at /home/user/projects/subfolder/repo2)
  - user/repo3 (at /home/user/projects/repo3)

About to migrate 7 repositories to new-username
Continue? [y/N]:
```

## Command Line Options

| Option | Required | Description |
|--------|----------|-------------|
| `--local-path` | Yes | Path to scan for local GitHub repositories |
| `--source-user` | Yes | Source GitHub username |
| `--target-user` | Yes | Target GitHub username |
| `--dry-run` | No | Preview migration without making changes |
| `--source-token` | No* | GitHub token for source account |
| `--target-token` | No* | GitHub token for target account |

*Required but can be set via environment variables

## GitHub Token Setup

### Creating Personal Access Tokens

1. Go to GitHub Settings: https://github.com/settings/tokens
2. Click "Generate new token" → "Generate new token (classic)"
3. Give it a descriptive name (e.g., "Migration Script - Source")
4. Select scopes:
   - `repo` (Full control of private repositories)
   - `read:org` (Read org and team membership)
5. Click "Generate token"
6. Copy the token immediately (you won't see it again!)
7. Repeat for target account

### Token Security

- Never commit tokens to version control
- Use environment variables or secure credential storage
- Consider using tokens with limited scope and short expiration
- Revoke tokens after migration is complete

## Examples

### Example 1: Dry Run First

```bash
# Always do a dry run first to see what would happen
export GITHUB_SOURCE_TOKEN="ghp_source_token"
export GITHUB_TARGET_TOKEN="ghp_target_token"

./migrate_github_repos.py \
  --local-path ~/code \
  --source-user alice \
  --target-user bob \
  --dry-run
```

### Example 2: Full Migration

```bash
# After verifying dry run looks good, run actual migration
./migrate_github_repos.py \
  --local-path ~/code \
  --source-user alice \
  --target-user bob
```

### Example 3: Multiple Directory Roots

If you have repositories in multiple locations, run the script multiple times:

```bash
# Scan first location
./migrate_github_repos.py --local-path ~/projects --source-user alice --target-user bob --dry-run

# Then scan second location
./migrate_github_repos.py --local-path ~/work --source-user alice --target-user bob --dry-run
```

## Troubleshooting

### "gh command not found"

Install GitHub CLI:
```bash
# Check if gh is installed
which gh

# If not, install it (see Installation section)
```

### "Authentication failed"

- Verify your tokens are correct
- Check token has required scopes (`repo`, `read:org`)
- Ensure tokens haven't expired

### "No forked repositories found"

- Verify the source username is correct
- Check that the source token has access to the account
- Ensure you have forked repositories on the source account

### Repository Already Exists

If a repository already exists on the target account, the fork will fail. The script will continue with remaining repositories.

## Important Notes

1. **Forked Repositories Only**: This script only migrates forked repositories, not original repositories
2. **Fork Relationship**: The new forks will maintain the relationship with the original upstream repository
3. **No Data Loss**: Original repositories on the source account are not modified or deleted
4. **Local Repositories**: The script never modifies your local repositories
5. **Rate Limits**: GitHub API has rate limits. For large migrations, you may need to run in batches

## Output Explanation

The script uses color-coded output:
- **Green (✓)**: Success
- **Yellow (⚠)**: Warning or skipped
- **Red (✗)**: Error
- **Blue**: Informational
- **Cyan**: In progress

## Advanced Usage

### Filtering Specific Directories

To exclude certain directories from the scan, modify them before running:

```bash
# Create a wrapper script that excludes node_modules, vendor, etc.
find ~/projects -type d \( -name node_modules -o -name vendor \) -prune
```

### Batch Processing

For very large migrations, you can process repositories in batches by running the script multiple times and manually managing the list.

## License

This script is provided as-is for your use. Modify as needed for your specific requirements.

## Support

For issues or questions:
1. Check the Troubleshooting section above
2. Verify all prerequisites are installed
3. Run in dry-run mode first to identify issues
4. Check GitHub CLI documentation: https://cli.github.com/manual/
