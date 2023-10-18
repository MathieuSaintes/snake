import pygame, random, os
pygame.init()

blk = 30
ww = 30 * blk
wh = 20 * blk
bd = 2 * blk
fps = 6

right = (blk, 0)
left = (-blk, 0)
up = (0, -blk)
down = (0, blk)

class Cell(pygame.Rect):
    def __init__(self, x, y):
        super().__init__(x, y, blk, blk)

class Bomb(Cell):
    def reset(self):
        self.x = random.randrange(p.bombs_area.left, p.bombs_area.right, blk)
        self.y = random.randrange(p.bombs_area.top, p.bombs_area.bottom, blk)
    def draw(self):
        w.blit(bomb_img, self)

class Bombs(list):
    def __init__(self, l):
        super().__init__(Bomb(0,0) for _ in range(3))
        self.reset()
    def reset(self):
        for i in range(len(self)):
            self[i].reset()
            while self[i] in self[:i] or self[i] == snake[0]:
                self[i].reset()

class Fruit(Cell):
    def __init__(self):
        super().__init__(0, 0)
        self.reset()
    def reset(self):
        self.x = random.randrange(p.x + blk, p.right - blk, blk)
        self.y = random.randrange(p.y + blk, p.bottom - blk, blk)
        if self in snake or self in bombs:
            self.reset()

class Part(Cell):
    
    def __init__(self, x, y, index):
        super().__init__(x, y)
        self.index = index
    
    def img(self):
        
        # head
        if self.index == 0:
            return head_img
        
        # tail
        elif self.index == len(snake) - 1:
            
            prev = snake[-2]
            
            if self == prev and len(snake) == 2:
                return empty_surface
            elif self == prev and len(snake) > 2:
                prev = snake[-3]
            
            if prev.y == self.y - blk:
                return tail_up
            elif prev.y == self.y + blk:
                return tail_down
            elif prev.x == self.x - blk:
                return tail_left
            elif prev.x == self.x + blk:
                return tail_right

        # body parts
        else:

            prev = snake[self.index - 1]
            after = snake[self.index + 1]
            
            if self == after:
                return empty_surface
            
            if prev.x == self.x == after.x:
                return body_vertical
            elif prev.y == self.y == after.y:
                return body_horizontal
            
            elif (prev.y == self.y > after.y and prev.x < self.x == after.x) or (after.y == self.y > prev.y and after.x < self.x == prev.x):
                return body_top_left
            elif (prev.y == self.y > after.y and prev.x > self.x == after.x) or (after.y == self.y > prev.y and after.x > self.x == prev.x):
                return body_top_right
            elif (prev.y == self.y < after.y and prev.x < self.x == after.x) or (after.y == self.y < prev.y and after.x < self.x == prev.x):
                return body_bottom_left
            elif (prev.y == self.y < after.y and prev.x > self.x == after.x) or (after.y == self.y < prev.y and after.x > self.x == prev.x):
                return body_bottom_right


class Snake(list):
    def __init__(self):
        super().__init__([Part(0, 0, 0)])
        self.reset()
    def reset(self):
        del self[1:]
        self[0].x, self[0].y = p.center
        self.motion = 0, 0    
    def movesforward(self):
        for i in range(len(self)-1,0,-1):
            self[i].clamp_ip(self[i-1])
        self[0].move_ip(self.motion)
    def growtail(self):
        tail = self[-1]
        self.append(Part(tail.x, tail.y, tail.index + 1))

class PlayArea(pygame.Rect):
    def __init__(self):
        super().__init__(0,0,0,0)
        self.reset()
    def reset(self):
        self.size = ww - 2 * bd, wh - 2 * bd
        self.center = wr.center
        self.bombs_area = self.inflate(-10 * blk, -10 * blk)
        self.update_nts()
    def update_nts(self):
        self.nts = random.choice(['left', 'right', 'bottom', 'top'])
        self.NTS = pygame.Rect({
            'left': (self.left, self.top, blk, self.height),
            'right': (self.right - blk, self.top, blk, self.height),
            'top': (self.left, self.top, self.width, blk),
            'bottom': (self.left, self.bottom - blk, self.width, blk)
            }[self.nts]
        )
    def shrink(self):
        if self.nts == 'right' or self.nts == 'left':
            self.w -= blk
            if self.nts == 'left':
                self.x += blk
        else:
            self.h -= blk
            if self.nts == 'top':
                self.y += blk
        self.update_nts()
        
class MessagePen(pygame.font.Font):
    
    def __init__(self):
        super().__init__(None, 30)
        self.reset()
    
    def reset(self):
        self.message = ''
    
    def write(self):
        
        failure_message_surface = self.render(self.message, True, 'red')
        restart_message_surface = self.render('Press any key to restart', True, 'blue')
        
        failure_message_rectangle = failure_message_surface.get_rect()
        restart_message_rectangle = restart_message_surface.get_rect()
        restart_message_rectangle.midtop = failure_message_rectangle.midbottom

        message_rectangle = failure_message_rectangle.union(restart_message_rectangle)
        message_rectangle.center = wr.center
        failure_message_rectangle.midtop = message_rectangle.midtop
        restart_message_rectangle.midbottom = message_rectangle.midbottom

        w.blits(((failure_message_surface, failure_message_rectangle), (restart_message_surface, restart_message_rectangle)))


class ScorePen(pygame.font.Font):
    def __init__(self):
        super().__init__(None, 20)
    def draw(self):
        score_surface = self.render(f'Score: {score}, Highest: {highest_score}', True, 'black')
        w.blit(score_surface, (10, 10))

def display():
    w.fill('grey')
    w.fill('white', p)
    w.fill('yellow', p.NTS)
    w.blit(fruit_img, fruit)
    for bomb in bombs:
        bomb.draw()
    for part in snake:
        w.blit(part.img(), part)
    for explosion in explosions:
        w.blit(explosion_img, explosion)
    scorepen.draw()
    if fail:
        messagepen.write()
    pygame.display.update()

def restart():
    p.reset()
    snake.reset()
    bombs.reset()
    fruit.reset()
    messagepen.reset()
    global score, fail, explosions, head_img
    score = 0
    fail = False
    explosions = []
    head_img = head_right
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
            elif event.type == pygame.KEYDOWN:
                display()
                return
        clock.tick(fps)


# Prepare surfaces
w = pygame.display.set_mode((ww,wh))
wr = w.get_rect()
pygame.display.set_caption('Mathieu\'s Snake Game')

path = os.path.dirname(__file__) + '/'
bomb_img = pygame.transform.smoothscale(pygame.image.load(path + 'images/bomb.png').convert_alpha(), (blk,blk))
explosion_img = pygame.transform.smoothscale(pygame.image.load(path + 'images/explosion.png').convert_alpha(), (blk,blk))
fruit_img = pygame.transform.scale(pygame.image.load(path + 'images/fruit.png').convert_alpha(), (blk,blk))

sprite_sheet = pygame.image.load(path + 'images/snake-graphics.png').convert_alpha()
sprite_width = sprite_sheet.get_width() // 5
sprite_height = sprite_sheet.get_height() // 4

def get_sprite(i,j):
    sprite = pygame.Surface((sprite_width, sprite_height), pygame.SRCALPHA)
    sprite.blit(sprite_sheet, (0, 0), (i * sprite_width, j * sprite_height, sprite_width, sprite_height))
    sprite = pygame.transform.smoothscale(sprite, (blk, blk))
    return sprite

head_up = get_sprite(3,0)
head_right = get_sprite(4,0)
head_left = get_sprite(3,1)
head_down = get_sprite(4,1)

tail_up = get_sprite(3,2)
tail_down = get_sprite(4,3)
tail_left = get_sprite(3,3)
tail_right = get_sprite(4,2)
empty_surface = pygame.Surface((0,0))

body_horizontal = get_sprite(1,0)
body_vertical = get_sprite(2,1)

body_top_left = get_sprite(2,2)
body_top_right = get_sprite(0,1)
body_bottom_left = get_sprite(2,0)
body_bottom_right = get_sprite(0,0)


# Game initialization
p = PlayArea()
snake = Snake()
bombs = Bombs(3)
fruit = Fruit()

score, highest_score = 0, 0
pause = False
fail = False
explosions = []
head_img = head_right

messagepen = MessagePen()
scorepen = ScorePen()

clock = pygame.time.Clock()

display()

# Game Loop
while True:

    # Event Handling Loop
    # Get new event until quit, pause, new direction, or end of queue
    while (event := pygame.event.poll()).type != pygame.NOEVENT:

        if event.type == pygame.QUIT:
            quit()

        elif event.type == pygame.KEYDOWN:

            if event.key == pygame.K_SPACE:
                pause = not pause

            elif not pause and event.key in (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN):

                if event.key == pygame.K_LEFT and snake.motion != right:
                    snake.motion = left
                    head_img = head_left
                elif event.key == pygame.K_RIGHT and snake.motion != left:
                    snake.motion = right
                    head_img = head_right
                elif event.key == pygame.K_UP and snake.motion != down:
                    snake.motion = up
                    head_img = head_up
                elif event.key == pygame.K_DOWN and snake.motion != up:
                    snake.motion = down
                    head_img = head_down    
            
                break

    # Update game state
    if not pause and snake.motion != (0,0):
        
        snake.movesforward()

        # collision with the wall
        if not p.contains(snake[0]):
            messagepen.message = 'Crash into the wall'
            fail = True
            explosions = [snake[0]]

        # collision with the tail
        elif len(snake) > 1 and snake[0] in snake[1:]:
            messagepen.message = 'Head in the Tail'
            fail = True

        # collision with a bomb
        elif snake[0] in bombs:
            messagepen.message = 'Head in a bomb!'
            explosions = [snake[0]]
            fail = True

        # snake eats the fruit
        elif snake[0] == fruit:

            snake.growtail()
            p.shrink()
            explosions = [part for part in snake if not p.contains(part)]

            if len(explosions) > 0:
                messagepen.message = 'Wall shrinked on the snake!'
                fail = True
                p.NTS = (0,0,0,0)
            
            else: 
                fruit.reset()
                score += 1
                if score > highest_score:
                    highest_score = score
                
        # Display
        display()

        if fail:
            restart()

    #
    clock.tick(fps)