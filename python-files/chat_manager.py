import json
import datetime
import os
from threading import Thread, Lock

class ChatManager:
    def __init__(self, messages_file, users_file):
        self.messages_file = messages_file
        self.users_file = users_file
        self.lock = Lock()
        self.setup_files()
    
    def setup_files(self):
        if not os.path.exists(self.messages_file):
            with open(self.messages_file, 'w') as f:
                json.dump({}, f)
    
    def create_channel(self, channel_name, creator):
        with self.lock:
            with open(self.messages_file, 'r') as f:
                data = json.load(f)
            
            if channel_name not in data:
                data[channel_name] = {
                    'type': 'channel',
                    'creator': creator,
                    'created_at': datetime.datetime.now().isoformat(),
                    'members': [creator],
                    'messages': []
                }
                
                with open(self.messages_file, 'w') as f:
                    json.dump(data, f)
                return True
            return False
    
    def send_message(self, channel_name, username, message, message_type='text'):
        with self.lock:
            with open(self.messages_file, 'r') as f:
                data = json.load(f)
            
            if channel_name not in data:
                return False
            
            message_data = {
                'id': len(data[channel_name]['messages']) + 1,
                'sender': username,
                'message': message,
                'type': message_type,
                'timestamp': datetime.datetime.now().isoformat()
            }
            
            data[channel_name]['messages'].append(message_data)
            
            with open(self.messages_file, 'w') as f:
                json.dump(data, f)
            
            return True
    
    def get_channel_messages(self, channel_name, limit=100):
        with open(self.messages_file, 'r') as f:
            data = json.load(f)
        
        if channel_name in data:
            messages = data[channel_name]['messages'][-limit:]
            return messages
        return []
    
    def add_user_to_channel(self, channel_name, username, admin_user):
        with self.lock:
            with open(self.messages_file, 'r') as f:
                data = json.load(f)
            
            if channel_name in data and admin_user == data[channel_name]['creator']:
                if username not in data[channel_name]['members']:
                    data[channel_name]['members'].append(username)
                    
                    with open(self.messages_file, 'w') as f:
                        json.dump(data, f)
                    return True
            return False
    
    def get_user_channels(self, username):
        with open(self.messages_file, 'r') as f:
            data = json.load(f)
        
        user_channels = []
        for channel_name, channel_data in data.items():
            if username in channel_data['members']:
                user_channels.append({
                    'name': channel_name,
                    'type': channel_data['type'],
                    'member_count': len(channel_data['members'])
                })
        
        return user_channels
    
    def create_direct_chat(self, user1, user2):
        chat_id = f"dm_{min(user1, user2)}_{max(user1, user2)}"
        
        with self.lock:
            with open(self.messages_file, 'r') as f:
                data = json.load(f)
            
            if chat_id not in data:
                data[chat_id] = {
                    'type': 'direct',
                    'participants': [user1, user2],
                    'created_at': datetime.datetime.now().isoformat(),
                    'messages': []
                }
                
                with open(self.messages_file, 'w') as f:
                    json.dump(data, f)
            
            return chat_id
    
    def send_direct_message(self, sender, receiver, message):
        chat_id = self.create_direct_chat(sender, receiver)
        return self.send_message(chat_id, sender, message)
    
    def get_direct_messages(self, user1, user2):
        chat_id = f"dm_{min(user1, user2)}_{max(user1, user2)}"
        return self.get_channel_messages(chat_id)
    
    def search_messages(self, query, username):
        with open(self.messages_file, 'r') as f:
            data = json.load(f)
        
        results = []
        for channel_id, channel_data in data.items():
            if username in channel_data.get('members', []) or username in channel_data.get('participants', []):
                for message in channel_data['messages']:
                    if query.lower() in message['message'].lower():
                        results.append({
                            'channel': channel_id,
                            'sender': message['sender'],
                            'message': message['message'],
                            'timestamp': message['timestamp']
                        })
        
        return results
    
    def delete_message(self, channel_name, message_id, username):
        with self.lock:
            with open(self.messages_file, 'r') as f:
                data = json.load(f)
            
            if channel_name in data:
                for i, message in enumerate(data[channel_name]['messages']):
                    if message['id'] == message_id and message['sender'] == username:
                        data[channel_name]['messages'].pop(i)
                        
                        with open(self.messages_file, 'w') as f:
                            json.dump(data, f)
                        return True
            return False
    
    def get_channel_info(self, channel_name):
        with open(self.messages_file, 'r') as f:
            data = json.load(f)
        
        if channel_name in data:
            return data[channel_name]
        return None