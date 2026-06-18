# 抖音视频下载器 - 部署到 PythonAnywhere

## 步骤一：创建 Web 应用

1. 在 PythonAnywhere Dashboard，点击右侧 **「Open web tab 打开网络应用后」**
2. 点击 **「Add a new web app」**
3. 选择 **「Flask」** 框架
4. Python 版本选 **「Python 3.11」**（或你有的最新版）
5. 项目名称输入：**`douyin-web`**

## 步骤二：上传代码

### 方式 A：通过 Bash 上传（推荐）

1. 点顶部菜单 **Consoles → Bash**
2. 依次执行：

```bash
cd ~

# 如果你有 GitHub 仓库，直接 clone：
git clone <你的仓库地址> douyin-web

# 或者用我们提供的打包方式（看下方）
```

### 方式 B：手动上传文件

1. 点顶部菜单 **Files**
2. 进入 `/home/lian68/`
3. 创建文件夹 `douyin-web`
4. 上传以下文件：
   - `app.py`
   - `wsgi.py`
   - `requirements.txt`
   - 整个 `templates/` 文件夹
   - 整个 `static/` 文件夹

## 步骤三：安装依赖

1. 点顶部菜单 **Consoles → Bash**（或打开已有的 Bash）
2. 执行：

```bash
pip3 install --user -r ~/douyin-web/requirements.txt
```

## 步骤四：配置 Web 应用

1. 点击顶部菜单 **Web**
2. 找到你的 Web 应用，点击 **Configuration / 配置**
3. **Source code / 源代码**：改为 `/home/lian68/douyin-web/wsgi.py`
4. **Working directory / 工作目录**：改为 `/home/lian68/douyin-web`
5. **WSGI configuration file / WSGI 配置文件**：改为 `/home/lian68/douyin-web/wsgi.py`
6. 向下滚动找到 **Virtualenv / 虚拟环境**，如果需要创建一个：
   - 点 **Add new virtualenv / 新建虚拟环境**
   - 路径填：`/home/lian68/.virtualenvs/douyin-web-env`
   - Python 选 **3.11**
7. 确认后点底部 **Save / 保存**

## 步骤五：在虚拟环境中装依赖

```bash
source ~/.virtualenvs/douyin-web-env/bin/activate
pip install Flask yt-dlp
deactivate
```

## 步骤六：重启服务

回到 **Web** 页面，点击绿色的 **Reload / 重载** 按钮。

等待几秒后，你的网站就上线了！
访问地址通常是：`https://lian68.pythonanywhere.com/`

## 常见问题

**Q: 提示 "Internal Server Error"？**
A: 去 **Web** 页面查看 **Error log / 错误日志**，把报错信息发给我

**Q: 视频下载很慢？**
A: 免费版 PythonAnywhere 的网络带宽有限，这是正常的。视频文件较大时可能需要等一会儿

**Q: 如何更新代码？**
A: 上传新文件覆盖旧文件后，回 **Web** 页面点 **Reload / 重载**
