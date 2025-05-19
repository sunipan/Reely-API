import os, yt_dlp
from flask import Flask, request, jsonify

app = Flask(__name__)

POT_BASE = os.environ.get("POT_BASE", "http://pot-provider.railway.internal:4416")

# Re-usable yt-dlp options
YDL_OPTS = {
    "quiet": True,
    "skip_download": True,
    # tell yt-dlp where to fetch PO-Tokens
    "extractor_args": {
        "youtube": [f"getpot_bgutil_baseurl={POT_BASE}"],
    },
}


@app.route("/metadata")
def metadata():
    url = request.args.get("url")
    if not url:
        return jsonify({"error": "URL parameter missing"}), 400
    with yt_dlp.YoutubeDL(YDL_OPTS) as ydl:
        info = ydl.extract_info(url, download=False)
    # strip heavy fields to keep payload small
    wanted = {
        k: info[k]
        for k in ("id", "title", "uploader", "duration", "webpage_url", "formats")
    }
    return jsonify(wanted)
