from multiprocessing.connection import Client
import traceback
import pygame
import sys, os
import pygame.mixer


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

# Importante: DELTA tiene que tener el mismo valor que el de myRoom
DELTA = 30
SIZE = (34*DELTA, 26*DELTA)
WALL_HEIGTH = DELTA
WALL_WIDTH = DELTA
PLAYER_HEIGTH = 60
PLAYER_WIDTH = 45
STAR_HEIGTH = 90
STAR_WIDTH = 90 

FPS = 60

SIDES = ["left", "right"]
SIDESSTR = ["left", "right"]

# Dibujamos el laberinto
def maze():
    WALLS_POSITIONS = []
    for i in range(6):
        WALLS_POSITIONS.append( (i*DELTA, 4*DELTA) )
    for i in range (14):
        WALLS_POSITIONS.append( (31*DELTA, (4+i)*DELTA) ) #recta vertical
    for i in range(7):
        WALLS_POSITIONS.append( (31*DELTA, (22+i)*DELTA) )
    for i in range (20):
        WALLS_POSITIONS.append( (3*DELTA, (4+i)*DELTA) ) #recta vertical 
    for i in range (10):
        WALLS_POSITIONS.append( (6*DELTA, i*DELTA) ) #recta vertical 
    for i in range (10):
        WALLS_POSITIONS.append( (6*DELTA, (12+i)*DELTA) ) #recta vertical
    for i in range (3):
        WALLS_POSITIONS.append( (6*DELTA, (24+i)*DELTA) ) #recta vertical
    for i in range (23):
        WALLS_POSITIONS.append( ((6+i)*DELTA, 18*DELTA) ) #recta horizontal   
    for i in range (15):
        WALLS_POSITIONS.append( (28*DELTA, i*DELTA) ) #recta vertical dere
    for i in range(7):
        WALLS_POSITIONS.append( ((28+i)*DELTA, 4*DELTA) )
    for i in range (6):
        WALLS_POSITIONS.append( (9*DELTA, (19+i)*DELTA) ) #recta vertical izq
    for i in range (6):
        WALLS_POSITIONS.append( (13*DELTA, (21+i)*DELTA) ) #recta vertical izq
    for i in range (10):
        WALLS_POSITIONS.append( ((28-i)*DELTA, 21*DELTA) ) #recta horizontal 
    for i in range (2):
        WALLS_POSITIONS.append( (22*DELTA, (26-i)*DELTA) ) #recta vertical dere   
    for i in range (2):
        WALLS_POSITIONS.append( (16*DELTA, (19+i)*DELTA) ) #recta vertical der
    for i in range (3):
        WALLS_POSITIONS.append( (26*DELTA, (22+i)*DELTA) ) #recta vertical der  
    for i in range (15):
        WALLS_POSITIONS.append( ((28-i)*DELTA, 6*DELTA) ) #recta horizontal   
    for i in range (15):
        WALLS_POSITIONS.append( (10*DELTA, (4+i)*DELTA) ) #recta 
    for i in range (15):
        WALLS_POSITIONS.append( ((10+i)*DELTA, 3*DELTA) ) #recta horizontal 
    for i in range (11):
        WALLS_POSITIONS.append( ((14+i)*DELTA, 9*DELTA) ) #recta horizontal 
    for i in range (6):
        WALLS_POSITIONS.append( (14*DELTA, (10+i)*DELTA) ) #recta       
    for i in range (6):
        WALLS_POSITIONS.append((21*DELTA, (12+i)*DELTA)) #recta        
    WALLS_POSITIONS.append( (24*DELTA, 14*DELTA) ) #bloque
    WALLS_POSITIONS.append( (25*DELTA, 14*DELTA) ) #bloque
    
    return WALLS_POSITIONS
    
WALLS_POSITIONS = maze()


class Player():
    def __init__(self, side):
        self.side = side
        self.pos = [None, None]
        
    def get_pos(self):
        return self.pos

    def get_side(self):
        return self.side

    def set_pos(self, pos):
        self.pos = pos
    
    def __str__(self):
        return f"P<{SIDES[self.side], self.pos}>"
    

class Game():
    def __init__(self):
        self.players = [Player(i) for i in range(2)]
        self.score = [0,0]
        self.lives = [3,3]
        self.running = True

    def get_player(self, side):
        return self.players[side]

    def set_pos_player(self, side, pos):
        self.players[side].set_pos(pos)

    def get_score(self):
        return self.score
    
    def get_lives(self):
        return self.lives

    def set_score(self, score):
        self.score = score
    
    def set_lives(self, lives):
        self.lives = lives

    def update(self, gameinfo):
        self.set_pos_player(LEFT_PLAYER, gameinfo['pos_left_player'])
        self.set_pos_player(RIGHT_PLAYER, gameinfo['pos_right_player'])
        self.set_score(gameinfo['score'])
        self.set_lives(gameinfo['lives'])
        self.running = gameinfo['is_running']

    def is_running(self):
        return self.running

    def stop(self):
        self.running = False

    def __str__(self):
        return f"G<{self.players[RIGHT_PLAYER]}:{self.players[LEFT_PLAYER]}>"


class PlayerSprite(pygame.sprite.Sprite):
    def __init__(self,player):
        super().__init__()
        self.player = player
        if self.player.get_side() == RIGHT_PLAYER:
            self.image = pygame.image.load('bowser.png')
        else:
            self.image = pygame.image.load('mario.png')
        self.image.set_colorkey(WHITE)
        self.image.set_colorkey(GRAY)
        self.image = pygame.transform.scale(self.image,(PLAYER_WIDTH,
                                                        PLAYER_HEIGTH))
        self.rect = self.image.get_rect()
        self.update()
    
    def update(self):
        pos = self.player.get_pos()
        self.rect.centerx, self.rect.centery = pos

    def __str__(self):
        return f"S<{self.player}>"


class WallSprite(pygame.sprite.Sprite):
    def __init__(self, pos): 
        super().__init__()
        self.image = pygame.image.load('wall_image.png')
        self.image.set_colorkey(WHITE)
        self.image = pygame.transform.scale(self.image,(WALL_WIDTH,
                                                        WALL_HEIGTH))
        self.rect = self.image.get_rect()
        self.rect.center = pos


class StarSprite(pygame.sprite.Sprite):
    def __init__(self,pos):
        super().__init__()
        self.image = pygame.image.load('star.png')
        self.image.set_colorkey(WHITE)
        self.image.set_colorkey(GRAY)
        self.image = pygame.transform.scale(self.image,(STAR_WIDTH,
                                                        STAR_HEIGTH))
        self.rect = self.image.get_rect()
        self.rect.center = pos


class Display():
    def __init__(self, game):
        self.game = game
        
        # Se agrupan los sprites
        self.walls = [WallSprite(pos) for pos in WALLS_POSITIONS]
        self.players = [PlayerSprite(self.game.get_player(i)) for i in range(2)]
        self.star = StarSprite( (SIZE[X]//2, SIZE[Y]//2) )
        self.all_sprites = pygame.sprite.Group()
        self.player_group = pygame.sprite.Group()
        for player in self.players:
            self.all_sprites.add(player)
            self.player_group.add(player)
        for wall in self.walls:
            self.all_sprites.add(wall)
        self.all_sprites.add(self.star)
        
        # Se cargan las imagenes que se usan en refresh
        self.screen = pygame.display.set_mode(SIZE)
        self.clock =  pygame.time.Clock()  #FPS
        self.background = pygame.image.load('background.png')
        self.background = pygame.transform.scale(self.background, SIZE)
        self.heart = pygame.image.load('heart.png')
        self.heart = pygame.transform.scale(self.heart, (90,70))
        self.toad = pygame.image.load('toad.png')
        self.toad = pygame.transform.scale(self.toad, (60,70))
        self.mario_winner = pygame.image.load('mario_winner.png')
        self.mario_winner = pygame.transform.scale(self.mario_winner,(SIZE))
        self.bowser_winner = pygame.image.load('bowser_winner.png')
        self.bowser_winner = pygame.transform.scale(self.bowser_winner,(SIZE))
        
        pygame.init()
        pygame.mixer.init()
        pygame.mixer.music.load("music.mp3")
        pygame.mixer.music.play(loops=-1)


    # Comprobamos si un jugador colisiona con alguna pared cuando realiza un 
    # movimiento, en ese caso no enviamos al servidor del juego el comando que
    # ejecuta dicho movimiento
    # Para comprobar si hay colisión entre una pared y un jugador comparamos
    # el centro de dicha pared y el centro del jugador.
    # La variable global DELTA representa la distancia que avanza un jugador
    # cuando realiza un movimiento.
    # Como la posición del centro de cada pared es múltiplo de DELTA, entonces
    # la comparación está bien definida.
    def analyze_events(self, side, game):
        events = []
        collision = False
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                player = self.game.get_player(side)
                player_pos = player.get_pos()
                if event.key == pygame.K_ESCAPE:
                    events.append("quit")
                
                if event.key == pygame.K_UP:
                    collision = False
                    player_pos_y = player_pos[Y] - DELTA
                    for wall_pos in WALLS_POSITIONS:
                        if (player_pos[X], player_pos_y) == wall_pos:
                            collision = True
                            events.append("player collide wall")
                    if collision == False:
                        events.append("up")
                        
                elif event.key == pygame.K_DOWN:
                    collision = False
                    player_pos_y = player_pos[Y] + DELTA
                    for wall_pos in WALLS_POSITIONS:
                        if (player_pos[X], player_pos_y) == wall_pos:
                            collision = True
                            events.append("player collide wall")
                    if collision == False:
                        events.append("down")
                        
                elif event.key == pygame.K_RIGHT:
                    collision = False
                    player_pos_x = player_pos[X] + DELTA
                    for wall_pos in WALLS_POSITIONS:
                        if (player_pos_x, player_pos[Y]) == wall_pos:
                            collision = True
                            events.append("player collide wall")
                    if collision == False:
                        events.append("right")
                    
                elif event.key == pygame.K_LEFT:
                    collision = False
                    player_pos_x = player_pos[X] - DELTA
                    for wall_pos in WALLS_POSITIONS:
                        if (player_pos_x, player_pos[Y]) == wall_pos:
                            collision = True
                            events.append("player collide wall")
                    if collision == False:
                        events.append("left")
                        
            elif event.type == pygame.QUIT:
                events.append("quit")

        if pygame.sprite.collide_rect(self.star, self.players[side]):
            events.append("player collide star")

        return events

    # Con la siguiente función representamos por pantalla la nueva información
    # de ambos jugadores recibida a través del servidor del juego
    def refresh(self):
        self.player_group.update()
        self.screen.blit(self.background, (0, 0))
        score = self.game.get_score()
        lives = self.game.get_lives()
        font = pygame.font.Font(None,50)
        
        self.screen.blit(self.heart, (0,5))
        self.screen.blit(self.heart, (SIZE[X]-85,5))
        text = font.render(f"{lives[LEFT_PLAYER]}", 1, WHITE)
        self.screen.blit(text, (35,25))
        text = font.render(f"{lives[RIGHT_PLAYER]}", 1, WHITE)
        self.screen.blit(text, (SIZE[X]-50, 25))
        
        self.screen.blit(self.toad, (85,5))
        self.screen.blit(self.toad, (SIZE[X]-150,5))
        text = font.render(f"{score[LEFT_PLAYER]}", 1, BLACK)
        self.screen.blit(text, (105, 10))
        text = font.render(f"{score[RIGHT_PLAYER]}", 1, BLACK)
        self.screen.blit(text, (SIZE[X]-130, 10))
        
        self.all_sprites.draw(self.screen)
        pygame.display.flip()
        
        # Si un jugador gana, o el otro pierde, entonces aparece la pantalla
        # del jugador ganador
        if score[0] == 5 or lives[1] == 0:
            self.game_over(0)    
        elif score[1] == 5 or lives[0] == 0:
            self.game_over(1)
        
        
    def game_over(self,side):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            if side == LEFT_PLAYER:
            	font1 = pygame.font.Font(None, 75)
            	text1 = font1.render("Game Over", True, WHITE)
            	font2 = pygame.font.Font(None, 75)
            	text2 = font2.render("is the Winner!", True, WHITE)
            	self.screen.blit(self.mario_winner, (0,0))
            	self.screen.blit(text1, (600, 100))
            	self.screen.blit(text2, (600, 600))
            	pygame.display.flip()
            elif side == RIGHT_PLAYER:
            	font = pygame.font.Font(None, 75)
            	text1 = font.render("Game Over", True, BLACK)
            	text2 = font.render("Bowser is the Winner!", True, BLACK)
            	self.screen.blit(self.bowser_winner, (0,0))
            	self.screen.blit(text1, (100, 400))
            	self.screen.blit(text2, (50, 500))
            	pygame.display.flip()
                 
    def tick(self):
        self.clock.tick(FPS)

    @staticmethod
    def quit():
        pygame.quit()


def main(ip_address):
    try:
        with Client((ip_address, 6000), authkey=b'secret password') as conn:
            game = Game()
            side, gameinfo = conn.recv()
            print(f"I am playing {SIDESSTR[side]}")
            game.update(gameinfo)
            display = Display(game)
            while game.is_running():
                events = display.analyze_events(side,game)
                for ev in events:
                    conn.send(ev)
                    if ev == 'quit':
                        game.stop()
                conn.send("next")
                gameinfo = conn.recv()
                game.update(gameinfo)
                display.refresh()
                display.tick()
    except:
        traceback.print_exc()
    finally:
        pygame.quit()


if __name__=="__main__":
    ip_address = "127.0.0.1"
    if len(sys.argv)>1:
        ip_address = sys.argv[1]
    main(ip_address)
