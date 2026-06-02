import os
import random
from flask import Flask, request, jsonify, redirect
from yt_dlp import YoutubeDL

app = Flask(__name__)

# API Key
ARTISTBOTS_KEY = os.environ.get("ARTISTBOTS_KEY", "velvetaura_secret_2026")

# အစ်ကို ပေးထားသော Proxy (၁၀) ခု စာရင်း
PROXIES = [
    "http://qduuujrj:bf1ttoecf2d5@31.59.20.176:6754",
    "http://qduuujrj:bf1ttoecf2d5@23.95.150.145:6114",
    "http://qduuujrj:bf1ttoecf2d5@198.23.239.134:6540",
    "http://qduuujrj:bf1ttoecf2d5@45.38.107.97:6014",
    "http://qduuujrj:bf1ttoecf2d5@107.172.163.27:6543",
    "http://qduuujrj:bf1ttoecf2d5@198.105.121.200:6462",
    "http://qduuujrj:bf1ttoecf2d5@216.10.27.159:6837",
    "http://qduuujrj:bf1ttoecf2d5@142.111.67.146:5611",
    "http://qduuujrj:bf1ttoecf2d5@191.96.254.138:6185",
    "http://qduuujrj:bf1ttoecf2d5@31.58.9.4:6077"
]

HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ArtistBots API - Velvet Aura</title>
    <style>
        body { margin: 0; padding: 0; height: 100vh; display: flex; justify-content: center; align-items: center; background: linear-gradient(135deg, #5b73df, #8263cf); font-family: sans-serif; color: white; flex-direction: column;}
        h1 { font-size: 4rem; text-shadow: 2px 5px 10px rgba(0,0,0,0.3); margin: 0;}
        p { font-size: 1.2rem; opacity: 0.9; }
        .status { margin-top: 20px; padding: 10px 20px; background: rgba(0,0,0,0.2); border-radius: 20px; font-size: 0.9rem; }
    </style>
</head>
<body>
    <h1>LuffyxHancock</h1>
    <p>Advanced Audio & Video Streaming API</p>
    <div class="status">🟢 API is running with Rotating Proxies Protection</div>
</body>
</html>
"""

@app.route('/')
def home():
    return HTML_PAGE

@app.route('/download', methods=['GET'])
def download_api():
    video_url = request.args.get('url')    
    download_type = request.args.get('type', 'audio')  
    api_key = request.args.get('api_key')  

    if not api_key or api_key != ARTISTBOTS_KEY:
        return jsonify({"status": "error", "message": "Unauthorized: Invalid API Key"}), 401

    if not video_url:
        return jsonify({"status": "error", "message": "Missing 'url' parameter"}), 400

    if not video_url.startswith(('http://', 'https://')):
        video_url = f"https://www.youtube.com/watch?v={video_url}"

    # သီချင်းတစ်ပုဒ် တောင်းတိုင်း Proxy (၁၀) ခုထဲမှ တစ်ခုကို ကျပန်း ရွေးချယ်မည်
    selected_proxy = random.choice(PROXIES)

    # yt-dlp Settings
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best' if download_type == "video" else 'bestaudio/best',
        'quiet': True,
        'nocheckcertificate': True,
        'cookiefile': 'cookies.txt', 
        'proxy': selected_proxy, # ရွေးချယ်လိုက်သော Proxy ကို အသုံးပြုမည်
        'extractor_args': {
            'youtube': {
                'player_client': ['android', 'ios', 'web']
            }
        },
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
            'Sec-Fetch-Mode': 'navigate'
        }
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            direct_stream_url = info.get('url')
            
            if not direct_stream_url:
                return jsonify({"status": "error", "message": "Could not extract stream URL"}), 500
            
            return redirect(direct_stream_url)

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8000))
    app.run(host='0.0.0.0', port=port)
