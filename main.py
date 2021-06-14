import pygame
import random
from pygame.locals import *
from pygame.scrap import lost

pygame.init()
screen_width = 500
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Rush Arkanoid")
gameIcon = pygame.image.load("icon.png")
pygame.display.set_icon(gameIcon)
# BG color in RGBA
bg = (17, 17, 27, 0.75)

# bricks colors
copper_brick = (184, 115, 51)
iron_brick = (161, 157, 148)
gold_brick = (212, 175, 55)

# game variables
colums = 6
rows = 6
clock = pygame.time.Clock()
fps = 60
ball_is_live = False
gameover = 0
# font
font = pygame.font.SysFont("Arial Bold", 30)
# paddle variables
paddle_color = (108, 142, 180)
paddle_outline = (61, 12, 2)

# ball variables
ball_color = (123, 126, 115)
ball_outline = (233, 235, 226)
wall_bounce_sounds = [
    pygame.mixer.Sound("sounds/bounce1.wav"),
    pygame.mixer.Sound("sounds/bounce2.wav"),
    pygame.mixer.Sound("sounds/bounce3.wav"),
]

# Music and sounds loading
paddle_bounce_sound = pygame.mixer.Sound("sounds/paddlebounce1.wav")
brick_bounce_sound = pygame.mixer.Sound("sounds/brickbounce1.wav")
won_music = pygame.mixer.Sound("music/won.mp3")
lost_music = pygame.mixer.Sound("music/lost.mp3")

# text color
text_col = (255, 255, 255)


def text_draw(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))


# brick wall
class wall:
    def __init__(self) -> None:
        self.width = screen_width // colums
        self.height = 25

    def create(self):
        self.bricks = []
        single_brick = []
        for row in range(rows):
            brick_row = []
            for col in range(colums):
                # generate x,y cords to make rectangle
                brick_x = col * self.width
                brick_y = row * self.height
                rectangle = pygame.Rect(brick_x, brick_y, self.width, self.height)
                # bricks strength
                if row < 2:
                    strength = 3
                elif row < 4:
                    strength = 2
                elif row < 6:
                    strength = 1
                # rect and color data
                single_brick = [rectangle, strength]
                brick_row.append(single_brick)
            self.bricks.append(brick_row)

    def draw(self):
        for row in self.bricks:
            for brick in row:
                if brick[1] == 3:
                    brick_col = gold_brick
                if brick[1] == 2:
                    brick_col = iron_brick
                if brick[1] == 1:
                    brick_col = copper_brick
                pygame.draw.rect(screen, brick_col, brick[0])
                pygame.draw.rect(screen, bg, (brick[0]), 4)


# paddle
class paddle:
    def __init__(self) -> None:
        self.reset()

    def move(self):
        # reset the position of the paddle
        self.direction = 0
        key = pygame.key.get_pressed()
        if key[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
            self.direction = -1
        if key[pygame.K_RIGHT] and self.rect.right < screen_width:
            self.rect.x += self.speed
            self.direction = 1

    def draw(self):
        pygame.draw.rect(screen, paddle_color, self.rect)
        pygame.draw.rect(screen, paddle_outline, self.rect, 3)

    def reset(self):
        self.height = 12
        self.width = int(screen_width / colums)
        self.x = int((screen_width / 2) - (self.width / 2))
        self.y = screen_height - (self.height * 2)
        self.speed = 6
        self.rect = Rect(self.x, self.y, self.width, self.height)
        self.direction = 0


class ball:
    def __init__(self, x, y) -> None:
        self.reset(x, y)

    def move(self):
        collision_thresh = 5

        # bricks collision
        wall_is_destroyed = True
        row_counter = 0
        for row in wall.bricks:
            i_counter = 0
            for item in row:
                # collision check
                if self.rect.colliderect(item[0]):
                    if (
                        abs(
                            self.rect.bottom - item[0].top < collision_thresh
                            and self.speed_y
                        )
                        > 0
                    ):
                        self.speed_y *= -1
                        pygame.mixer.Sound.play(brick_bounce_sound)
                        pygame.mixer.music.stop()
                    if (
                        abs(
                            self.rect.top - item[0].bottom < collision_thresh
                            and self.speed_y
                        )
                        > 0
                    ):
                        self.speed_y *= -1
                        pygame.mixer.Sound.play(brick_bounce_sound)
                        pygame.mixer.music.stop()
                    if (
                        abs(
                            self.rect.right - item[0].left < collision_thresh
                            and self.speed_x
                        )
                        > 0
                    ):
                        self.speed_x *= -1
                        pygame.mixer.Sound.play(brick_bounce_sound)
                        pygame.mixer.music.stop()
                    if (
                        abs(
                            self.rect.left - item[0].right < collision_thresh
                            and self.speed_x
                        )
                        > 0
                    ):
                        self.speed_x *= -1
                        pygame.mixer.Sound.play(brick_bounce_sound)
                        pygame.mixer.music.stop()
                    # reduce brick strength
                    if wall.bricks[row_counter][i_counter][1] > 1:
                        wall.bricks[row_counter][i_counter][1] -= 1
                    else:
                        wall.bricks[row_counter][i_counter][0] = (0, 0, 0, 0)
                if wall.bricks[row_counter][i_counter][0] != (0, 0, 0, 0):
                    wall_is_destroyed = False
                i_counter += 1
            row_counter += 1

        if wall_is_destroyed:
            self.gameover = 1
        # collision with side walls
        if self.rect.left < 0 or self.rect.right > screen_width:
            self.speed_x *= -1
            pygame.mixer.Sound.play(random.choice(wall_bounce_sounds))
            pygame.mixer.music.stop()
        # check for top and bottom walls
        if self.rect.top < 0:
            self.speed_y *= -1
            pygame.mixer.Sound.play(random.choice(wall_bounce_sounds))
            pygame.mixer.music.stop()
        if self.rect.bottom > screen_height:
            self.gameover = -1
        # check for collision with the paddle
        if self.rect.colliderect(paddle):
            # checks if the collision happend at the top of the paddle
            if (
                abs(self.rect.bottom - paddle.rect.top) < collision_thresh
                and self.speed_y > 0
            ):
                self.speed_y *= -1
                # adds speed to the ball if the paddle is moving at the same direction as the paddle
                self.speed_x += paddle.direction
                # sets a max speed the ball can go
                if self.speed_x > self.max_speed:
                    self.speed_x = self.max_speed
                elif self.speed_x < 0 and self.speed_x < -self.max_speed:
                    self.speed_x = -self.max_speed
            pygame.mixer.Sound.play(paddle_bounce_sound)
            pygame.mixer.music.stop()
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y
        return self.gameover

    def draw(self):
        pygame.draw.circle(
            screen,
            ball_color,
            (self.rect.x + self.ball_radi, self.rect.y + self.ball_radi),
            self.ball_radi,
        )
        pygame.draw.circle(
            screen,
            ball_outline,
            (self.rect.x + self.ball_radi, self.rect.y + self.ball_radi),
            self.ball_radi,
            1,
        )

    def reset(self, x, y):
        self.ball_radi = 7
        self.x = x - self.ball_radi
        self.y = y
        self.rect = Rect(self.x, self.y, self.ball_radi * 2, self.ball_radi * 2)
        self.speed_x = 4
        self.speed_y = -4
        self.max_speed = 5
        self.gameover = 0


# create the wall
wall = wall()
wall.create()
# create the paddle
paddle = paddle()
# create the ball
ball = ball(paddle.x + (paddle.width // 2), paddle.y - paddle.height)

running = True
while running:
    clock.tick(fps)
    screen.fill(bg)
    # drawing objects
    wall.draw()
    paddle.draw()
    ball.draw()
    if ball_is_live:
        paddle.move()
        gameover = ball.move()
        if gameover != 0:
            ball_is_live = False
    if not ball_is_live:
        if gameover == 0:
            text_draw(
                text="CLICK ANYWHERE TO START THE BALL",
                font=font,
                text_col=text_col,
                x=100,
                y=screen_height // 2 + 100,
            )
        elif gameover == 1:
            text_draw(
                text="YOU WON!",
                font=font,
                text_col=text_col,
                x=50,
                y=screen_height // 2 + 50,
            )
            text_draw(
                text="CLICK ANYWHERE TO START THE BALL",
                font=font,
                text_col=text_col,
                x=100,
                y=screen_height // 2 + 100,
            )
            pygame.mixer.Sound.play(won_music)
            pygame.mixer.music.stop()
        elif gameover == -1:
            text_draw(
                text="YOU LOST!",
                font=font,
                text_col=text_col,
                x=50,
                y=screen_height // 2 + 50,
            )
            text_draw(
                text="CLICK ANYWHERE TO START THE BALL",
                font=font,
                text_col=text_col,
                x=100,
                y=screen_height // 2 + 100,
            )
            pygame.mixer.Sound.play(lost_music)
            pygame.mixer.music.stop()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONUP and ball_is_live == False:
            ball_is_live = True
            ball.reset(paddle.x + (paddle.width // 2), paddle.y - paddle.height)
            paddle.reset()
            wall.create()
    pygame.display.update()

pygame.quit()
