# Ctrl + S      To save the track.
# Ctrl + A      To select/unselect all dots.
# Escape        To unselect selected dots.
# + or -        To change the size of the dots.
# Use arrows to move selected dots.

# Next buttons can be changed.
# A             To add a dot. Simply hold the button and drag the mouse.
# S             To select/unselect a dot under the cursor.
# D or Delete   To delete all selected dots.
# C             To show/unshow how track ends connect.
# W             To set the start position for the car.
# L             To load an existing track.

import os            # To manage dirs.
import json          # To save data.
import time          # For time.sleep().
import pygame as pg  # For interface.


# Window settings.
FPS = 60                                   # Frames per second.
W, H = 1920, 1080                          # Resolution of the screen.
timer = pg.time.Clock()                    # Used to get normal FPS using timer.tick().
main_window = pg.display.set_mode((W, H))  # Initializing graphic system.
background = pg.Surface((W,H))
background.fill((60,60,60))                # Grey background.
# Button settings.
button_delay = 0.2                         # Pause after click.
add_dot_button = pg.K_a
select_dot_button = pg.K_s
delete_dot_button = pg.K_d                 # And Delete button.
connect_ends_button = pg.K_c               # Connect/unconnect the ends of the track.
set_start_pos_button = pg.K_w              # Set the start position for the car.
load_track_button = pg.K_l                 # Load an existing track.
# Other settings.
track_size = 50                            # Half of the track width.
dot_distance = 50  # In case you hold add_dot_button and drag the mouse.
dot_radius = 5                             # Default dot radius.
dot_speed = 2      # Move speed of the dot in pixels.
connect_ends = False                       # Should the ends be visually connected.
directory_to_use = ""
# Lists that are used in the program.
dots = []            # List containing all of the dots (x,y).
chosen_dots = []     # Dots here share the memory space with original ones.
track_lines = []     # Lines of the track calculated from the dots list.
start_position = []  # Start position cordinates for the car.

def load_track() -> None:
    """Load an existing  track."""
    global start_position, dots, directory_to_use
    choice = input("\nTry to load an existing track? y/N: ")
    if choice in ['y', 'Y', 'Yes', "yes"]:
        directory = input("Specify full directory: ")
        try:  # In case something goes wrong.
            print("\nTrying to load from:\n", directory)
            with open(directory, "r") as file:
                data = json.load(file)
                if len(data) != 4:
                    raise Exception("The track is not supported.")
                else:
                    start_position = data[0]
                    dots = data[3]
        except Exception as e:  # If smth went wrong.
            print("Could not load the track!")
            print("\n", e, "error occured.")
            load_track()
        else:
            directory_to_use = directory
            print("Loaded the track.\n")

def save() -> None:
    """Save data, if fail output the lists."""
    global directory_to_use, start_position
    if directory_to_use != "":
        try:  # In case something goes wrong.
            print("Trying to save in:\n", directory_to_use)
            track, praise = count_track_and_praise()
            if start_position == []: start_position = dots[0]
            data = [start_position, track, praise, dots]  # Data to be saved.
            with open(directory_to_use, "w") as file:
                json.dump(data, file)
        except Exception as e:  # If smth went wrong.
            print("Dots of your track:\n", dots)
            print("\n", e, "error occured.")
            choice = input("\nTry to save again in other directory? Y/n: ")
            if choice not in ["n", "no", "No", "N"]:
                directory_to_use = input("Specify the existing directory with file name: ")
                print("\nTrying again...")
                save()
        else:
            print("Saved successfully!")
            time.sleep(button_delay)
    else:
        directory_to_use = input("Specify the existing directory with file name: ")
        save()

def distance(dot1: list, dot2: list) -> int:
    """Take two dots, return distance between them."""
    return ((dot1[0]-dot2[0])**2 + (dot1[1]-dot2[1])**2) **0.5

def add_dot() -> None:
    """Add dot to the dots list."""
    mouse_position = list(pg.mouse.get_pos())
    if len(dots):  # If dots list is not empty.
        if distance(mouse_position, dots[-1]) > dot_distance:
        # ^ Don't add the dot if it's in the dot_distance range.
            dots.append(mouse_position)
    else:
        dots.append(mouse_position)

def select_dot() -> None:
    """Find and select or unselect the dot."""
    mouse_position = list(pg.mouse.get_pos())
    for dot in dots:
        if distance(mouse_position, dot) <= dot_radius:
            if dot in chosen_dots:
                chosen_dots.remove(dot)
            else:
                chosen_dots.append(dot)
            break
    time.sleep(button_delay)

def select_all() -> None:
    """Select or unselect all dots."""
    if chosen_dots == dots:
        chosen_dots.clear()
    else:
        chosen_dots.clear()
        chosen_dots.extend(dots)
    time.sleep(button_delay)

def delete_dot() -> None:
    """Delete chosen dots."""
    for el in chosen_dots:
        dots.remove(el)
    chosen_dots.clear()

def resize_dots(size: int) -> None:
    """Change the size of the dots."""
    global dot_radius
    if dot_radius + size > 0:
        dot_radius += size
    time.sleep(button_delay)

def escape() -> None:
    """Escape an uncomfortable situation."""
    chosen_dots.clear()

def count_track_lines() -> None:
    """Count track_lines."""
    track_lines.clear()  # Don't need old lines.
    for i in range(len(dots)):
        # For ease of use.
        x1, y1 = dots[i-1]
        x2, y2 = dots[i]
        # Lenght of x, y and dots.
        x_shift = x1 - x2
        y_shift = y1 - y2
        line_len = distance(dots[i-1], dots[i])
        if line_len == 0: continue  # Just in case.
        # To normalize the lenght of the perpendicular.
        sin = y_shift / line_len  # For x normalization.
        cos = x_shift / line_len  # For y normalization.
        # Count normalized dots from the line centre.
        nx1 = round(x1 - (x_shift/2) - sin*track_size)  # new x1.
        nx2 = round(x1 - (x_shift/2) + sin*track_size)  # new x2.
        ny1 = round(y1 - (y_shift/2) + cos*track_size)  # new y1.
        ny2 = round(y1 - (y_shift/2) - cos*track_size)  # new y2.
        track_lines.append([nx1, ny1])  # First dot.
        track_lines.append([nx2, ny2])  # Second dot.

def draw_everything() -> None:
    """Draw every point and line."""
    # Sizes of the dots (radius).
    chosen_size = dot_radius * 7/5
    track_size  = dot_radius * 3/5
    start_size  = dot_radius * 3
    for el in dots: pg.draw.circle(main_window, (255,100,100), el, dot_radius)
    for el in chosen_dots: pg.draw.circle(main_window, (255,255,100), el, chosen_size)
    indent = 0 if connect_ends else 2  # Indent determines whether to draw some items or not.
    for i in range(indent, len(track_lines)):
        pg.draw.circle(main_window, (255,100,255), track_lines[i], track_size)
    if len(start_position):
        pg.draw.circle(main_window, (150,150,255), start_position, start_size) 

    for i in range(indent, len(track_lines), 2):            # Praise lines.
        pg.draw.line(main_window, (255,200,255), track_lines[i], track_lines[i+1], 1)
    for i in range(-2+indent*2, len(track_lines)-2, 2):     # Track lines.
        pg.draw.line(main_window, (100,255,255), track_lines[i],   track_lines[i+2], 1)
        pg.draw.line(main_window, (100,255,255), track_lines[i+1], track_lines[i+3], 1)

def count_track_and_praise() -> list:
    """Count and return normal track lines and praise."""
    track = []  # Exported track lines.
    praise = []  # Exported praise lines.
    # Track lines.
    for i in range(-2, len(track_lines)-2, 2):
        track.append( [track_lines[i],   track_lines[i+2]] )
        track.append( [track_lines[i+1], track_lines[i+3]] )
    # Praise lines.
    for i in range(0, len(track_lines), 2):
        praise.append( [track_lines[i], track_lines[i+1]] )
    return track, praise


load_track()

executing = True  # Used to close the program.
while executing:
    for el in pg.event.get():  # Get events.
        if el.type == pg.QUIT:
            executing = False  # Quit.
            save()

    main_window.blit(background, (0,0))  # Draw background over previous frame.
    count_track_lines()  # Count the lines.
    draw_everything()  # And draw everything.
    # Check all the keys and call relevant functions.
    keys = pg.key.get_pressed()

    if keys[pg.K_LCTRL] and keys[pg.K_a]:
        select_all()                                        # Select all.
    elif keys[pg.K_LCTRL] and keys[pg.K_s]:
        save()                                              # Save.
    elif keys[pg.K_ESCAPE]:
        escape()                                            # Escape.
    elif keys[add_dot_button]:
        add_dot()                                           # Add dot.
    elif keys[select_dot_button]:
        select_dot()                                        # Select dot.
    elif keys[delete_dot_button] or keys[pg.K_DELETE]:
        delete_dot()                                        # Delete dot.
    elif keys[connect_ends_button]:
        connect_ends = not connect_ends                     # Connect ends.
        time.sleep(button_delay)
    elif keys[set_start_pos_button]:
        start_position = pg.mouse.get_pos()                 # Set start pos.
        time.sleep(button_delay)
    elif keys[load_track_button]:
        choice = input("Save current track? Y/n: ")
        if choice not in ["n", "no", "No", "N"]:
            directory_to_use = ""
            save()
        load_track()                                        # Load track.

    elif keys[pg.K_EQUALS]:
        resize_dots(1)                                      # Resize dots.
    elif keys[pg.K_MINUS]:
        resize_dots(-1)                                     # Resize dots.

    # Movement
    x = -dot_speed if keys[pg.K_LEFT] else dot_speed if keys[pg.K_RIGHT] else 0
    y = -dot_speed if   keys[pg.K_UP] else dot_speed if keys[pg.K_DOWN]  else 0
    if x or y:
        for dot in chosen_dots:
            dot[0] += x
            dot[1] += y

    pg.display.update()
    timer.tick(FPS)