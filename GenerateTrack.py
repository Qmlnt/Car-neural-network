import pygame as pg
import sys
import json

from vector import *

WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLUE = (0, 0, 225)

sc = pg.display.set_mode((1300, 800))
pg.display.update()

line_lenght = 40

click = False
movedot = 0
path = []

save = False

dump = [[], []]

while 1:
	for i in pg.event.get():
		if i.type == pg.QUIT:
			sys.exit()
		if i.type == pg.MOUSEBUTTONDOWN:
			print(i.button)
			if i.button == 2:
				path.append([Vec2(i.pos[0], i.pos[1]), "line"])
			if i.button == 3:
				print("click", i.pos)
				for j in range(len(path)):
					print(path[j][0].x, path[j][0].y)
					if path[j][0].x + 5 > i.pos[0] and\
					   path[j][0].x - 5 < i.pos[0] and\
					   path[j][0].y + 5 > i.pos[1] and\
					   path[j][0].y - 5 < i.pos[1] and\
					   j != 0 and j != len(path)-1:

						path[j][1] = "bline"
			if i.button == 1:
				print("midclick")
				for j in range(len(path)):
					print(path[j][0].x, path[j][0].y)
					if path[j][0].x + 5 > i.pos[0] and\
					   path[j][0].x - 5 < i.pos[0] and\
					   path[j][0].y + 5 > i.pos[1] and\
					   path[j][0].y - 5 < i.pos[1]:

						click = not click
						movedot = j
		if i.type == pg.KEYDOWN:
			print(i.key)
			if i.key == 61:
				line_lenght += 2
			if i.key == pg.K_MINUS:
				line_lenght -= 2
			if i.key == 115:
				save = True



	sc.fill(WHITE)
	pressed = pg.mouse.get_pressed()
	pos = pg.mouse.get_pos()

	if click == True:
		path[movedot][0].x = pos[0]
		path[movedot][0].y = pos[1]


	for i in range(len(path)):
		if path[i][1] == "line":
			pg.draw.rect(sc,
						 BLUE,
						 (path[i][0].x-5, path[i][0].y-5, 10, 10))
			if i < len(path)-1 and path[i+1][1] == "line":
				pg.draw.line(sc,
							 BLUE,
							 (path[i][0].x, path[i][0].y),
							 (path[i+1][0].x, path[i+1][0].y),
							 3)
		elif path[i][1] == "bline":
			pg.draw.rect(sc,
						 GREEN,
						 (path[i][0].x-5, path[i][0].y-5, 10, 10))

			try:
				if path[i-1][1] == "line" and path[i+1][1] == "line":
					bezier_curve = Bezier3(path[i-1][0], path[i][0], path[i+1][0])
					dots = bezier_curve.get_vecs(line_lenght)
					for j in dots:
						pg.draw.line(sc,
									 BLUE,
									 (j[2].x, j[2].y),
									 (j[1].x, j[1].y),
									 3)
						dump[0].append([[int(j[2].x), int(j[2].y)],
									    [int(j[1].x), int(j[1].y)]])
				elif path[i-1][1] == "line" and path[i+1][1] == "bline" and path[i+2][1] == "line":
					bezier_curve = Bezier4(path[i-1][0], path[i][0], path[i+1][0], path[i+2][0])
					dots = bezier_curve.get_vecs(line_lenght)
					for j in dots:
						pg.draw.line(sc,
									 BLUE,
									 (j[2].x, j[2].y),
									 (j[1].x, j[1].y),
									 3)
						dump[0].append([[int(j[2].x), int(j[2].y)],
									    [int(j[1].x), int(j[1].y)]])
			except IndexError:
				continue

	if save == True:
		for i in range(len(dump[0])-1):
			curr_line = dump[0][i]
			next_line = dump[0][i+1]

			dump[1].append([curr_line[0], next_line[0]])
			dump[1].append([curr_line[1], next_line[1]])

		with open("data_file.json", "w") as write_file:
			dump[0], dump[1] = dump[1], dump[0]
			json.dump(dump, write_file)

	pg.display.update()


	pg.time.delay(20)