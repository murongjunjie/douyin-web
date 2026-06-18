"""
Vercel Serverless Function - 抖音视频解析API
路径: /api/download
"""

import json
import re
import yt_dlp


def handler(request):
    """Vercel Serverless 入口函数"""

    # 只接受 POST 请求
    if request.method != "POST":
        return {
            "statusCode": 405,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"success": False, "error": "请使用 POST 请求"})
        }

    try:
        # 解析请求体
        body = request.body.decode("utf-8") if request.body else "{}"
        data = json.loads(body) if body else {}
        url = (data.get("url") or "").strip()

        if not url:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"success": False, "error": "请输入抖音视频链接"})
            }

        # 从粘贴文本中提取链接
        url_match = re.search(r'https?://[^\s<>"]+', url)
        if url_match:
            url = url_match.group(0)
        elif re.match(r'^[\d.]+\s+\d+/\d+', url) or ' #' in url:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"success": False, "error": "检测到抖音分享文本，但未找到有效链接。请使用「复制链接」功能获取完整链接（格式如 https://v.douyin.com/xxx/）"})
            }
        else:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"success": False, "error": "未识别到有效链接，请粘贴完整的抖音分享链接"})
            }

        # yt-dlp 解析视频信息
        ydl_opts = {
            "format": "best",
            "no_playlist": True,
            "quiet": True,
            "no_warnings": True,
            "skip_download": True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            title = info.get("title", "未命名")
            duration = info.get("duration", 0)

            # 获取视频直链
            video_url = info.get("url") or ""
            if not video_url and "formats" in info:
                formats = info["formats"]
                best = next((f for f in formats if f.get("ext") == "mp4"), formats[-1])
                video_url = best.get("url", "")

            if not video_url:
                return {
                    "statusCode": 400,
                    "headers": {"Content-Type": "application/json"},
                    "body": json.dumps({"success": False, "error": "无法获取视频直链，可能视频需要登录或已删除"})
                }

            return {
                "statusCode": 200,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({
                    "success": True,
                    "title": title,
                    "duration": duration,
                    "video_url": video_url,
                    "mode": "direct"
                })
            }

    except Exception as e:
        err_msg = str(e)
        if "Unsupported URL" in err_msg or "generic" in err_msg.lower():
            error_text = "该链接无法解析，可能原因：\n1. 分享链接已过期\n2. 视频已被删除或设为私密\n3. 链接格式不正确"
        elif "HTTP Error" in err_msg or "403" in err_msg or "404" in err_msg:
            error_text = f"视频无法访问：{err_msg[:150]}"
        else:
            error_text = f"解析失败：{err_msg[:200]}"

        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"success": False, "error": error_text})
        }


# Vercel 兼容：同时支持 ASGI 和 WSGI 调用方式
class Request:
    """模拟 Vercel 的 request 对象"""
    def __init__(self, method="GET", body=None):
        self.method = method
        self.body = body


# 如果直接运行此文件用于测试
if __name__ == "__main__":
    import sys

    test_request = Request(method="POST", body=json.dumps({"url": sys.argv[1] if len(sys.argv) > 1 else ""}).encode())
    result = handler(test_request)
    print(result["body"])
