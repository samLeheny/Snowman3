import math
import numpy as np


class Vector:

    def __init__(self, data=None):
        self._data = (0.0, 0.0, 0.0)
        if data:
            self.data = data


    @classmethod
    def create_from_points(cls, a, b):
        dimensions = len(a)
        result_vector = [b[i] - a[i] for i in range(dimensions)]
        return Vector(data=result_vector)


    def __repr__(self):
        return f'<{ ", ".join(str(x) for x in self.data) }>'


    def __add__(self, v):
        return Vector(a + b for a, b in zip(self.data, v.data))


    def __radd__(self, v):
        return Vector(a + b for a, b in zip(v.data, self.data))


    def __sub__(self, v):
        return Vector(a - b for a, b in zip(self.data, v.data))


    def __mul__(self, n):
        return Vector(a * n for a in self.data)


    def __rmul__(self, n):
        return self.__mul__(n)


    def __div__(self, n):
        return Vector(a / float(n) for a in self.data)


    @property
    def data(self):
        return self._data


    @data.setter
    def data(self, data):
        self._data = tuple(float(val) for val in data)


    def set_axis(self, axis):
        self.data = axis


    def magnitude(self):
        return math.sqrt(sum(x**2 for x in self.data))


    def magnitude_squared(self):
        return sum(x**2 for x in self.data)


    def normalize(self):
        mag = self.magnitude()
        if mag == 0.0:
            return Vector([0.0] * len(self.data))
        return self / mag


    def pad(self, n):
        return Vector(self.data[x] if x < len(self.data) else 0 for x in range(n))


    def dot(self, v):
        return sum(a * b for a, b in zip(self.data, v.data))


    def __len__(self):
        return len(self.data)


    def __getitem__(self, k):
        return self.data[k]


    def cross(self, b):
        result = np.cross(np.array(self.data), np.array(b)).tolist()
        return Vector(data=result)


    def dimension(self):
        return len(self.data)


def find_fraction_along_line(point, start, end, extrapolate_line=False):
    main_line = end - start
    point_line = point - start
    if main_line.mag() == 0.0 or point_line.mag() == 0.0:
        return 0.0
    percent_along_line = main_line.dot(point_line) / main_line.magnitude_squared()
    if extrapolate_line:
        return percent_along_line
    return max(min(percent_along_line, 1.0), 0.0)


def find_closest_point_on_line(point, start, end, extrapolate_line=False):
    main_line = end - start
    point_line = point - start
    if main_line.mag() == 0.0 or point_line.mag() == 0.0:
        return Vector(start)
    percent_along_line = main_line.dot(point_line) / main_line.magnitude_squared()
    if not extrapolate_line:
        percent_along_line = max(min(percent_along_line, 1.0), 0.0)
    return start + (main_line * percent_along_line)