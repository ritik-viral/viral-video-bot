import os
import json
import requests
from gtts import gTTS
from google import genai

GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]
PEXELS_API_KEY = os.environ["PEXELS_API_KEY"]
TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

ARTICLE = """
PASTE ARTICLE HERE
"""

PROMPT = f"""
Analyze the news article.

Create a SHORT VERTICAL VIDEO.

Requirements:

- 20 to 60 seconds
- highly engaging
- strong hook
- youtube shorts style
- return ONLY JSON

Format:

{{
"title":"",
"script":"",
"pexels_query":""
}}

Article:

{ARTICLE}
"""

client = genai.Client(api_key=GEMINI_API_KEY)

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=PROMPT
)

text = response.text.strip()

if text.startswith("```json"):
    text = text.replace("```json", "").replace("```", "").strip()

data = json.loads(text)

script = data["script"]
query = data["pexels_query"]

tts = gTTS(script)
tts.save("voice.mp3")

headers = {
    "Authorization": PEXELS_API_KEY
}

r = requests.get(
    "https://api.pexels.com/videos/search",
    headers=headers,
    params={
        "query": query,
        "per_page": 1
    }
)

video = r.json()["videos"][0]
video_url = video["video_files"][0]["link"]

video_data = requests.get(video_url)

with open("video.mp4", "wb") as f:
    f.write(video_data.content)

os.system(
    'ffmpeg -y -i video.mp4 -i voice.mp3 -shortest final.mp4'
)

url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendVideo"

requests.post(
    url,
    data={
        "chat_id": TELEGRAM_CHAT_ID
    },
    files={
        "video": open("final.mp4", "rb")
    }
)

print("DONE")
