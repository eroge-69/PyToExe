
from flask import Flask, render_template, request, jsonify, session
import random
import uuid

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

class MemoryGame:
    def __init__(self):
        self.card_values = ['🍎', '🍌', '🍇', '🍊', '🍓', '🥝']
        self.cards = self.card_values * 2
        random.shuffle(self.cards)
        self.revealed = [False] * len(self.cards)
        self.matched = [False] * len(self.cards)
        self.first_choice = None
        self.second_choice = None
        self.pairs_found = 0
        self.total_pairs = len(self.cards) // 2
        self.moves = 0
        self.can_click = True

    def get_card_display(self, index):
        if self.revealed[index] or self.matched[index]:
            return self.cards[index]
        return '❓'

    def flip_card(self, index):
        if not self.can_click or self.revealed[index] or self.matched[index]:
            return False
        
        self.revealed[index] = True
        
        if self.first_choice is None:
            self.first_choice = index
        elif self.second_choice is None:
            self.second_choice = index
            self.moves += 1
            self.can_click = False
        
        return True

    def check_match(self):
        if self.first_choice is not None and self.second_choice is not None:
            if self.cards[self.first_choice] == self.cards[self.second_choice]:
                self.matched[self.first_choice] = True
                self.matched[self.second_choice] = True
                self.pairs_found += 1
                result = 'match'
            else:
                self.revealed[self.first_choice] = False
                self.revealed[self.second_choice] = False
                result = 'no_match'
            
            self.first_choice = None
            self.second_choice = None
            self.can_click = True
            return result
        return None

    def is_game_won(self):
        return self.pairs_found == self.total_pairs

@app.route('/')
def index():
    session['game_id'] = str(uuid.uuid4())
    session['game'] = MemoryGame().__dict__
    return render_template('index.html')

@app.route('/flip_card', methods=['POST'])
def flip_card():
    game_data = session.get('game')
    if not game_data:
        return jsonify({'error': 'No game found'})
    
    game = MemoryGame()
    game.__dict__.update(game_data)
    
    card_index = int(request.json['index'])
    
    if game.flip_card(card_index):
        session['game'] = game.__dict__
        
        response = {
            'success': True,
            'cards': [game.get_card_display(i) for i in range(len(game.cards))],
            'revealed': game.revealed,
            'matched': game.matched,
            'can_click': game.can_click,
            'moves': game.moves,
            'pairs_found': game.pairs_found,
            'total_pairs': game.total_pairs
        }
        
        # Check for match if two cards are revealed
        match_result = game.check_match()
        if match_result:
            response['match_result'] = match_result
            response['can_click'] = game.can_click
            session['game'] = game.__dict__
        
        response['game_won'] = game.is_game_won()
        
        return jsonify(response)
    
    return jsonify({'success': False})

@app.route('/new_game', methods=['POST'])
def new_game():
    session['game'] = MemoryGame().__dict__
    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
