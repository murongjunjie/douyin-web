# -*- coding: utf-8 -*-
"""
抖音视频下载器 - Web 版
提供网页界面，用户粘贴抖音链接即可下载视频
集成广告联盟广告位（Google AdSense 兼容）
"""

import os
import re
import uuid
import time
import threading
from flask import Flask, render_template, request, jsonify, send_from_directory, url_for
import yt_dlp

app = Flask(__name__)

# 下载目录
DOWNLOAD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "downloads")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# ============ 广告配置 ============
# 替换为你的 Google AdSense 发布商 ID
ADSENSE_CLIENT = "ca-pub-XXXXXXXXXXXXXXXX"
# 替换为你的广告位 ID
ADSENSE_SLOT = "XXXXXXXXXX"
# 是否启用广告（未配置 AdSense 前显示占位符）
AD_ENABLED = False

# ============ 清理旧文件 ============
def cleanup_old_files():
    """清理超过 1 小时的下载文件"""
    now = time.time()
    for f in os.listdir(DOWNLOAD_DIR):
        filepath = os.path.join(DOWNLOAD_DIR, f)
        if os.path.isfile(filepath) and now - os.path.getmtime(filepath) > 3600:
            try:
                os.remove(filepath)
            except Exception:
                pass

# 启动时清理一次
cleanup_old_files()
# 后台定时清理
def _cleanup_loop():
    while True:
        time.sleep(1800)
        cleanup_old_files()

threading.Thread(target=_cleanup_loop, daemon=True).start()


# ============ 路由 ============

@app.route("/")
def index():
    return render_template("index.html",
                           adsense_client=ADSENSE_CLIENT,
                           adsense_slot=ADSENSE_SLOT,
                           ad_enabled=AD_ENABLED)


@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


@app.route("/download", methods=["POST"])
def download_video():
    """API: 接收抖音链接，解析视频直链（不下载），返回给前端直接下载"""
    data = request.get_json(silent=True) or {}
    url = (data.get("url") or "").strip()

    if not url:
        return jsonify({"success": False, "error": "请输入抖音视频链接"}), 400

    # 从粘贴的文本中提取链接（支持抖音分享文本、纯链接等多种格式）
    url_match = re.search(r'https?://[^\s<>"]+', url)
    if url_match:
        url = url_match.group(0)
    elif re.match(r'^[\d.]+\s+\d+/\d+', url) or ' #' in url:
        # 看起来是抖音分享文本但没包含链接
        return jsonify({"success": False, "error": "检测到抖音分享文本，但未找到有效链接。请使用「复制链接」功能获取完整链接（格式如 https://v.douyin.com/xxx/）"}), 400
    else:
        return jsonify({"success": False, "error": "未识别到有效链接，请粘贴完整的抖音分享链接（支持 v.douyin.com / www.douyin.com / 抖音分享文本）"}), 400

    ydl_opts = {
        "format": "best",
        "no_playlist": True,
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,  # 只解析，不下载
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            title = info.get("title", "未命名")
            duration = info.get("duration", 0)
            # 获取视频直链
            video_url = info.get("url") or ""
            # 如果没有直接的 url，尝试从 formats 里找最佳格式
            if not video_url and "formats" in info:
                formats = info["formats"]
                # 优先选最高画质的 mp4
                best = next((f for f in formats if f.get("ext") == "mp4" and f.get("filesize")), formats[-1])
                video_url = best.get("url", "")

            if not video_url:
                return jsonify({"success": False, "error": "无法获取视频直链，可能视频需要登录或已删除"}), 400

            return jsonify({
                "success": True,
                "title": title,
                "duration": duration,
                "video_url": video_url,  # 前端直接用这个链接下载
                "mode": "direct",  # 告诉前端是直链模式
            })
    except yt_dlp.utils.DownloadError as e:
        err_msg = str(e)
        if "Unsupported URL" in err_msg or "generic" in str(e.__dict__):
            return jsonify({"success": False, "error": "⚠️ 该链接无法解析，可能原因：\n1. 分享链接已过期（超过24小时）\n2. 视频已被删除或设为私密\n3. 链接格式不正确\n\n请重新打开抖音，复制最新的「分享链接」再试"}), 400
        elif "HTTP Error" in err_msg or "403" in err_msg or "404" in err_msg:
            return jsonify({"success": False, "error": f"⚠️ 视频无法访问：{err_msg[:150]}\n可能视频已下架或需要登录才能查看"}), 400
        else:
            return jsonify({"success": False, "error": f"解析失败：{err_msg[:200]}"}), 500
    except Exception as e:
        return jsonify({"success": False, "error": f"服务器错误：{str(e)[:200]}"}), 500


@app.route("/file/<filename>")
def serve_file(filename):
    """提供已下载文件的下载"""
    return send_from_directory(DOWNLOAD_DIR, filename, as_attachment=True)


@app.route("/ads.txt")
def ads_txt():
    """广告联盟验证文件 - 替换为你的 AdSense 发布商 ID"""
    return "google.com, pub-XXXXXXXXXXXXXXXX, DIRECT, f08c47fec0942fa0", 200, {"Content-Type": "text/plain"}


@app.route("/robots.txt")
def robots_txt():
    content = "User-agent: *\nAllow: /\nDisallow: /downloads/\n\nSitemap: /sitemap.xml"
    return content, 200, {"Content-Type": "text/plain"}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
