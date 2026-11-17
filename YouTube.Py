import os, json, asyncio, edge_tts
from moviepy.editor import ColorClip, AudioFileClip, TextClip, CompositeVideoClip
from PIL import Image, ImageDraw
import google.generativeai as genai
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials

# 1. मुफ़्त Gemini AI से वायरल टॉपिक और हिंदी स्क्रिप्ट लिखवाना
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
prompt = 'भारत में YouTube पर ट्रेंडिंग हो रहे किसी एक रोचक विषय पर 35 सेकंड की हिंदी Shorts स्क्रिप्ट लिखो। केवल JSON दो: {"title": "टाइटल #shorts", "script": "हिंदी स्क्रिप्ट बिना इमोजी के", "thumb": "3 शब्द"}'
res = genai.GenerativeModel("gemini-1.5-flash").generate_content(prompt).text.strip("`json\n ")
data = json.loads(res)

# 2. मुफ़्त हिंदी आवाज़ (Microsoft Edge TTS) बनाना
asyncio.run(edge_tts.Communicate(data["script"], "hi-IN-MadhurNeural").save("voice.mp3"))

# 3. थंबनेल बनाना (thumbnail.jpg)
img = Image.new("RGB", (1280, 720), color=(20, 20, 45))
ImageDraw.Draw(img).text((100, 300), data["thumb"], fill=(255, 215, 0))
img.save("thumbnail.jpg")

# 4. वीडियो बनाना (final.mp4)
audio = AudioFileClip("voice.mp3")
bg = ColorClip(size=(1080, 1920), color=(15, 25, 35), duration=audio.duration)
txt = TextClip(data["title"], fontsize=60, color="white", size=(900, None), method="caption").set_position("center").set_duration(audio.duration)
CompositeVideoClip([bg, txt]).set_audio(audio).write_videofile("final.mp4", fps=24, codec="libx264", audio_codec="aac")

# 5. सीधे YouTube पर अपलोड करना
t = json.loads(os.environ["YT_TOKEN_JSON"])
creds = Credentials(token=t.get("access_token"), refresh_token=t.get("refresh_token"), token_uri="https://googleapis.com", client_id="://googleusercontent.com")
yt = build("youtube", "v3", credentials=creds)

req = yt.videos().insert(
    part="snippet,status",
    body={"snippet": {"title": data["title"], "description": data["script"]}, "status": {"privacyStatus": "public", "selfDeclaredMadeForKids": False}},
    media_body=MediaFileUpload("final.mp4")
)
resp = req.execute()
yt.thumbnails().set(videoId=resp["id"], media_body=MediaFileUpload("thumbnail.jpg")).execute()
print("Uploaded:", resp["id"])
