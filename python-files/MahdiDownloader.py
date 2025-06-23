import webview
import os
import json
import yt_dlp

HTML_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Mahdi Video Downloader</title>
  <style>
    body {
      background: linear-gradient(135deg, #d0e7ff, #f0f9ff);
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      display: flex;
      align-items: center;
      justify-content: center;
      height: 100vh;
      margin: 0;
    }
    .container {
      background: white;
      border-radius: 16px;
      box-shadow: 0 12px 24px rgba(0, 0, 0, 0.15);
      padding: 40px;
      width: 90%;
      max-width: 600px;
      box-sizing: border-box;
    }
    .title {
      font-size: 28px;
      font-weight: 800;
      text-align: center;
      color: #0077cc;
      margin-bottom: 24px;
      display: flex;
      justify-content: center;
      align-items: center;
      gap: 10px;
    }
    .title img {
      width: 32px;
      height: 32px;
    }
    label {
      font-weight: 600;
      margin-bottom: 8px;
      display: block;
    }
    input[type="text"], select {
      width: 100%;
      padding: 10px;
      font-size: 16px;
      border-radius: 8px;
      border: 1px solid #ccc;
      box-sizing: border-box;
      margin-bottom: 16px;
    }
    button {
      padding: 10px 16px;
      font-size: 16px;
      background-color: #0077ff;
      color: white;
      border: none;
      border-radius: 8px;
      cursor: pointer;
      transition: background-color 0.3s ease;
      margin: 5px;
    }
    button:hover {
      background-color: #005dd1;
    }
    .progress-container {
      margin-top: 20px;
      background: #e0e0e0;
      border-radius: 10px;
      overflow: hidden;
    }
    .progress-bar {
      height: 20px;
      width: 0%;
      background-color: #28a745;
      text-align: center;
      color: white;
      line-height: 20px;
      transition: width 0.4s ease;
    }
    .button-group {
      display: flex;
      justify-content: space-between;
      margin-top: 10px;
    }
    .download-list {
      margin-top: 30px;
      background: #fafafa;
      border-radius: 8px;
      padding: 10px;
      max-height: 180px;
      overflow-y: auto;
      font-size: 14px;
    }
    .download-list-item {
      border-bottom: 1px solid #ddd;
      padding: 8px 0;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    .download-status {
      font-weight: bold;
    }
    .meta-info {
      font-size: 12px;
      color: gray;
    }
  </style>
</head>
<body>
  <div class="container">
    <div class="title">
      <img src="https://via.placeholder.com/32?text=M" alt="Logo" />
      <span>Mahdi Video Downloader</span>
    </div>
    <form onsubmit="startDownload(event)">
      <label for="video-url">URL:</label>
      <input type="text" id="video-url" placeholder="Paste your video link here" />
      <label for="file-type">File type:</label>
      <select id="file-type">
        <option value="mp4">MP4</option>
        <option value="mkv">MKV</option>
        <option value="webm">WEBM</option>
        <option value="avi">AVI</option>
      </select>
      <label for="resolution">Resolution:</label>
      <select id="resolution">
        <option value="2160">4K</option>
        <option value="1440">1440p</option>
        <option value="1080">1080p</option>
        <option value="720">720p</option>
        <option value="480">480p</option>
        <option value="360">360p</option>
        <option value="240">240p</option>
      </select>
      <button type="submit">Download</button>
    </form>
    <div class="progress-container">
      <div class="progress-bar" id="progress-bar">0%</div>
    </div>
    <div class="button-group">
      <button onclick="cancelDownload()">Cancel</button>
      <button onclick="retryDownload()">Retry</button>
    </div>
    <div class="download-list" id="download-list">
      <strong>Download List:</strong>
    </div>
  </div>
  <script>
    function startDownload(event) {
      event.preventDefault();
      const url = document.getElementById('video-url').value;
      const filetype = document.getElementById('file-type').value;
      const resolution = document.getElementById('resolution').value;
      const bar = document.getElementById('progress-bar');
      const list = document.getElementById('download-list');

      bar.style.width = '10%';
      bar.innerText = 'Starting...';

      window.pywebview.api.download_video(url, filetype, resolution).then(result => {
        const res = JSON.parse(result);
        const item = document.createElement('div');
        item.className = 'download-list-item';

        if (res.status === 'completed') {
          alert('✅ Download Completed');
          item.innerHTML = '<span class="download-status">✅ Completed</span><div class="meta-info">' + url + '</div>';
          bar.style.width = '100%';
          bar.innerText = '100%';
        } else {
          alert('❌ Download Failed');
          item.innerHTML = '<span class="download-status">❌ Failed</span><div class="meta-info">' + url + '</div>';
          bar.style.width = '0%';
          bar.innerText = 'Failed';
        }

        list.appendChild(item);
      });
    }

    function cancelDownload() {
      alert('Cancel not implemented yet.');
    }

    function retryDownload() {
      startDownload(new Event('submit'));
    }
  </script>
</body>
</html>
"""

class Api:
    def download_video(self, url, filetype, resolution):
        try:
            os.makedirs('downloads', exist_ok=True)
            outtmpl = os.path.join('downloads', '%(title)s.%(ext)s')
            ydl_opts = {
                'outtmpl': outtmpl,
                'format': f'bestvideo[height<={resolution}]+bestaudio/best',
                'merge_output_format': filetype,
                'quiet': True,
                'noplaylist': False,
                'postprocessors': [{
                    'key': 'FFmpegVideoConvertor',
                    'preferedformat': filetype,
                }]
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            return json.dumps({'status': 'completed'})
        except Exception as e:
            return json.dumps({'status': 'failed', 'error': str(e)})

if __name__ == '__main__':
    api = Api()
    webview.create_window("Mahdi Video Downloader", html=HTML_CONTENT, js_api=api, width=720, height=800)
    webview.start()
