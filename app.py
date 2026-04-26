from flask import Flask, request, jsonify
import yt_dlp
import os

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({
        "status": "online",
        "message": "YouTube Downloader API is running. Use /api/yt-dl?url=...&quality=..."
    })

@app.route('/api/yt-dl', methods=['GET'])
def get_video_info():
    video_url = request.args.get('url')
    quality = request.args.get('quality')

    if not video_url:
        return jsonify({
            "status": "error", 
            "message": "Parameter 'url' wajib diisi!"
        }), 400

    # Memetakan kualitas ke format yt-dlp
    # Kita prioritaskan mp4 agar mudah diputar/didownload
    formats = {
        '144': 'bestvideo[height<=144][ext=mp4]+bestaudio[ext=m4a]/best[height<=144][ext=mp4]/best',
        '360': 'bestvideo[height<=360][ext=mp4]+bestaudio[ext=m4a]/best[height<=360][ext=mp4]/best',
        '480': 'bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/best[height<=480][ext=mp4]/best',
        '720': 'bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720][ext=mp4]/best',
        '1080': 'bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080][ext=mp4]/best'
    }

    selected_format = formats.get(quality, 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best')

    ydl_opts = {
        'format': selected_format,
        'quiet': True,
        'no_warnings': True,
        'skip_download': True,
        'nocheckcertificate': True,
        'headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            
            # Mengambil URL direct download
            # yt-dlp terkadang menaruhnya di 'url' atau di 'requested_formats'
            download_url = info.get('url')
            if not download_url and 'requested_formats' in info:
                # Mengambil format video terbaik yang digabung
                download_url = info['requested_formats'][0].get('url')

            return jsonify({
                "status": "success",
                "title": info.get('title'),
                "thumbnail": info.get('thumbnail'),
                "duration": info.get('duration'),
                "quality_requested": quality if quality else "best",
                "download_url": download_url
            })
            
    except Exception as e:
        return jsonify({
            "status": "error", 
            "message": str(e)
        }), 500

if __name__ == '__main__':
    # Gunakan port dari environment variable untuk Render
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
