# 🐛 Issue Reporting Guide

To help fix the bot, please provide:

## What specific issue are you experiencing?

### 1. Bot won't start?
- [ ] Error message when running `python bot.py`
- [ ] Bot crashes immediately
- [ ] No response in Telegram

### 2. Commands not working?
- [ ] `/start` doesn't work
- [ ] `/browse` doesn't work
- [ ] `/menu` doesn't work
- [ ] Other commands not working

### 3. Buttons not working?
- [ ] Inline buttons (Like/Pass) don't respond
- [ ] Menu buttons don't respond
- [ ] Settings buttons don't work

### 4. Registration issues?
- [ ] Can't complete registration
- [ ] Stuck on a step
- [ ] Profile not saving

### 5. Browse/Match issues?
- [ ] No profiles showing
- [ ] Matches not detected
- [ ] Can't like/pass profiles

### 6. Other issues?
- [ ] Error messages in console
- [ ] Database errors
- [ ] Import errors

## Please provide:

1. **Exact error message** (if any)
2. **What you tried to do** (command/button)
3. **What happened** (or didn't happen)
4. **Console output** (if available)

## Quick Checks

Run these to diagnose:

```powershell
# Check if bot is running
Get-Process python

# Test bot import
python -c "import bot; print('OK')"

# Check database
python -c "from database import db_manager; print('OK')"

# Run diagnostics
python diagnose_bot.py
```

## Common Fixes

1. **Restart bot:**
   ```powershell
   Get-Process python | Stop-Process
   python bot.py
   ```

2. **Reinstall dependencies:**
   ```powershell
   pip install -r requirements.txt --upgrade
   ```

3. **Check token:**
   - Verify BOT_TOKEN in config.py
   - Test token with @BotFather

4. **Clear and restart:**
   - Stop bot
   - Delete `__pycache__` folders
   - Restart bot

