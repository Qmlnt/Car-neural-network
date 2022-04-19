import time # time.sleep()
from teach_neural import * # Everything we need is there

# The most important part is to load the weights.
directory = "best\\score 269\\gen 33"
car = Car()
car.weights = [] # Clearing the weights of the car.
for i in range(len(os.listdir(directory))): # Loading weights.
    car.weights.append(np.load(f"{directory}\\weight{i}.npy"))

W, H = 1920, 1080   # Resolution of the screen.
timer = pg.time.Clock() # Used to get normal FPS, timer.tick() > time.sleep().
main_window = pg.display.set_mode((W, H)) # Initializing graphic system.
background = pg.image.load("background.png") # The background.
# Just in case somthing needs to be changed.
#car_sprite = pg.transform.smoothscale(pg.image.load("car.png"), (30,15))
#with open("data.json", "r") as file:
#    track_lines, praise = json.load(file)

executing = True # Used to quit from the program
while executing:
    for el in pg.event.get(): # Get events.
        if el.type == pg.QUIT:
            executing = False # Quitting.

    main_window.blit(background, (0,0)) # Drawing background over previous frame.
    # Drawing all lines.
    for el in praise: pg.draw.line(main_window, (255,150,50), el[0], el[1], 1)
    for el in track_lines: pg.draw.line(main_window, (100,255,100), el[0], el[1], 1)
    # Drawing car.
    main_window.blit(pg.transform.rotate(car_sprite, car.angle), (car.r.x, car.r.y))

    inputs = np.array(car.distances())         # Get distances.
    outputs = car.query(1 - inputs/distance)   # Ask neural with normalized inputs.
    car.move(outputs)                          # Move the car.
    if car.collisions():                       # Checking for collisions.
        print("Collision on score", car.score)
        time.sleep(1) # A small pause to watch where the car has crashed.

    pg.display.update() # Updating the display for changes to be applied.
    timer.tick(FPS) # This makes normal delays to get stable FPS.