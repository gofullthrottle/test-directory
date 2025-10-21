#!/bin/bash
# Example migration script
# Copy this file and modify for your specific use case

# Configuration
LOCAL_PATH="$HOME/projects"  # Path to scan for local repositories
SOURCE_USER="old-username"   # Your old GitHub username
TARGET_USER="new-username"   # Your new GitHub username

# Set your GitHub tokens
# IMPORTANT: Never commit these tokens to version control!
# Option 1: Set them here (not recommended)
# export GITHUB_SOURCE_TOKEN="ghp_your_source_token_here"
# export GITHUB_TARGET_TOKEN="ghp_your_target_token_here"

# Option 2: Load from a secure file (recommended)
# source ~/.github_tokens

# Option 3: Prompt for tokens (most secure)
read -sp "Enter source GitHub token: " GITHUB_SOURCE_TOKEN
echo
export GITHUB_SOURCE_TOKEN

read -sp "Enter target GitHub token: " GITHUB_TARGET_TOKEN
echo
export GITHUB_TARGET_TOKEN

# Step 1: Dry run to see what would be migrated
echo "========================================="
echo "Step 1: Dry run"
echo "========================================="
./migrate_github_repos.py \
  --local-path "$LOCAL_PATH" \
  --source-user "$SOURCE_USER" \
  --target-user "$TARGET_USER" \
  --dry-run

# Ask for confirmation
echo ""
echo "========================================="
read -p "Does the dry run look correct? Continue with migration? [y/N]: " confirm

if [[ $confirm == [yY] || $confirm == [yY][eE][sS] ]]; then
    # Step 2: Actual migration
    echo "========================================="
    echo "Step 2: Running migration"
    echo "========================================="
    ./migrate_github_repos.py \
      --local-path "$LOCAL_PATH" \
      --source-user "$SOURCE_USER" \
      --target-user "$TARGET_USER"

    echo ""
    echo "Migration complete!"
else
    echo "Migration cancelled."
fi

# Clean up tokens from environment
unset GITHUB_SOURCE_TOKEN
unset GITHUB_TARGET_TOKEN
