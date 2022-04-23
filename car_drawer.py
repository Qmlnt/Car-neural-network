# Most of the code here is Ctrl+C and Ctrl+V from teach_neural.py,
# so I won't maintain this code normally and it could change tremendously at some point.
# Something was removed, something that could be used like collisions() was not touched.

import os
import math
import json
import numpy as np
import pygame as pg
from scipy.special import expit as sigmoid


car_sprite_dir = "Images\\car.png"
track_directory = "tracks\\track.json"
weights_directory = "best\\score 389\\gen 16"

# Window settings.
FPS = 60                                   # Frames per second.
W, H = 1920, 1080                          # Resolution of the screen.
timer = pg.time.Clock()                    # Used to get normal FPS using timer.tick().
main_window = pg.display.set_mode((W, H))  # Initializing graphic system.
background = pg.Surface((W,H))
background.fill((60,60,60))                # Grey background.
# Car settings.
car_angle = 180
car_sprite = pg.transform.smoothscale(pg.image.load(car_sprite_dir), (30,15))
car_front = car_sprite.get_rect().width/2
car_side = car_sprite.get_rect().height/2
distance = 300      # How far the car will see (in pixels).
turn_coef = 0.1    # The differrence between outputs to turn.
move_coef = 0.2     # The differrence between outputs to move.
turn_speed = 15     # Turn speed in degrees per frame, 15 is ok.
acceleration = 2    # Accel of the car, 2 is 0.2 pixels per frame.
max_speed = 120     # Max speed, 120 is 12 pixels per frame.

with open(track_directory, "r") as file:
    start_position, track_lines, praise = json.load(file)[:3]

def sin(angle):  return math.sin(math.radians(angle))
def cos(angle):  return math.cos(math.radians(angle))

# Modified class from teach_neural.py
class Car():
    def __init__(self, name = "Car") -> None:
        self.name = name  # For identification purposes.
        self.defaults()   # Initializing defaults.
        self.weights = [] # Neural weights
    # Loading weights from the file.
        for i in range(len(os.listdir(weights_directory))):
            self.weights.append(np.load(f"{weights_directory}\\weight{i}.npy"))

    def defaults(self) -> None:
        """Set car variables to defaults."""
        self.angle = car_angle
        self.r = car_sprite.get_rect(center=(start_position))
        self.scored = []
        self.score = 0
        self.speed = 0
        self.cur_time = 0
        self.last_score_time = 0

    def intersect(self, first_line: list, second_line: list) -> int:
        """
        Take two line cordinates.
        Return x and y of intersection point, else False.
        """
        # For ease of use.
        [x1f, y1f], [x2f, y2f] = first_line
        [x1s, y1s], [x2s, y2s] = second_line
        # The line formula is Ax + By = C
        # A = y2 - y1                   ^
        # B = x1 - x2                   ^
        # C = A*x1 + B*y1, from formula ^
        a1, a2 = y2f - y1f, y2s - y1s
        b1, b2 = x1f - x2f, x1s - x2s
        c1, c2 = a1*x1f + b1*y1f, a2*x1s + b2*y1s
        #   1) (A1x + B1y = C1) * B2
        #   2) (A2x + B2y = C2) * B1
        # 1) - 2) is (A1x*B2 + B1y*B2 = C1*B2) - (A2x*B1 + B2y*B1 = C2*B1)
        # A1*B2*x - A2*B1*x = C1*B2 - C2*B1
        # x = (C1*B2 - C2*B1) / (A1*B2 - A2*B1)
        # d is A1*B2 - A2*B1 because we'll use it 3 times
        # y = (C2*A1 - C1*A2) / d, using the same method as for x (A2,A1 instead of B2,B1)
        d = a1*b2 - a2*b1
        # Also d can't be equal to 0, in this case lines are parallel, return False.
        if d != 0:
            x = (b2*c1 - b1*c2) / d
            y = (a1*c2 - a2*c1) / d
            # In case the line is horisontal or vertical, we do a little adjustment.
            if x1s == x2s:
                x1s-=2; x2s+=2
            if y1s == y2s:
                y1s-=2; y2s+=2
            if x1f == x2f:
                x1f-=2; x2f+=2
            if y1f == y2f:
                y1f-=2; y2f+=2
            # Finnaly we check if x and y belong to the lines.
            if ((min(x1s,x2s) <=x<= max(x1s,x2s)) and (min(y1s,y2s) <=y<= max(y1s,y2s))
            and (min(x1f,x2f) <=x<= max(x1f,x2f)) and (min(y1f,y2f) <=y<= max(y1f,y2f))):
                return x, y
        return False # Otherwise return False.

    def pos(self, angle: int) -> tuple:
        """Return x and y of the point located on the angle."""
        # Basically we get x and y of a point lying on the circle with a radius of the diameter variable.
        return (int(self.r.centerx+distance*cos(self.angle+angle)), int(self.r.centery-distance*sin(self.angle+angle)))

    def query(self, inputs: list) -> np.ndarray:
        """Take adjusted inputs, return neural outputs."""
        # Here some matrix magic happens.
        # The signals go from the beginning to the end of the neural weights.
        # In the end signals variable is the neural output.
        signals = np.array(inputs, ndmin=2).T
        for el in self.weights:
            signals = sigmoid(np.dot(el, signals))
        return signals

    def distances(self) -> list:
        """Return distances to the track lines."""
        # Here are 8 positions to check for track lines collisions.
        trackers = (self.pos(0), self.pos(15), self.pos(45), self.pos(90), self.pos(180), self.pos(270), self.pos(315), self.pos(345))
        # This cycle must find the nearest line (if any) for each position.
        inputs = [distance]*len(trackers)
        for el in track_lines:
            for i in range(len(trackers)):
                dist = self.intersect((self.r.center, trackers[i]), el)
                if dist:
                    # Pythagoras theorem.
                    dist = int(((dist[0]-self.r.centerx)**2+(dist[1]-self.r.centery)**2)**0.5)
                    if dist < inputs[i]: inputs[i] = dist
        # In the end we have distances for each dot in trackers list.
        return inputs

    def collisions(self) -> bool:
        """Check for collisionns with track and praise. Return True if the car is dead."""
        # Get the cordinates of the car rect; pygame rect is incorrect because if we rotate the car, the rect will be not suitable for collisions.
        square = (
            (int(self.r.centerx+car_front*cos(self.angle)-car_side*sin(self.angle)), int(self.r.centery-car_front*sin(self.angle)-car_side*cos(self.angle))), # top right
            (int(self.r.centerx-car_front*cos(self.angle)+car_side*sin(self.angle)), int(self.r.centery+car_front*sin(self.angle)+car_side*cos(self.angle))), # bottom left
            (int(self.r.centerx-car_front*cos(self.angle)-car_side*sin(self.angle)), int(self.r.centery+car_front*sin(self.angle)-car_side*cos(self.angle))), # top left
            (int(self.r.centerx+car_front*cos(self.angle)+car_side*sin(self.angle)), int(self.r.centery-car_front*sin(self.angle)+car_side*cos(self.angle)))  # bottom right
        )
        # As the car goes backwards, we kill it, praise[0] is the line behind it.
        #if self.intersect(square[0:2], praise[0]) and self.score == 0: return True
    #!!! ^ IF statement to uncomment if you came from move().
        if len(self.scored) == len(praise): # If the car has finished the lap,
            self.scored = []                # ^ we should reset scored lines.
        for el in praise:
            for i in range(0, 3, 2): # 0 and 2.
                # ^ The collision system is X shaped.
                if self.intersect(square[i:i+2], el) and (el not in self.scored):
                    self.last_score_time = self.cur_time
                    self.scored.append(el)
                    self.score += 1
        # Checking collisions with track.
        for el in track_lines:
            for i in range(0, 3, 2): # 0 and 2.
                # ^ The collision system is X shaped.
                if self.intersect(square[i:i+2], el):
                    return True # The car is dead.
        return False # Not necessary.

    def move(self, actions: list) -> None:
        """Take output of the neural, move car."""
        # For ease of use.
        forward, backward, right, left = actions
        turn_diff = right - left
        way_diff = forward - backward
        # Moving forward or backward.
        if way_diff > move_coef and self.speed < max_speed:
            self.speed+=acceleration
        # -max_speed instead of 0 if you want the car to move backwards,
        # ^ the IF statement in the collisions() might be helpfull then.
        elif way_diff < -move_coef and self.speed > 0:
            self.speed-=acceleration
        # Turning right or left.
        if turn_diff > turn_coef:
            self.angle = (self.angle-turn_speed)%360 # %360 to normalize the angle.
        elif turn_diff < -turn_coef:
            self.angle = (self.angle+turn_speed)%360
        # Float causes troubles, rounding the number should do.
        self.r.centerx += round(cos(self.angle)*self.speed/10)
        self.r.centery -= round(sin(self.angle)*self.speed/10)
        # In case the car was rotated, we need to get a new rect with the center of the previous one.
        self.r = pg.transform.rotate(car_sprite, self.angle).get_rect(center=self.r.center)


car = Car()

executing = True  # Used to close the program.
while executing:
    for el in pg.event.get():  # Get events.
        if el.type == pg.QUIT:
            executing = False  # Quit.

    main_window.blit(background, (0,0)) # Drawing background over previous frame.
    # Drawing all lines.
    # for el in praise: pg.draw.line(main_window, (255,200,255), el[0], el[1], 1)
    for el in track_lines: pg.draw.line(main_window, (100,255,255), el[0], el[1], 1)

    # Drawing car.
    main_window.blit(pg.transform.rotate(car_sprite, car.angle), (car.r.x, car.r.y))
    inputs = np.array(car.distances())         # Get distances.
    outputs = car.query(1 - inputs/distance)   # Ask neural with normalized inputs.
    car.move(outputs)                          # Move the car.

    pg.display.update()
    timer.tick(FPS)