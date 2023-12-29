# Chat_Games
Run server.py first and then as many clients as you want (running client.py)
# server.py
The server.py script is designed to handle a multiplayer gaming server. It includes necessary classes and functions to handle connected players, manage game interactions, and coordinate game requests and responses. This README file provides a detailed explanation of the various functions and classes within the script.

# Functions
- send_msg_all(username, msg, playerbase): This function sends a message from a user to all other users in the playerbase.
- send_msg_private(username, msg, opponent, playerbase): This function sends a private message from one user to a specified opponent.
- handle_client_in_game(username, conn, playerbase): This function handles a client who is currently in a game. It carries out game-specific actions based on commands from the user, and updates the game state and user status accordingly.
- handle_client_not_in_game(username, conn, playerbase): This function handles a client who is not currently in a game. It processes non-game related commands from the user.
- handle_client(username, conn, playerbase): This function manages client connections, depending on whether the user is in a game or not. It also cleans up the playerbase when a client connection is closed.
- sign_in(conn, playerbase): This function manages the sign-in process for a new client. It adds the new player to the playerbase and starts a new process to handle the client's connection.
- process_input(username, msg, conn, playerbase): This function manages the processing of manages, using the playerbase class for those actions where syncronization is required

# Classes
# Playerbase:
The Playerbase class is designed to manage all the players currently connected to the server. It stores details of each player and provides various methods to manage the players. 

- __init__(self, manager): This constructor initializes the player base.
- add(self, username, connection, client_address, client_port, client_authkey): Adds a new player to the player base.
- remove(self, username): Removes a player from the player base.
- remove_game_request(self, username, challenger, game): Removes a game request made to a player.
- is_playing(self, username): Checks if a player is currently in a game.
- requests(self, username): Retrieves all game requests for a player.
- challenge(self, username, challenged, game): Issues a game challenge to another player.
- acceptance(self, username, challenger, game): Manages the acceptance of a game challenge.
- waiting_ready(self, username1, username2, game): Manages the waiting process for both players to be ready.
- start_game(self, username1, username2, game_id): Starts a game between two players.
- reset(self, username): Resets a player's game status after they finish a game.

# Dictionaries
Game Dictionary (games)
The games dictionary stores the instances of games that can be played. The keys of this dictionary are integers representing the game ID, and the values are instances of the respective game classes. This dictionary is utilized to manage and coordinate the games being played by players on the server.

# client.py
The client.py script is responsible for all client-side activities, ranging from communicating with the server, receiving and handling messages from the server, to processing player input and managing game states.

Here's a brief summary of the major components in this script:

# Functions:

- delay(factor = 3) : introduces a random delay with a default factor of 3.
- info(): prints out basic commands and information for the client.
- client_listener(client_data): starts a listener to receive incoming messages.
- receive_messages(player): handles receiving messages from the server, adjusting player state accordingly.
- get_username(conn, client_data): prompts the user for a username and sends it to the server for validation.
- handle_not_in_game(conn, player): processes player commands when not in a game.
- handle_in_game(conn, player): manages the client during gameplay.
- client(server_address, client_data): Manages the creation of a Client and initializes the listener and the operating loop.

# Classes:
# General:
The General class is designed to manage a client's interaction with the game server. It maintains the state of a client's game progress, manages challenges from other players, and coordinates communication between the client and the server.

- __init__(self, manager, conn): This constructor initializes the General class with shared variables and synchronization primitives. This includes flags to indicate the client's connection status and game progress, dictionaries to store challenges and updated information, and several mutexes and condition variables for synchronization.
- add_challenge(self, challenger, game): This method adds a challenge from a challenger for a specific game to the challenges dictionary.
- remove_challenge(self, challenger, game): This method removes a challenge from the challenges dictionary.
- accept_challenge(self, challenger, game): This method allows a player to accept a challenge from a challenger for a specific game.
- refuse_challenge(self, challenger, game): This method allows a player to refuse a challenge from a challenger for a specific game.
- start_playing(self, challenger, game): This method sets the player to be in a game and updates relevant game information.
- is_playing(self): This method checks if the player is currently in a game.
- return_challenges(self): This method retrieves the challenges dictionary.
- change_match_status(self, b): This method changes the match status and notifies waiting threads.
- change_side_and_game(self, information): This method changes the side and game information and notifies waiting threads.
- change_update_info(self, information): This method changes the updated information and notifies waiting threads.
- side_and_game_info(self): This method retrieves the side and game information.
- update_info(self): This method retrieves the updated information.
- reset(self): This method resets player-related variables.

# Games dictionary:

- games = {1: Game1(), 2:Game2()}: The games dictionary stores the instances of games that can be played. The keys of this dictionary are integers representing the game ID, and the values are instances of the respective game classes. This dictionary is utilized to manage and coordinate the games being played by players on the server.

In general, this script primarily focuses on setting up the client-server connection, processing incoming messages from the server, and handling both user input and gameplay mechanics. The main goal is to provide an interactive and robust multiplayer gaming experience.
