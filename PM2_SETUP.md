# PM2 Setup Guide for TTNN Calculator

## Why PM2?
- ✅ Auto-restart on crash
- ✅ Persist after server reboot
- ✅ Environment variables saved
- ✅ Log management
- ✅ Process monitoring
- ✅ Zero-downtime updates

## Setup Instructions

### 1. Install PM2 (if not already installed)
```bash
npm install -g pm2
# or
sudo npm install -g pm2
```

### 2. Edit Environment Variables
Edit the `ecosystem.config.js` file and replace the placeholder values:

```bash
cd /home/aswin/ttnn-web-calculator
nano ecosystem.config.js
```

Replace these values:
- `FLASK_SECRET_KEY`: Generate a new secret key
- `RESEND_API_KEY`: Your Resend API key (starts with `re_`)

**Generate a secure FLASK_SECRET_KEY:**
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

### 3. Stop Existing Server
```bash
# Kill any existing Python processes
pkill -f "python.*app.py"

# Or if using start.sh
pkill -f start.sh
```

### 4. Start with PM2
```bash
cd /home/aswin/ttnn-web-calculator
pm2 start ecosystem.config.js
```

### 5. Save PM2 Configuration
This ensures the app restarts after reboot:
```bash
pm2 save
```

### 6. Setup Auto-Start on Boot
```bash
pm2 startup
# Follow the command output instructions (usually run a sudo command)

# Then save again
pm2 save
```

## PM2 Commands

### View Status
```bash
pm2 status
# or
pm2 ls
```

Output:
```
┌─────┬────────────────────┬─────────┬─────────┬─────────┬──────────┐
│ id  │ name               │ status  │ restart │ uptime  │ cpu      │
├─────┼────────────────────┼─────────┼─────────┼─────────┼──────────┤
│ 0   │ ttnn-calculator    │ online  │ 0       │ 5m      │ 0%       │
└─────┴────────────────────┴─────────┴─────────┴─────────┴──────────┘
```

### View Logs
```bash
# Real-time logs (all)
pm2 logs ttnn-calculator

# Real-time logs (errors only)
pm2 logs ttnn-calculator --err

# Real-time logs (output only)
pm2 logs ttnn-calculator --out

# Show last 100 lines
pm2 logs ttnn-calculator --lines 100
```

### Restart Application
```bash
pm2 restart ttnn-calculator

# Or restart all
pm2 restart all
```

### Stop Application
```bash
pm2 stop ttnn-calculator

# Or stop all
pm2 stop all
```

### Delete from PM2
```bash
pm2 delete ttnn-calculator

# Or delete all
pm2 delete all
```

### Monitor Resources
```bash
pm2 monit
```

Shows real-time:
- CPU usage
- Memory usage
- Logs

### Reload (Zero Downtime)
```bash
pm2 reload ttnn-calculator
```

### Show Detailed Info
```bash
pm2 show ttnn-calculator
```

## Environment Variables

### Current Configuration
In `ecosystem.config.js`:
```javascript
env: {
  FLASK_SECRET_KEY: 'your-secret-key-here',
  RESEND_API_KEY: 're_your_api_key_here',
  FLASK_ENV: 'production',
  PYTHONUNBUFFERED: '1'
}
```

### Add More Variables
Edit `ecosystem.config.js` and add to the `env` section:
```javascript
env: {
  FLASK_SECRET_KEY: 'xxx',
  RESEND_API_KEY: 're_xxx',
  CUSTOM_VAR: 'value',
  ANOTHER_VAR: 'value'
}
```

Then restart:
```bash
pm2 restart ttnn-calculator
```

### View Environment Variables
```bash
pm2 show ttnn-calculator | grep -A 20 "env:"
```

## Log Management

### Log Files Location
- Error logs: `~/.pm2/logs/ttnn-calculator-error.log`
- Output logs: `~/.pm2/logs/ttnn-calculator-out.log`

### View Logs
```bash
# Real-time
pm2 logs ttnn-calculator

# View error log file
tail -f ~/.pm2/logs/ttnn-calculator-error.log

# View output log file
tail -f ~/.pm2/logs/ttnn-calculator-out.log
```

### Clear Logs
```bash
pm2 flush ttnn-calculator
# or
pm2 flush all
```

### Rotate Logs (Prevent Large Files)
```bash
pm2 install pm2-logrotate

# Configure rotation
pm2 set pm2-logrotate:max_size 10M
pm2 set pm2-logrotate:retain 7
pm2 set pm2-logrotate:compress true
```

## Troubleshooting

### Check if Running
```bash
pm2 status ttnn-calculator
```

Status should be: `online`

### App Keeps Restarting
```bash
# Check logs for errors
pm2 logs ttnn-calculator --err --lines 50

# Check if port is already in use
sudo lsof -i :5000

# Check Python environment
pm2 show ttnn-calculator
```

### Environment Variables Not Working
```bash
# Verify they're set in PM2
pm2 show ttnn-calculator | grep -A 20 "env:"

# Test in app
pm2 logs ttnn-calculator | grep "RESEND_API_KEY"
```

### After Reboot, App Not Running
```bash
# Check PM2 startup configuration
pm2 startup

# Ensure you saved
pm2 save

# Check PM2 is running
pm2 status
```

### Update Configuration
After editing `ecosystem.config.js`:
```bash
# Delete old instance
pm2 delete ttnn-calculator

# Start with new config
pm2 start ecosystem.config.js

# Save
pm2 save
```

## Advanced Configuration

### Multiple Environments
Create different configs:

**ecosystem.config.js** (production):
```javascript
module.exports = {
  apps: [{
    name: 'ttnn-calculator',
    env: {
      FLASK_ENV: 'production',
      RESEND_API_KEY: 're_prod_key'
    }
  }]
};
```

**ecosystem.dev.config.js** (development):
```javascript
module.exports = {
  apps: [{
    name: 'ttnn-calculator-dev',
    env: {
      FLASK_ENV: 'development',
      RESEND_API_KEY: 're_dev_key'
    }
  }]
};
```

Start specific environment:
```bash
pm2 start ecosystem.dev.config.js
```

### Memory Limits
In `ecosystem.config.js`:
```javascript
max_memory_restart: '1G'  // Restart if memory exceeds 1GB
```

### Cron Restarts
```javascript
cron_restart: '0 3 * * *'  // Restart at 3 AM daily
```

### Watch for File Changes
```javascript
watch: true,
watch_delay: 1000,
ignore_watch: ['node_modules', 'logs', '*.log']
```

## Complete Workflow

### Initial Setup
```bash
cd /home/aswin/ttnn-web-calculator

# 1. Edit config
nano ecosystem.config.js
# Set FLASK_SECRET_KEY and RESEND_API_KEY

# 2. Start with PM2
pm2 start ecosystem.config.js

# 3. Save configuration
pm2 save

# 4. Setup auto-start
pm2 startup
# Run the sudo command shown

# 5. Save again
pm2 save
```

### Daily Operations
```bash
# Check status
pm2 status

# View logs
pm2 logs ttnn-calculator

# Restart if needed
pm2 restart ttnn-calculator
```

### After Code Updates
```bash
cd /home/aswin/ttnn-web-calculator

# Pull latest code
git pull

# Restart app (zero downtime)
pm2 reload ttnn-calculator

# Or force restart
pm2 restart ttnn-calculator
```

### After Server Reboot
```bash
# PM2 should auto-start the app
# Verify it's running
pm2 status

# If not running
pm2 resurrect
# or
pm2 start ecosystem.config.js
```

## Security Best Practices

### 1. Never Commit Secrets
Add to `.gitignore`:
```
ecosystem.config.js
.env
```

### 2. Use Environment File (Alternative)
Create `.env` file:
```bash
FLASK_SECRET_KEY=xxx
RESEND_API_KEY=re_xxx
```

Update `ecosystem.config.js`:
```javascript
env_file: '.env'
```

### 3. Restrict File Permissions
```bash
chmod 600 ecosystem.config.js
chmod 600 .env
```

## Comparison: PM2 vs start.sh

### start.sh (Old Way)
❌ Must run manually after reboot
❌ No auto-restart on crash
❌ Environment vars in shell only
❌ No log management
❌ Manual process monitoring

### PM2 (New Way)
✅ Auto-starts after reboot
✅ Auto-restarts on crash
✅ Environment vars in config file
✅ Built-in log management
✅ Easy monitoring (pm2 monit)
✅ Zero-downtime updates

## Summary

**Quick Reference:**
```bash
# Start
pm2 start ecosystem.config.js

# Status
pm2 status

# Logs
pm2 logs ttnn-calculator

# Restart
pm2 restart ttnn-calculator

# Stop
pm2 stop ttnn-calculator

# Save (persist after reboot)
pm2 save

# Auto-start on boot
pm2 startup
pm2 save
```

**Your environment variables will now persist across reboots!** 🎉

---

For more info: https://pm2.keymetrics.io/docs/usage/quick-start/
