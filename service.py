import os, yt_dlp
from flask import Flask, request, jsonify
from yt_dlp.utils import DownloadError, ExtractorError

app = Flask(__name__)

# Re-usable yt-dlp options
YDL_OPTS = {
    "quiet": True,
    "skip_download": True,
    "socket_timeout": 15,
}


def _simplify_formats(formats):
    simplified = []
    for f in formats or []:
        simplified.append(
            {
                "format_id": f.get("format_id"),
                "ext": f.get("ext"),
                "protocol": f.get("protocol"),
                "vcodec": f.get("vcodec"),
                "acodec": f.get("acodec"),
                "tbr": f.get("tbr"),
                "fps": f.get("fps"),
                "width": f.get("width"),
                "height": f.get("height"),
                "url": f.get("url"),
                "manifest_url": f.get("manifest_url"),
            }
        )
    return simplified


def _best_thumbnail(info):
    thumbs = info.get("thumbnails") or []
    if not thumbs:
        return info.get("thumbnail")
    best = max(thumbs, key=lambda t: (t.get("height") or 0, t.get("width") or 0))
    return best.get("url")


@app.route("/metadata")
def metadata():
    url = request.args.get("url")
    if not url:
        return jsonify({"error": "URL parameter missing"}), 400
    raw = request.args.get("raw", "false").lower() in ("1", "true", "yes")

    # copy base opts per-request to avoid accidental mutation
    ydl_opts = dict(YDL_OPTS)
    ydl_opts.setdefault("noplaylist", True)

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
    except (DownloadError, ExtractorError) as e:
        return jsonify({"error": "Failed to extract metadata", "details": str(e)}), 502
    except Exception as e:
        return jsonify({"error": "Unexpected server error", "details": str(e)}), 500

    if raw:
        return jsonify(info)

    # simplified, stable-ish shape
    if info.get("entries") is not None:
        entries = []
        for entry in info.get("entries") or []:
            if not entry:
                continue
            entries.append(
                {
                    "id": entry.get("id"),
                    "title": entry.get("title"),
                    "uploader": entry.get("uploader") or entry.get("channel"),
                    "duration": entry.get("duration"),
                    "webpage_url": entry.get("webpage_url"),
                }
            )
        payload = {
            "type": info.get("_type") or "playlist",
            "id": info.get("id"),
            "title": info.get("title"),
            "webpage_url": info.get("webpage_url"),
            "entries": entries,
        }
        return jsonify(payload)

    payload = {
        "type": info.get("_type") or "video",
        "id": info.get("id"),
        "title": info.get("title"),
        "uploader": info.get("uploader") or info.get("channel"),
        "channel": info.get("channel"),
        "duration": info.get("duration"),
        "upload_date": info.get("upload_date"),
        "webpage_url": info.get("webpage_url"),
        "thumbnail": _best_thumbnail(info),
        "live_status": info.get("live_status"),
        "view_count": info.get("view_count"),
        "like_count": info.get("like_count"),
        "formats": _simplify_formats(info.get("formats")),
    }
    return jsonify(payload)


@app.route("/")
def health():
    return jsonify({"ok": True})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")))
