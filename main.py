from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request
import yt_dlp
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create the FastAPI instance
app = FastAPI()

# Mount the static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Specify the download directory
download_dir = "downloads"
os.makedirs(download_dir, exist_ok=True)

@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/download")
async def download_video(video_url: str = Form(...)):
    try:
        logger.info(f"Received URL: {video_url}")

        # Setting up options for yt-dlp
        ydl_opts = {
            'outtmpl': f'{download_dir}/%(title)s.%(ext)s',
            'format': 'best',
            'socket_timeout': 30,  # Increase timeout
            'verbose': True,  # Enable verbose logging
        }

        # Downloading the video
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=True)
            video_title = info_dict.get('title', None)
            video_file = f"{download_dir}/{video_title}.mp4"

        logger.info(f"Downloaded video to: {video_file}")
        return {"message": "Video downloaded successfully!", "file_path": video_file}

    except Exception as e:
        logger.error(f"Error occurred during video download: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
