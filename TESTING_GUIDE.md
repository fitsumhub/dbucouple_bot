# 🤖 Bot Testing Guide

Complete guide to test your University Connect Bot.

## 📋 Prerequisites

1. ✅ Bot is running (check with `Get-Process python`)
2. ✅ Bot token is correct in `config.py`
3. ✅ Database file exists (`university_connect.db`)

## 🔍 Step 1: Find Your Bot

1. Open **Telegram** app (mobile or desktop)
2. Search for your bot name (the one you gave to @BotFather)
3. Click **Start** or send `/start`

## 🧪 Testing Checklist

### ✅ Basic Functionality Tests

#### 1. Registration Flow (`/start`)
- [ ] Send `/start` command
- [ ] Bot asks for name → Enter your name
- [ ] Bot asks for age → Enter age (16-100)
- [ ] Bot asks for department → Enter department
- [ ] Bot asks for bio → Enter bio (10-500 chars)
- [ ] Bot asks for photo → Send a photo
- [ ] Bot confirms "✅ Profile created successfully!"
- [ ] Menu buttons appear

#### 2. Menu Buttons Test
- [ ] **🔍 Browse Profiles** - Shows profiles
- [ ] **👤 My Profile** - Shows your profile with Edit button
- [ ] **💕 My Matches** - Shows matches (empty if none)
- [ ] **💌 Liked Me** - Shows who liked you (empty if none)
- [ ] **📊 Statistics** - Shows your stats
- [ ] **⚙️ Settings** - Opens preferences menu
- [ ] **ℹ️ Help** - Shows help information

#### 3. Browse Profiles Test
- [ ] Click "🔍 Browse Profiles"
- [ ] Profile appears with photo and info
- [ ] Test buttons:
  - [ ] **❤️ Like** - Shows "❤️ Liked!" message
  - [ ] **❌ Pass** - Shows "⏭ Passed!" and next profile
  - [ ] **👤 View Full Profile** - Shows complete profile
  - [ ] **🔄 Skip** - Skips to next profile
  - [ ] **🔙 Back to Menu** - Returns to main menu

#### 4. Profile View Test
- [ ] Click "👤 My Profile"
- [ ] Your profile photo and info displayed
- [ ] **✏️ Edit Profile** button appears
- [ ] Click "✏️ Edit Profile" → Starts registration flow

#### 5. Settings/Preferences Test
- [ ] Click "⚙️ Settings"
- [ ] Preferences menu appears with buttons
- [ ] Test age filters:
  - [ ] All Ages
  - [ ] 18-25
  - [ ] 26-30
  - [ ] 31+
- [ ] Test department filters:
  - [ ] All Departments
  - [ ] Computer Science
  - [ ] Engineering
  - [ ] Business
- [ ] Click "✅ Apply Filters & Browse"
- [ ] Profiles filtered correctly
- [ ] Click "🗑️ Clear All Filters"
- [ ] Click "❌ Cancel"

#### 6. Match System Test (Requires 2 Users)

**Setup:**
- Create 2 test accounts (or use 2 different Telegram accounts)
- Register both profiles

**Test Steps:**
1. User A browses and likes User B
2. User B browses and likes User A
3. Both should see "💘 It's a match!" message
4. Check "💕 My Matches" - should show the match
5. Check "💌 Liked Me" - should show users who liked you

#### 7. Statistics Test
- [ ] Click "📊 Statistics"
- [ ] Shows:
  - [ ] Likes Given count
  - [ ] Likes Received count
  - [ ] Matches count
  - [ ] Profile Views count

#### 8. Liked Me Test
- [ ] Click "💌 Liked Me"
- [ ] Shows users who liked you (if any)
- [ ] Each profile has:
  - [ ] **❤️ Like Back** button
  - [ ] **❌ Pass** button
  - [ ] **👤 View Full Profile** button

## 🐛 Common Issues & Solutions

### Issue: Bot not responding
**Solution:**
```powershell
# Check if bot is running
Get-Process python

# Check logs
Get-Content logs/bot.log -Tail 50
```

### Issue: "Profile not found"
**Solution:**
- Complete registration with `/start`
- Make sure you finish all steps including photo

### Issue: "No users found"
**Solution:**
- Register at least 2 profiles
- Clear filters if any are active
- Check database has users

### Issue: Buttons not working
**Solution:**
- Restart the bot
- Check if handlers are registered in `bot.py`
- Verify callback handlers are set up

### Issue: Database errors
**Solution:**
```powershell
# Check database exists
Test-Path university_connect.db

# Check database permissions
Get-Item university_connect.db | Select-Object FullName, Mode
```

## 📊 Testing with Multiple Users

### Option 1: Use Multiple Telegram Accounts
1. Create 2+ Telegram accounts
2. Test each feature with different accounts
3. Test matching between accounts

### Option 2: Use Test Accounts
1. Create test profiles with different names
2. Use different photos for each
3. Test interactions between them

## 🔄 Quick Test Commands

```bash
# Test bot is running
Get-Process python

# View recent logs
Get-Content logs/bot.log -Tail 20

# Restart bot
# Stop current process (Ctrl+C)
& "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe" bot.py
```

## ✅ Success Criteria

Your bot is working correctly if:
- ✅ Registration completes successfully
- ✅ Menu buttons all respond
- ✅ Browsing shows profiles
- ✅ Like/Pass buttons work
- ✅ Matches are detected
- ✅ Statistics display correctly
- ✅ Settings/filters work
- ✅ All inline buttons respond

## 🎯 Advanced Testing

### Test Error Handling
- Send invalid input during registration
- Try to browse without completing profile
- Test with empty database

### Test Edge Cases
- Very long names/bios
- Special characters in text
- Multiple rapid button clicks
- Network interruption scenarios

## 📝 Testing Notes

- Keep the bot running while testing
- Check console/logs for errors
- Test on both mobile and desktop Telegram
- Test with different network conditions

---

**Happy Testing! 🚀**

