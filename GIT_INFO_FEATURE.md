# Git Commit Information Display

## ✨ New Feature: Live Commit Tracking

The web calculator now displays **real-time git commit information** from the TT-Metal repository!

---

## 🎯 What's Displayed

### Commit Information Bar
Located just below the title, showing:

1. **Commit Hash** (short version)
   - Example: `f4163c2539`
   - Monospaced font with purple highlight
   - Easy to copy for reference

2. **Time Ago**
   - Human-readable time format
   - Examples: "11 hours ago", "2 days ago", "3 weeks ago"
   - Green color for easy visibility

3. **Commit Message**
   - Latest commit description
   - Example: "[Fabric] fabric router to have heartbeat feature (#31255)"
   - Gray color for readability

---

## 📊 Visual Display

### Format:
```
TT-Metal Commit: [f4163c2539] • 11 hours ago • [Fabric] fabric router...
```

### Styling:
- **Background**: Light white with slight transparency
- **Commit Hash**: Purple highlighted box, monospaced font
- **Time**: Green text, bold
- **Message**: Gray text
- **Separators**: Light gray bullets (•)

---

## 🔧 Technical Details

### API Endpoint
```
GET /api/git/info
```

**Response:**
```json
{
  "success": true,
  "full_hash": "f4163c25390344acb7257b707a6dfa494a87f72f",
  "short_hash": "f4163c2539",
  "time_ago": "11 hours ago",
  "message": "[Fabric] fabric router to have heartbeat feature (#31255)"
}
```

### Implementation
- Reads from `/home/aswin/tt-metal` git repository
- Uses `git log -1` to get latest commit
- Formats time with `%cr` (relative time)
- Updates automatically on page load
- Graceful fallback if git info unavailable

---

## 💡 Benefits

### For Users:
✅ **Version Awareness**: Know exactly which TT-Metal version you're testing
✅ **Time Context**: See how recent the code is
✅ **Quick Reference**: Copy commit hash for bug reports
✅ **Transparency**: Always visible at top of page

### For Developers:
✅ **Debug Aid**: Easy to identify which commit is being tested
✅ **Issue Reporting**: Include commit hash in bug reports
✅ **Version Tracking**: Match results to specific commits
✅ **Team Coordination**: Everyone sees the same commit info

---

## 🎮 Examples

### Recent Commit (Hours)
```
TT-Metal Commit: f4163c2539 • 11 hours ago • [Fabric] fabric router...
```

### Older Commit (Days)
```
TT-Metal Commit: a1b2c3d4e5 • 2 days ago • Add support for new operations
```

### Very Old Commit (Weeks)
```
TT-Metal Commit: 9876543210 • 3 weeks ago • Initial version of feature X
```

---

## 🔄 Real-Time Updates

The git information:
- ✅ Loads automatically on page refresh
- ✅ Shows current HEAD commit
- ✅ Updates when you pull new changes
- ✅ Falls back gracefully if unavailable

**To see updated commit info:**
1. Pull latest changes: `cd /home/aswin/tt-metal && git pull`
2. Refresh the calculator page
3. See new commit hash and time!

---

## 🎨 Visual Design

### Color Scheme:
- **Container**: White with rounded corners
- **Commit Hash**: `#667eea` (purple) on `#f0f0f0` (light gray bg)
- **Time Ago**: `#28a745` (green)
- **Message**: `#666` (medium gray)
- **Separators**: `#999` (light gray)

### Typography:
- **Commit Hash**: `Courier New` (monospaced)
- **Rest**: Default system font
- **Sizes**: 0.9em (compact but readable)

---

## 📍 Location

The git info bar appears:
```
┌────────────────────────────────────┐
│   🧮 TTNN Operation Calculator     │
│   Test and visualize operations    │
│                                    │
│ TT-Metal Commit: f4163c2539 • ... │ ← HERE
│                                    │
│   [Type Operation Name]            │
│   ...                              │
└────────────────────────────────────┘
```

---

## 🚀 Try It Now!

**URL**: http://localhost:5000

1. Open the calculator
2. Look just below the subtitle
3. See the commit information bar
4. Note the commit hash, time, and message

**Current commit shown:**
- Hash: `f4163c2539`
- Time: `11 hours ago`
- Message: `[Fabric] fabric router to have heartbeat feature (#31255)`

---

## 🔍 Use Cases

### Debugging
```
User: "I'm getting error X"
Dev: "What commit are you on?"
User: "f4163c2539 - shows at top of calculator"
Dev: "Ah, that's before the fix. Pull latest!"
```

### Testing
```
Tester: "Testing operation Y"
Tester: "Commit: f4163c2539 (11 hours ago)"
Tester: "Results: ..."
→ Clear version tracking in test reports
```

### Collaboration
```
Team Member 1: "The calculator shows commit a1b2c3d"
Team Member 2: "Same here, we're in sync!"
→ Easy version coordination
```

---

## ⚙️ Configuration

The git path is set in `app.py`:
```python
cwd='/home/aswin/tt-metal'
```

To use a different repo, change this path in the `git_info()` function.

---

## 🎉 Summary

✅ **Live commit tracking** from TT-Metal repo
✅ **Human-readable time** (e.g., "11 hours ago")
✅ **Short commit hash** for easy reference
✅ **Commit message** for context
✅ **Auto-updates** on page refresh
✅ **Clean visual design** integrated into UI

**Always know which version you're testing!** 🚀
