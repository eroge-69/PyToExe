from flask import Flask
import pyperclip
import json

# 获取用户输入并读取对应文件
while True:
    try:
        choice = int(input("请选择要读取的名单文件编号（1-9）："))
        if 1 <= choice <= 9:
            filename = f'name{choice}.txt'
            break
        else:
            print("请输入1-9之间的数字！")
    except ValueError:
        print("请输入有效的数字！")

try:
    with open(filename, 'r', encoding="utf-8") as f:
        name = [i.replace('\n','') for i in f]
except:
    try:
        with open(filename, 'r', encoding="gbk") as f:
            name = [i.replace('\n','') for i in f]
    except FileNotFoundError:
        print(f"错误：找不到文件 {filename}")
        exit()

app = Flask(__name__)
@app.route('/')
def main():
    
    info = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>点名器</title>
<style>
/* 页面整体背景色 */
body {
    background: linear-gradient(135deg, #667eea 0%%, #764ba2 100%%);
    margin: 0;
    padding: 0;
    font-family: 'Microsoft YaHei', Arial, sans-serif;
    min-height: 100vh;
}

/* 主要显示区域样式 */
#Uname {
    margin: 0 auto;
    margin-top: 100px;
    font-size: 280px;
    font-weight: 800;
    text-align: center;
    line-height: 1.2;
    color: #fff;
    text-shadow: 4px 4px 8px rgba(0,0,0,0.3);
    padding: 20px;
    border-radius: 20px;
    background: rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(10px);
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
    width: 90%%;
    max-width: 1200px;
}

/* 按钮容器 */
.btn {
    width: 200px;
    height: 200px;
    margin: 0 auto;
    margin-top: 80px;
    text-align: center;
}

/* 按钮样式 */
.btn button {
    width: 150px;
    height: 150px;
    border-radius: 50%%;
    font-size: 28px;
    font-weight: bold;
    background: linear-gradient(45deg, #ff6b6b, #ffa502);
    color: white;
    border: none;
    cursor: pointer;
    box-shadow: 0 6px 20px rgba(0,0,0,0.2);
    transition: all 0.3s ease;
}

/* 按钮悬停效果 */
.btn button:hover {
    transform: scale(1.05);
    box-shadow: 0 8px 25px rgba(0,0,0,0.3);
}

/* 按钮按下效果 */
.btn button:active {
    transform: scale(0.95);
}

/* 响应式设计 */
@media (max-width: 768px) {
    #Uname {
        font-size: 180px;
        margin-top: 50px;
        padding: 15px;
    }
    
    .btn {
        margin-top: 60px;
    }
    
    .btn button {
        width: 120px;
        height: 120px;
        font-size: 22px;
    }
}

@media (max-width: 480px) {
    #Uname {
        font-size: 120px;
    }
    
    .btn button {
        width: 100px;
        height: 100px;
        font-size: 18px;
    }
}
</style>
</head>
<body>
<div id="Uname">认真听讲</div>
<div class="btn">
<button onclick="demo()" id="bt">开始</button>
</div>
<script>
var Uname=document.getElementById('Uname');
var arr=%s
var btn=document.getElementById('bt');
var clock=0;
var st=true;

function demo(){
    if(st){
        start();
        btn.innerHTML="结束";
        st=false;
    }else{
        stop();
        btn.innerHTML="开始";
        st=true;
    }
}

function start(){
    clock=setInterval(function(){
        var inde=Math.floor(Math.random()*arr.length);
        Uname.innerHTML=arr[inde];
    }, 50)
}

function stop(){
    clearInterval(clock);
}
</script>
</body>
</html>""" % (json.dumps(name, ensure_ascii=False))
    return info

pyperclip.copy('http://127.0.0.1:5000/')
app.run()
