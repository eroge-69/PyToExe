from flask import Flask, request, render_template_string
from pytube import YouTube

app = Flask(__name__)

HTML = '''
<!doctype html>
<title>YouTube Downloader</title>
<h2>YouTube Video Downloader</h2>
<form method=post>
  <input type=text name=url placeholder="Enter YouTube URL" style="width:300px">
  <input type=submit value=Download>
</form>
<p>{{ message }}</p>
'''

@app.route('/', methods=['GET', 'POST'])
def index():
    message = ''
    if request.method == 'POST':
        url = request.form['url']
        try:
            yt = YouTube(url)
            stream = yt.streams.get_highest_resolution()
            stream.download()
            message = f"Downloaded: {yt.title}"
        except Exception as e:
            message = f"Error: {str(e)}"
    return render_template_string(HTML, message=message)

if __name__ == '__main__':
    app.run(debug=True)
