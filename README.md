# Networked Tic-Tac-Toe Game

## 📋 Table of Contents
1. [Overview](#overview)
2. [Features](#features)
3. [Requirements](#requirements)
4. [Installation](#installation)
5. [Running the Game](#running-the-game)
6. [How to Play](#how-to-play)
7. [Troubleshooting](#troubleshooting)
8. [Technical Details](#technical-details)

---

## 🎮 Overview

A fully-featured networked Tic-Tac-Toe game that allows two players to compete in real-time over a network connection. The game features user authentication, a clean graphical interface, real-time gameplay, and in-game chat functionality.

---

## ✨ Features

### Core Features
- **User Authentication**: Register and login with username/password
- **Real-Time Gameplay**: Instant move updates using TCP socket communication
- **Quick Match System**: Automatic matchmaking with waiting players
- **Visual Game Board**: Clean, colorful 3x3 grid interface
- **Turn Indicators**: Clear display of whose turn it is
- **Win Detection**: Automatic detection of wins, losses, and draws
- **Winning Highlight**: Visual highlighting of winning combinations
- **In-Game Chat**: Real-time text chat with your opponent
- **Disconnect Handling**: Graceful handling of player disconnections

### Technical Features
- **Multi-threaded Server**: Supports multiple concurrent games
- **JSON Communication**: Structured message format
- **Thread-Safe Operations**: Protected shared data structures
- **Automatic Reconnection**: Players can rejoin after disconnection
- **Clean UI/UX**: Modern color scheme and intuitive interface

---

## 📦 Requirements

### System Requirements
- Python 3.7 or higher
- Network connection (local or internet)
- Operating System: Windows, macOS, or Linux

### Python Packages
All required packages are part of Python's standard library:
- `socket` - Network communication
- `threading` - Concurrent handling
- `json` - Data serialization
- `tkinter` - GUI (usually pre-installed with Python)

---

## 🚀 Installation

### Step 1: Check Python Installation
```bash
python --version
# or
python3 --version
```

If Python is not installed, download it from [python.org](https://www.python.org/downloads/)

### Step 2: Download the Game Files
Save the following files in the same directory:
- `tictactoe_server.py` - Server application
- `tictactoe_client.py` - Client application

### Step 3: Verify tkinter Installation
```bash
python -m tkinter
```
A small window should appear. If you get an error, install tkinter:

**Ubuntu/Debian:**
```bash
sudo apt-get install python3-tk
```

**Fedora:**
```bash
sudo dnf install python3-tkinter
```

**macOS/Windows:**
tkinter is usually pre-installed

---

## 🎯 Running the Game

### For Local Play (Same Computer)

#### 1. Start the Server
Open a terminal/command prompt and run:
```bash
python tictactoe_server.py
```

You should see:
```
==================================================
TIC-TAC-TOE SERVER
==================================================
[SERVER] Started on 0.0.0.0:5555
[SERVER] Waiting for connections...
```

#### 2. Start Client 1
Open a NEW terminal/command prompt and run:
```bash
python tictactoe_client.py
```

#### 3. Start Client 2
Open ANOTHER terminal/command prompt and run:
```bash
python tictactoe_client.py
```

### For Network Play (Different Computers)

#### 1. Start Server (Host Computer)
```bash
python tictactoe_server.py
```

Find your IP address:
- **Windows**: `ipconfig` (look for IPv4 Address)
- **macOS/Linux**: `ifconfig` or `ip addr` (look for inet)

#### 2. Modify Client (Player Computers)
Edit `tictactoe_client.py`, line ~293:
```python
# Change this line:
client = TicTacToeClient(host='127.0.0.1', port=5555)

# To this (use server's IP):
client = TicTacToeClient(host='192.168.1.100', port=5555)
```

#### 3. Start Clients
Run on each player's computer:
```bash
python tictactoe_client.py
```

#### 4. Firewall Configuration
Ensure port 5555 is open on the server computer:

**Windows:**
- Open Windows Firewall
- Add inbound rule for port 5555 (TCP)

**Linux:**
```bash
sudo ufw allow 5555/tcp
```

**macOS:**
- System Preferences → Security & Privacy → Firewall → Firewall Options
- Allow incoming connections for Python

---

## 🎲 How to Play

### Creating an Account

1. **Launch the client** - The login screen will appear
2. **Register**:
   - Enter a unique username
   - Enter a password
   - Click "Register"
   - You'll see a success message
3. **Login**:
   - Enter your username and password
   - Click "Login"

### Starting a Game

1. **Quick Match**:
   - Click "Quick Match" button
   - Wait for an opponent to join
   - Game starts automatically when matched

2. **Playing**:
   - **X** always goes first
   - Click any empty square to place your symbol
   - Your turn is indicated by green "YOUR TURN" text
   - Opponent's turn shows red "OPPONENT'S TURN" text

3. **Winning**:
   - Get three in a row (horizontal, vertical, or diagonal)
   - Winning combination highlights in green
   - Game announces the winner

4. **Chatting**:
   - Type message in chat box at bottom
   - Press Enter or click "Send"
   - Messages appear with timestamp

### Game Rules

1. Players alternate turns placing X or O
2. First player to get 3 in a row wins
3. If all 9 squares are filled with no winner, it's a draw
4. You cannot place your symbol on an occupied square
5. You cannot move during opponent's turn

---

## 🔧 Troubleshooting

### Connection Issues

**Problem**: "Could not connect to server"
- **Solution**: 
  - Verify server is running
  - Check IP address is correct
  - Ensure firewall allows port 5555
  - Try using `127.0.0.1` for local testing

**Problem**: Server shows no connections
- **Solution**:
  - Check if port 5555 is already in use
  - Try a different port (edit both server and client)
  - Restart the server

### Login Issues

**Problem**: "Invalid credentials"
- **Solution**: 
  - Register first if new user
  - Check username/password spelling
  - Usernames are case-sensitive

**Problem**: "Username already exists"
- **Solution**: 
  - Choose a different username
  - This prevents duplicate accounts

### Gameplay Issues

**Problem**: "Not your turn"
- **Solution**: 
  - Wait for opponent to move
  - Check turn indicator at top

**Problem**: Game freezes or doesn't update
- **Solution**: 
  - Check network connection
  - Restart client
  - Rejoin game

**Problem**: Opponent disconnected
- **Solution**: 
  - You'll be notified automatically
  - Return to lobby
  - Start a new game

### GUI Issues

**Problem**: Window doesn't appear
- **Solution**: 
  - Verify tkinter is installed
  - Try running: `python -m tkinter`
  - Reinstall tkinter package

**Problem**: Buttons don't respond
- **Solution**: 
  - Click directly on button center
  - Ensure it's your turn
  - Check if game is over

---

## 🔍 Technical Details

### Architecture

```
┌─────────────┐         ┌─────────────┐
│  Client 1   │◄───────►│             │
│   (GUI)     │         │   Server    │
└─────────────┘         │  (Handler)  │
                        │             │
┌─────────────┐         │             │
│  Client 2   │◄───────►│             │
│   (GUI)     │         └─────────────┘
└─────────────┘
```

### Communication Protocol

**Message Format**: JSON over TCP
```json
{
    "type": "message_type",
    "data": {...}
}
```

**Message Types**:
- `register`: New user registration
- `login`: User authentication
- `create_game`: Start matchmaking
- `game_start`: Game initialization
- `move`: Player move
- `game_update`: Board state update
- `game_over`: Game completion
- `chat`: Chat message
- `leave_game`: Exit game

### Server Features

- **Multi-threaded**: Each client handled in separate thread
- **Thread-safe**: Locks protect shared data
- **Automatic Matching**: Pairs waiting players
- **Game Management**: Tracks multiple concurrent games
- **User Persistence**: Maintains user accounts

### Client Features

- **Event-driven GUI**: Responsive tkinter interface
- **Async Communication**: Background message receiving
- **State Management**: Tracks game state locally
- **Error Handling**: Graceful error messages
- **Auto-reconnect**: Can reconnect after disconnection

### Network Protocol

- **Protocol**: TCP (Transmission Control Protocol)
- **Port**: 5555 (configurable)
- **Encoding**: UTF-8
- **Format**: JSON serialization
- **Buffer Size**: 4096 bytes

### Security Considerations

⚠️ **Note**: This is a demonstration project. For production use:
- Implement password hashing (bcrypt, argon2)
- Add SSL/TLS encryption
- Implement rate limiting
- Add input validation
- Use proper database for user storage
- Implement session tokens
- Add SQL injection protection

---

## 📝 Advanced Configuration

### Changing Server Port

**In `tictactoe_server.py`** (line 292):
```python
server = TicTacToeServer(host='0.0.0.0', port=DESIRED_PORT)
```

**In `tictactoe_client.py`** (line 293):
```python
client = TicTacToeClient(host='SERVER_IP', port=DESIRED_PORT)
```

### Customizing Colors

Edit color codes in `tictactoe_client.py`:
```python
# Background colors
bg='#2c3e50'  # Dark blue-gray
bg='#34495e'  # Medium blue-gray

# Text colors  
fg='#ecf0f1'  # Off-white
fg='#e74c3c'  # Red
fg='#3498db'  # Blue
fg='#2ecc71'  # Green
```

### Running on Cloud Server

1. Deploy server to cloud (AWS, DigitalOcean, etc.)
2. Note public IP address
3. Configure security groups to allow port 5555
4. Update client with server's public IP
5. Players connect from anywhere!

---

## 🎓 Learning Resources

### Concepts Covered
- **Socket Programming**: TCP client-server communication
- **Threading**: Concurrent execution
- **GUI Development**: tkinter interface design
- **Network Protocols**: Message-based communication
- **Game Logic**: Win condition checking
- **State Management**: Client-server synchronization

### Next Steps
- Add AI opponent
- Implement ranking system
- Add game history
- Create tournament mode
- Add replay functionality
- Implement spectator mode