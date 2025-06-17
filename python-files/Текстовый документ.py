To convert the provided HTML code into Python, we need to consider that HTML is primarily for web development, while Python is a general-purpose programming language. However, we can create a Python script that simulates the functionality described in the HTML using a web framework like Flask to serve the HTML content and handle the interactions.

Here's a Python script using Flask to create a similar web application:

```python
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Initial data
data = {
    "day": 1,
    "money": 10000,
    "tech_level": 1,
    "components": {
        "phone-cpu": {"price": 100, "count": 0},
        "phone-screen": {"price": 80, "count": 0},
        "phone-battery": {"price": 60, "count": 0},
        "phone-case": {"price": 40, "count": 0},
        "phone-camera": {"price": 90, "count": 0},
    }
}

@app.route('/')
def index():
    return render_template('index.html', data=data)

@app.route('/produce_component', methods=['POST'])
def produce_component():
    component_id = request.json['component_id']
    price = data['components'][component_id]['price']

    if data['money'] >= price:
        data['components'][component_id]['count'] += 1
        data['money'] -= price
        return jsonify({"success": True, "data": data})
    else:
        return jsonify({"success": False, "message": "Not enough money"})

@app.route('/next_day', methods=['POST'])
def next_day():
    data['day'] += 1
    return jsonify({"success": True, "data": data})

if __name__ == '__main__':
    app.run(debug=True)
```

### HTML Template (`templates/index.html`)

```html
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Электронная фабрика</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .game-container {
            background-color: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }
        .status-bar {
            display: flex;
            justify-content: space-between;
            margin-bottom: 20px;
            padding: 10px;
            background-color: #e9e9e9;
            border-radius: 5px;
        }
        .tab {
            overflow: hidden;
            border: 1px solid #ccc;
            background-color: #f1f1f1;
            border-radius: 5px 5px 0 0;
        }
        .tab button {
            background-color: inherit;
            float: left;
            border: none;
            outline: none;
            cursor: pointer;
            padding: 10px 16px;
            transition: 0.3s;
        }
        .tab button:hover {
            background-color: #ddd;
        }
        .tab button.active {
            background-color: #4CAF50;
            color: white;
        }
        .tabcontent {
            display: none;
            padding: 15px;
            border: 1px solid #ccc;
            border-top: none;
            border-radius: 0 0 5px 5px;
            background-color: white;
        }
        .component, .product {
            border: 1px solid #ddd;
            padding: 10px;
            margin: 5px 0;
            border-radius: 5px;
            background-color: #f9f9f9;
        }
        button {
            background-color: #4CAF50;
            border: none;
            color: white;
            padding: 8px 12px;
            text-align: center;
            text-decoration: none;
            display: inline-block;
            font-size: 14px;
            margin: 4px 2px;
            cursor: pointer;
            border-radius: 5px;
        }
        button:disabled {
            background-color: #cccccc;
            cursor: not-allowed;
        }
        .log {
            height: 150px;
            overflow-y: scroll;
            border: 1px solid #ddd;
            padding: 10px;
            margin-top: 20px;
            background-color: #f9f9f9;
            border-radius: 5px;
        }
    </style>
</head>
<body>
    <div class="game-container">
        <h1>Электронная фабрика</h1>

        <div class="status-bar">
            <div>День: <span id="day">{{ data['day'] }}</span></div>
            <div>Баланс: $<span id="money">{{ data['money'] }}</span></div>
            <div>Уровень технологии: <span id="tech-level">{{ data['tech_level'] }}</span></div>
        </div>

        <div class="tab">
            <button class="tablinks active" onclick="openTab(event, 'components')">Компоненты</button>
            <button class="tablinks" onclick="openTab(event, 'production')">Производство</button>
            <button class="tablinks" onclick="openTab(event, 'sales')">Продажи</button>
            <button class="tablinks" onclick="openTab(event, 'research')">Исследования</button>
            <button class="tablinks" onclick="nextDay()">Следующий день</button>
        </div>

        <div id="components" class="tabcontent" style="display: block;">
            <h2>Производство компонентов</h2>
            <div class="phone-components">
                <h3>Для телефонов</h3>
                <div class="component">
                    <span>Процессор ($100)</span>
                    <button onclick="produceComponent('phone-cpu', 100)">Произвести</button>
                    <span id="phone-cpu-count">{{ data['components']['phone-cpu']['count'] }}</span> шт.
                </div>
                <div class="component">
                    <span>Экран ($80)</span>
                    <button onclick="produceComponent('phone-screen', 80)">Произвести</button>
                    <span id="phone-screen-count">{{ data['components']['phone-screen']['count'] }}</span> шт.
                </div>
                <div class="component">
                    <span>Аккумулятор ($60)</span>
                    <button onclick="produceComponent('phone-battery', 60)">Произвести</button>
                    <span id="phone-battery-count">{{ data['components']['phone-battery']['count'] }}</span> шт.
                </div>
                <div class="component">
                    <span>Корпус ($40)</span>
                    <button onclick="produceComponent('phone-case', 40)">Произвести</button>
                    <span id="phone-case-count">{{ data['components']['phone-case']['count'] }}</span> шт.
                </div>
                <div class="component">
                    <span>Камера ($90)</span>
                    <button onclick="produceComponent('phone-camera', 90)">Произвести</button>
                    <span id="phone-camera-count">{{ data['components']['phone-camera']['count'] }}</span> шт.
                </div>
            </div>
        </div>
    </div>

    <script>
        function openTab(evt, tabName) {
            var i, tabcontent, tablinks;
            tabcontent = document.getElementsByClassName("tabcontent");
            for (i = 0; i < tabcontent.length; i++) {
                tabcontent[i].style.display = "none";
            }
            tablinks = document.getElementsByClassName("tablinks");
            for (i = 0; i < tablinks.length; i++) {
                tablinks[i].className = tablinks[i].className.replace(" active", "");
            }
            document.getElementById(tabName).style.display = "block";
            evt.currentTarget.className += " active";
        }

        function produceComponent(componentId, price) {
            fetch('/produce_component', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ component_id: componentId })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    updateUI(data.data);
                } else {
                    alert(data.message);
                }
            });
        }

        function nextDay() {
            fetch('/next_day', {
                method: 'POST'
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    updateUI(data.data);
                }
            });
        }

        function updateUI(data) {
            document.getElementById('day').innerText = data.day;
            document.getElementById('money').innerText = data.money;
            document.getElementById('tech-level').innerText = data.tech_level;
            document.getElementById('phone-cpu-count').innerText = data.components['phone-cpu'].count;
            document.getElementById('phone-screen-count').innerText = data.components['phone-screen'].count;
            document.getElementById('phone-battery-count').innerText = data.components['phone-battery'].count;
            document.getElementById('phone-case-count').innerText = data.components['phone-case'].count;
            document.getElementById('phone-camera-count').innerText = data.components['phone-camera'].count;
        }
    </script>
</body>
</html>
```

### Explanation

1. **Flask Application**: The Flask application serves the HTML template and handles the interactions via AJAX requests.
2. **Routes**:
   - `/`: Renders the main page with the initial data.
   - `/produce_component`: Handles the production of components.
   - `/next_day`: Advances to the next day.
3. **HTML Template**: The HTML template uses Jinja2 templating to dynamically insert the initial data.
4. **JavaScript**: Handles the UI interactions and sends AJAX requests to the Flask backend.

This setup allows you to run a web application that mimics the functionality of the provided HTML code using Python and Flask.