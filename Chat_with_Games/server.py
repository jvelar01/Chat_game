from multiprocessing.connection import Listener, Client
from multiprocessing import Manager, Process, Lock, Value, Semaphore

from random import random
from time import sleep
#from mygame import MyGame  # Asumiendo que este es tu juego en pygame
import sys
import traceback
from roomPingPong import Player1, Ball, Game1, DELTA1, SIZE1
from roomMarioBowser import Player2, Game2, DELTA2, SIZE2
    
LEFT_PLAYER = 0
RIGHT_PLAYER = 1
SIDESSTR = ["left", "right"]
SIZE = (700, 525)
X=0
Y=1


def delay(factor = 3):
    sleep(random()/factor)
    

m = Manager()

games = {1 : Game1(m), 2 : Game2(m)}


class Playerbase:
    def __init__(self, manager):
        # Playerbase Initialization
        self.manager = manager
        self.players = manager.dict()
        self.mutex = Lock()
        self.game_requests = manager.dict()
        self.ready = manager.dict()
        self.waiting = Semaphore(0)


    def add(self, username, connection, client_address, client_port, client_authkey):
        # Adds a player to the base
        self.mutex.acquire()
        if username not in self.players:
            self.players[username] = self.manager.dict({
                'username': username,
                'connection': connection,
                'is_playing': False,
                'address': client_address,
                'port': client_port,
                'authkey': client_authkey,
                'side': None,
                'current_game': None
            })
            self.game_requests[username] = self.manager.dict()
            self.mutex.release()
        else:
            self.mutex.release()
            raise ValueError("Username already exists in player base")


    def remove(self, username):
        # Removes a player from the base
        self.mutex.acquire()
        if username in self.players:
            del self.players[username]
            del self.game_requests[username]
            self.mutex.release()
        else:
            self.mutex.release()
            raise ValueError("Username does not exist in player base")


    def remove_game_request(self, username, challenger, game):
        # Remove a game request
        self.mutex.acquire()
        try:
            if len(self.game_requests[username][challenger]) == 1:
                del self.game_requests[username][challenger]
            else:
                challenges = self.game_requests[username][challenger]
                challenges.remove(game)
                self.game_requests[username][challenger] = challenges
        except:
            pass
        self.mutex.release()

    def is_playing(self, username):
        # Check if a player is playing
        return self.players[username]['is_playing']

    def requests(self, username):
        # Fetch all game requests for a player
        self.mutex.acquire()
        player = self.players[username]

        if self.game_requests[username]:
            reply = 'You have the following requests: \n'
            for challenger, game in self.game_requests[username].items():
                reply += f'{challenger} has challenged you to {game}\n'
        else:
            reply = 'You currently do not have any current requests'
        player['connection'].send({'type' : 'msg', 'msg' : reply})
        self.mutex.release()

    def challenge(self, username, challenged, game):
        # Issue a challenge to another player
        self.mutex.acquire()
        try:
            player = self.players[username]
            if challenged not in self.players:
                player['connection'].send({'type' : 'msg', 'msg':f'The player {challenged} does not exist'})
            elif game not in games:
                player['connection'].send({'type' : 'msg', 'msg':f'The game {game} is not valid or does not exist'})
            else:
                opponent = self.players[challenged]
                # Create a challenge message
                msg = {
                    'type': 'challenge',
                    'game': game,
                    'challenger': username
                }
                # Send the challenge to the challenged player
                opponent['connection'].send(msg)
                if username in self.game_requests[challenged]:
                    self.game_requests[challenged][username].append(game)
                else:
                    self.game_requests[challenged][username] = self.manager.list([game])
        except Exception as e:
            traceback.print_exc()
        self.mutex.release()

    def acceptance(self, username, challenger, game):
        # Acceptance of a challenge
        self.mutex.acquire()
        player = self.players[username]
        if challenger in self.game_requests[username]:
            if challenger not in self.players:
                player['connection'].send({'type' : 'p_accepting', 'msg' : f'Challenger {challenger} currently not available', 'bool' : False})
                self.mutex.release()

                self.remove_game_request(username, challenger)
            elif self.is_playing(challenger):
                
                player['connection'].send({'type' : 'p_accepting', 'msg': f'{challenger} is currently playing other game', 'bool' : False})
                self.mutex.release()

            else:
                try:
                    # Accept the challenge
                    self.ready[(username, challenger, int(game))] = 0
                    self.players[challenger]['connection'].send({'type' : 'acceptance', 'msg' : f'Ready to play against {username}', 'opponent' : username, 'game' : game})
                    player['connection'].send({'type' : 'p_accepting', 'msg' : f'Ready to play', 'bool' : True})
                    self.mutex.release()
                    self.remove_game_request(username, challenger, game)
                    
                    # Start the game
                except Exception as e:
                    self.mutex.release()
                    player['connection'].send({'type' : 'p_accepting', 'msg': 'Other type of problem', 'bool' : False})
                    traceback.print_exc()
        else:
            self.mutex.release()
            player['connection'].send({'type' : 'p_accepting', 'msg' :f'You have not received any game request from {challenger}', 'bool' : False})
    
    def waiting_ready(self, username1, username2, game):
        # Waiting for both players to be ready
        self.mutex.acquire()
        game = int(game)
        count = 0
        if (username1, username2, game) in self.ready:
            self.ready[(username1, username2, game)] += 1
            count = self.ready[(username1, username2, game)]
        elif (username2, username1, game) in self.ready:
            self.ready[(username2, username1, game)] += 1
            count = self.ready[(username2, username1, game)]
        
        if count == 2:
            self.mutex.release()
            self.start_game(username1, username2, game)
            self.waiting.release()
        else:
            self.mutex.release()
            self.waiting.acquire()

    def start_game(self, username1, username2, game_id):
        # Start a game between two players
        if self.players[username1]['is_playing'] or self.players[username2]['is_playing']:
            raise Exception("One or both players are already playing a game")
        else:
            try:
                self.players[username1]['current_game'] = game_id
                self.players[username2]['current_game'] = game_id
                self.players[username1]['is_playing'] = True
                self.players[username2]['is_playing'] = True
                self.players[username1]['side'] = 0
                self.players[username2]['side'] = 1

            except Exception as e:
                traceback.print_exc()

    def reset(self, username):
        # Reset a player's game status
        self.players[username]['current_game'] = None
        self.players[username]['is_playing'] = False
        self.players[username]['side'] = None



def send_msg_all(username, msg, playerbase):
    # Iterate through the list of players and send the message
    for recv_username, recv_player_dict in playerbase.players.items():
        with Client(address=(recv_player_dict['address'], recv_player_dict['port']),
                    authkey=recv_player_dict['authkey']) as conn:
            if username == 'Local':
                conn.send(f'{msg}')
            elif recv_username != username:
                conn.send(f'{username}: {msg}')
            else:
                conn.send(f"Message {msg} processed")

def send_msg_private(username, msg, opponent, playerbase):
    # Get the recipient player details
    recv_player_dict = playerbase.players[opponent]
    # Establish a client connection and send the message
    with Client(address=(recv_player_dict['address'], recv_player_dict['port']),
                authkey=recv_player_dict['authkey']) as conn:
        if username == 'Local':
            conn.send(msg)
        else:
            conn.send(f'Private {username}: {msg}')

def process_input(username, msg, conn, playerbase):
    # Process user input received from the client

    if isinstance(msg, str):
        # If the message is a string, parse the command and execute the corresponding action
        msg_parts = msg.split()
        try:
            command = msg_parts[0].lower()
        except IndexError:
            command = ''

        if command == 'players':
            # Command: players
            # Get the list of connected players (excluding the current user) and send it back to the client
            reply = list(playerbase.players.keys())
            reply.remove(username)
            conn.send({'type': 'msg', 'msg': f'The connected players are: {reply}'})

        elif command == 'games':
            # Command: games
            # Get the list of available games and send it back to the client
            reply = ''
            for number, title in list(games.items()):
                reply += f'{number}: {str(title)} \n'
            playerbase.players[username]['connection'].send({'type': 'msg', 'msg': f'The available games are:\n{reply}'})

        elif command == 'challenge':
            # Command: challenge <Player> <Game>
            # Send a game challenge to the specified player
            if len(msg_parts) < 3:
                conn.send({'type': 'msg', 'msg': 'Usage: Challenge <Player> <Game>'})
            else:
                opponent = msg_parts[1]
                if opponent == username:
                    playerbase.players[username]['connection'].send({'type': 'msg', 'msg': 'Not allowed to challenge yourself, change player'})
                else:
                    game = int(msg_parts[2])
                    playerbase.challenge(username, opponent, game)

        elif command == 'private':
            # Command: private <Player> <Message>
            # Send a private message to the specified player
            if len(msg_parts) < 3:
                conn.send({'type': 'msg', 'msg': 'Usage: Private <Player> <Message>'})
            else:
                receiver = msg_parts[1]
                if receiver not in playerbase.players:
                    conn.send({'type': 'msg', 'msg': f'The player {receiver} does not exist'})
                else:
                    private_msg = ' '.join(msg_parts[2:])
                    send_msg_private(username, private_msg, receiver, playerbase)

        elif command == 'requests':
            # Command: requests
            # Show the pending game requests for the current user
            playerbase.requests(username)

        elif command == 'accept':
            # Command: accept <Challenger> <Game>
            # Accept a game challenge from the specified challenger
            if len(msg_parts) < 3:
                conn.send({'type': 'problem', 'msg': 'You must specify the challenger\'s name and the selected game'})
            else:
                challenger = msg_parts[1]
                game = msg_parts[2]
                playerbase.acceptance(username, challenger, game)

        elif command == 'refuse':
            # Command: refuse <Challenger> <Game>
            # Refuse a game challenge from the specified challenger
            try:
                playerbase.remove_game_request(username, msg_parts[1], msg_parts[2])
            except:
                conn.send({'type': 'msg', 'msg': 'Incorrect challenger username, could not refuse any challenge'})

        elif command == '':
            # Empty command, do nothing
            pass

        else:
            # Command: <PublicMessage>
            # Send a public message to all connected players
            public_msg = ' '.join(msg_parts)
            send_msg_all(username, public_msg, playerbase)
            conn.send({'type': 'msg', 'msg': 'Public message sent correctly'})
    else:
        if msg['type'] == 'ready':
            # Message type: ready
            # Handle the readiness status of the player for a game
            playerbase.waiting_ready(username, msg['opponent'], msg['game'])



def handle_client_in_game(username, conn, playerbase):
    # Get the game information for the current player
    game_id = playerbase.players[username]['current_game']
    game = games[game_id]
    side = playerbase.players[username]['side']

    try:
        print(f"Starting player {SIDESSTR[side]}: {game.get_info()}")
        conn.send({'type': 'side', 'info': (side, game.get_info())})
        
        # Game loop
        while game.is_running():
            command = ""
            while command != "next":
                command = conn.recv()
                if command == "up":
                    game.moveUp(side)
                elif command == "down":
                    game.moveDown(side)
                elif command == "right":
                    game.moveRight(side)
                elif command == "left":
                    game.moveLeft(side)
                elif command == "collide":
                    game.ball_collide(side)
                elif command == "player collide star":
                    game.player_collide_star(side)
                elif command == "player collide wall":
                    game.player_collide_wall(side)
                elif command == "quit":
                    game.stop()
            
            if side == 1 and game_id == 1:
                game.move_ball()
            if game_id == 2:
                game.finish()
            
            information = game.get_info()
            conn.send({'type': 'ingame', 'info': information})
        
        # Game ended
        player = playerbase.players[username]
        player['is_playing'] = False
        playerbase.players[username] = player
    
    except:
        traceback.print_exc()
        game.stop()
        
    
    finally:
        # Reset player status and print game end
        reset_game = 'Game' + str(game_id)
        reset_game = globals()[reset_game]
        games[game_id] = reset_game(Manager())
        playerbase.reset(username)
        print(f"Game ended: {game}")



def handle_client_not_in_game(username, conn, playerbase):
    # Handle the client when they are not in a game
    try:
        msg = conn.recv()
        print(f'Received message: {msg} from {username}')
        if msg == "quit":
            return False
        else:
            process_input(username, msg, conn, playerbase)
    except EOFError:
        print('Connection abruptly closed by client')
        return False

    return True


def handle_client(username, conn, playerbase):
    # Handle the client connection
    connected = True
    while connected:
        print(username, 'playing:', playerbase.is_playing(username))
        if playerbase.is_playing(username):
            print(username, 'in game')
            handle_client_in_game(username, conn, playerbase)
        else:
            connected = handle_client_not_in_game(username, conn, playerbase)

    playerbase.remove(username)
    send_msg_all(username, f"Abandoned the chat", playerbase)
    print(username, 'connection closed')


def sign_in(conn, playerbase):
    # Sign in process for a client connection
    not_accepted = True
    while not_accepted:
        msg = conn.recv()
        username = msg['username']

        # Check if the username is available and not reserved
        if (username not in playerbase.players) and (username != 'Local'):
            not_accepted = False
            print('Username ', username, ' chosen correctly')

        # Send the acceptance status to the client
        conn.send(not not_accepted)
    
    # Add the player to the playerbase
    playerbase.add(username, conn, msg['client_address'], msg['client_port'], msg['client_authkey'])

    try:
        print('Starting handle_client for', username)

        # Create a new process to handle the client's connection
        p = Process(target=handle_client, args=(username, conn, playerbase))
        p.start()

        # Notify all players in the lobby about the new player
        send_msg_all('Local', f"{username} added to the players lobby", playerbase)

    except Exception as e:
        # Remove the player from the playerbase in case of an error
        playerbase.remove(username)
        traceback.print_exc()

def server(ip_address, server_port):
    # Set up the server listener
    with Listener(address=(ip_address, server_port),
                  authkey=b'secret password server') as listener:
        playerbase = Playerbase(Manager())  # Create the player database

        while True:
            print("Accepting connections ...")
            try:
                # Accept a new client connection
                conn = listener.accept()
                pid = listener.last_accepted
                print(f"{pid} connected")

                # Create a new process to handle the client's sign-in process and connection
                p = Process(target=sign_in, args=(conn, playerbase))
                p.start()
            except Exception as e:
                traceback.print_exc()


if __name__ == "__main__":
    ip_address = "127.0.0.1"
    server_port = 6000

    # Read the command-line arguments for IP address and server port, if provided
    if len(sys.argv) > 1:
        ip_address = sys.argv[1]
    if len(sys.argv) > 2:
        server_port = sys.argv[2]

    # Start the server
    server(ip_address, server_port)

        
        
