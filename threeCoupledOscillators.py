import pygame
import math
import numpy as np
import random
# pygame setup



def createBackground(screen,midx,midy, number, mom_ratio):
            background = pygame.Surface(screen.get_size())
            background = background.convert()
            background.fill((20, 20, 20))
            font = pygame.font.Font(None, 64)
            text = font.render(f"{number} oscillators!  momentum deviation: {mom_ratio:.1f}", True, (10, 10, 10))
            textpos = text.get_rect(centerx=midx, y=3.5*midy/2)
            background.blit(text, textpos)
            screen.blit(background, (0, 0))  # This line makes it actually appear


class Spring:
    def __init__(self, b1, b2, k, visible, rest_length=None):
        self.b1 = b1
        self.b2 = b2
        self.k = k
        if rest_length is None:
            self.rest_length = np.linalg.norm(np.array(b1.pos) - np.array(b2.pos))
        else:
            self.rest_length = rest_length
        self.visible = visible
    
    # def springForce(self, dt): OLD VERSION
    #     pos1 = np.array(self.b1.pos)
    #     pos2 = np.array(self.b2.pos)
    #     displacement = pos2 - pos1
    #     distance = np.linalg.norm(displacement)
    #     if distance == 0:
    #         return  # prevent division by zero
    #     direction = displacement / distance
    #     stretch = distance - self.rest_length
    #     force = self.k * stretch * direction

    #     # Update velocities assuming unit mass and basic Euler integration
    #     self.b1.vx += force[0] * dt
    #     self.b1.vy += force[1] * dt
    #     self.b2.vx -= force[0] * dt
    #     self.b2.vy -= force[1] * dt


    def springForce(self):
        #changing the force to try and velocity verlet
        pos1 = np.array(self.b1.pos)
        pos2 = np.array(self.b2.pos)
        displacement = pos2 - pos1
        distance = np.linalg.norm(displacement)

        if distance == 0:
            return
        
        direction = displacement / distance
        stretch = distance - self.rest_length
        force = self.k * stretch * direction

        # Assume unit mass
        self.b1.ax += force[0] / self.b1.mass
        self.b1.ay += force[1] / self.b1.mass
        self.b2.ax -= force[0] / self.b2.mass
        self.b2.ay -= force[1] / self.b2.mass


    def drawSpring(self,screen,colour):
         pygame.draw.line(screen,colour,self.b1.pos,self.b2.pos)



class Ball:
    def __init__(self, x, y, r, vx, vy,ax,ay,visible, color="red"):
        self.x = x
        self.y = y
        self.pos = [x,y]
        self.r = r
        self.color = color
        self.vx = vx  # horizontal velocity
        self.vy = vy # vertical velocity
        self.vel = [vx,vy]
        self.top = self.y + r
        self.bottom = self. y - r
        self.left = self.x - r
        self.right = self.x + r
        self.ax = ax
        self.ay = ay
        self.mass = r**2 / 1000
        self.trail = []  # list of past positions
        self.max_trail_length = 50  # number of points to keep
        self.visible = visible


    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.r)

    # def drawTrail(self,screen,x=1280,y=720):
    #     self.surf = pygame.Surface((x, y))
    #     self.surf.set_colorkey((0, 0, 0))  # Optional: make black transparent
    #     self.surf.set_alpha(255)  # Fully opaque 
    #     screen.blit(self.surf, (0, 0))
    #     pygame.draw.circle(screen, "darkred", self.pos, 2)


    def drawTrail(self, screen):
        if len(self.trail) > 1:
            pygame.draw.lines(screen, (200, 200, 200), False, self.trail, 2)


    def get_pos(self):
        return (self.x, self.y)

    def update_bounds(self):
        self.top = self.y - self.r
        self.bottom = self.y + self.r
        self.left = self.x - self.r
        self.right = self.x + self.r

    def update_pos(self):
        self.x +=  self.vx
        self.y +=  self.vy
        self.pos = [self.x, self.y]

    def verlet_update(self, dt):
        # Step 1: Update positions
        self.x += self.vx * dt + 0.5 * self.ax * dt**2
        self.y += self.vy * dt + 0.5 * self.ay * dt**2

        # Store current acceleration to use in velocity update
        ax_old = self.ax
        ay_old = self.ay

        # We do not update acceleration here — spring forces will update it again

        self.update_bounds()
        self.pos = [self.x, self.y]


        self.trail.append((self.x, self.y))
        if len(self.trail) > self.max_trail_length:
            self.trail.pop(0)


        # Return old acceleration for use in velocity update
        return ax_old, ay_old
    
    def verlet_finish_velocity(self, ax_old, ay_old, dt):
        self.vx += 0.5 * (ax_old + self.ax) * dt
        self.vy += 0.5 * (ay_old + self.ay) * dt
        self.vel = [self.vx, self.vy]




    def Collision(self,obj):
        # Simple reversal of vertical direction
        self.vy *= -1

        # adjusts ball.y to prevent sticking
        #ball.y = obj.y - ball.r
        
        self.update_bounds()

    def paddleCollision(self, obj):
        
        # Simple reversal of vertical direction
        if (obj.x + obj.w) < self.x or obj.x > self.x:
            self.vx *= -1 
        else: 
            self.vy *= -1
        
        # #Makes the collision less boring
        hit_pos = (self.x - obj.x) / obj.w  
        self.vx = (hit_pos - 0.5) * 10  

        # adjusts ball.y to prevent sticking
        self.y = obj.y - self.r
        self.update_bounds()

    def ballCollision(self, obj):
        dx = self.x - obj.x
        dy = self.y - obj.y
        distance = math.hypot(dx, dy)

        if distance < self.r + obj.r and distance != 0:
            # Simple elastic collision response
            self.vx, obj.vx = obj.vx, self.vx
            self.vy, obj.vy = obj.vy, self.vy

            # Move balls apart to avoid sticking
            overlap = 0.5 * (self.r + obj.r - distance + 1)
            norm_dx = dx / distance
            norm_dy = dy / distance
            self.x += norm_dx * overlap
            self.y += norm_dy * overlap
            obj.x -= norm_dx * overlap
            obj.y -= norm_dy * overlap

            self.update_bounds()
            obj.update_bounds()

        elif distance == 0:
            # Balls are exactly overlapping – resolve by nudging one slightly
            # Random small displacement to separate them
            angle = random.uniform(0, 2 * math.pi)
            self.x += math.cos(angle)
            self.y += math.sin(angle)
            self.update_bounds()


    def wallCollision(self, screen_height, screen_width):
        if self.bottom > screen_height:
            self.vy *= -1
            self.y = screen_height - self.r  # Clamp to bottom

        elif self.top < 0:
            self.vy *= -1
            self.y = self.r  # Clamp to top

        if self.right > screen_width:
            self.vx *= -1
            self.x = screen_width - self.r  # Clamp to right

        elif self.left < 0:
            self.vx *= -1
            self.x = self.r  # Clamp to left

        self.update_bounds()

    def reset_acceleration(self):
        self.ax = 0
        self.ay = 0

    








def main():
            
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))

    trail_surface = pygame.Surface((1280, 720))
    trail_surface.set_colorkey((0, 0, 0))  # Optional: make black transparent
    trail_surface.set_alpha(255)  # Fully opaque


    clock = pygame.time.Clock()
    running = True
    dt = 0

    screenw = screen.get_width()
    screenh = screen.get_height()
    midx = screenw / 2
    midy = screenh / 2
    k_const = 1
    k = k_const
    ball_count = 5
    radMin = 5
    radMax = 30
    y_start = int(0.3* midy)
    x_start = int(0.3 * midx)
    velRange = 4
    draw_centre = False

    
    
    balls = []
    #invisiBalls
    for i in range(ball_count):
         balls.append(Ball(midx + random.randrange(-x_start,x_start),
                           midy +  random.randrange(-y_start,y_start),
                           random.randrange(radMin,radMax),
                           random.randrange(-velRange,velRange),
                           random.randrange(-velRange,velRange),
                           False, 
                           0,0))
         
    initialMomentum = sum(np.sqrt(ball.vx**2 + ball.vy**2) * ball.mass for ball in balls)

    springs = []
    
    #invisible Springs
    for i in range(ball_count -1):
        for j in range(i+1, ball_count):
            springs.append(Spring(balls[i], balls[j], k, False, 200))

 
    while running:

        # poll for events
        # pygame.QUIT event means the user clicked X to close your window
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        

        newMomentum = sum(np.sqrt(ball.vx**2 + ball.vy**2) * ball.mass for ball in balls)


        createBackground(screen,midx,midy, len(balls), (newMomentum / initialMomentum))
        screen.blit(trail_surface, (0, 0))

        
        poses = [0,0]
        for ball in balls:
            ball.reset_acceleration()
            ball_rect = pygame.Rect(ball.x - ball.r, ball.y - ball.r, ball.r * 2, ball.r * 2)
            if ball.visible == True:
                ball.draw(screen)
            ball.drawTrail(screen)
            # Reset all accelerations
    

        # Calculate forces (update accelerations)
        for spring in springs:
            spring.springForce()

        # Verlet integration: update positions and store old accelerations
        old_accels = [ball.verlet_update(dt) for ball in balls]

        # Recalculate forces (update new accelerations)
        for ball in balls:
            ball.reset_acceleration()
        for spring in springs:
            spring.springForce()

        # Verlet integration: update velocities using old and new acceleration
        for ball, (ax_old, ay_old) in zip(balls, old_accels):
            ball.verlet_finish_velocity(ax_old, ay_old, dt)
            ball.update_bounds()
            ball.wallCollision(screenh, screenw)
            poses[0] += ball.x
            poses[1] += ball.y
        centre = [poses[0] / len(balls) , poses[1] / len(balls)]
            

        if draw_centre == True:
            pygame.draw.circle(trail_surface, "darkred", (int(centre[0]), int(centre[1])), 2)
        
        #centre_obj = pygame.Rect(centre[0],centre[1],30,30)
        #pygame.draw.rect(screen, "red", centre_obj )

        for i, ball in enumerate(balls):
            for j, other_ball in enumerate(balls):
                if i != j:
                    # Do something with ball and other_ball
                    # For example, handle collisions
                    ball.ballCollision(other_ball)




        for spring in springs:
                if spring.visible == True:
                    spring.drawSpring(screen,"blue")
                spring.springForce()


        # for i in range(ball_count -1):
        #     for j in range(i+1, ball_count):
        #         springs.append(Spring(balls[i], balls[j], 0.5, 600))

        # flip() the display 
        pygame.display.flip()

        # limits FPS to 60
        # dt is delta time in seconds since last frame, used for framerate-
        fps = 600
        dt = clock.tick(fps) / 1000
    pygame.quit()


main()