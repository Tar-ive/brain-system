# Complete Gmail & Apple Reminders Integration Setup

## 🚀 **Quick Start - You Need to Complete These Steps**

### **Step 1: Gmail API Setup (5 minutes)**

1. **Go to Google Cloud Console**: https://console.cloud.google.com/
2. **Create New Project**:
   - Click "Select a project" → "New Project"
   - Project name: `brain-gmail-integration`
   - Click "Create"

3. **Enable Gmail API**:
   - Go to "APIs & Services" → "Library"
   - Search "Gmail API" → Click it → "Enable"

4. **Setup OAuth Consent Screen**:
   - Go to "APIs & Services" → "OAuth consent screen"
   - Choose "External" user type
   - App name: "Brain Gmail Integration"
   - User support email: Your email
   - Developer contact: Your email
   - Click "Save and Continue" (skip scopes and test users)

5. **Create OAuth Credentials**:
   - Go to "APIs & Services" → "Credentials"
   - "Create Credentials" → "OAuth client ID"
   - Application type: "Desktop application"
   - Name: "Brain Gmail Client"
   - Click "Create"
   - **DOWNLOAD** the JSON file
   - Save it as: `/Users/tarive/brain-poc/mcp-gmail/credentials.json`

6. **Add Gmail Scopes**:
   - Back to "OAuth consent screen"
   - "Data Access" tab → "Add or remove scopes"
   - Search "Gmail API"
   - Select `.../auth/gmail.modify` (read, compose, send emails)
   - Click "Update" → "Save"

### **Step 2: Configure Claude MCP Integration**

I'll add both Gmail and Apple Reminders to your Claude configuration:

```bash
# Add to ~/.claude.json (I'll help you with this)
```

## ✅ **What's Already Done**

### **Gmail MCP Server**
- ✅ Cloned from jeremyjordan/mcp-gmail
- ✅ Dependencies installed with `uv sync`
- ✅ Ready for OAuth credentials

### **Apple Reminders MCP Server**
- ✅ Cloned from FradSer/mcp-server-apple-reminders
- ✅ Dependencies installed with `npm install`
- ✅ Swift binary compiled successfully
- ✅ Ready to use (no additional setup needed)

## 🧠 **Brain System Integration Commands**

### **Gmail Commands**
```bash
# Email a founder
brain_email_founder "founder@startup.com" "Partnership Inquiry" "Hi, I'd like to discuss a potential partnership..."

# Search founder communications
brain_search_founder_emails "founder@startup.com"

# List all founder communications
brain_founder_communications
```

### **Apple Reminders Commands**
```bash
# Add reminder from brain tags
brain_add_reminder "make baby chutney" "today 6pm"

# Sync all reminders with brain system
brain_sync_reminders

# Add goal as reminder with due date
brain_goal_reminder "complete O1 visa application" "December 31, 2025"
```

### **Baby Care Commands**
```bash
# Plan baby care activities
brain_plan_baby_care

# Log care activity
brain_baby_care "reading time with picture books"

# Send care reminder
brain_care_reminder "baby" "dinner time in 30 minutes"
```

## 🔧 **Next Steps After You Complete Gmail Setup**

1. **Test Gmail Integration**:
   ```bash
   cd /Users/tarive/brain-poc/mcp-gmail
   uv run python scripts/test_gmail_setup.py
   ```

2. **Test Apple Reminders**:
   ```bash
   cd /Users/tarive/brain-poc/mcp-server-apple-reminders
   npm test
   ```

3. **Configure Claude MCP**:
   I'll update your `~/.claude.json` to include both services

4. **Test Brain Integration**:
   Test the unified commands with your brain system

## 📋 **Benefits You'll Get**

### **Gmail Integration**
- ✅ Send emails to founders directly from brain system
- ✅ All founder communications automatically logged
- ✅ Search previous emails by founder name
- ✅ XML tagging: `<people>founder@email.com</people>`

### **Apple Reminders Integration**
- ✅ Auto-sync `<chores>` and `<goals>` tags to Apple Reminders
- ✅ Set due dates and notifications
- ✅ Two-way sync between brain system and Apple Reminders
- ✅ Organized by priority and due dates

### **Baby Care Tracking**
- ✅ `<people>baby</people>` care activities logged
- ✅ Automated reminders via Apple Reminders
- ✅ Progress tracking and care planning
- ✅ Integration with iMessage for notifications

## 🎯 **Ready to Go Commands**

Once you complete the Gmail setup, you'll have:

```bash
# Complete workflow example
brain_store "<people>founder@techstartup.com</people> potential partnership candidate"
brain_email_founder "founder@techstartup.com" "Partnership Inquiry" "Hi, I'd like to explore collaboration opportunities..."

brain_store "<chores>make baby chutney</chores> tonight for dinner"
brain_add_reminder "make baby chutney" "today 5pm"

brain_store "<goals>complete O1 visa application</goals> priority deadline December"
brain_goal_reminder "complete O1 visa application" "December 15, 2025"
```

**The system will automatically:**
- Send the email via Gmail API
- Log the interaction in your brain system
- Add reminders to Apple Reminders
- Store everything with proper XML tags
- Sync across all 5 dimensions (personal, work, research, uni, startup)

---

**Your Action Items:**
1. ⏰ **Complete Gmail Google Cloud setup** (5 minutes)
2. 📂 **Save credentials.json file** in the right location
3. ✅ **Let me know when done** - I'll configure Claude and test everything

**Priority**: Get Gmail working first since it's #priority asap for founder messaging!