import copy
from Snowman3.utilities.vector import Vector
import Snowman3.utilities.decorators as dec


class Matrix:

    @dec.flatten_args
    def __init__(self, *args, **kwargs):
        scale = kwargs.pop('scale', [1.0, 1.0, 1.0])
        translation = kwargs.pop('translation', None)
        self.current_row = 0
        self.current_column = 0

        if translation and args:
            raise Exception('You must provide either *args or transform kwarg (not both.)')
        if not args or args[0] is None:
            if translation:
                t = translation
                self.data = (
                    (scale[0], 0.0, 0.0, 0.0),
                    (0.0, scale[1], 0.0, 0.0),
                    (0.0, 0.0, scale[2], 0.0),
                    (t[0], t[1], t[2], 1.0)
                )
            else:
                self.data = (
                    (scale[0], 0.0, 0.0, 0.0),
                    (0.0, scale[1], 0.0, 0.0),
                    (0.0, 0.0, scale[2], 0.0),
                    (0.0, 0.0, 0.0, 1.0)
                )
        elif isinstance(args[0], Matrix):
            self.data = copy.deepcopy(args[0].data)
        elif isinstance(args[0], Vector):
            t = args[0].data
            self.data = (
                (scale[0], 0.0, 0.0, 0.0),
                (0.0, scale[1], 0.0, 0.0),
                (0.0, 0.0, scale[2], 0.0),
                (t[0], t[1], t[2], 1.0)
            )
        elif len(args) == 3:
            t = args
            self.data = (
                (scale[0], 0.0, 0.0, 0.0),
                (0.0, scale[1], 0.0, 0.0),
                (0.0, 0.0, scale[2], 0.0),
                (t[0], t[1], t[2], 1.0)
            )
        else:
            raise Exception(f'Invalid matrix data: {args}')


    def __copy__(self):
        return self.__class__(self)


    '''def __repr__(self):
        return repr(self.data)'''


    def __mul__(self, n):
        self_transpose = self.get_transpose()
        return Matrix([[sum(a * b for a, b in zip(x_row, y_col)) for y_col in self_transpose.data] for x_row in n.data])


    def __rmul__(self, n):
        return self.__mul__(n)


    def __add__(self, m):
        return Matrix((a + b for a, b in zip(c, d)) for c, d in zip(self.data, m.data))


    def __sub__(self, m):
        return Matrix((a - b for a, b in zip(c, d)) for c, d in zip(self.data, m.data))


    def __len__(self):
        return len(self.data)


    def __getitem__(self, k):
        row, column = divmod(k, len(self.data))
        return self.data[row][column]


    def mirror_matrix(self, axis='x'):
        axis = {'x': 0, 'y': 1, 'z': 2}[axis.lower()]
        self.data = tuple(
            tuple(column * -1 if i == axis else column for i, column in enumerate(row)) for row in self.data
        )


    def x_vector(self):
        return Vector([self.data[0][0],
                       self.data[0][1],
                       self.data[0][2]])


    def y_vector(self):
        return Vector([self.data[1][0],
                       self.data[1][1],
                       self.data[1][2]])


    def z_vector(self):
        return Vector([self.data[2][0],
                       self.data[2][1],
                       self.data[2][2]])


    def row_count(self):
        return len(self.data)


    def column_count(self):
        return len(self.data[0]) if self.row_count() > 0 else 0


    def set_scale(self, scale):
        d = self.data
        self.data = (
            (scale[0], d[0][1], d[0][2], d[0][3]),
            (d[1][0], scale[1], d[1][2], d[1][3]),
            (d[2][0], d[2][1], scale[2], d[2][3]),
            (d[3][0], d[3][1], d[3][2], d[3][3])
        )


    def set_translation(self, translate):
        d = self.data
        t = translate
        self.data = (d[0], d[1], d[2], (t[0], t[1], t[2]))
        return self


    def set_axes(self, x_axis, y_axis, z_axis):
        d = self.data
        self.data = (
            (x_axis[0], x_axis[1], x_axis[2], 0.0),
            (y_axis[0], y_axis[1], y_axis[2], 0.0),
            (z_axis[0], z_axis[1], z_axis[2], 0.0),
            (d[3][0], d[3][1], d[3][2], d[3][3]),
        )


    def get_translation(self):
        return Vector([self.data[3][0], self.data[3][1], self.data[3][2]])


    def get_scale(self):
        return Vector([self.data[0][0], self.data[1][1], self.data[2][2]])


    def get_transpose(self):
        result = self.__new__(self.__class__)
        result.data = zip(*self.data)
        return result


    def flip_x(self):
        d = self.data
        self.data = (
            (d[0][0] * -1, d[0][1] * -1, d[0][2] * -1, d[0][3]),
            (d[1][0], d[1][1], d[1][2], d[1][3]),
            (d[2][0], d[2][1], d[2][2], d[2][3]),
            (d[3][0], d[3][1], d[3][2], d[3][3]),
        )


    def flip_y(self):
        d = self.data
        self.data = (
            (d[0][0], d[0][1], d[0][2], d[0][3]),
            (d[1][0] * -1, d[1][1] * -1, d[1][2] * -1, d[1][3]),
            (d[2][0], d[2][1], d[2][2], d[2][3]),
            (d[3][0], d[3][1], d[3][2], d[3][3]),
        )


    def flip_z(self):
        d = self.data
        self.data = (
            (d[0][0], d[0][1], d[0][2], d[0][3]),
            (d[1][0], d[1][1], d[1][2], d[1][3]),
            (d[2][0] * -1, d[2][1] * -1, d[2][2] * -1, d[2][3]),
            (d[3][0], d[3][1], d[3][2], d[3][3]),
        )


    def interpolate(self, target_matrix, i=0.5):
        result = Matrix()
        X1 = self.x_vector()
        Y1 = self.y_vector()
        Z1 = self.z_vector()
        T1 = self.get_translation()
        X2 = target_matrix.x_vector()
        Y2 = target_matrix.y_vector()
        Z2 = target_matrix.z_vector()
        T2 = target_matrix.get_translation()
        result.data = [[], [], [], []]
        result.data[0].extend(list((X1 * i) + (X2 * (1.0 - i))))
        result.data[0].append(0)
        result.data[1].extend(list((Y1 * i) + (Y2 * (1.0 - i))))
        result.data[1].append(0)
        result.data[2].extend(list((Z1 * i) + (Z2 * (1.0 - i))))
        result.data[2].append(0)
        result.data[3].extend(list((T1 * i) + (T2 * (1.0 - i))))
        result.data[3].append(1)
        return result


    '''def invert_matrix(self, tol=8):
        """
        WARNING! This fails when matrix values are close to zero...
        Consider using maya api if any issues come up
        """
        # Make sure self's matrix can be inverted
        det = get_determinant(self)
        if det == 0:
            raise ArithmeticError('Singular Matrix!')
        import maya.api.OpenMaya as om
        self_matrix = om.MMatrix(self.data)
        self.inverted = self_matrix.inverse()
        identity_matrix = Matrix()
        # Check if identity matrix list is an inverse of self's matrix with specific tolerance
        if check_matrix_equality(om.MMatrix(identity_matrix.data), (self_matrix * self_inverted), tol):
            tuples = []
            for i in range(4):
                results = []
                for j in range(4):
                    results = []
                    for j in range(4):
                        result = self_inverted.getElement(i, j)
                        results.append(result)
                    tuples.append(tuple(results))
                return Matrix(tuple(tuples))
            else:
                resit ArithmeticError('Matrix inverse outside of tolerance.')


    def aimed_towards_axis(self, axis='y', aim_axis='y', up_axis='x', up_matrix=None):
        """Align matrix to face the given global axis, with the existing or given up direction"""
        axis_dict = {'x': 0, 'y': 1, 'z': 2}
        axis_id = axis_dict[axis[-1].lower()]
        aim_axis_id = axis_dict[aim_axis[-1].lower()]
        up_axis_id = axis_dict[up_axis[-1].lower()]
        if aim_axis_id == up_axis_id:
            raise StandardError('aim_axis cannot match secondary_axis!')
        axis_neg = -1 if '-' in axis else 1
        aim_neg = -1 if '-' in aim_axis is else 1
        up_neg = -1 if '-' in up_axis else 1
        d = self.data
        result = Matrix(self)
        new_axes = [[]] * 3
        # Get aim vector towards given axis(eg. scene up)
        axis_vec = [axis_neg * aim_neg if i == axis_id else 0 for i in range(3)]
        #Product up vector into the plane that faces 'axis' and normalize it
        if up_matrix is not None:
            up_vector = up_matrix.get_translation() - self.get_translation() # no need to normalize here
        else:
            up_vector = d[up_axis_id] # 4
        projected_axis = Vector([0.0 if i == axis_id else up_vector[i] * up_neg for i in range(3)])
        sec_axis_new = projected_axis.normalize()
        new_axes[up_axis_id] = sec_axis_new.data
        # Calculate the third axis - reverse cross product direction if necessary to avoid negative scale
        other_axis_id = 3 - aim_axis_id - up_axis_id
        if axis_id == (up_axis_id + 1) %3: # x * y = z axis order
            other_axis_new = sec_axis_new.cross_product(axis_vec)
        else:
            other_axis_new = Vector(axis_vec).cross_product(sec_axis_new)
        new_axes[other_axis_id] = other_axis_new.data
        result.set_axes(*new_axes)
        return result'''


def compose_matrix_from_vectors(position, aim_vector, up_vector, rotate_order='xyz'):
    y_vector = up_vector
    z_vector = aim_vector
    x_vector = y_vector.cross_product(z_vector)
    y_vector = x_vector.cross_product
    matrix_list = []
    vector_dictionary = dict( x=x_vector, y=y_vector, z=z_vector)
    vector_list = [x for x in rotate_order]
    for i in range(3):
        matrix_list.extend(vector_dictionary[vector_list[i]].normalize().data)
        matrix_list.append(0.0)
    matrix_list.extend(position.data)
    matrix_list.append(1.0)
    return Matrix(matrix_list)


def compose_matrix(position, aim_position, up_position, rotate_order='xyz'):
    up_vector = up_position - position
    aim_vector = aim_position - position
    return compose_matrix_from_vectors( position, aim_vector, up_vector, rotate_order=rotate_order )
