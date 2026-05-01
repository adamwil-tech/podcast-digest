import feedparser
import anthropic
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

# Your podcasts
PODCASTS = {
    "Modern Wisdom": "https://feeds.megaphone.fm/modernwisdom",
    "Timesuck": "https://feeds.megaphone.fm/timesuck",
    "Morning Brew Daily": "https://feeds.megaphone.fm/morningbrewdaily",
    "Prof G Markets": "https://feeds.megaphone.fm/profgmarkets",
    "Diary of a CEO": "https://feeds.megaphone.fm/diaryofaceo",
    "Prof G Pod": "https://feeds.megaphone.fm/profgpod",
    "Mr. Ballen": "https://feeds.megaphone.fm/mrballen",
}

# Step 1 — Fetch latest episode from each podcast
def get_latest_episodes():
    episodes = []
    for show, url in PODCASTS.items():
        feed = feedparser.parse(url)
        if feed.entries:
            entry = feed.entries[0]
            episodes.append({
                "show": show,
                "title": entry.get("title", "No title"),
                "summary": entry.get("summary", "No description available")
            })
    return episodes

# Step 2 — Use Claude to summarize topics
def summarize_episodes(episodes):
    client = anthropic.Anthropic()
    summaries = []

    for ep in episodes:
        response = client.messages.create(
            model="claude-opus-4-5",
            max_tokens=200,
            messages=[{
                "role": "user",
                "content": f"In 2-3 bullet points, what topics are covered in this podcast episode?\n\nShow: {ep['show']}\nTitle: {ep['title']}\nDescription: {ep['summary']}"
            }]
        )
        summary = response.content[0].text
        summaries.append({
            "show": ep["show"],
            "title": ep["title"],
            "summary": summary
        })

    return summaries

# Step 3 — Format the email
def format_email(summaries):
    body = "<h2>🎙️ Your Morning Podcast Digest</h2>"
    for ep in summaries:
        body += f"<h3>{ep['show']}</h3>"
        body += f"<p><strong>{ep['title']}</strong></p>"
        body += f"<p>{ep['summary'].replace(chr(10), '<br>')}</p>"
        body += "<hr>"
    return body

# Step 4 — Send the email
def send_email(html_body):
    message = Mail(
        from_email="adamwil@gmail.com",
        to_emails="adamwil@gmail.com",
        subject="☕ Your Morning Podcast Digest",
        html_content=html_body
    )
    sg = SendGridAPIClient(os.environ.get("SENDGRID_API_KEY"))
    response = sg.send(message)
    print(f"Email sent! Status: {response.status_code}")

# Run it
episodes = get_latest_episodes()
summaries = summarize_episodes(episodes)
html_body = format_email(summaries)
send_email(html_body)