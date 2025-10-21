# Quick Start Guide

Get started migrating your GitHub repositories in 5 minutes!

## Prerequisites Check

```bash
# Check if you have the required tools
python3 --version  # Should be 3.6 or higher
git --version      # Any recent version
gh --version       # GitHub CLI
```

If `gh` is not installed, install it:
```bash
# macOS
brew install gh

# Ubuntu/Debian
sudo apt install gh

# Other: https://cli.github.com/
```

## Step 1: Get Your GitHub Tokens

1. Go to https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Name it "Migration Script"
4. Select these scopes:
   - ✅ `repo`
   - ✅ `read:org`
5. Click "Generate token"
6. Copy the token (starts with `ghp_`)
7. Do this for BOTH your source and target accounts

## Step 2: Set Up Environment

```bash
# Set your tokens as environment variables
export GITHUB_SOURCE_TOKEN="ghp_your_source_token_here"
export GITHUB_TARGET_TOKEN="ghp_your_target_token_here"
```

## Step 3: Run Dry Run

```bash
# Replace the values below with your information
./migrate_github_repos.py \
  --local-path ~/projects \
  --source-user your-old-username \
  --target-user your-new-username \
  --dry-run
```

This will show you:
- Which repositories were found locally
- Which repositories will be migrated
- Which repositories will be skipped

## Step 4: Run Migration

If the dry run looks good:

```bash
./migrate_github_repos.py \
  --local-path ~/projects \
  --source-user your-old-username \
  --target-user your-new-username
```

The script will ask for confirmation before proceeding.

## Alternative: Use the Example Script

```bash
# Copy and edit the example script
cp example_migration.sh my_migration.sh
nano my_migration.sh  # Edit with your settings

# Make it executable
chmod +x my_migration.sh

# Run it
./my_migration.sh
```

## What Happens During Migration?

1. **Scan**: Script finds all GitHub repos in your local directory
2. **List**: Script gets all your forked repos from GitHub
3. **Filter**: Removes local repos from migration list
4. **Confirm**: Shows summary and asks for confirmation
5. **Migrate**: Forks the remaining repos to your new account

## Example Output

```
Scanning /home/user/projects for GitHub repositories...
  ✓ Found: alice/repo1 at /home/user/projects/repo1
  ✓ Found: alice/repo2 at /home/user/projects/repo2

Found 2 GitHub repositories locally

Fetching forked repositories from alice...
Found 5 forked repositories

Migration Summary:
  Total forked repositories: 5
  Repositories to migrate: 3
  Repositories skipped (local): 2

Skipping local repositories:
  - alice/repo1 (at /home/user/projects/repo1)
  - alice/repo2 (at /home/user/projects/repo2)

About to migrate 3 repositories to bob
Continue? [y/N]: y

Starting migration...
  Forking: original-owner/repo3...
  ✓ Successfully forked to bob
  Forking: original-owner/repo4...
  ✓ Successfully forked to bob
  Forking: original-owner/repo5...
  ✓ Successfully forked to bob

Migration Complete!
  Successful: 3
```

## Tips

- **Always run dry-run first** to preview changes
- **Backup important data** before any migration
- **Check token permissions** if you get authentication errors
- **Run in batches** if you have hundreds of repositories
- **Revoke tokens** after migration is complete

## Need Help?

See the full [MIGRATION_README.md](MIGRATION_README.md) for:
- Detailed documentation
- Troubleshooting guide
- Advanced usage examples
- Security best practices
