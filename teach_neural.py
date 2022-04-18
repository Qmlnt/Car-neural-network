# Basically this script makes random cars and takes the best of them to the next gen to save the progress,
# ^ the saved cars are loaded and mutated to the other cars and so it goes...
import os  # To make dirs.
import json  # To load track lines and praise.
import pygame as pg  # To get car rect and show car progress.
import math          # Cos and sin.
import numpy as np   # Matrix operations.
from scipy.special import expit as sigmoid # Activation function.
import random # For random_choices() to selct cars for next gen.

# SETTINGS
FPS = 60            # Frames per second.
cars_number = 200   # 100 will do, but 200 is much better, 400 is great but takes some time.
neural_structure = [8,6,6,4] # 8 inputs, 2 hidden layers with 6 nerons, 4 outputs.
inherit = 5         # How many of the best cars will be in the next gen.
distance = 300      # How far the car will see (in pixels).
turn_coef = 0.1     # The differrence between outputs to turn.
move_coef = 0.2     # The differrence between outputs to move.
turn_speed = 15     # Turn speed in degrees per frame, 15 is ok.
acceleration = 2    # Accel of the car, 2 is 0.2 pixels per frame.
max_speed = 120     # Max speed, 120 is 12 pixels per frame.
max_time = FPS * 30 # Used to limit the time of the car life.
score_time_limit = FPS * 2 # Used to kill non productive cars.
car_sprite = pg.transform.smoothscale(pg.image.load("car.png"), (30,15))
# ^ Car img should be faced right, angle can be changed in the defaults(), img is resized to 30x15 pixels.
# AUTO SETTINGS
car_front = car_sprite.get_rect().width/2
car_side = car_sprite.get_rect().height/2
# OTHER
cars = []
generation = 0

# Making a degree version of math sin and cos.
def sin(angle):  return math.sin(math.radians(angle))
def cos(angle):  return math.cos(math.radians(angle))
# Loading data.
with open("data.json", "r") as file:
    track_lines, praise = json.load(file)


class Car():
    def __init__(self, name) -> None:
        self.name = name  # For identification purposes.
        self.defaults()   # Initializing defaults.
        self.weights = [] # Neural weights
        for i in range(len(neural_structure)-1): # Random weights for guaranteed success.
            self.weights.append(np.random.normal(0.0, neural_structure[i+1]**-0.5, (neural_structure[i+1],neural_structure[i])))

    def defaults(self) -> None:
        """Set car variables to defaults."""
        self.angle = 180
        self.r = car_sprite.get_rect(center=(956, 953))
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

    def random_train(self, mutation_rate: float) -> None:
        """Take mutation rate, mutate neural weights."""
        # Here we add a random number between -mutate and +mutate to each neural weight.
        for i in range(len(self.weights)):
            self.weights[i] += np.random.normal(0.0, mutation_rate, self.weights[i].shape)

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
        # ^ IF statement to uncomment if you came from move().
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
        # Float causes troubles, rounding the number and transforming it to int
        self.r.centerx += int(round(cos(self.angle)*self.speed/10, 0)) # ^  to remove
        self.r.centery -= int(round(sin(self.angle)*self.speed/10, 0)) # ^ .0 should do.
        # In case the car was rotated, we need to get a new rect with the center of the previous one.
        self.r = pg.transform.rotate(car_sprite, self.angle).get_rect(center=self.r.center)

    def run(self) -> None:
        """Unite all of the car functions."""
        self.defaults() # Setting defaults.
        #     Time is not up since last score time                  and general time is not up.
        while self.cur_time < self.last_score_time+score_time_limit and self.cur_time < max_time:
            self.cur_time += 1
            inputs = np.array(self.distances())         # Get distances.
            outputs = self.query(1 - inputs/distance)   # Ask neural with normalized inputs.
            self.move(outputs)                          # Move the car.
            if self.collisions():                       # Check for collisions.
                break

W, H = 1920, 1080 # Width and height of the interface window.
main_window = pg.display.set_mode((W, H)) # Initializing graphic system.
background = pg.image.load("background.png") # The background.
# A blank background may be loaded by uncommenting next line.
#background = pg.Surface((W,H)); background.fill((30,30,30))

if __name__ == "__main__":
    # Initializing cars.
    for i in range(cars_number):
        cars.append(Car(i))
        print(i, end=" ")
    print("\nInitialized!\n")

    # Unlimited amount of generations, just Ctrl+C or close therminal to stop.
    while True:
        main_window.blit(background, (0,0)) # Drawing background over previous gen cars.
        # Next 2 lines blit praise and track lines.
        for el in praise: pg.draw.line(main_window, (255,150,50), el[0], el[1], 1)
        for el in track_lines: pg.draw.line(main_window, (100,255,100), el[0], el[1], 1)

        generation += 1
        for el in cars:
            el.run() # Start the car.
            pg.event.get() # Check for events, otherwise the game window will lag a lot.
            # Drawing the last frame of the car to see how far it has gone.
            main_window.blit(pg.transform.rotate(car_sprite, el.angle), (el.r.x, el.r.y))
            pg.display.update() # Updating the display for changes to be applied.
            print(" ", el.name, "-", el.score, " ", sep='', end='|', flush=True)
        print()
        # Get 1 neural for each score.
        best = {el.score: el.weights for el in cars}
        scores = list(best.keys())
        scores.sort(reverse=True)
        print("Scores:", scores) # To see all of the
        # Only best cars will go further.
        if len(scores) > inherit:
            scores = scores[0:inherit]
        # Store best weights in best.
        best = [best[sc] for sc in scores]
        # Saving the best car.
        directory = f"best\\score {scores[0]}\\gen {generation}"
        os.makedirs(directory, exist_ok=True)
        for i in range(len(best[0])):
            np.save(f"{directory}\\weight{i}.npy", best[0][i])
        # Load best cars to next gen.
        inh = len(scores)
        for i in range(inh):
            cars[i].weights = best[i]
        # The higher the parent's score, the more cars inherit its weights.
        new_w = random.choices(best, weights=scores, k=cars_number-inh)
        # Update and mutate the rest of the cars.
        for i in range(inh, cars_number):
            # Need to separate the memory by copying the weights.
            cars[i].weights = [el.copy() for el in new_w[i-inh]]
            # Mutating the weights with a nice formulla y = 1/ (x+1)^0.5
            cars[i].random_train( 1/ ((scores[0]+1)**0.5) )
        # General output, all of other print() can be disabled.
        print("\nGen:", generation, "Mutation rate:", round(1/ ((scores[0]+1)**0.5), 3), "\nBest scores:", scores, "\n")
