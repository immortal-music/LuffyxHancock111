import os
from flask import Flask, request, jsonify, redirect
from yt_dlp import YoutubeDL

app = Flask(__name__)

# သင့်ရဲ့ လုံခြုံရေး API Key (youtube.py ထဲက configuration နဲ့ တူရပါမယ်)
ARTISTBOTS_KEY = os.environ.get("ARTISTBOTS_KEY", "velvetaura_secret_2026")

# Main Route - UI ပေါ်စေရန်
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
    <div class="status">🟢 API is running smoothly with anti-bot bypass</div>
</body>
</html>
"""

@app.route('/')
def home():
    return HTML_PAGE

# ----------------------------------------------------
# 1. MAIN DOWNLOAD ENDPOINT (youtube.py မှ လှမ်းခေါ်မည့် Route)
# ----------------------------------------------------
@app.route('/download', methods=['GET'])
def download_api():
    # Parameters များကို ဖတ်ခြင်း
    video_url = request.args.get('url')    
    download_type = request.args.get('type', 'audio')  
    api_key = request.args.get('api_key')  

    # API Key စစ်ဆေးခြင်း
    if not api_key or api_key != ARTISTBOTS_KEY:
        return jsonify({"status": "error", "message": "Unauthorized: Invalid API Key"}), 401

    if not video_url:
        return jsonify({"status": "error", "message": "Missing 'url' parameter"}), 400

    # Full Link ဖြစ်အောင် ပြင်ပေးခြင်း
    if not video_url.startswith(('http://', 'https://')):
        video_url = f"https://www.youtube.com/watch?v={video_url}"

    # ----------------------------------------------------
    # [Anti-Bot Bypass] လူအစစ်ကဲ့သို့ တုပသော yt-dlp Settings
    # ----------------------------------------------------
    ydl_opts = {
        # Format သတ်မှတ်ခြင်း
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best' if download_type == "video" else 'bestaudio/best',
        'quiet': True,
        'nocheckcertificate': True,
        
        # ၁။ လူအစစ်၏ Cookies ကို အသုံးပြုခြင်း (cookies.txt ဖိုင် မဖြစ်မနေ ရှိရပါမည်)
        'cookiefile': 'cookies.txt',
        
        # ၂။ Android, iOS နှင့် Web App များမှ ဝင်သယောင် ဖန်တီးခြင်း
        'extractor_args': {
            'youtube': {
                'player_client': ['android', 'ios', 'web']
            }
        },
        
        # ၃။ Chrome Browser အစစ်ကဲ့သို့ Header များကို လိမ်လည်ခြင်း
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
            'Sec-Fetch-Mode': 'navigate'
        },
        
        # ၄။ လူများကဲ့သို့ Request များကြားတွင် ၁ စက္ကန့် မှ ၃ စက္ကန့်အထိ အချိန်ခဏဆွဲခြင်း
        'sleep_interval_requests': 1,
        'max_sleep_interval': 3,
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            # YouTube မှ Direct Streaming Link ကို ဆွဲယူခြင်း
            info = ydl.extract_info(video_url, download=False)
            
            direct_stream_url = info.get('url')
            
            if not direct_stream_url:
                return jsonify({"status": "error", "message": "Could not extract stream URL"}), 500
            
            # Bot ထံသို့ Streaming Link ကို တိုက်ရိုက် လွှဲပေးလိုက်ခြင်း
            return redirect(direct_stream_url)

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8000))
    app.run(host='0.0.0.0', port=port)
