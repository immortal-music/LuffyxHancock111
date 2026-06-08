from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
from fastapi.responses import FileResponse
import yt_dlp
import os
import asyncio
import uvicorn # ထပ်ထည့်ထားသည်

app = FastAPI(title="Velvet Aura Downloader API")

VALID_API_KEYS = {
    "VelvetAura2026SecureKey", 
    "PyaesoneSpecialKey123"
}

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def delete_file(file_path: str):
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
    if api_key not in VALID_API_KEYS:
        raise HTTPException(status_code=403, detail="Invalid API Key.")

    ydl_opts = {
        'outtmpl': f'{DOWNLOAD_DIR}/%(id)s.%(ext)s',
        'format': 'bestaudio[ext=m4a]/bestaudio/best' if is_audio else 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best',
        'quiet': False,
        'username': 'oauth2',
        'no_warnings': True,
        'noplaylist': True,
        'geo_bypass': True,
        'extractor_args': {'youtube': {'player_client': ['android', 'ios', 'web']}},
    }

    if os.path.exists("cookies.txt"):
        ydl_opts['cookiefile'] = "cookies.txt"

    try:
        def _download():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                return ydl.prepare_filename(info)
        
        file_path = await asyncio.to_thread(_download)

        if not file_path or not os.path.exists(file_path):
            raise HTTPException(status_code=500, detail="Failed to download file to API server.")

        background_tasks.add_task(delete_file, file_path)
        
        return FileResponse(
            path=file_path, 
            filename=os.path.basename(file_path),
            media_type="audio/mp4" if is_audio else "video/mp4"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Server ကို အမြဲတမ်း အသက်သွင်းထားမည့် အပိုင်း
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
