 <h2>环境监测</h2>
            <div>
  <p>温度: <span id="temperature">--</span>°C</p >
                <p>湿度: <span id="humidity">--</span>%</p >
            </div>
            <canvas id="envChart" width="400" height="200"></canvas>
        </div>
        
        <div class="card">
            <h2>灯光控制</h2>
            <p>状态: <span id="lightStatus">关闭</span></p >
            <div class="controls">
                <button onclick="controlDevice('light', {status: true})">开启</button>
                <button onclick="controlDevice('light', {status: false})">关闭</button>
            </div>
            <p>亮度: <span id="lightBrightness">0</span>%</p >
            <input type="range" id="brightnessSlider" min="0" max="100" 
                   onchange="controlDevice('light', {brightness: this.value})">
        </div>
        
        <div class="card">
