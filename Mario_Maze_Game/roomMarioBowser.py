from multiprocessing.connection import Listener
from multiprocessing import Process, Manager, Value, Lock
import traceback
import sys
from random import random
from time import sleep

LEFT_PLAYER = 0
RIGHT_PLAYER = 1
SIDESSTR = ["left", "right"]
SIZE = (1020, 780)
X=0
Y=1
DELTA = 30

# Clase Player que utilizaremos para representar la posición de cada jugador
# y para movernos en cada dirección
class Player():
    def __init__(self, side):
        self.side = side
        if side == LEFT_PLAYER:
            self.pos = [30, SIZE[Y]//2]
        else:
            self.pos = [SIZE[X] - 30, SIZE[Y]//2]
    
    def get_pos(self):
        return self.pos

    def get_side(self):
        return self.side

    def moveDown(self):
        self.pos[Y] += DELTA
        if self.pos[Y] > SIZE[Y]:
            self.pos[Y] = SIZE[Y]

    def moveUp(self):
        self.pos[Y] -= DELTA
        if self.pos[Y] < 0:
            self.pos[Y] = 0
    
    def moveRight(self):
        self.pos[X] += DELTA
        if self.pos[X] > SIZE[X]:
            self.pos[X] = SIZE[X]
            
    def moveLeft(self):
        self.pos[X] -= DELTA
        if self.pos[X] < 0:
            self.pos[X] = 0
    
    # Cuando un jugador alcanza el tesoro entonces vuelve a su posición inicial 
    def reset(self):
        if self.side == LEFT_PLAYER:
            self.pos = [30, SIZE[Y]//2]
        else:
            self.pos = [SIZE[X] - 30, SIZE[Y]//2]

    def __str__(self):
        return f"P<{SIDESSTR[self.side]}, {self.pos}>"
    

class Game():
    def __init__(self, manager):
        self.players = manager.list([Player(LEFT_PLAYER),Player(RIGHT_PLAYER)])
        self.score = manager.list( [0,0] )
        self.lives = manager.list( [3,3] )
        self.running = Value('i', 1) # 1 running
        self.lock = Lock()
        
    def get_player(self, side):
        return self.players[side]
    
    def get_score(self):
        return list(self.score)
    
    def get_lives(self):
        return list(self.lives)
    
    def is_running(self):
        return self.running.value == 1
    
    # Con la función finish comprobamos si algún jugador llega a 5 puntos,
    # en tal caso se termina el juego
    def finish(self):
        score = self.get_score()
        lives = self.get_lives()
        if score[0] == 5 or score[1] == 5 or lives[0] == 0 or lives[1] == 0:
            sleep(random()/3)
            self.running.value = 0
    
    def stop(self):
        self.running.value = 0

    def moveUp(self, player):
        self.lock.acquire()
        p = self.players[player]
        p.moveUp()
        self.players[player] = p
        self.lock.release()

    def moveDown(self, player):
        self.lock.acquire()
        p = self.players[player]
        p.moveDown()
        self.players[player] = p
        self.lock.release()
    
    def moveRight(self, player):
        self.lock.acquire()
        p = self.players[player]
        p.moveRight()
        self.players[player] = p
        self.lock.release()
    
    def moveLeft(self, player):
        self.lock.acquire()
        p = self.players[player]
        p.moveLeft()
        self.players[player] = p
        self.lock.release()

    def get_info(self):
        info = {
            'pos_left_player': self.players[LEFT_PLAYER].get_pos(),
            'pos_right_player': self.players[RIGHT_PLAYER].get_pos(),
            'score': list(self.score),
            'lives': list(self.lives),
            'is_running': self.running.value == 1
        }
        return info
    
    # Cuando un jugador colisiona con la estrella, suma un punto en el marcador
    # y vuelve a su posición inicial
    def player_collide_star(self,player):
        self.lock.acquire()
        p = self.players[player]
        if player == LEFT_PLAYER:
            self.score[0] +=1
        elif player == RIGHT_PLAYER:
            self.score[1] +=1
        p.reset()
        self.players[player] = p
        self.lock.release()
        
    # Cuando un jugador colisiona con alguna pared, pierde una vida
    # y vuelve a su posición inicial
    def player_collide_wall(self,player):
        self.lock.acquire()
        p = self.players[player]
        if player == LEFT_PLAYER:
            self.lives[0] -=1
        elif player == RIGHT_PLAYER:
            self.lives[1] -=1
        p.reset()
        self.players[player] = p
        self.lock.release()

    def __str__(self):
        return f"G<{self.players[RIGHT_PLAYER]}:{self.players[LEFT_PLAYER]}:{self.running.value}>"


def player(side, conn, game):
    try:
        print(f"starting player {SIDESSTR[side]}:{game.get_info()}")
        conn.send( (side, game.get_info()) )
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
                elif command == "player collide star":
                    game.player_collide_star(side)
                elif command == "player collide wall":
                    game.player_collide_wall(side)
                elif command == "quit":
                    game.stop()

            game.finish()
            conn.send(game.get_info())
    except:
        traceback.print_exc()
        conn.close()
    finally:
        print(f"Game ended {game}")


def main(ip_address):
    manager = Manager()
    try:
        with Listener((ip_address, 6000),
                      authkey=b'secret password') as listener:
            n_player = 0
            players = [None, None]
            game = Game(manager)
            while True:
                print(f"accepting connection {n_player}")
                conn = listener.accept()
                players[n_player] = Process(target=player,
                                            args=(n_player, conn, game))
                n_player += 1
                if n_player == 2:
                    players[0].start()
                    players[1].start()
                    n_player = 0
                    players = [None, None]
                    game = Game(manager)

    except Exception as e:
        traceback.print_exc()

if __name__=='__main__':
    ip_address = "127.0.0.1"
    if len(sys.argv)>1:
        ip_address = sys.argv[1]

    main(ip_address)
