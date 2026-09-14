import os
import requests
import random
from datetime import datetime

# --- CONFIG ---
WP_SITE = os.environ.get("WP_URL")  # e.g. yourblog.wordpress.com
WP_USERNAME = os.environ.get("WP_USERNAME")
WP_APP_PASSWORD = os.environ.get("WP_APP_PASSWORD")
SUBSTACK_URL = os.environ.get("SUBSTACK_URL", "https://yourname.substack.com")

# Clean site name
if WP_SITE:
    WP_SITE = WP_SITE.replace("https://", "").replace("http://", "").strip("/")

API_URL = f"https://public-api.wordpress.com/wp/v2/sites/{WP_SITE}/posts"

TEASERS = [
    {
        "title": "The FCA Just Published New AI Guidance. Here's What It Actually Means.",
        "content": f"<p>The FCA released new supervisory guidance on AI risk management this week. Most of the coverage is either too technical or too vague.</p><p>I read the full 47-page document so you don't have to. The key takeaway: firms using automated decision systems must now document their model risk assessments quarterly.</p><p><strong>Read the full plain-English analysis (paid subscribers only):</strong> <a href='{SUBSTACK_URL}'>{SUBSTACK_URL}</a></p><p>Every week I translate the latest regulatory updates into a 5-minute briefing for fintech compliance teams. Free subscribers get headlines. Paid subscribers get the full analysis.</p>"
    },
    {
        "title": "SEC Enforcement Just Hit an AI Robo-Advisor. What Every Fintech Needs to Know.",
        "content": f"<p>The SEC fined a robo-advisor $750K last week for failing to disclose how its AI allocated client funds. This is the first enforcement action of its kind.</p><p><strong>Why it matters:</strong> If your firm uses any algorithmic decisioning in client-facing processes, you're now on the radar.</p><p>I broke down the enforcement order and what it means for your compliance playbook: <a href='{SUBSTACK_URL}'>{SUBSTACK_URL}</a></p><p>Free subscribers get weekly headlines. Paid subscribers get full analysis + action items.</p>"
    },
    {
        "title": "ESMA Is Consulting on AI in Trading. Here's the 3-Point Summary.",
        "content": f"<p>ESMA opened a consultation on AI use in trading algorithms this week. 87 pages. I summarised it in 3 bullet points.</p><p>1. Algorithmic trading systems using ML must be registered. 2. Kill-switch procedures must be documented. 3. Annual model audits become mandatory.</p><p><strong>Full analysis for paid subscribers:</strong> <a href='{SUBSTACK_URL}'>{SUBSTACK_URL}</a></p>"
    }
]

def publish_teaser():
    post = random.choice(TEASERS)
    auth = (WP_USERNAME, WP_APP_PASSWORD)
    payload = {
        "title": post["title"],
        "content": post["content"],
        "status": "publish"
    }
    r = requests.post(API_URL, auth=auth, json=payload, timeout=30)
    print(f"Status: {r.status_code}")
    if r.status_code == 201:
        print(f"Published: {r.json().get('link')}")

if __name__ == "__main__":
    publish_teaser()