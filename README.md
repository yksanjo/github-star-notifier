# StarAlert ⭐

> **GitHub Star Notifier** - Get notified when someone stars your repository, with context about who starred and why. Never miss a potential contributor or user.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Status: Active](https://img.shields.io/badge/status-active-success.svg)](https://github.com/yksanjo/StarAlert-)
[![GitHub stars](https://img.shields.io/github/stars/yksanjo/StarAlert-?style=social)](https://github.com/yksanjo/StarAlert-)

**StarAlert** sends you real-time notifications when someone stars your GitHub repository, including information about the stargazer. Perfect for open-source maintainers who want to engage with their community.

## Features

- ⭐ Real-time star notifications
- 👤 Starred user information
- 🔍 Context about stargazers
- 💬 Slack/Discord/Email notifications
- 📊 Star analytics and trends
- 🎯 Filter by user type (developer, company, etc.)

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

Create a `.env` file:

```env
GITHUB_TOKEN=ghp_your_token_here
GITHUB_REPO=owner/repo-name

# Notification Settings
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/YOUR/WEBHOOK/URL
EMAIL_NOTIFICATIONS=false
EMAIL_TO=your-email@example.com
```

## Usage

### Start Monitoring

```bash
python notify.py
```

### Check Stars Once

```bash
python notify.py --check-once
```

### View Star History

```bash
python notify.py --history
```

### Filter Notifications

```bash
python notify.py --min-followers 100  # Only notify for users with 100+ followers
```

## Notification Format

```
⭐ New Star!
Repository: owner/repo
Stargazer: @username (John Doe)
Bio: Software engineer at Company
Followers: 1,234
Location: San Francisco, CA
Starred at: 2024-01-15 10:30 AM
```

## License

MIT License


