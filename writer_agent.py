import os
import json
from groq import Groq
from datetime import datetime


def get_working_model(client):
    """Fetch available models and pick the best chat model."""
    try:
        models = client.models.list()
        available = [m.id for m in models.data]
        # Preference order: GPT-OSS 120B → Qwen 3.6 27B → Llama 3.1 8B
        for preferred in ["openai/gpt-oss-120b", "qwen/qwen3.6-27b", "llama-3.1-8b-instant"]:
            if preferred in available:
                return preferred
        return available[0] if available else "llama-3.1-8b-instant"
    except Exception:
        return "openai/gpt-oss-120b"  # Fallback


# --- CONFIG ---
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
SUBSTACK_URL = os.environ.get("SUBSTACK_URL", "https://yourname.substack.com")

client = Groq(api_key=GROQ_API_KEY)

PROMPT_TEMPLATE = """You are a regulatory intelligence analyst writing for fintech compliance professionals.

Today's date: {date}

Here are the regulatory updates detected today:
{updates}

Write an 800-word plain-English analysis. Structure:
1. HEADLINE (attention-grabbing, specific)
2. WHAT HAPPENED (2-3 paragraphs, factual)
3. WHY IT MATTERS (2-3 paragraphs, practical implications for fintech compliance teams)
4. WHAT TO DO (3-5 bullet action items)

Tone: Direct, professional, no jargon. Write for a busy compliance officer who has 5 minutes.
Do NOT include a call-to-action or subscription pitch. That goes in the separate teaser.
"""


def load_intel():
    with open("raw_intel.json", "r") as f:
        items = json.load(f)
    # Take top 5 most recent for the prompt
    return items[:5]


def generate_analysis(items):
    MODEL = get_working_model(client)

    updates_text = "\n\n".join([
        f"[{i['source']}] {i['title']}\n{i['summary']}\nLink: {i['link']}"
        for i in items
    ])

    prompt = PROMPT_TEMPLATE.format(
        date=datetime.now().strftime("%B %d, %Y"),
        updates=updates_text
    )

    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=1500
    )

    return response.choices[0].message.content


def save_draft(analysis):
    filename = f"draft_{datetime.now().strftime('%Y%m%d')}.md"
    with open(filename, "w") as f:
        f.write(analysis)
    print(f"Draft saved: {filename}")
    print(f"Word count: {len(analysis.split())}")


def publish_to_substack(analysis):
    cookie_string = os.environ.get("SUBSTACK_COOKIE")
    print(f"[DEBUG] Cookie length: {len(cookie_string) if cookie_string else 0}")
    print(f"[DEBUG] Cookie preview: {cookie_string[:50] if cookie_string else "EMPTY"}"):
    from substack import Api
    from substack.post import Post

    api = Api(
        email=os.environ.get("SUBSTACK_EMAIL"),
        password=os.environ.get("SUBSTACK_PASSWORD"),
        publication_url=SUBSTACK_URL
    )

    post = Post(
        title=analysis.split("\n")[0].replace("# ", "").strip(),
        subtitle="Your weekly AI regulation briefing for fintech compliance teams.",
        user_id=os.environ.get("SUBSTACK_USER_ID"),
        audience="everyone"
    )
    post.from_markdown(analysis)
    api.publish_draft(api.post_draft(post), send=True, share_automatically=False)
    print("Published to Substack")


if __name__ == "__main__":
    intel = load_intel()
    if not intel:
        print("No intel found. Run curator_agent.py first.")
    else:
        analysis = generate_analysis(intel)
        save_draft(analysis)
        print("Draft ready. Publish manually to Substack.")