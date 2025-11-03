"""
Networked Tic-Tac-Toe Game Server
Handles multiple game rooms, player authentication, and real-time gameplay
"""

import socket
import threading
import json
import time
from datetime import datetime

class TicTacToeServer:
    def __init__(self, host='0.0.0.0', port=5555):
        self.host = host
        self.port = port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        # Data structures
        self.users = {}  # username: password
        self.clients = {}  # conn: username
        self.games = {}  # game_id: Game object
        self.waiting_players = []  # List of (conn, username)
        self.player_games = {}  # username: game_id
        
        self.lock = threading.Lock()
        
    def start(self):
        """Start the server"""
        self.server.bind((self.host, self.port))
        self.server.listen(5)
        print(f"[SERVER] Started on {self.host}:{self.port}")
        print("[SERVER] Waiting for connections...")
        
        while True:
            try:
                conn, addr = self.server.accept()
                thread = threading.Thread(target=self.handle_client, args=(conn, addr))
                thread.daemon = True
                thread.start()
                print(f"[CONNECTION] New connection from {addr}")
            except Exception as e:
                print(f"[ERROR] {e}")
                
    def handle_client(self, conn, addr):
        """Handle individual client connections"""
        try:
            while True:
                data = conn.recv(4096).decode('utf-8')
                if not data:
                    break
                    
                try:
                    message = json.loads(data)
                    self.process_message(conn, message)
                except json.JSONDecodeError:
                    self.send_message(conn, {'type': 'error', 'message': 'Invalid message format'})
                    
        except Exception as e:
            print(f"[ERROR] Client handler error: {e}")
        finally:
            self.disconnect_client(conn)
            
    def process_message(self, conn, message):
        """Process incoming messages from clients"""
        msg_type = message.get('type')
        
        if msg_type == 'register':
            self.handle_register(conn, message)
        elif msg_type == 'login':
            self.handle_login(conn, message)
        elif msg_type == 'create_game':
            self.handle_create_game(conn)
        elif msg_type == 'join_game':
            self.handle_join_game(conn, message)
        elif msg_type == 'get_games':
            self.handle_get_games(conn)
        elif msg_type == 'move':
            self.handle_move(conn, message)
        elif msg_type == 'chat':
            self.handle_chat(conn, message)
        elif msg_type == 'leave_game':
            self.handle_leave_game(conn)
            
    def handle_register(self, conn, message):
        """Handle user registration"""
        username = message.get('username')
        password = message.get('password')
        
        with self.lock:
            if username in self.users:
                self.send_message(conn, {'type': 'register_response', 'success': False, 
                                        'message': 'Username already exists'})
            else:
                self.users[username] = password
                self.send_message(conn, {'type': 'register_response', 'success': True, 
                                        'message': 'Registration successful'})
                
    def handle_login(self, conn, message):
        """Handle user login"""
        username = message.get('username')
        password = message.get('password')
        
        with self.lock:
            if username in self.users and self.users[username] == password:
                self.clients[conn] = username
                self.send_message(conn, {'type': 'login_response', 'success': True, 
                                        'message': 'Login successful', 'username': username})
            else:
                self.send_message(conn, {'type': 'login_response', 'success': False, 
                                        'message': 'Invalid credentials'})
                
    def handle_create_game(self, conn):
        """Create a new game and add player to waiting list"""
        username = self.clients.get(conn)
        if not username:
            self.send_message(conn, {'type': 'error', 'message': 'Not logged in'})
            return
            
        with self.lock:
            # Remove from any existing game
            if username in self.player_games:
                old_game_id = self.player_games[username]
                if old_game_id in self.games:
                    del self.games[old_game_id]
                del self.player_games[username]
            
            # Add to waiting list
            self.waiting_players.append((conn, username))
            self.send_message(conn, {'type': 'waiting', 'message': 'Waiting for opponent...'})
            
            # Try to match players
            if len(self.waiting_players) >= 2:
                self.match_players()
                
    def handle_join_game(self, conn, message):
        """Join an existing game"""
        game_id = message.get('game_id')
        username = self.clients.get(conn)
        
        if not username:
            self.send_message(conn, {'type': 'error', 'message': 'Not logged in'})
            return
            
        with self.lock:
            if game_id in self.games:
                game = self.games[game_id]
                if game.player2 is None:
                    game.player2 = username
                    game.player2_conn = conn
                    self.player_games[username] = game_id
                    self.start_game(game)
                else:
                    self.send_message(conn, {'type': 'error', 'message': 'Game is full'})
            else:
                self.send_message(conn, {'type': 'error', 'message': 'Game not found'})
                
    def match_players(self):
        """Match two waiting players into a game"""
        if len(self.waiting_players) < 2:
            return
            
        p1_conn, p1_username = self.waiting_players.pop(0)
        p2_conn, p2_username = self.waiting_players.pop(0)
        
        game_id = f"game_{int(time.time())}_{p1_username}"
        game = Game(game_id, p1_username, p2_username, p1_conn, p2_conn)
        self.games[game_id] = game
        self.player_games[p1_username] = game_id
        self.player_games[p2_username] = game_id
        
        self.start_game(game)
        
    def start_game(self, game):
        """Start a game and notify both players"""
        game_state = {
            'type': 'game_start',
            'game_id': game.game_id,
            'player1': game.player1,
            'player2': game.player2,
            'board': game.board,
            'current_turn': game.current_turn
        }
        
        p1_state = game_state.copy()
        p1_state['your_symbol'] = 'X'
        p1_state['opponent'] = game.player2
        
        p2_state = game_state.copy()
        p2_state['your_symbol'] = 'O'
        p2_state['opponent'] = game.player1
        
        self.send_message(game.player1_conn, p1_state)
        self.send_message(game.player2_conn, p2_state)
        
    def handle_get_games(self, conn):
        """Send list of available games"""
        with self.lock:
            games_list = []
            for game_id, game in self.games.items():
                if game.player2 is None:
                    games_list.append({
                        'game_id': game_id,
                        'player1': game.player1,
                        'status': 'waiting'
                    })
                    
            self.send_message(conn, {'type': 'games_list', 'games': games_list})
            
    def handle_move(self, conn, message):
        """Handle a player's move"""
        username = self.clients.get(conn)
        if not username or username not in self.player_games:
            return
            
        game_id = self.player_games[username]
        game = self.games.get(game_id)
        
        if not game:
            return
            
        position = message.get('position')
        result = game.make_move(username, position)
        
        if result['valid']:
            # Send update to both players
            update = {
                'type': 'game_update',
                'board': game.board,
                'current_turn': game.current_turn,
                'position': position,
                'player': username
            }
            
            self.send_message(game.player1_conn, update)
            self.send_message(game.player2_conn, update)
            
            # Check for game over
            if result.get('winner') or result.get('draw'):
                game_over = {
                    'type': 'game_over',
                    'winner': result.get('winner'),
                    'draw': result.get('draw'),
                    'winning_combo': result.get('winning_combo')
                }
                self.send_message(game.player1_conn, game_over)
                self.send_message(game.player2_conn, game_over)
        else:
            self.send_message(conn, {'type': 'invalid_move', 'message': result.get('message')})
            
    def handle_chat(self, conn, message):
        """Handle chat messages"""
        username = self.clients.get(conn)
        if not username or username not in self.player_games:
            return
            
        game_id = self.player_games[username]
        game = self.games.get(game_id)
        
        if not game:
            return
            
        chat_msg = {
            'type': 'chat',
            'username': username,
            'message': message.get('message'),
            'timestamp': datetime.now().strftime('%H:%M:%S')
        }
        
        # Send to both players
        self.send_message(game.player1_conn, chat_msg)
        self.send_message(game.player2_conn, chat_msg)
        
    def handle_leave_game(self, conn):
        """Handle player leaving a game"""
        username = self.clients.get(conn)
        if username and username in self.player_games:
            game_id = self.player_games[username]
            game = self.games.get(game_id)
            
            if game:
                # Notify other player
                other_conn = game.player2_conn if game.player1 == username else game.player1_conn
                self.send_message(other_conn, {'type': 'opponent_left', 
                                               'message': f'{username} has left the game'})
                
                # Clean up
                del self.games[game_id]
                if game.player1 in self.player_games:
                    del self.player_games[game.player1]
                if game.player2 and game.player2 in self.player_games:
                    del self.player_games[game.player2]
                    
    def disconnect_client(self, conn):
        """Handle client disconnection"""
        with self.lock:
            username = self.clients.get(conn)
            if username:
                # Remove from waiting list
                self.waiting_players = [(c, u) for c, u in self.waiting_players if c != conn]
                
                # Leave any active game
                self.handle_leave_game(conn)
                
                del self.clients[conn]
                print(f"[DISCONNECT] {username} disconnected")
                
        try:
            conn.close()
        except:
            pass
            
    def send_message(self, conn, message):
        """Send a message to a client"""
        try:
            conn.send(json.dumps(message).encode('utf-8'))
        except Exception as e:
            print(f"[ERROR] Failed to send message: {e}")


class Game:
    """Represents a Tic-Tac-Toe game"""
    def __init__(self, game_id, player1, player2, player1_conn, player2_conn):
        self.game_id = game_id
        self.player1 = player1
        self.player2 = player2
        self.player1_conn = player1_conn
        self.player2_conn = player2_conn
        self.board = ['' for _ in range(9)]
        self.current_turn = player1
        self.game_over = False
        
    def make_move(self, player, position):
        """Make a move on the board"""
        if self.game_over:
            return {'valid': False, 'message': 'Game is over'}
            
        if player != self.current_turn:
            return {'valid': False, 'message': 'Not your turn'}
            
        if position < 0 or position > 8:
            return {'valid': False, 'message': 'Invalid position'}
            
        if self.board[position] != '':
            return {'valid': False, 'message': 'Position already taken'}
            
        # Make the move
        symbol = 'X' if player == self.player1 else 'O'
        self.board[position] = symbol
        
        # Check for winner
        winner, winning_combo = self.check_winner()
        if winner:
            self.game_over = True
            return {'valid': True, 'winner': self.player1 if winner == 'X' else self.player2, 
                   'winning_combo': winning_combo}
            
        # Check for draw
        if '' not in self.board:
            self.game_over = True
            return {'valid': True, 'draw': True}
            
        # Switch turns
        self.current_turn = self.player2 if player == self.player1 else self.player1
        return {'valid': True}
        
    def check_winner(self):
        """Check if there's a winner"""
        winning_combinations = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],  # Rows
            [0, 3, 6], [1, 4, 7], [2, 5, 8],  # Columns
            [0, 4, 8], [2, 4, 6]              # Diagonals
        ]
        
        for combo in winning_combinations:
            if (self.board[combo[0]] != '' and 
                self.board[combo[0]] == self.board[combo[1]] == self.board[combo[2]]):
                return self.board[combo[0]], combo
                
        return None, None


if __name__ == '__main__':
    server = TicTacToeServer(host='0.0.0.0', port=5555)
    print("=" * 50)
    print("TIC-TAC-TOE SERVER")
    print("=" * 50)
    server.start()