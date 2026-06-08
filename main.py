from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
from fastapi.responses import FileResponse
import yt_dlp
import os
import asyncio

app = FastAPI(title="Velvet Aura Downloader API")

VALID_API_KEYS = {
    "VelvetAura2026SecureKey", 
    "PyaesoneSpecialKey123"
}

# Downloads ဖိုင်တွဲ တည်ဆောက်ထားခြင်း
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def delete_file(file_path: str):
    """Telegram Bot ဆီ ဖိုင်ပို့ပြီးတာနဲ့ Server ပေါ်ကနေ ပြန်ဖျက်မည့် Function (Storage မပြည့်အောင်)"""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"🗑️ Deleted temp file: {file_path}")
    except Exception as e:
        print(f"⚠️ Error deleting file: {e}")

@app.get("/")
def read_root():
    return {"message": "Velvet Aura Download Server is Running!"}

@app.get("/api/download")
async def download_media(
    background_tasks: BackgroundTasks,
    url: str = Query(..., description="YouTube URL to download"),
    api_key: str = Query(..., description="Your secret API key"),
    is_audio: bool = Query(True, description="True for audio, False for video")
):
    # ၁။ API Key စစ်ဆေးခြင်း
    if api_key not in VALID_API_KEYS:
        raise HTTPException(status_code=403, detail="Invalid API Key.")

    # ၂။ yt-dlp Settings
    ydl_opts = {
        'outtmpl': f'{DOWNLOAD_DIR}/%(id)s.%(ext)s', # ဖိုင်ကို downloads ဖိုင်တွဲထဲ ထည့်မည်
        'format': 'bestaudio[ext=m4a]/bestaudio/best' if is_audio else 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best',
        'quiet': True,
        'no_warnings': True,
        'noplaylist': True,
        'geo_bypass': True,
        'extractor_args': {'youtube': {'player_client': ['android', 'ios', 'web']}},
    }

    if os.path.exists("cookies.txt"):
        ydl_opts['cookiefile'] = "cookies.txt"

    # ၃။ API Server ပေါ်သို့ သီချင်းအရင် ဒေါင်းလုဒ်ဆွဲခြင်း
    try:
        def _download():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True) # download=True သုံးထားပါသည်
                return ydl.prepare_filename(info)
        
        # Blocking မဖြစ်အောင် Thread ဖြင့် run ခြင်း
        file_path = await asyncio.to_thread(_download)

        if not file_path or not os.path.exists(file_path):
            raise HTTPException(status_code=500, detail="Failed to download file to API server.")

        # ၄။ ရလာသော ဖိုင်ကို Bot ဆီသို့ ပို့ပေးခြင်း နှင့် ပို့ပြီးပါက ပြန်ဖျက်ရန် သတ်မှတ်ခြင်း
        background_tasks.add_task(delete_file, file_path)
        
        return FileResponse(
            path=file_path, 
            filename=os.path.basename(file_path),
            media_type="audio/mp4" if is_audio else "video/mp4"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
