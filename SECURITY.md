# Security Best Practices

## Important: Never Commit Secrets!

This repository uses Google OAuth credentials. **Never commit real credentials to the repository**.

### What's Safe to Commit

✅ These files are safe - they use placeholders:
- `.env.example`
- `claude_desktop_config.json.example`
- `MCP_SETUP.md` (now uses placeholders)

### What's Not Safe to Commit

❌ Never commit these files:
- `.env` - Contains real credentials
- `claude_desktop_config.json` - Contains real credentials
- Any files with `GOOGLE_CLIENT_ID` or `GOOGLE_CLIENT_SECRET` with real values

### What's Gitignored

These files are automatically ignored by git (see `.gitignore`):
- `.env`
- `claude_desktop_config.json`
- `config/tokens/` (OAuth tokens)
- `workspace/` (workspace files)

### Setting Up Locally

1. **Copy the example files:**
   ```bash
   cp env.example .env
   cp claude_desktop_config.json.example claude_desktop_config.json
   ```

2. **Fill in your real credentials:**
   - Edit `.env` with your actual Google OAuth credentials
   - Edit `claude_desktop_config.json` with your actual paths and credentials

3. **Never commit:**
   - `.env`
   - `claude_desktop_config.json`

### Getting Your Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create or select a project
3. Enable the Google Workspace APIs you need
4. Go to "Credentials" → "Create Credentials" → "OAuth 2.0 Client ID"
5. Copy the Client ID and Client Secret to your `.env` file

### If You Accidentally Push Secrets

If you ever accidentally push secrets:

1. **Immediately revoke the credentials** in Google Cloud Console
2. **Generate new credentials**
3. **Update your `.env` and `claude_desktop_config.json` files** locally
4. **Remove secrets from git history** (use `git filter-branch` or BFG Repo-Cleaner)
5. **Force push** the cleaned history

**Remember**: Secrets in git history can be found by anyone who clones the repository!

### Resources

- [GitHub Secret Scanning](https://docs.github.com/code-security/secret-scanning)
- [Google OAuth 2.0 Best Practices](https://developers.google.com/identity/protocols/oauth2/web-server#bestpractices)

