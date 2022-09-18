import pygame, sys
from enum import Enum
from pygame.locals import *
import random
from pickle import NONE
 
pygame.init()
 
FPS = 60  # not used
GameClock = pygame.time.Clock()
 
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
 
# Screen information
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600

Gravity = 1000.0 / 1000000
 
DisplaySurface = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
DisplaySurface.fill(WHITE)
pygame.display.set_caption("Game")

KeyMatrix = dict()
nowTicks = pygame.time.get_ticks();


class Vector:
    
    def __init__(self, x, y):
            self.x, self.y = x, y

    def dot(self, other):
        """The scalar (dot) product of self and other. Both must be vectors."""

        if not isinstance(other, Vector):
            raise TypeError('Can only take dot product of two Vector objects')
        return self.x * other.x + self.y * other.y

    # Alias the __matmul__ method to dot so we can use a @ b as well as a.dot(b).
    __matmul__ = dot

    def __sub__(self, other):
        """Vector subtraction."""
        return Vector(self.x - other.x, self.y - other.y)

    def __add__(self, other):
        """Vector addition."""
        if isinstance(other, Point):
            return Point(self.x + other.x, self.y + other.y)
        return Vector(self.x + other.x, self.y + other.y)

    def __mul__(self, scalar):
        """Multiplication of a vector by a scalar."""

        if isinstance(scalar, int) or isinstance(scalar, float):
            return Vector(self.x * scalar, self.y * scalar)
        raise TypeError('Can only multiply Vector by a scalar')

    def __rmul__(self, scalar):
        """Reflected multiplication so vector * scalar also works."""
        return self.__mul__(scalar)

    def __neg__(self):
        """Negation of the vector (invert through origin.)"""
        return Vector(-self.x, -self.y)

    def __truediv__(self, scalar):
        """True division of the vector by a scalar."""
        return Vector(self.x / scalar, self.y / scalar)

    
class Point:
    
    def __init__(self, x, y):
        self.x, self.y = x, y

    def __sub__(self, other):
        if isinstance(other, Point):
            return Vector(self.x - other.x, self.y - other.y)
        if isinstance(other, Vector):
            return Point(self.x - other.x, self.y - other.y)
        raise TypeError('Can only subtract Vector or Point')

    def __add__(self, other):
        """Vector addition."""
        if isinstance(other, Vector):
            return Point(self.x + other.x, self.y + other.y)
        raise TypeError('Can only add Vector')
    
 
class Enemy(pygame.sprite.Sprite):

    def __init__(self):
        super().__init__() 
        self.image = pygame.image.load("Enemy.png")
        self.rect = self.image.get_rect()
        self.rect.center = (random.randint(40, SCREEN_WIDTH - 40), 0) 
 
    def move(self):
        self.rect.move_ip(0, 10)
        if (self.rect.bottom > 600):
            self.rect.top = 0
            self.rect.center = (random.randint(30, 370), 0)
 
    def draw(self, surface):
        surface.blit(self.image, self.rect) 
 
 
class Player(pygame.sprite.Sprite):
    
    MOVE_NONE = 0
    MOVE_RUN = 1
    MOVE_JUMP = 2

    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("Player.png")
        self.rect = self.image.get_rect()
        self.position = Point (SCREEN_WIDTH / 2, SCREEN_HEIGHT - self.image.get_size()[1]);
        self.acceleration = 1.0000000005 / 1000000
        self.jumpVelocity = 500.0 / 1000
        self.deceleration = self.acceleration * 3
        self.maxSpeed = 5.0;
        self.groundLevel = self.position.y
        self.movementType = Player.MOVE_NONE
        self.currentHVelocity = 0.0
        self.currentVVelocity = 0.0
        self.rect.center = (self.position.x, self.position.y)
 
    def update(self):
        if (pygame.K_LEFT in KeyMatrix or pygame.K_RIGHT in KeyMatrix): # and self.position.y == self.groundLevel:
            if pygame.K_LEFT in KeyMatrix:
                self.directionH = -1 
                self.moveHStart = KeyMatrix[pygame.K_LEFT]
                if pygame.K_RIGHT in KeyMatrix:
                    KeyMatrix[pygame.K_RIGHT] = nowTicks
            else:
                self.directionH = 1 
                self.moveHStart = KeyMatrix[pygame.K_RIGHT]
            self.movementType |= Player.MOVE_RUN
        else:
            if self.movementType & Player.MOVE_RUN:
                self.moveHStop = nowTicks
            self.movementType &= ~Player.MOVE_RUN

        if pygame.K_SPACE in KeyMatrix and self.position.y == self.groundLevel:
            self.moveVStart = KeyMatrix[pygame.K_SPACE]
            self.movementType |= Player.MOVE_JUMP

        if self.movementType & Player.MOVE_RUN:
            self.currentHVelocity = self.acceleration * (nowTicks - self.moveHStart);
        else:
            if self.currentHVelocity > 0:
                self.currentHVelocity -= self.deceleration * (nowTicks - self.moveHStop)
                if self.currentHVelocity < 0:
                    self.currentHVelocity = 0
        if self.currentHVelocity > 0:
            if self.currentHVelocity > self.maxSpeed:
                self.currentHVelocity = self.maxSpeed
            x_move = self.currentHVelocity * (nowTicks - self.moveHStart);
            self.position.x += self.directionH * x_move
        if self.position.x > SCREEN_WIDTH:
            self.position.x = SCREEN_WIDTH
            self.currentHVelocity = 0
        if self.position.x < 0:
            self.position.x = 0
            self.currentHVelocity = 0
            
        if self.movementType & Player.MOVE_JUMP:
            tJump = nowTicks - self.moveVStart
            self.currentVVelocity = self.jumpVelocity - Gravity * tJump;
            self.position.y = self.groundLevel - self.jumpVelocity * tJump + Gravity / 2 * tJump * tJump
            if self.position.y > self.groundLevel:
                self.position.y = self.groundLevel
                self.movementType &= ~Player.MOVE_JUMP
        self.rect.center = (int(self.position.x), int(self.position.y))

    def draw(self, surface):
        surface.blit(self.image, self.rect)

 
player = Player()
E1 = Enemy()
 
while True: 
    nowTicks = pygame.time.get_ticks();
    for event in pygame.event.get(): 
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key not in KeyMatrix:
                KeyMatrix[event.key] = nowTicks 
        if event.type == pygame.KEYUP:
            if event.key in KeyMatrix:
                del KeyMatrix[event.key]
                
    player.update()
     
    DisplaySurface.fill(WHITE)
    player.draw(DisplaySurface)
         
    pygame.display.update()
    GameClock.tick()
