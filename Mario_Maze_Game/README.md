# roomMarioBowser

This code sets up a multiplayer game with two players, manages their positions, scores, and
lives, and provides communication between the main process and player processes using
multiprocessing and inter-process communication.

1. Player class:

    • The Player class represents a player in the game. Each player has a side (left or
    right) and a position on the game board.
    
    • The __init__ method initializes the player's side and sets the initial position
    based on the side.
    
    • The get_pos method returns the current position of the player.
    
    • The get_side method returns the side of the player.
    
    • The moveDown, moveUp, moveRight, and moveLeft methods update the
    player's position by moving it in the respective direction.
    
    • The reset method resets the player's position to its initial position based on
    the side.

2. Game class:

    • The Game class represents the game itself. It manages the players, their
    scores, lives, and the game state.
    
    • The __init__ method initializes the game by creating two players, setting the
    initial score and lives, and managing the game state with a running flag and a
    lock for synchronization.
    
    • The get_player method returns the player object for the specified side.
    
    • The get_score method returns a list of the current scores for both players.
    
    • The is_running method checks whether the game is still running based on the
    running flag.
    
    • The finish method checks if any player has reached a score of 5 or has lost the
    3 lives because has collied with the maze three times. If so, it sets the running
    flag to 0 (indicating the game is finished).
    
    • The stop method sets the running flag to 0, stopping the game.
    
    • The moveUp, moveDown, moveRight, and moveLeft methods update the
    position of the player specified by the argument.
    
    • The get_info method returns a dictionary containing information about the
    game state, including the positions, scores, lives, and the running status.
    
    • The player_collide_star method is called when a player collides with a star. It
    increments the score for the corresponding player, resets their position, and
    updates the player object.

    • The player_collide_wall method is called when a player collides with a wall. It
    decrements the lives for the corresponding player, resets their position, and
    updates the player object.

3. player function:

    • The player function represents the logic for a player process. It receives
    commands from the main process through a connection and updates the
    game state accordingly.
    
    • It starts by sending the player's side and the initial game state to the main
    process through the connection.
    
    • Inside the main loop, it receives commands from the main process and
    executes the corresponding game methods based on the received command.
    
    • The loop continues until the received command is "next," which indicates that
    the player should wait for the next command.
    
    • After each command execution, it checks if the game should finish based on
    the score and sends the updated game state back to the main process through
    the connection.
    
    • If any exception occurs during the execution of the player process, it prints the
    traceback and closes the connection.
    
    • Finally, it prints a message indicating the end of the game.

4. main function:
    • The main function is the entry point of the script. It sets up a listener to accept
    incoming connections from players.
    
    • It creates a Manager object for managing shared data between processes.
    
    • It enters a loop to accept connections from players in pairs. When two players
    have connected, it starts a new game by creating a Game object and two
    player processes.
    
    • The player processes are started as separate processes using the Process class
    from the multiprocessing module.
    
    • The function player is called for each player process, passing the player's side,
    the connection object, and the game object.
    
    • If an exception occurs during the execution of the main process, it prints the
    traceback.
    
    • The script can be run with an optional IP address argument. If no argument is
    provided, the default IP address is "127.0.0.1".

# playerMarioBowser

This code sets up a game using the Pygame library, handles player input and events, updates
the game state, and displays the game graphics and information on the screen.

1. maze(): This function defines the positions of walls in the game maze and returns a list
of wall positions.

2. Player class: It represents a player in the game. Each player has a side (left or right)
and a position in the game maze.
    • get_pos(): Returns the position of the player.
    • get_side(): Returns the side of the player.
    • set_pos(): Sets the position of the player.

3. Game class: It represents the game state and contains information about the players,
score, lives, and running state of the game.

    • get_player(): Returns the player object for a given side.
    
    • set_pos_player(): Sets the position of a player.
    
    • get_score(): Returns the score of the game.
    
    • get_lives(): Returns the remaining lives of the players.
    
    • set_score(): Sets the score of the game.
    
    • set_lives(): Sets the remaining lives of the players.
    
    • update(): Updates the game state with new information from the server.
    
    • is_running(): Returns the running state of the game.
    
    • stop(): Stops the game.

4. PlayerSprite class: It represents a player's sprite in the game and inherits from the
pygame.sprite.Sprite class.

    • __init__(): Initializes the sprite with the corresponding image based on the
player's side.

    • update(): Updates the position of the sprite based on the player's position.

5. WallSprite class: It represents a wall sprite in the game and also inherits from the
pygame.sprite.Sprite class.

    • __init__(): Initializes the sprite with the wall image at the specified position.

6. StarSprite class: It represents a star sprite in the game and inherits from the
pygame.sprite.Sprite class.

   • __init__(): Initializes the sprite with the star image at the specified position.

7. Display class: It handles the game display, including the initialization of pygame,
loading images, refreshing the display, and handling events.

    • __init__(self, game): The constructor initializes the Display object. It takes a
    game parameter, which is an instance of the Game class. It initializes various
    attributes such as sprites, screen, clock, and images used for rendering.
    
    • analyze_events(self, side, game): This method analyzes the events (user
    input) that occur during the game. It takes the side parameter to determine
    which player's events to analyze and the game parameter for accessing player
    and wall positions. It checks for keyboard events such as key presses and
    collisions between players and walls. It returns a list of events that occurred.
    
    • refresh(self): This method refreshes the game display. It updates the player
    group, blits the background image, displays the score and lives of both players,
    draws all the sprites on the screen, and updates the display.
    
    • game_over(self, side): This method handles the game over scenario when one
    of the players wins. It displays a game over screen with a corresponding
    winner message based on the side parameter. It continuously checks for a quit
    event to exit the game.

8. main function: It establishes a connection with the server, receives game information,
updates the game state, and handles the game display. The script runs in a loop,
sending user events to the server, receiving updated game information, and refreshing
the display. It terminates when the game is no longer running. If an error occurs, it
prints the traceback information. The script can be executed directly, and the IP
address can be passed as a command-line argument.
