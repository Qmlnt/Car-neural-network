from math import pi, cos, sin, radians, sqrt

class Vec2:
	def __init__(self, x=0, y=0):
		self.x = x
		self.y = y

	def __add__(self, second):
		return Vec2(self.x + second.x,
					self.y + second.y)

	def __sub__(self, second):
		return Vec2(self.x - second.x,
					self.y - second.y)

	def __mul__(self, second):
		if type(second) == Vec2:
			return self.x*second.x + self.y*second.y
		else:
			return Vec2(self.x*second,
						self.y*second)

	def __div__(self, k):
		return Vec2(self.x/k,
					self.y/k)

	def __floordiv__(self, k):
		return Vec2(self.x//k,
					self.y//k)

	def __pos__(self):
		return self

	def __neg__(self):
		return self*-1

	def lenght(self):
		return sqrt(self.x**2 + self.y**2)

	def normalize(self, k=1):
		inv_lenght = k / self.lenght()
		return Vec2(self.x*inv_lenght,
					self.y*inv_lenght)

	def rotate(self, angle: int):
		x=self.x*cos(radians(angle))-self.y*sin(radians(angle));
		y=self.y*cos(radians(angle))+self.x*sin(radians(angle));
		return Vec2(x, y)

class Bezier3:
	def __init__(self, p0: Vec2, p1: Vec2, p2: Vec2):
		self.p0 = p0
		self.p1 = p1
		self.p2 = p2

	def bezier_func(self, x):
		t1 = 1 - x*2 + x*x
		t2 = x*2 - x*x*2
		t3 = x*x
		return self.p0*t3 + self.p1*t2 + self.p2*t1

	def get_tangent(self, x, line_lenght):
		vect1 = self.bezier_func(x)
		vect2 = self.bezier_func(x+0.001)

		result = (vect1 - vect2).normalize(line_lenght/2).rotate(-90)

		return (vect1, vect1 + result, vect1 - result)

	def get_vecs(self, line_lenght):
		vecs = []
		for i in range(10):
			vecs.append(self.get_tangent(i/10, line_lenght))

		return vecs

class Bezier4:
	def __init__(self, p0: Vec2, p1: Vec2, p2: Vec2, p3: Vec2):
		self.p0 = p0
		self.p1 = p1
		self.p2 = p2
		self.p3 = p3

	def bezier_func(self, x):
		t1 = (1 - x)**3
		t2 = 3*x*(1 - x)**2
		t3 = 3*x**2*(1 - x)
		t4 = x**3
		return self.p0*t1 + self.p1*t2 + self.p2*t3 + self.p3*t4

	def get_tangent(self, x, line_lenght):
		vect1 = self.bezier_func(x)
		vect2 = self.bezier_func(x+0.001)

		result = (vect1 - vect2).normalize(line_lenght/2).rotate(-90)

		return (vect1, vect1 + result, vect1 - result)

	def get_vecs(self, line_lenght):
		vecs = []
		for i in range(10):
			vecs.append(self.get_tangent(i/10, line_lenght))

		return vecs