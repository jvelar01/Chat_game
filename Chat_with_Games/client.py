from multiprocessing.connection import Client, Listener
from random import random, randint
from time import sleep
from ctypes import c_bool, c_int

from multiprocessing import Process, Manager, Value, Lock, Condition
import sys
import traceback
import pygame
import sys

from playerPingPong import Player1, Ball, Game1, Paddle, BallSprite, Display1,\
    SIZE1, PLAYER_HEIGHT1, PLAYER_WIDTH1, BALL_COLOR, BALL_SIZE, PLAYER_COLOR
from playerMarioBowser import Player2, Game2, PlayerSprite, WallSprite,\
    StarSprite, Display2, SIZE2, PLAYER_HEIGHT2, PLAYER_WIDTH2, DELTA,\
    WALL_HEIGTH, WALL_WIDTH, STAR_HEIGTH, STAR_WIDTH

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128,128,128)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255,255,0)
GREEN = (0,255,0)
X = 0
Y = 1

LEFT_PLAYER = 0
RIGHT_PLAYER = 1

FPS = 60

SIDES = ["left", "right"]
SIDESSTR = ["left", "right"]

games = {1: Game1(), 2:Game2()}

def delay(factor = 3):
    sleep(random()/factor)

def info():
    # Print basic commands and information for the client
    print('Here are the basic commands to chat and challenge other players: \n')
    print('1. Info: Type "Info" in the command line to read this information again \n')
    print('2. Players: Type "Players" to see the list of players connected to the server \n')
    print('3. Challenge <Player> <Game>: Type "Challenge" followed by the player name and game ID to challenge another player to play \n')
    print('4. Quit: Type "Quit" to quit the connection \n')
    print('5. Private <Username> <Message>: Type "Private" followed by the username and message to send a private message to another player \n')
    print('6. Requests: Type "Requests" to show your game requests \n')
    print('7. Accept <Username> <Game>: Type "Accept" followed by the username and game ID to accept a game challenge from another player \n')
    print('8. Games: Type "Games" to see the available games \n')
    print('9. Inbox: Type "Inbox" to see the available challenges and accept or refuse them \n')



def client_listener(client_data):
    # Start the client listener to receive incoming messages
    try:
        # Try opening a listener using the provided client address and port
        cl = Listener(address=(client_data['client_address'], client_data['client_port']), authkey=client_data['client_authkey'])
    except:
        # If the provided port is not available, generate a random port number
        client_data['client_port'] = randint(49152, 65535)
        cl = Listener(address=(client_data['client_address'], client_data['client_port']), authkey=client_data['client_authkey'])
    
    print(f'Connected to General Chat')
    
    while True:
        # Accept incoming connections and receive messages
        conn = cl.accept()
        m = conn.recv()
        print(m)



class General:
    def __init__(self, manager, conn):
        # Initialize the General class with shared variables and synchronization primitives
        self.manager = manager
        self.conn = conn
        self.connected = Value(c_bool, True)  # Flag to indicate if the client is connected
        self.challenges = manager.dict()  # Dictionary to store challenges from other players
        self.current_game = Value(c_int, 0)  # Current game ID for the player
        self.in_game = Value(c_bool, False)  # Flag to indicate if the player is in a game
        self.opponent = manager.Value(str, 'Local')  # Opponent player's name
        self.edit_mutex = Lock()  # Mutex for modifying the challenges dictionary
        self.mutex = Lock()  # Mutex for synchronization
        self.confirmation = Condition(self.mutex)  # Condition variable for confirmation synchronization
        self.side_available = Condition(self.mutex)  # Condition variable for side and game information availability
        self.update_available = Condition(self.mutex)  # Condition variable for updated information availability
        self.match_done = Value(c_bool, False)  # Flag to indicate if a match is done
        self.is_match_done = Value(c_bool, False)  # Flag to indicate if the match is done signal is received
        self.side_info_received = Value(c_bool, False)  # Flag to indicate if side and game information is received
        self.side_info = manager.list([0, 0])  # List to store side and game information
        self.updated_information_received = Value(c_bool, False)  # Flag to indicate if updated information is received
        self.updated_information = manager.dict()  # Dictionary to store updated information for the player

    def add_challenge(self, challenger, game):
        # Add a challenge from a challenger for a specific game to the challenges dictionary
        self.edit_mutex.acquire()
        if challenger in self.challenges:
            if game not in self.challenges[challenger]:
                self.challenges[challenger].append(game)
        else:
            self.challenges[challenger] = self.manager.list([game])
        self.edit_mutex.release()

    def remove_challenge(self, challenger, game):
        # Remove a challenge from the challenges dictionary
        self.edit_mutex.acquire()
        try:
            if len(self.challenges[challenger]) == 1:
                del self.challenges[challenger]
            else:
                proposed_games = self.challenges[challenger]
                proposed_games.remove(game)
                self.challenges[challenger] = proposed_games
        except Exception as e:
            traceback.print_exc()
        self.edit_mutex.release()

    def accept_challenge(self, challenger, game):
        # Accept a challenge from a challenger for a specific game
        self.mutex.acquire()
        self.conn.send(f'Accept {challenger} {game}')
        self.confirmation.wait_for(lambda: self.is_match_done.value)
        self.is_match_done.value = False
        self.remove_challenge(challenger, game)
        if self.match_done:
            self.match_done = None
            self.mutex.release()
            self.start_playing(challenger, game)
        else:
            self.mutex.release()

    def refuse_challenge(self, challenger, game):
        # Refuse a challenge from a challenger for a specific game
        self.mutex.acquire()
        self.remove_challenge(challenger, game)
        self.conn.send(f'Refuse {challenger} {game}')
        self.mutex.release()

    def start_playing(self, challenger, game):
        # Set the player to be in a game and update relevant game information
        self.mutex.acquire()
        self.in_game.value = True
        self.current_game.value = int(game)
        self.opponent.value = challenger
        self.mutex.release()

    def is_playing(self):
        # Check if the player is currently in a game
        return self.in_game.value

    def return_challenges(self):
        # Get the challenges dictionary
        self.edit_mutex.acquire()
        challenges = self.challenges
        self.edit_mutex.release()
        return challenges

    def change_match_status(self, b):
        # Change the match status and notify waiting threads
        self.mutex.acquire()
        self.match_done.value = b
        self.is_match_done.value = True
        self.confirmation.notify()
        self.mutex.release()

    def change_side_and_game(self, information):
        # Change the side and game information and notify waiting threads
        self.mutex.acquire()
        self.side_info[0] = information[0]
        self.side_info[1] = information[1]
        self.side_info_received.value = True
        self.side_available.notify()
        self.mutex.release()

    def change_update_info(self, information):
        # Change the updated information and notify waiting threads
        self.mutex.acquire()
        for key, value in information.items():
            self.updated_information[key] = value
        self.updated_information_received.value = True
        self.update_available.notify()
        self.mutex.release()

    def side_and_game_info(self):
        # Get the side and game information
        self.mutex.acquire()
        self.side_available.wait_for(lambda: self.side_info_received.value)
        information = (self.side_info[0], self.side_info[1])
        self.side_info_received.value = False
        self.mutex.release()
        return information

    def update_info(self):
        # Get the updated information
        self.mutex.acquire()
        self.update_available.wait_for(lambda: self.updated_information_received.value)
        information = self.updated_information
        self.updated_information_received.value = False
        self.mutex.release()
        return information

    def reset(self):
        # Reset player-related variables
        self.mutex.acquire()
        self.opponent.value = 'Local'
        self.in_game.value = False
        self.current_game.value = 0
        self.mutex.release()



def receive_messages(player):
    # Receive messages from the server and handle them accordingly
    while True:
        msg = player.conn.recv()

        if msg['type'] == 'msg':
            # Print received messages
            print(msg['msg'])
        elif msg['type'] == 'challenge':
            # Add a challenge from another player
            player.add_challenge(msg['challenger'], msg['game'])
        elif msg['type'] == 'acceptance':
            # Handle an acceptance message for a challenge
            print('An acceptance msg has been received, press Intro to enter the game')
            player.start_playing(msg['opponent'], msg['game'])
        elif msg['type'] == 'side':
            # Handle the side and game information for a game
            player.change_side_and_game(msg['info'])
        elif msg['type'] == 'ingame':
            # Handle the updated information for a game
            player.change_update_info(msg['info'])
        elif msg['type'] == 'problem':
            # Handle a problem message from the server
            print('The following problem has been received: ', msg['msg'])
        elif msg['type'] == 'p_accepting':
            # Handle the acceptance status of a match
            player.change_match_status(msg['bool'])



def get_username(conn, client_data):
    # Get the username from the user and send it to the server for validation
    waiting_for_acceptance = True
    while waiting_for_acceptance:
        username = input('Write your username in lowercase if possible. Forbidden Usernames: "Local"\n')
        username = username.replace(" ", "_")
        usernmae = username.lower()
        client_data['username'] = username
        conn.send(client_data)
        passing = conn.recv()
        if passing:
            # The username is accepted
            waiting_for_acceptance = False
            print(f'This is your new username: {username}')
        else:
            # The username is not accepted
            print('Incorrect Username')
    
    return username



def client(server_address, client_data):
    # Main client function
    print('Trying to connect...')
    with Client(address=(server_address, 6000), authkey=b'secret password server') as conn:
        cl = Process(target=client_listener, args=(client_data,))
        cl.start()
        delay()
        username = get_username(conn, client_data)
        m = Manager()
        player = General(m, conn)
        
        inbox_process = Process(target=receive_messages, args=(player,))
        inbox_process.start()

        while player.connected.value:
            if not player.in_game.value:
                # Handle the client when not in a game
                handle_not_in_game(conn, player)
            else:
                # Handle the client when in a game
                handle_in_game(conn, player)
    
        cl.join()
    print('End client')
    conn.close()



def handle_not_in_game(conn, player):
    # Handle the client when not in a game

    if not player.is_playing():
        delay(2)
        print('Write your command:')
        msg = input('>')
        msg_final = msg.lower()
        if msg_final == 'info':
            # Display information about available commands
            info()
        elif msg_final == 'inbox':
            # Display challenges received by the player and handle them
            print('Entering inbox')
            challenges = player.return_challenges()
            for challenger, games_challenged in list(challenges.items()):
                for g in games_challenged:
                    print(f'{challenger} has challenged you to play {g}, press y to accept and n to refuse')
                    msg = input('>')
                    if msg == 'y':
                        player.accept_challenge(challenger, g)
                        print('Challenge accepted')
                        
                        if player.is_playing:
                            print('Press Intro to access the game')
                            break
                        else:
                            print('Acceptance failed')
                    elif msg == 'n':
                        player.refuse_challenge(challenger, g)
            print('You have no more new challenges')
        else:
            # Send the command to the server
            conn.send(msg_final)
        player.connected.value = msg_final != 'quit'



def handle_in_game(conn, player):
    # Handle the client when in a game
    game = games[player.current_game.value]
    conn.send({'type': 'ready', 'opponent': player.opponent.value, 'game': player.current_game.value})
    side, gameinfo = player.side_and_game_info()
    print(f"I am playing {SIDESSTR[side]}")
    game.update(gameinfo)
    Display = 'Display' + str(player.current_game.value)
    Display = globals()[Display]
    display = Display(game)
    while game.is_running():
        try:
            events = display.analyze_events(side, game)
            for ev in events:
                conn.send(ev)
                if ev == 'quit':
                    game.stop()
            conn.send("next")
            gameinfo = player.update_info()
            game.update(gameinfo)
            display.refresh()
            display.tick()
        except:
            game.stop()
    player.reset()



if __name__ == '__main__':
    server_address = '127.0.0.1'
    client_address = '127.0.0.1'
    client_port = randint(49152, 65535)

    if len(sys.argv) > 1:
        client_port = int(sys.argv[1])
    if len(sys.argv) > 2:
        client_address = sys.argv[2]
    if len(sys.argv) > 3:
        server_address = sys.argv[3]
    client_data = {
        'client_address': client_address,
        'client_port': client_port,
        'client_authkey': b'secret client server'
    }
    client(server_address, client_data)

