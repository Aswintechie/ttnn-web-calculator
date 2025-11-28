# Bug Report Feature - Setup & Usage

## Overview
One-click bug reporting that automatically captures complete context and sends detailed reports via email using Resend API.

## Features

### 🐛 Floating Bug Report Button
- **Always accessible** - Fixed position in bottom-right corner
- **Eye-catching design** - Red gradient with glow effect
- **Smooth animations** - Hover lift and shadow enhancement
- **Non-intrusive** - Stays out of the way until needed

### 📧 Automatic Data Capture
The bug report automatically includes:
- Current operation name
- All input values (type, value, dtype, shape)
- Optional parameters
- Result data (TTNN & PyTorch values)
- Error messages and stack traces
- System information:
  - Machine type (Wormhole N150)
  - Git commit hash, time, message
  - Queue statistics
- Browser information:
  - User agent
  - IP address
- User description of the issue

### ✨ User Experience
1. User clicks **🐛 Report Bug** button
2. Modal appears with description field
3. User describes the issue
4. Clicks **Submit Report**
5. Email sent automatically with full context
6. Confirmation message shown

## Setup Instructions

### 1. Install Resend Package
```bash
cd /home/aswin/tt-metal
source python_env/bin/activate
pip install resend
```

### 2. Get Resend API Key
1. Sign up at [resend.com](https://resend.com)
2. Verify your sending domain (aswincloud.com)
3. Generate an API key from dashboard

### 3. Set Environment Variable

**Option A: Temporary (current session)**
```bash
export RESEND_API_KEY="re_your_api_key_here"
```

**Option B: Permanent (add to bashrc)**
```bash
echo 'export RESEND_API_KEY="re_your_api_key_here"' >> ~/.bashrc
source ~/.bashrc
```

**Option C: In start script**
Edit `start.sh`:
```bash
#!/bin/bash
export RESEND_API_KEY="re_your_api_key_here"
cd /home/aswin/tt-metal
source python_env/bin/activate
cd /home/aswin/ttnn-web-calculator
python app.py
```

### 4. Verify Configuration
```bash
python -c "import os; print('API Key:', 'SET' if os.environ.get('RESEND_API_KEY') else 'NOT SET')"
```

### 5. Start Server
```bash
cd /home/aswin/ttnn-web-calculator
bash start.sh
```

## Email Format

The bug report email includes:

### 📝 User Description
What the user typed describing the issue

### ⚙️ Operation Details
```
Operation: ttnn.add
Number of Inputs: 2

Input 1:
  Type: tensor
  Value: 5.0
  Dtype: bfloat16
  Shape: 1,1,32,32

Input 2:
  Type: tensor
  Value: 3.0
  Dtype: bfloat16
  Shape: 1,1,32,32

Optional Param: 1.0 (if applicable)
```

### 📊 Result Data
```
Success: True
TTNN Value: 8.0
PyTorch Value: 8.0
Shape: [1, 1, 32, 32]
Error: (if any)
```

### 🖥️ System Information
```
Machine: Wormhole N150
Git Commit: a1b2c3d
Commit Time: 2 hours ago
Commit Message: Latest fixes
Queue Stats:
  - Total Requests: 127
  - Currently Waiting: 0
  - Max Wait Time: 0.456s
```

### 🔍 Browser Info
```
User Agent: Mozilla/5.0 ...
IP Address: 192.168.1.100
```

## Configuration Options

### Change Recipient Email
In `app.py`:
```python
BUG_REPORT_EMAIL = "your-email@domain.com"
```

### Change Sender Email
In `app.py`:
```python
CONTACT_EMAIL = "your-email@domain.com"
```

### Customize Email Template
Edit the `email_html` variable in `submit_bug_report()` function.

## Testing

### Test Bug Report Submission
1. Open the calculator
2. Perform any operation
3. Click **🐛 Report Bug**
4. Enter description: "Test bug report"
5. Click Submit
6. Check your email inbox

### Test Without Resend
If RESEND_API_KEY is not set:
- Button still appears
- User can click and describe issue
- Shows error message with fallback
- Directs user to email directly

## Troubleshooting

### Button Not Visible
- Check browser console for errors
- Verify JavaScript loaded correctly
- Try hard refresh (Ctrl+Shift+R)

### Email Not Sending
1. **Check API Key**
   ```bash
   echo $RESEND_API_KEY
   ```

2. **Check Resend Installation**
   ```python
   python -c "import resend; print('Resend version:', resend.__version__)"
   ```

3. **Check Domain Verification**
   - Log into Resend dashboard
   - Verify sending domain is verified

4. **Check Server Logs**
   ```bash
   tail -f /tmp/flask.log
   ```

5. **Test Resend Directly**
   ```python
   import resend
   import os
   
   resend.api_key = os.environ.get('RESEND_API_KEY')
   
   params = {
       "from": "test@aswincloud.com",
       "to": ["contact@aswincloud.com"],
       "subject": "Test Email",
       "html": "<p>Test message</p>"
   }
   
   result = resend.Emails.send(params)
   print(result)
   ```

### Error: "Domain not verified"
- Add DNS records in your domain provider
- Wait for DNS propagation (up to 48 hours)
- Verify in Resend dashboard

### Error: "API key invalid"
- Regenerate API key in Resend dashboard
- Update environment variable
- Restart server

## Security Considerations

### API Key Protection
- ✅ Stored in environment variable (not in code)
- ✅ Not exposed to frontend
- ✅ Not logged in output
- ✅ Not committed to Git

### Data Privacy
- Bug reports contain:
  - ✅ Operation data (necessary for debugging)
  - ✅ IP address (for abuse prevention)
  - ✅ Browser info (for compatibility debugging)
  - ❌ No personal user data
  - ❌ No passwords or sensitive info

### Rate Limiting
Consider adding rate limiting:
```python
# In app.py
from functools import wraps
import time

bug_report_limiter = {}

def rate_limit(max_per_hour=10):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            ip = request.remote_addr
            now = time.time()
            
            if ip in bug_report_limiter:
                reports = bug_report_limiter[ip]
                # Remove old reports (>1 hour)
                reports = [t for t in reports if now - t < 3600]
                
                if len(reports) >= max_per_hour:
                    return jsonify({
                        'success': False,
                        'error': 'Rate limit exceeded. Please try again later.'
                    })
                
                reports.append(now)
                bug_report_limiter[ip] = reports
            else:
                bug_report_limiter[ip] = [now]
            
            return f(*args, **kwargs)
        return wrapped
    return decorator

# Apply to endpoint
@app.route('/api/bug-report', methods=['POST'])
@login_required
@rate_limit(max_per_hour=10)
def submit_bug_report():
    ...
```

## Benefits

### For Users
✅ Quick and easy bug reporting
✅ No need to manually collect data
✅ Direct feedback channel
✅ Confirmation of submission

### For Developers
✅ Complete context automatically captured
✅ All relevant data in one email
✅ Easy to investigate issues
✅ Faster bug resolution
✅ Better product quality

## Alternative: Without Resend

If you prefer not to use Resend:

### Option 1: Use SMTP
Replace Resend with Python's `smtplib`

### Option 2: Log to File
```python
@app.route('/api/bug-report', methods=['POST'])
@login_required
def submit_bug_report():
    data = request.json
    
    # Save to file
    with open('bug_reports.json', 'a') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'data': data
        }, f)
        f.write('\n')
    
    return jsonify({'success': True})
```

### Option 3: Webhook
Send to Slack, Discord, or other webhook service

## Summary

The bug report feature provides:
- ✨ One-click reporting
- 📧 Automatic email via Resend
- 🎯 Complete context capture
- 🚀 Fast developer investigation
- ✅ Better user feedback loop

**Setup Time:** 5 minutes  
**Result:** Professional bug reporting system!

---

For support: contact@aswincloud.com
