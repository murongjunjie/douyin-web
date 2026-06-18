// ===== 抖音视频下载器 - 前端逻辑 =====

/**
 * 从粘贴文本中提取抖音链接
 * 支持格式：
 *   - https://v.douyin.com/xxxxx/
 *   - https://www.douyin.com/video/xxxxx
 *   - 包含链接的整段分享文本
 */
function extractDouyinUrl(text) {
    // 匹配抖音短链接和长链接
    const patterns = [
        /https?:\/\/v\.douyin\.com\/[A-Za-z0-9]+\/?/i,
        /https?:\/\/(www\.)?douyin\.com\/video\/[0-9]+/i,
        /https?:\/\/(www\.)?douyin\.com\/user\/[A-Za-z0-9_-]+/i,
        /https?:\/\/www\.douyin\.com\/[^\s"']+/i,
    ];
    for (const pattern of patterns) {
        const match = text.match(pattern);
        if (match) return match[0];
    }
    return null;
}

function startDownload() {
    const urlInput = document.getElementById('video-url');
    const btn = document.getElementById('download-btn');
    const btnText = btn.querySelector('.btn-text');
    const btnLoading = btn.querySelector('.btn-loading');
    const errorMsg = document.getElementById('error-msg');
    const resultSection = document.getElementById('result-section');

    let url = urlInput.value.trim();

    // 隐藏之前的错误和结果
    errorMsg.style.display = 'none';
    resultSection.style.display = 'none';

    if (!url) {
        showError('请粘贴抖音分享链接或包含链接的分享文本');
        return;
    }

    // 自动从分享文本中提取链接
    const extracted = extractDouyinUrl(url);
    if (!extracted) {
        showError('未识别到抖音链接，请确保粘贴内容包含 https://v.douyin.com/... 或 https://www.douyin.com/...');
        return;
    }
    // 如果提取成功，自动更新输入框为纯链接
    if (extracted !== url) {
        urlInput.value = extracted;
        url = extracted;
    }

    // 按钮加载状态
    btn.disabled = true;
    btnText.style.display = 'none';
    btnLoading.style.display = 'inline';

    // 发起下载请求（Vercel Serverless API）
    fetch('/api/download', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: url })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showResult(data);
        } else {
            showError(data.error || '下载失败，请重试');
        }
    })
    .catch(err => {
        showError('网络错误，请检查链接后重试');
    })
    .finally(() => {
        btn.disabled = false;
        btnText.style.display = 'inline';
        btnLoading.style.display = 'none';
    });
}

function showError(msg) {
    const errorMsg = document.getElementById('error-msg');
    errorMsg.textContent = msg;
    errorMsg.style.display = 'block';
}

function showResult(data) {
    const section = document.getElementById('result-section');
    document.getElementById('result-title').textContent = data.title || '未命名';
    document.getElementById('result-duration').textContent = formatDuration(data.duration);

    const downloadLink = document.getElementById('download-link');

    if (data.mode === 'direct' && data.video_url) {
        // 直链模式：浏览器直接下载，不通过服务器
        document.getElementById('result-size').textContent = '获取中...';
        // 获取文件大小（异步）
        fetch(data.video_url, { method: 'HEAD' })
            .then(r => {
                const size = r.headers.get('content-length');
                document.getElementById('result-size').textContent = size ? formatSize(parseInt(size)) : '未知';
            })
            .catch(() => {
                document.getElementById('result-size').textContent = '未知';
            });
        // 设置直链下载
        downloadLink.href = data.video_url;
        downloadLink.download = (data.title || 'video') + '.mp4';
        downloadLink.target = '_blank';
        downloadLink.rel = 'noopener';
    } else {
        // 服务器下载模式（原逻辑）
        document.getElementById('result-size').textContent = formatSize(data.filesize);
        downloadLink.href = data.download_url;
        downloadLink.removeAttribute('download');
        downloadLink.removeAttribute('target');
        downloadLink.removeAttribute('rel');
    }

    section.style.display = 'block';
    section.scrollIntoView({ behavior: 'smooth', block: 'center' });
}

function formatSize(bytes) {
    if (!bytes || bytes === 0) return '未知';
    const mb = bytes / (1024 * 1024);
    if (mb < 1) return (bytes / 1024).toFixed(1) + ' KB';
    return mb.toFixed(2) + ' MB';
}

function formatDuration(seconds) {
    if (!seconds) return '未知';
    const min = Math.floor(seconds / 60);
    const sec = seconds % 60;
    return min + '分' + sec + '秒';
}

// 回车键触发下载
document.getElementById('video-url').addEventListener('keydown', function(e) {
    if (e.key === 'Enter') {
        startDownload();
    }
});

// 粘贴自动提取链接
document.getElementById('video-url').addEventListener('paste', function(e) {
    // 等粘贴完成后再提取
    setTimeout(() => {
        const val = this.value;
        const extracted = extractDouyinUrl(val);
        if (extracted && extracted !== val) {
            this.value = extracted;
        }
    }, 50);
});
