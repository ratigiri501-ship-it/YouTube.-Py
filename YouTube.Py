import os, json, asyncio, edge_tts
from moviepy.editor import ImageClip, AudioFileClip
from PIL import Image, ImageDraw
import google.generativeai as genai
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials

genai.configure(api_key=os.environ["GEMINI_API_KEY"])
prompt = 'भारत में YouTube पर ट्रेंडिंग हो रहे किसी रोचक विषय पर 35 सेकंड की हिंदी Shorts स्क्रिप्ट लिखो। केवल JSON दो: {"title": "टाइटल #shorts", "script": "हिंदी स्क्रिप्ट बिना इमोजी के", "thumb": "3 शब्द"}'
res = genai.GenerativeModel("gemini-2.5-flash").generate_content(prompt).text.strip("`json\n ")
data = json.loads(res)

asyncio.run(edge_tts.Communicate(data["script"], "hi-IN-MadhurNeural").save("voice.mp3"))

img = Image.new("RGB", (1080, 1920), color=(20, 25, 45))
ImageDraw.Draw(img).text((120, 900), data["thumb"], fill=(255, 215, 0))
img.save("screen.jpg")

audio = AudioFileClip("voice.mp3")
ImageClip("screen.jpg").set_duration(audio.duration).set_audio(audio).write_videofile("final.mp4", fps=24, codec="libx264", audio_codec="aac")

t = json.loads(os.environ["YT_TOKEN_JSON"])
creds = Credentials(token=t.get("access_token"), refresh_token=t.get("refresh_token"), token_uri="https://googleapis.com", client_id="://googleusercontent.com")
yt = build("youtube", "v3", credentials=creds)

resp = yt.videos().insert(
    part="snippet,status",
    body={"snippet": {"title": data["title"], "description": data["script"]}, "status": {"privacyStatus": "public", "selfDeclaredMadeForKids": False}},
    media_body=MediaFileUpload("final.mp4")
).execute()
print("Uploaded:", resp["id"])
