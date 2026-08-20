"""
Generates one Hindi personal-finance / government-scheme article using the
Sarvam AI chat completion API, and saves it as a Hugo-ready Markdown post.

Run manually:   python scripts/generate_post.py
Run in CI:      triggered by .github/workflows/generate-and-deploy.yml

Requires env var: SARVAM_API_KEY
"""

import os
import json
import random
import datetime
from pathlib import Path

from openai import OpenAI  # Sarvam exposes an OpenAI-compatible endpoint

ROOT = Path(__file__).resolve().parent.parent
TOPICS_FILE = ROOT / "data" / "topics.json"
USED_FILE = ROOT / "data" / "used_topics.json"
POSTS_DIR = ROOT / "content" / "posts"

SARVAM_API_KEY = os.environ.get("SARVAM_API_KEY")
if not SARVAM_API_KEY:
    raise SystemExit("ERROR: set the SARVAM_API_KEY environment variable / GitHub secret.")

client = OpenAI(base_url="https://api.sarvam.ai/v1", api_key=SARVAM_API_KEY)


def load_json(path, default):
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return default


def pick_topic():
    topics = load_json(TOPICS_FILE, [])
    used = load_json(USED_FILE, [])
    remaining = [t for t in topics if t not in used]

    # once every topic has been used, start the cycle again
    if not remaining:
        used = []
        remaining = topics

    topic = random.choice(remaining)
    used.append(topic)
    USED_FILE.write_text(json.dumps(used, ensure_ascii=False, indent=2), encoding="utf-8")
    return topic


def slugify_fallback(topic: str) -> str:
    import hashlib
    return hashlib.sha1(topic.encode("utf-8")).hexdigest()[:8]


def generate_article(topic: str) -> tuple[str, str, str]:
    system_prompt = (
        "आप एक अनुभवी वित्तीय लेखक हैं जो आम भारतीय पाठकों के लिए सरल हिंदी में "
        "स्पष्ट, सटीक और उपयोगी लेख लिखते हैं। जानकारी सामान्य शिक्षा के उद्देश्य से है, "
        "यह वित्तीय सलाह नहीं है — इसका उल्लेख लेख के अंत में जरूर करें। "
        "आधिकारिक शब्दावली सही रखें, लेकिन भाषा सरल और सुलभ रखें। "
        "लेख को Markdown में लिखें, उपयुक्त उप-शीर्षकों (##) के साथ।"
    )
    user_prompt = (
        f"विषय: {topic}\n\n"
        "इस विषय पर लगभग 700-900 शब्दों का एक लेख लिखें। इसमें शामिल करें:\n"
        "- संक्षिप्त परिचय\n"
        "- पात्रता / जरूरी शर्तें (यदि लागू हो)\n"
        "- चरण-दर-चरण प्रक्रिया\n"
        "- जरूरी दस्तावेज़\n"
        "- आम गलतियाँ या सावधानियाँ\n"
        "- निष्कर्ष के साथ डिस्क्लेमर कि यह सामान्य जानकारी है, वित्तीय सलाह नहीं\n\n"
        "IMPORTANT FORMATTING INSTRUCTIONS:\n"
        "Your response must be in the following format exactly:\n"
        "SLUG: <an english/hinglish url slug for this topic, e.g. epf-paisa-kaise-nikale>\n"
        "DESCRIPTION: <a short 150-character meta description in Hindi summarizing the article>\n"
        "CONTENT:\n"
        "<the hindi markdown article body without H1>\n\n"
        "Do not include any other text before SLUG: or between SLUG:, DESCRIPTION: and CONTENT:."
    )

    response = client.chat.completions.create(
        model="sarvam-105b-conversations",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.6,
        max_tokens=1800,
    )
    raw_text = response.choices[0].message.content.strip()
    
    slug = ""
    description = ""
    body = raw_text
    
    if "CONTENT:" in raw_text:
        parts = raw_text.split("CONTENT:", 1)
        header = parts[0]
        body = parts[1].strip()
        
        for line in header.split("\n"):
            if line.startswith("SLUG:"):
                slug = line.replace("SLUG:", "").strip().lower()
                import re
                slug = re.sub(r'[^a-z0-9\-]', '', slug.replace(' ', '-'))
                slug = re.sub(r'\-+', '-', slug).strip('-')
            elif line.startswith("DESCRIPTION:"):
                description = line.replace("DESCRIPTION:", "").strip()
                # strip quotes if ai added them
                if description.startswith('"') and description.endswith('"'):
                    description = description[1:-1]
                
    if not slug:
        slug = slugify_fallback(topic)
        
    return slug, description, body


def build_front_matter(title: str, date: str, description: str) -> str:
    # clean description for yaml
    desc_clean = description.replace('"', '\\"')
    return (
        "---\n"
        f'title: "{title}"\n'
        f"date: {date}\n"
        f'description: "{desc_clean}"\n'
        "draft: false\n"
        'tags: ["personal-finance", "government-schemes"]\n'
        "---\n\n"
    )


def main():
    POSTS_DIR.mkdir(parents=True, exist_ok=True)
    topic = pick_topic()
    print(f"Generating article for topic: {topic}")

    slug, description, body = generate_article(topic)
    date = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S+00:00")
    filename = POSTS_DIR / f"{datetime.date.today().isoformat()}-{slug}.md"

    content = build_front_matter(topic, date, description) + body + "\n"
    filename.write_text(content, encoding="utf-8")
    print(f"Saved: {filename}")


if __name__ == "__main__":
    main()
