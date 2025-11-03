"""
Networked Tic-Tac-Toe Game Client
GUI-based client using tkinter for the game interface
"""

import socket
import threading
import json
import tkinter as tk
from tkinter import messagebox, scrolledtext
from datetime import datetime

class TicTacToeClient:
    def __init__(self, host='127.0.0.1', port=5555):
        self.host = host
        self.port = port
        self.client = None
        self.username = None
        self.game_id = None
        self.your_symbol = None
        self.opponent = None
        self.current_turn = None
        self.board = ['' for _ in range(9)]
        
        # GUI
        self.root = tk.Tk()
        self.root.title("Networked Tic-Tac-Toe")
        self.root.geometry("800x700")
        self.root.configure(bg='#2c3e50')
        
        self.setup_login_screen()
        
    def connect_to_server(self):
        """Connect to the game server"""
        try:
            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client.connect((self.host, self.port))
            
            # Start listening thread
            thread = threading.Thread(target=self.receive_messages, daemon=True)
            thread.start()
            return True
        except Exception as e:
            messagebox.showerror("Connection Error", f"Could not connect to server: {e}")
            return False
            
    def receive_messages(self):
        """Receive messages from server"""
        while True:
            try:
                data = self.client.recv(4096).decode('utf-8')
                if not data:
                    break
                    
                message = json.loads(data)
                self.handle_message(message)
            except Exception as e:
                print(f"Error receiving message: {e}")
                break
                
    def handle_message(self, message):
        """Handle incoming messages from server"""
        msg_type = message.get('type')
        
        if msg_type == 'register_response':
            self.handle_register_response(message)
        elif msg_type == 'login_response':
            self.handle_login_response(message)
        elif msg_type == 'waiting':
            self.show_waiting_screen()
        elif msg_type == 'game_start':
            self.handle_game_start(message)
        elif msg_type == 'game_update':
            self.handle_game_update(message)
        elif msg_type == 'game_over':
            self.handle_game_over(message)
        elif msg_type == 'chat':
            self.handle_chat(message)
        elif msg_type == 'opponent_left':
            self.handle_opponent_left(message)
        elif msg_type == 'error':
            messagebox.showerror("Error", message.get('message'))
            
    def send_message(self, message):
        """Send message to server"""
        try:
            self.client.send(json.dumps(message).encode('utf-8'))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to send message: {e}")
            
    # ===== LOGIN SCREEN =====
    def setup_login_screen(self):
        """Setup the login/register screen"""
        self.clear_screen()
        
        frame = tk.Frame(self.root, bg='#34495e', padx=40, pady=40)
        frame.place(relx=0.5, rely=0.5, anchor='center')
        
        tk.Label(frame, text="TIC-TAC-TOE", font=('Arial', 32, 'bold'), 
                bg='#34495e', fg='#ecf0f1').pack(pady=20)
        
        tk.Label(frame, text="Username:", font=('Arial', 12), 
                bg='#34495e', fg='#ecf0f1').pack(pady=5)
        self.username_entry = tk.Entry(frame, font=('Arial', 12), width=25)
        self.username_entry.pack(pady=5)
        
        tk.Label(frame, text="Password:", font=('Arial', 12), 
                bg='#34495e', fg='#ecf0f1').pack(pady=5)
        self.password_entry = tk.Entry(frame, font=('Arial', 12), width=25, show='*')
        self.password_entry.pack(pady=5)
        
        btn_frame = tk.Frame(frame, bg='#34495e')
        btn_frame.pack(pady=20)
        
        tk.Button(btn_frame, text="Login", font=('Arial', 12), bg='#27ae60', 
                 fg='white', width=10, command=self.login).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Register", font=('Arial', 12), bg='#3498db', 
                 fg='white', width=10, command=self.register).pack(side=tk.LEFT, padx=5)
                 
    def login(self):
        """Login to the server"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if not username or not password:
            messagebox.showwarning("Input Error", "Please enter username and password")
            return
            
        if not self.client:
            if not self.connect_to_server():
                return
                
        self.send_message({
            'type': 'login',
            'username': username,
            'password': password
        })
        
    def register(self):
        """Register a new account"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if not username or not password:
            messagebox.showwarning("Input Error", "Please enter username and password")
            return
            
        if not self.client:
            if not self.connect_to_server():
                return
                
        self.send_message({
            'type': 'register',
            'username': username,
            'password': password
        })
        
    def handle_register_response(self, message):
        """Handle registration response"""
        if message.get('success'):
            messagebox.showinfo("Success", "Registration successful! Please login.")
        else:
            messagebox.showerror("Error", message.get('message'))
            
    def handle_login_response(self, message):
        """Handle login response"""
        if message.get('success'):
            self.username = message.get('username')
            self.setup_lobby_screen()
        else:
            messagebox.showerror("Error", message.get('message'))
            
    # ===== LOBBY SCREEN =====
    def setup_lobby_screen(self):
        """Setup the game lobby"""
        self.clear_screen()
        
        tk.Label(self.root, text=f"Welcome, {self.username}!", font=('Arial', 24, 'bold'),
                bg='#2c3e50', fg='#ecf0f1').pack(pady=20)
        
        btn_frame = tk.Frame(self.root, bg='#2c3e50')
        btn_frame.pack(pady=20)
        
        tk.Button(btn_frame, text="Quick Match", font=('Arial', 14, 'bold'), 
                 bg='#e74c3c', fg='white', width=15, height=2,
                 command=self.quick_match).pack(pady=10)
        
    def quick_match(self):
        """Start quick match (create game)"""
        self.send_message({'type': 'create_game'})
        
    def show_waiting_screen(self):
        """Show waiting for opponent screen"""
        self.clear_screen()
        
        tk.Label(self.root, text="Waiting for opponent...", font=('Arial', 24),
                bg='#2c3e50', fg='#ecf0f1').pack(pady=100)
        
        # Add a cancel button
        tk.Button(self.root, text="Cancel", font=('Arial', 12), 
                 bg='#e74c3c', fg='white', width=10,
                 command=self.cancel_waiting).pack(pady=20)
        
    def cancel_waiting(self):
        """Cancel waiting and return to lobby"""
        self.send_message({'type': 'leave_game'})
        self.setup_lobby_screen()
        
    # ===== GAME SCREEN =====
    def handle_game_start(self, message):
        """Handle game start"""
        self.game_id = message.get('game_id')
        self.your_symbol = message.get('your_symbol')
        self.opponent = message.get('opponent')
        self.current_turn = message.get('current_turn')
        self.board = message.get('board')
        
        self.setup_game_screen()
        
    def setup_game_screen(self):
        """Setup the game board"""
        self.clear_screen()
        
        # Top info bar
        info_frame = tk.Frame(self.root, bg='#34495e', height=80)
        info_frame.pack(fill=tk.X, pady=(0, 10))
        info_frame.pack_propagate(False)
        
        self.player_label = tk.Label(info_frame, 
                                     text=f"You: {self.username} ({self.your_symbol})",
                                     font=('Arial', 14, 'bold'), bg='#34495e', fg='#ecf0f1')
        self.player_label.pack(side=tk.LEFT, padx=20, pady=20)
        
        self.opponent_label = tk.Label(info_frame,
                                       text=f"Opponent: {self.opponent}",
                                       font=('Arial', 14, 'bold'), bg='#34495e', fg='#ecf0f1')
        self.opponent_label.pack(side=tk.RIGHT, padx=20, pady=20)
        
        self.turn_label = tk.Label(info_frame, text="", font=('Arial', 12),
                                   bg='#34495e', fg='#f39c12')
        self.turn_label.pack(pady=5)
        self.update_turn_label()
        
        # Game board
        board_frame = tk.Frame(self.root, bg='#2c3e50')
        board_frame.pack(expand=True)
        
        self.buttons = []
        for i in range(3):
            for j in range(3):
                pos = i * 3 + j
                btn = tk.Button(board_frame, text='', font=('Arial', 36, 'bold'),
                              width=4, height=2, bg='#ecf0f1', fg='#2c3e50',
                              relief=tk.RAISED, bd=5,
                              command=lambda p=pos: self.make_move(p))
                btn.grid(row=i, column=j, padx=5, pady=5)
                self.buttons.append(btn)
        
        # Chat area
        chat_frame = tk.Frame(self.root, bg='#34495e', height=200)
        chat_frame.pack(fill=tk.BOTH, padx=10, pady=10)
        chat_frame.pack_propagate(False)
        
        tk.Label(chat_frame, text="Chat", font=('Arial', 12, 'bold'),
                bg='#34495e', fg='#ecf0f1').pack()
        
        self.chat_display = scrolledtext.ScrolledText(chat_frame, height=6, 
                                                      font=('Arial', 10),
                                                      bg='#2c3e50', fg='#ecf0f1',
                                                      wrap=tk.WORD)
        self.chat_display.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.chat_display.config(state=tk.DISABLED)
        
        chat_input_frame = tk.Frame(chat_frame, bg='#34495e')
        chat_input_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.chat_entry = tk.Entry(chat_input_frame, font=('Arial', 10))
        self.chat_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.chat_entry.bind('<Return>', lambda e: self.send_chat())
        
        tk.Button(chat_input_frame, text="Send", font=('Arial', 10),
                 bg='#3498db', fg='white', command=self.send_chat).pack(side=tk.RIGHT)
        
        self.update_board()
        
    def update_turn_label(self):
        """Update the turn indicator"""
        if self.current_turn == self.username:
            self.turn_label.config(text="YOUR TURN", fg='#2ecc71')
        else:
            self.turn_label.config(text="OPPONENT'S TURN", fg='#e74c3c')
            
    def make_move(self, position):
        """Make a move on the board"""
        if self.current_turn != self.username:
            messagebox.showinfo("Not Your Turn", "Please wait for your turn")
            return
            
        if self.board[position] != '':
            messagebox.showinfo("Invalid Move", "This position is already taken")
            return
            
        self.send_message({
            'type': 'move',
            'position': position
        })
        
    def handle_game_update(self, message):
        """Handle game board update"""
        self.board = message.get('board')
        self.current_turn = message.get('current_turn')
        self.update_board()
        self.update_turn_label()
        
    def update_board(self):
        """Update the visual board"""
        for i, symbol in enumerate(self.board):
            self.buttons[i].config(text=symbol)
            if symbol == 'X':
                self.buttons[i].config(fg='#e74c3c')
            elif symbol == 'O':
                self.buttons[i].config(fg='#3498db')
                
    def handle_game_over(self, message):
        """Handle game over"""
        winner = message.get('winner')
        draw = message.get('draw')
        winning_combo = message.get('winning_combo')
        
        # Highlight winning combination
        if winning_combo:
            for pos in winning_combo:
                self.buttons[pos].config(bg='#2ecc71')
        
        # Show result
        if draw:
            result = "It's a Draw!"
            messagebox.showinfo("Game Over", result)
        elif winner == self.username:
            result = "You Win!"
            messagebox.showinfo("Game Over", result)
        else:
            result = "You Lose!"
            messagebox.showinfo("Game Over", result)
            
        # Return to lobby after 2 seconds
        self.root.after(2000, self.return_to_lobby)
        
    def return_to_lobby(self):
        """Return to lobby after game"""
        self.game_id = None
        self.your_symbol = None
        self.opponent = None
        self.board = ['' for _ in range(9)]
        self.setup_lobby_screen()
        
    def send_chat(self):
        """Send a chat message"""
        message = self.chat_entry.get().strip()
        if message:
            self.send_message({
                'type': 'chat',
                'message': message
            })
            self.chat_entry.delete(0, tk.END)
            
    def handle_chat(self, message):
        """Handle incoming chat message"""
        username = message.get('username')
        msg = message.get('message')
        timestamp = message.get('timestamp')
        
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, f"[{timestamp}] {username}: {msg}\n")
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)
        
    def handle_opponent_left(self, message):
        """Handle opponent leaving"""
        messagebox.showinfo("Opponent Left", message.get('message'))
        self.return_to_lobby()
        
    def clear_screen(self):
        """Clear all widgets from screen"""
        for widget in self.root.winfo_children():
            widget.destroy()
            
    def run(self):
        """Run the client"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()
        
    def on_closing(self):
        """Handle window closing"""
        if self.client:
            try:
                self.send_message({'type': 'leave_game'})
                self.client.close()
            except:
                pass
        self.root.destroy()


if __name__ == '__main__':
    # Change host to server IP address if running on different machines
    client = TicTacToeClient(host='127.0.0.1', port=5555)
    print("=" * 50)
    print("TIC-TAC-TOE CLIENT")
    print("=" * 50)
    print("Connecting to server...")
    client.run()