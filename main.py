import os
import json
import requests
from gtts import gTTS
from google import genai

GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]
PEXELS_API_KEY = os.environ["PEXELS_API_KEY"]

ARTICLE = """
G7 Summit Day 1 LIVE: PM Modi holds brief conversation with U.S. President Trump
Prime Minister Narendra Modi arrived in France on Tuesday to attend the G7 Summit and exchange views with world leaders on key global issues.
Prime Minister Narenda Modi talks to U.S. President Donald Trump before the plenary session at the G7 summit, on June 16, 2026, in Evian-les-Bains, France. | Photo Credit: AP

Prime Minister Narendra Modi and U.S. President Donald Trump on Tuesday (June 16, 2026) exchanged pleasantries and held a brief conversation at the G7 summit in the French commune of Evian-les-Bains in the first in-person encounter between the two leaders in nearly one-and-a-half years.


President Donald Trump on Tuesday (June 16, 2026) said the U.S. will soon be able to reimpose sanctions against Russian oil, at the G7 summit where leaders are seeking to ratchet up pressure against Moscow over its invasion of Ukraine. G7 leaders agreed on Tuesday (June 16, 2026) to intensify pressure on Russia to end more than four years of war against Ukraine, with U.S. President Donald Trump saying Moscow should “make a deal”. 
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

print("===================================")
print("VIDEO CREATED SUCCESSFULLY")
print("File: final.mp4")
print("===================================")
