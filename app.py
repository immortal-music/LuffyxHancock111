import os
from flask import Flask, request, jsonify, send_file
from yt_dlp import YoutubeDL

app = Flask(__name__)

# သင့်ရဲ့ လုံခြုံရေး API Key (youtube.py ထဲက configuration နဲ့ တူရပါမယ်)
# .env ထဲမှာ မသတ်မှတ်ထားရင် default အနေနဲ့ 'my_secret_key' ဖြစ်ပါမယ်
ARTISTBOTS_KEY = os.environ.get("ARTISTBOTS_KEY", "velvetaura_secret_2026")

# Main Route - UI ပေါ်စေရန်
HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ArtistBots API</title>
    <style>
        body { margin: 0; padding: 0; height: 100vh; display: flex; justify-content: center; align-items: center; background: linear-gradient(135deg, #5b73df, #8263cf); font-family: sans-serif; color: white; flex-direction: column;}
        h1 { font-size: 4rem; text-shadow: 2px 5px 10px rgba(0,0,0,0.3); margin: 0;}
        p { font-size: 1.2rem; opacity: 0.9; }
    </style>
</head>
<body>
    <h1>LuffyxHancock</h1>
    <p>Audio & Video Downloader API - Running successfully!</p>
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
    # youtube.py မှ ပို့လိုက်သော Query Parameters များကို ဖတ်ခြင်း
    video_url = request.args.get('url')    # YouTube Link သို့မဟုတ် Video ID
    download_type = request.args.get('type', 'audio')  # 'audio' သို့မဟုတ် 'video'
    api_key = request.args.get('api_key')  # Security API Key

    # API Key စစ်ဆေးခြင်း
    if not api_key or api_key != ARTISTBOTS_KEY:
        return jsonify({"status": "error", "message": "Unauthorized: Invalid API Key"}), 401

    if not video_url:
        return jsonify({"status": "error", "message": "Missing 'url' parameter"}), 400

    # youtube.py သည် Video ID သက်သက်ပဲ ပို့နိုင်သဖြင့် Full Link ဖြစ်အောင် ပြန်ပြင်ပေးခြင်း
    if not video_url.startswith(('http://', 'https://')):
        video_url = f"https://www.youtube.com/watch?v={video_url}"

    # ဒေါင်းလုဒ် Format သတ်မှတ်ခြင်း (Audio သို့မဟုတ် Video)
    if download_type == "video":
        # အသံရော ရုပ်ပါပါတဲ့ အကောင်းဆုံး format (720p အထိ Max limit ထားလိုက ထားနိုင်)
        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best',
            'quiet': True,
            'nocheckcertificate': True
        }
    else:
        # Audio Stream သီးသန့်အတွက်
        ydl_opts = {
            'format': 'bestaudio/best',
            'quiet': True,
            'nocheckcertificate': True
        }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            # YouTube မှ အချက်အလက်နှင့် Direct Streaming Link ကို ဆွဲယူခြင်း
            info = ydl.extract_info(video_url, download=False)
            
            # ၎င်း Direct Link သို့ Bot ဘက်မှ လှမ်းဝင်ပြီး Binary data ကို တစ်ဆင့်ချင်း သိမ်းယူသွားမည်
            direct_stream_url = info.get('url')
            
            if not direct_stream_url:
                return jsonify({"status": "error", "message": "Could not extract stream URL"}), 500
            
            # youtube.py ၏ aiohttp က သီချင်းဖိုင်/ဗီဒီယိုဖိုင်ကို တိုက်ရိုက် ဆွဲယူနိုင်ရန် Redirect လုပ်ပေးခြင်း
            from flask import redirect
            return redirect(direct_stream_url)

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8000))
    app.run(host='0.0.0.0', port=port)
