# Login Lockout Protection

## Overview
Brute force protection mechanism that locks user accounts after multiple failed login attempts.

## Features

### 🔒 **IP-Based Lockout**
- Tracks failed login attempts per IP address
- Each IP address has independent attempt counter
- Prevents distributed brute force attacks

### 📊 **Configuration**
```python
MAX_ATTEMPTS = 5           # Maximum failed attempts allowed
LOCKOUT_DURATION = 15 min  # Lockout period after max attempts
```

### ⚡ **Real-Time Feedback**
Users receive immediate feedback after each failed attempt:
- **Attempt 1-4**: "Invalid password. X attempts remaining."
- **Attempt 5**: Account locked for 15 minutes
- **During lockout**: Shows remaining lockout time

## How It Works

### 1. **First Failed Attempt**
```
User enters wrong password
↓
System records: {
    IP: "192.168.1.100",
    count: 1,
    first_attempt: timestamp,
    lockout_until: null
}
↓
Message: "Invalid password. 4 attempts remaining."
```

### 2. **Subsequent Attempts (2-4)**
```
Each failed attempt increments counter
↓
count: 2, 3, 4
↓
Message updates: "3 attempts remaining", "2 attempts...", "1 attempt..."
```

### 3. **Fifth Failed Attempt (Lockout)**
```
count reaches 5
↓
lockout_until = now + 15 minutes
↓
Login form disabled
Message: "Too many failed attempts. Account locked for 15 minutes."
```

### 4. **During Lockout Period**
```
Any login attempt (correct or incorrect)
↓
Check: current_time < lockout_until?
↓ Yes
Reject with message: "Account locked. Please try again in X minutes."
Form disabled: ✅
```

### 5. **After Lockout Expires**
```
current_time >= lockout_until
↓
Attempts reset automatically
↓
User can try again
```

### 6. **Successful Login**
```
Correct password entered
↓
Attempts cleared for that IP
↓
Session created
↓
Redirect to main page
```

## Visual Indicators

### Error Message (Incorrect Password)
```
┌─────────────────────────────────────────┐
│ ⚠️  Invalid password. 3 attempts        │
│     remaining.                           │
└─────────────────────────────────────────┘
(Red background, shake animation)
```

### Lockout Message
```
┌─────────────────────────────────────────┐
│ 🔒 Too many failed attempts.            │
│     Account locked for 12 minutes.      │
└─────────────────────────────────────────┘
(Yellow background, pulse animation, form disabled)
```

### Disabled Form
```
┌─────────────────────────────┐
│ Password                    │
│ ┌─────────────────────────┐ │
│ │ Account locked       👁️ │ │ <- Grayed out
│ └─────────────────────────┘ │
│                             │
│ [ 🔒 Locked ]               │ <- Disabled button
└─────────────────────────────┘
```

## Implementation Details

### Data Structure
```python
login_attempts = {
    "192.168.1.100": {
        "count": 5,
        "first_attempt": datetime(2024, 1, 1, 10, 0, 0),
        "lockout_until": datetime(2024, 1, 1, 10, 15, 0)
    },
    "192.168.1.101": {
        "count": 2,
        "first_attempt": datetime(2024, 1, 1, 10, 5, 0),
        "lockout_until": None
    }
}
```

### Functions

#### `is_locked_out(ip_address)`
Checks if an IP is currently locked out.

**Returns:**
- `(True, lockout_until)` - If locked out
- `(False, None)` - If not locked out or lockout expired

#### `record_failed_attempt(ip_address)`
Records a failed login attempt.

**Actions:**
- Creates new entry if first attempt
- Increments counter if existing entry
- Sets lockout time if max attempts reached

#### `reset_attempts(ip_address)`
Clears failed attempts after successful login.

**Actions:**
- Removes IP from tracking dictionary
- Allows fresh attempts

## Security Benefits

### ✅ **Prevents Brute Force**
- Limits password guessing attempts
- Forces waiting period between attempt cycles
- Makes automated attacks impractical

### ✅ **IP-Based Tracking**
- Each client tracked independently
- One compromised client doesn't affect others
- Legitimate users unaffected by attacks on different IPs

### ✅ **Automatic Recovery**
- No manual intervention needed
- Lockout expires automatically
- System self-heals after cooldown

### ✅ **User-Friendly**
- Clear feedback on remaining attempts
- Countdown timer during lockout
- No permanent account lock

## Attack Scenarios

### Scenario 1: Single IP Brute Force
```
Attacker tries from one IP:
Attempt 1-5: Blocked after 5 tries
Result: ❌ Locked for 15 minutes
```

### Scenario 2: Distributed Attack
```
Attacker uses multiple IPs:
Each IP: Independent 5-attempt limit
Result: ⚠️ Slows down attack significantly
```

### Scenario 3: Legitimate User Typo
```
User accidentally enters wrong password:
After 2-3 attempts: Gets clear warning
Realizes mistake: Enters correct password
Result: ✅ Successful login, attempts cleared
```

## Limitations & Considerations

### In-Memory Storage
- **Limitation**: Resets on server restart
- **Impact**: Lockouts cleared if server reboots
- **Mitigation**: Use Redis/database for persistence in production

### IP Address Tracking
- **Limitation**: NAT/Proxy users share IP
- **Impact**: Multiple users behind same NAT affected together
- **Mitigation**: Consider adding username to tracking key

### Cloudflare Tunnel
- **Consideration**: Cloudflare forwards real client IP
- **Check**: Verify `request.remote_addr` gets actual client IP
- **Alternative**: Use `X-Forwarded-For` header if needed

## Configuration Options

### Adjust Lockout Settings
```python
# In app.py

# More lenient (for testing/development)
MAX_ATTEMPTS = 10
LOCKOUT_DURATION = timedelta(minutes=5)

# More strict (for production)
MAX_ATTEMPTS = 3
LOCKOUT_DURATION = timedelta(minutes=30)

# Very strict (high-security environments)
MAX_ATTEMPTS = 3
LOCKOUT_DURATION = timedelta(hours=1)
```

### Custom Messages
Update `app.py` login route to customize messages:
```python
# Example: More friendly message
error = f'Oops! Wrong password. You have {attempts_left} more tries.'

# Example: More strict message
error = f'Security alert: {attempts_left} attempts remaining before lockout.'
```

## Monitoring & Logging

### Recommended Additions
```python
# Log failed attempts
import logging

def record_failed_attempt(ip_address):
    logger.warning(f"Failed login attempt from {ip_address}")
    # ... existing code ...

# Log lockouts
def is_locked_out(ip_address):
    if locked_out:
        logger.error(f"Login blocked - IP {ip_address} is locked out")
    # ... existing code ...
```

### Metrics to Track
- Total failed attempts per day
- Number of IPs locked out
- Average lockout duration
- Successful logins after lockout

## Testing

### Manual Test
1. Go to login page
2. Enter wrong password 5 times
3. Verify form disables and shows lockout message
4. Wait 15 minutes or restart server
5. Verify can login again

### Automated Test
```python
# See test output in commit message
# Tests: 5 failed attempts → lockout → rejection
```

## Best Practices

### For Administrators
1. ✅ Monitor login attempt logs
2. ✅ Adjust thresholds based on usage patterns
3. ✅ Consider persistent storage for production
4. ✅ Add IP whitelist for trusted sources
5. ✅ Implement email notifications for lockouts

### For Users
1. ✅ Use strong, memorable passwords
2. ✅ Note remaining attempts warning
3. ✅ Wait for lockout to expire
4. ✅ Contact admin if repeatedly locked out

## Future Enhancements

Potential improvements:
- [ ] Persistent storage (Redis/database)
- [ ] Email notification on lockout
- [ ] Admin panel to view/clear lockouts
- [ ] CAPTCHA after 3 attempts
- [ ] Exponential backoff (5 min, 15 min, 1 hour...)
- [ ] IP whitelist for trusted sources
- [ ] Rate limiting on login page
- [ ] Two-factor authentication option
- [ ] Account-based lockout (not just IP)
- [ ] Audit log of all login attempts

## Summary

✅ **Implemented:**
- 5 attempt limit per IP
- 15-minute lockout duration
- Real-time attempt counter
- Automatic lockout expiration
- User-friendly error messages
- Disabled form during lockout

🔒 **Security Level:** Medium-High
- Effective against basic brute force
- Suitable for internal/private applications
- Consider enhancements for public-facing apps

📊 **User Impact:** Minimal
- Only affects users who enter wrong password 5+ times
- Clear feedback and guidance
- Automatic recovery after timeout

