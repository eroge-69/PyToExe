from flask import Flask, request, render_template_string
from flask_socketio import SocketIO, emit
import threading
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

# Хранилище данных
online_users = {}  # {session_id: {'nickname': str, 'status': str}}
calls = {}        # {caller_id: target_id}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>LAN Call System</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
        .container { display: flex; }
        .users-column { flex: 1; padding: 10px; border-right: 1px solid #ccc; }
        .call-column { flex: 1; padding: 10px; }
        .user-card { padding: 10px; margin: 5px 0; border: 1px solid #ddd; border-radius: 4px; }
        .online { background-color: #e6ffe6; }
        .calling { background-color: #fff9e6; }
        .ringing { background-color: #e6f7ff; }
        .in-call { background-color: #ffe6e6; }
        button { margin-top: 5px; cursor: pointer; }
        #call-controls { display: none; margin-top: 20px; }
    </style>
</head>
<body>
    <h1>LAN Voice Chat</h1>
    
    <div id="login-section">
        <input type="text" id="nickname-input" placeholder="Enter your nickname">
        <button id="login-btn">Connect</button>
    </div>
    
    <div class="container" id="main-section" style="display:none">
        <div class="users-column">
            <h2>Online Users</h2>
            <div id="users-list"></div>
        </div>
        
        <div class="call-column">
            <h2>Call Controls</h2>
            <div id="call-controls">
                <p>Call with: <span id="call-partner"></span></p>
                <button id="reset-call-btn">End Call</button>
            </div>
            <div id="incoming-call" style="display:none">
                <p>Incoming call from: <span id="caller-name"></span></p>
                <button id="accept-call-btn">Accept</button>
                <button id="reject-call-btn">Reject</button>
            </div>
        </div>
    </div>

    <script src="https://cdn.socket.io/4.0.0/socket.io.min.js"></script>
    <script>
        const socket = io();
        let currentSession = '';
        let currentNickname = '';
        
        document.getElementById('login-btn').addEventListener('click', () => {
            const nickname = document.getElementById('nickname-input').value.trim();
            if (nickname) {
                currentNickname = nickname;
                socket.emit('set_nickname', nickname);
                document.getElementById('login-section').style.display = 'none';
                document.getElementById('main-section').style.display = 'flex';
            }
        });
        
        socket.on('user_list', users => {
            updateUsersList(users);
        });
        
        socket.on('user_online', users => {
            updateUsersList(users);
        });
        
        function updateUsersList(users) {
            const container = document.getElementById('users-list');
            container.innerHTML = '';
            
            users.forEach(user => {
                if (user.session_id === socket.id) return;
                
                const userCard = document.createElement('div');
                userCard.className = `user-card ${user.status}`;
                userCard.innerHTML = `
                    <strong>${user.nickname}</strong>
                    <p>Status: ${user.status}</p>
                `;
                
                if (user.status === 'available') {
                    const callBtn = document.createElement('button');
                    callBtn.textContent = 'Call';
                    callBtn.onclick = () => startCall(user.session_id);
                    userCard.appendChild(callBtn);
                }
                
                container.appendChild(userCard);
            });
        }
        
        function startCall(targetSession) {
            socket.emit('start_call', targetSession);
            showCallControls(`Calling ${getNicknameBySession(targetSession)}...`);
        }
        
        socket.on('incoming_call', data => {
            document.getElementById('caller-name').textContent = data.caller_nick;
            document.getElementById('incoming-call').style.display = 'block';
            
            document.getElementById('accept-call-btn').onclick = () => {
                socket.emit('accept_call', data.caller_session);
                document.getElementById('incoming-call').style.display = 'none';
                showCallControls(`In call with ${data.caller_nick}`);
            };
            
            document.getElementById('reject-call-btn').onclick = () => {
                socket.emit('reset_call');
                document.getElementById('incoming-call').style.display = 'none';
            };
        });
        
        socket.on('call_established', data => {
            showCallControls(`In call with ${data.caller_nick}`);
        });
        
        socket.on('call_end', () => {
            document.getElementById('call-controls').style.display = 'none';
        });
        
        document.getElementById('reset-call-btn').addEventListener('click', () => {
            socket.emit('reset_call');
            document.getElementById('call-controls').style.display = 'none';
        });
        
        function showCallControls(partnerInfo) {
            document.getElementById('call-partner').textContent = partnerInfo;
            document.getElementById('call-controls').style.display = 'block';
        }
        
        function getNicknameBySession(sessionId) {
            return 'User';
        }
        
        socket.on('connect', () => {
            currentSession = socket.id;
        });
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@socketio.on('connect')
def handle_connect():
    print(f'Client connected: {request.sid}')

@socketio.on('disconnect')
def handle_disconnect():
    user_session = request.sid
    if user_session in online_users:
        nickname = online_users[user_session]['nickname']
        del online_users[user_session]
        for caller, target in list(calls.items()):
            if caller == user_session or target == user_session:
                del calls[caller]
                socketio.emit('call_end', to=caller)
                if target != user_session:
                    socketio.emit('call_end', to=target)
        emit('user_offline', nickname, broadcast=True)
    print(f'Client disconnected: {request.sid}')

@socketio.on('set_nickname')
def handle_set_nickname(nickname):
    session_id = request.sid
    online_users[session_id] = {'nickname': nickname, 'status': 'available'}
    emit('user_online', list_users(), broadcast=True)
    emit('user_list', list_users())

def list_users():
    return [{'session_id': sid, 'nickname': data['nickname'], 'status': data['status']} 
            for sid, data in online_users.items()]

@socketio.on('start_call')
def handle_start_call(target_session):
    caller_session = request.sid
    caller_nick = online_users.get(caller_session, {}).get('nickname', 'Unknown')
    
    if target_session in online_users:
        online_users[caller_session]['status'] = 'calling'
        online_users[target_session]['status'] = 'ringing'
        calls[caller_session] = target_session
        emit('user_online', list_users(), broadcast=True)
        emit('incoming_call', {'caller_session': caller_session, 'caller_nick': caller_nick}, to=target_session)
        
        def call_timeout():
            time.sleep(30)
            if caller_session in calls and calls[caller_session] == target_session:
                handle_reset_call()
        threading.Thread(target=call_timeout).start()

@socketio.on('accept_call')
def handle_accept_call(caller_session):
    target_session = request.sid
    if caller_session in calls and calls[caller_session] == target_session:
        target_nick = online_users[target_session]['nickname']
        caller_nick = online_users[caller_session]['nickname']
        online_users[caller_session]['status'] = 'in_call'
        online_users[target_session]['status'] = 'in_call'
        emit('call_accepted', {'target_session': target_session, 'target_nick': target_nick}, to=caller_session)
        emit('call_established', {'caller_session': caller_session, 'caller_nick': caller_nick}, to=target_session)
        emit('user_online', list_users(), broadcast=True)

@socketio.on('reset_call')
def handle_reset_call():
    session_id = request.sid
    if session_id in calls:
        target_session = calls[session_id]
        del calls[session_id]
        if session_id in online_users:
            online_users[session_id]['status'] = 'available'
        if target_session in online_users:
            online_users[target_session]['status'] = 'available'
        emit('call_end', to=session_id)
        emit('call_end', to=target_session)
        emit('user_online', list_users(), broadcast=True)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5001, debug=True)