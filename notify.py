#!/usr/bin/env python3
"""
GitHub Star Notifier
Get notified when someone stars your repository
"""

import os
import sys
import argparse
import json
import time
from datetime import datetime
from typing import Dict, List, Optional
import requests
from dotenv import load_dotenv
import schedule

load_dotenv()

class GitHubStarNotifier:
    def __init__(self):
        self.token = os.getenv('GITHUB_TOKEN')
        self.repo = os.getenv('GITHUB_REPO')
        
        if not self.token:
            raise ValueError("GITHUB_TOKEN not set in environment")
        if not self.repo:
            raise ValueError("GITHUB_REPO not set in environment")
        
        self.headers = {
            'Authorization': f'token {self.token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        self.state_file = 'stars_state.json'
        self.known_stars = self.load_state()
        
        # Notification settings
        self.slack_webhook = os.getenv('SLACK_WEBHOOK_URL')
        self.discord_webhook = os.getenv('DISCORD_WEBHOOK_URL')
        self.email_enabled = os.getenv('EMAIL_NOTIFICATIONS', 'false').lower() == 'true'
        self.email_to = os.getenv('EMAIL_TO')
        self.min_followers = int(os.getenv('MIN_FOLLOWERS', 0))
    
    def load_state(self) -> set:
        """Load known stars from state file"""
        if os.path.exists(self.state_file):
            with open(self.state_file, 'r') as f:
                data = json.load(f)
                return set(data.get('known_stars', []))
        return set()
    
    def save_state(self):
        """Save known stars to state file"""
        data = {
            'known_stars': list(self.known_stars),
            'last_check': datetime.now().isoformat()
        }
        with open(self.state_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def get_stargazers(self) -> List[Dict]:
        """Get list of stargazers for the repository"""
        url = f"https://api.github.com/repos/{self.repo}/stargazers"
        stargazers = []
        page = 1
        per_page = 100
        
        while True:
            params = {'page': page, 'per_page': per_page}
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            if not data:
                break
            
            for stargazer in data:
                stargazers.append({
                    'login': stargazer['login'],
                    'id': stargazer['id'],
                    'avatar_url': stargazer['avatar_url'],
                    'html_url': stargazer['html_url']
                })
            
            # Check if there are more pages
            if len(data) < per_page:
                break
            page += 1
        
        return stargazers
    
    def get_user_info(self, username: str) -> Optional[Dict]:
        """Get detailed user information"""
        url = f"https://api.github.com/users/{username}"
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"❌ Error fetching user info for {username}: {e}")
            return None
    
    def send_slack_notification(self, star_info: Dict):
        """Send notification to Slack"""
        if not self.slack_webhook:
            return
        
        try:
            message = {
                "text": f"⭐ New Star on {self.repo}!",
                "blocks": [
                    {
                        "type": "header",
                        "text": {
                            "type": "plain_text",
                            "text": "⭐ New Star!"
                        }
                    },
                    {
                        "type": "section",
                        "fields": [
                            {
                                "type": "mrkdwn",
                                "text": f"*Repository:*\n{self.repo}"
                            },
                            {
                                "type": "mrkdwn",
                                "text": f"*Stargazer:*\n<{star_info['html_url']}|@{star_info['login']}>"
                            }
                        ]
                    }
                ]
            }
            
            if star_info.get('name'):
                message["blocks"].append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Name:* {star_info['name']}"
                    }
                })
            
            if star_info.get('bio'):
                message["blocks"].append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Bio:* {star_info['bio']}"
                    }
                })
            
            if star_info.get('followers') is not None:
                message["blocks"].append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Followers:* {star_info['followers']:,}"
                    }
                })
            
            requests.post(self.slack_webhook, json=message)
        except Exception as e:
            print(f"❌ Slack notification error: {e}")
    
    def send_discord_notification(self, star_info: Dict):
        """Send notification to Discord"""
        if not self.discord_webhook:
            return
        
        try:
            embed = {
                "title": "⭐ New Star!",
                "description": f"Someone starred **{self.repo}**",
                "color": 0x5865F2,
                "fields": [
                    {
                        "name": "Stargazer",
                        "value": f"[@{star_info['login']}]({star_info['html_url']})",
                        "inline": True
                    }
                ],
                "timestamp": datetime.now().isoformat()
            }
            
            if star_info.get('name'):
                embed["fields"].append({
                    "name": "Name",
                    "value": star_info['name'],
                    "inline": True
                })
            
            if star_info.get('bio'):
                embed["description"] += f"\n\n**Bio:** {star_info['bio']}"
            
            if star_info.get('followers') is not None:
                embed["fields"].append({
                    "name": "Followers",
                    "value": f"{star_info['followers']:,}",
                    "inline": True
                })
            
            message = {"embeds": [embed]}
            requests.post(self.discord_webhook, json=message)
        except Exception as e:
            print(f"❌ Discord notification error: {e}")
    
    def check_new_stars(self):
        """Check for new stars and send notifications"""
        print(f"🔍 Checking stars for {self.repo}...")
        
        stargazers = self.get_stargazers()
        new_stars = []
        
        for stargazer in stargazers:
            star_id = f"{stargazer['login']}_{stargazer['id']}"
            if star_id not in self.known_stars:
                new_stars.append(stargazer)
                self.known_stars.add(star_id)
        
        if new_stars:
            print(f"✅ Found {len(new_stars)} new star(s)!")
            
            for stargazer in new_stars:
                # Get detailed user info
                user_info = self.get_user_info(stargazer['login'])
                
                if user_info:
                    # Filter by minimum followers
                    if user_info.get('followers', 0) < self.min_followers:
                        print(f"⏭️  Skipping {stargazer['login']} (followers < {self.min_followers})")
                        continue
                    
                    star_info = {
                        'login': stargazer['login'],
                        'html_url': stargazer['html_url'],
                        'name': user_info.get('name'),
                        'bio': user_info.get('bio'),
                        'followers': user_info.get('followers', 0),
                        'location': user_info.get('location'),
                        'company': user_info.get('company'),
                        'starred_at': datetime.now().isoformat()
                    }
                    
                    # Send notifications
                    self.send_slack_notification(star_info)
                    self.send_discord_notification(star_info)
                    
                    # Print to console
                    print(f"\n⭐ New Star!")
                    print(f"   User: @{star_info['login']} ({star_info.get('name', 'N/A')})")
                    if star_info.get('bio'):
                        print(f"   Bio: {star_info['bio']}")
                    print(f"   Followers: {star_info['followers']:,}")
                    if star_info.get('location'):
                        print(f"   Location: {star_info['location']}")
        else:
            print("✓ No new stars")
        
        self.save_state()
    
    def show_history(self):
        """Show star history"""
        stargazers = self.get_stargazers()
        print(f"\n📊 Star History for {self.repo}")
        print("="*60)
        print(f"Total Stars: {len(stargazers)}")
        print("\nRecent Stargazers:")
        
        for i, stargazer in enumerate(stargazers[:10], 1):
            user_info = self.get_user_info(stargazer['login'])
            if user_info:
                print(f"{i}. @{stargazer['login']} - {user_info.get('name', 'N/A')} ({user_info.get('followers', 0):,} followers)")
    
    def run_continuous(self, interval: int = 300):
        """Run continuous monitoring"""
        print(f"🚀 Starting continuous star monitoring (checking every {interval}s)")
        
        schedule.every(interval).seconds.do(self.check_new_stars)
        
        # Initial check
        self.check_new_stars()
        
        while True:
            schedule.run_pending()
            time.sleep(60)


def main():
    parser = argparse.ArgumentParser(description='GitHub Star Notifier')
    parser.add_argument('--check-once', action='store_true', help='Check once and exit')
    parser.add_argument('--history', action='store_true', help='Show star history')
    parser.add_argument('--interval', type=int, default=300, help='Check interval in seconds (default: 300)')
    parser.add_argument('--min-followers', type=int, default=0, help='Minimum followers to notify')
    
    args = parser.parse_args()
    
    try:
        notifier = GitHubStarNotifier()
        notifier.min_followers = args.min_followers
        
        if args.history:
            notifier.show_history()
        elif args.check_once:
            notifier.check_new_stars()
        else:
            notifier.run_continuous(args.interval)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()


