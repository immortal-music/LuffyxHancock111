import os
import uuid
import glob
import random
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
from fastapi.responses import HTMLResponse, FileResponse
import yt_dlp
import httpx

# Render ပေါ်မှာ FFmpeg အလုပ်လုပ်နိုင်ရန် PATH သတ်မှတ်ခြင်း
ffmpeg_path = os.path.join(os.getcwd(), "ffmpeg")
if os.path.exists(ffmpeg_path):
    os.environ["PATH"] += os.pathsep + ffmpeg_path

# Cookies သိမ်းဆည်းမည့် လမ်းကြောင်းနှင့် Pastebin URL
COOKIE_URL = "https://pastebin.com/raw/9YqWBeCn"
COOKIE_FILE = "cookies.txt"

# Authentication Key
API_KEY = os.getenv("API_KEY", "LuffyxHancock")

# ပုံထဲမှ ရယူထားသော Proxy List များ
PROXIES = [
    "http://qduuujrj:bf1ttoecf2d5@38.154.203.95:5863",
    "http://qduuujrj:bf1ttoecf2d5@198.105.121.200:6462",
    "http://qduuujrj:bf1ttoecf2d5@64.137.96.74:6641",
    "http://qduuujrj:bf1ttoecf2d5@209.127.138.10:5784",
    "http://qduuujrj:bf1ttoecf2d5@38.154.185.97:6370",
    "http://qduuujrj:bf1ttoecf2d5@84.247.60.125:6095",
    "http://qduuujrj:bf1ttoecf2d5@142.111.67.146:5611",
    "http://qduuujrj:bf1ttoecf2d5@191.96.254.138:6185",
    "http://qduuujrj:bf1ttoecf2d5@31.58.9.4:6077",
    "http://qduuujrj:bf1ttoecf2d5@104.239.107.47:5699"
]

async def fetch_pastebin_cookies():
    """Pastebin မှ Cookies များကို ဆွဲယူပြီး ဖိုင်အဖြစ် သိမ်းဆည်းပေးမည့် Function"""
    try:
        async with httpx.AsyncClient() as client:
            print(f"🍪 Fetching cookies from Pastebin...")
            response = await client.get(COOKIE_URL, timeout=15.0)
            if response.status_code == 200 and len(response.text) > 50:
                with open(COOKIE_FILE, "w", encoding="utf-8") as f:
                    f.write(response.text)
                print("✅ Cookies updated successfully from Pastebin!")
                return True
            else:
                print("⚠️ Pastebin returned invalid or empty content.")
    except Exception as e:
        print(f"❌ Failed to fetch cookies from Pastebin: {e}")
    return False

def get_random_proxy():
    """Proxy List ထဲမှ Random တစ်ခုကို ရွေးချယ်ပေးမည့် Function"""
    if not PROXIES:
        return None
    return random.choice(PROXIES)

# FastAPI Lifespan သုံးပြီး Server စတက်တာနဲ့ Cookies ကို အရင်ဒေါင်းလုဒ်ဆွဲခိုင်းခြင်း
@asynccontextmanager
async def lifespan(app: FastAPI):
    await fetch_pastebin_cookies()
    yield

app = FastAPI(title="ArtistBots API", lifespan=lifespan)

@app.get("/", response_class=HTMLResponse)
@app.head("/", response_class=HTMLResponse)
async def index():
    # Landing Page UI
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>LuffyxHancock API</title>
        <style>
            body {
                margin: 0;
                padding: 0;
                height: 100vh;
                background: linear-gradient(135deg, #6c78eb, #8b6bed);
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                color: white;
            }
            .container {
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                text-align: center;
                width: 100%;
            }
            h1 {
                font-size: 2.5rem;
                margin-bottom: 8px;
                font-weight: bold;
                letter-spacing: 0.5px;
            }
            p {
                font-size: 0.95rem;
                opacity: 0.9;
                margin-bottom: 25px;
                font-weight: 300;
            }
            .badge {
                display: inline-flex;
                align-items: center;
                background: rgba(0, 0, 0, 0.15);
                padding: 8px 18px;
                border-radius: 20px;
                font-size: 0.8rem;
                font-weight: 500;
            }
            .dot {
                width: 10px;
                height: 10px;
                background-color: #4ade80;
                border-radius: 50%;
                margin-right: 10px;
                box-shadow: 0 0 8px #4ade80;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>LuffyxHancock</h1>
            <p>Advanced Audio & Video Streaming API</p>
            <div class="badge">
                <span class="dot"></span>
                API is running with Rotating Proxies Protection
            </div>
        </div>
    </body>
    </html>
    """

def cleanup_file(filepath: str):
    """Download ဆွဲပြီးသွားတဲ့ ဖိုင်တွေကို Server ပေါ်ကနေ ပြန်ဖျက်ပေးမယ့် Function"""
    try:
        if filepath and os.path.exists(filepath):
            os.remove(filepath)
    except Exception as e:
        print(f"Error removing file: {e}")

@app.get("/download")
async def download_media(
    background_tasks: BackgroundTasks,
    url: str = Query(..., description="YouTube Video ID or URL"),
    type: str = Query("audio", description="Media type: 'audio' or 'video'"),
    api_key: str = Query(None, description="Authentication Key")
):
    # API Key စစ်ဆေးခြင်း
    if API_KEY and api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized: Invalid API Key")

    # YouTube ID ဖြတ်ထုတ်ခြင်း
    video_id = url.split("v=")[-1].split("&")[0] if "v=" in url else url
    youtube_url = f"https://www.youtube.com/watch?v={video_id}"
    
    unique_id = uuid.uuid4().hex[:8]
    output_template = f"temp_{video_id}_{unique_id}"
    
    ydl_opts = {
        'outtmpl': f'{output_template}.%(ext)s',
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True,
        'socket_timeout': 30,
        'retries': 3,
    }

    # 🍪 Pastebin မှ Cookies ဖိုင်ရှိပါက ထည့်သွင်းအသုံးပြုခြင်း
    if os.path.exists(COOKIE_FILE) and os.path.getsize(COOKIE_FILE) > 0:
        ydl_opts['cookiefile'] = COOKIE_FILE
        print("🍪 Cookies injected into yt-dlp options.")

    # 🔒 Proxy ကို ကျပန်းရွေးချယ်ပြီး ထည့်သွင်းခြင်း
    selected_proxy = get_random_proxy()
    if selected_proxy:
        ydl_opts['proxy'] = selected_proxy
        print(f"🔒 Using Proxy: {selected_proxy}")

    if type == "video":
        ydl_opts['format'] = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'
        ydl_opts['merge_output_format'] = 'mp4'
    else:
        ydl_opts['format'] = 'bestaudio/best'
        ydl_opts['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]

    def run_ytdlp():
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.extract_info(youtube_url, download=True)

    try:
        await asyncio.to_thread(run_ytdlp)
    except Exception as e:
        error_msg = str(e)
        if selected_proxy:
            error_msg += f" (Failed while using proxy: {selected_proxy})"
        raise HTTPException(status_code=500, detail=f"Download failed: {error_msg}")

    # File ရှာခြင်း
    downloaded_file = None
    for file in glob.glob(f"{output_template}.*"):
        downloaded_file = file
        break

    if not downloaded_file:
        raise HTTPException(status_code=404, detail="Error: File processing failed")

    # Background task ဖြင့် ဖျက်ရန်
    background_tasks.add_task(cleanup_file, downloaded_file)

    # File ကို Stream ပြန်လုပ်ပေးခြင်း
    return FileResponse(
        path=downloaded_file, 
        filename=os.path.basename(downloaded_file),
        media_type='application/octet-stream'
    )

# Cookies ကို Manual Update လုပ်ချင်ပါက ခေါ်သုံးရန် Endpoint အပိုတစ်ခု
@app.get("/refresh-cookies")
async def refresh_cookies(api_key: str = Query(None)):
    if API_KEY and api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")
    success = await fetch_pastebin_cookies()
    if success:
        return {"status": "success", "message": "Cookies refreshed successfully!"}
    raise HTTPException(status_code=500, detail="Failed to refresh cookies from Pastebin")

if __name__ == "__main__":
    import uvicorn
    # Render ကနေ ပေးမယ့် PORT ကို ယူပါမယ်၊ မရှိရင် 8000 ကို သုံးပါမယ်
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)

