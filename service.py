from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp
import os

app = Flask(__name__)
CORS(app)

# Read provider URL from environment (set via docker-compose)
BGUTIL_BASEURL = os.getenv("GETPOT_BGUTIL_BASEURL", "http://localhost:4416")


@app.route("/metadata", methods=["GET"])
def get_metadata():
    url = request.args.get("url")
    if not url:
        return jsonify({"error": "URL query parameter is required"}), 400

    # enable get-pot plugin
    ydl_opts = {
        "skip_download": True,
        "quiet": True,
        "get_pot": True,  # ← turn on the yt-dlp-get-pot plugin
        "format": (
            "protocol=hls_native/"
            "bestvideo[ext=mp4][vcodec^=avc1]+bestaudio[ext=m4a]/"
            "best[ext=mp4]"
        ),
        "extractor_args": {
            "youtube": {
                # emulate web client
                "player_client": "mweb",
                # point at our BgUtil POT HTTP server
                "getpot_bgutil_baseurl": BGUTIL_BASEURL,
            }
        },
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return jsonify(info)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    app.run(host="0.0.0.0", port=port)
