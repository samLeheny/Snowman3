import pymel.core as pm
import numpy as np

def cross_product(a, b, normalize=False):
    """
        Gets cross product of input vectors a and b.
        Args:
            a ((numeric, numeric, numeric)): First of two input vectors.
            b ((numeric, numeric, numeric)): Second of two input vectors.
            normalize (bool): If on, will convert resulting vector to a unit vector (magnitude of 1, but same direction)
        Returns:
            ((float, float, float)) Cross product of a and b.
    """

    c = np.cross(np.array(a), np.array(b)).tolist()

    if normalize:
        c = normalize_vector(c)

    return c

up_direction = [0, 1, 0]
forward_direction = [0, 0, 1]

y_vector = up_direction
z_vector = forward_direction
x_vector = cross_product(y_vector, z_vector)

move_matrix = np.array([[0, 0, 0], [0, 0, 0], [0, 0, 0]])
move_matrix[:, 0] = x_vector
move_matrix[:, 1] = y_vector
move_matrix[:, 2] = z_vector
move_matrix = np.asmatrix(move_matrix)

x_sphere = pm.PyNode('xSphere')
y_sphere = pm.PyNode('ySphere')
z_sphere = pm.PyNode('zSphere')
a_sphere = pm.PyNode('aSphere')

init_x_pos = np.array([1, 0, 0])
init_y_pos = np.array([0, 1, 0])
init_z_pos = np.array([0, 0, 1])
init_a_pos = np.array([0.6, 0.6, 0.6])

x_pos = tuple(move_matrix.dot(init_x_pos).tolist()[0])
y_pos = tuple(move_matrix.dot(init_y_pos).tolist()[0])
z_pos = tuple(move_matrix.dot(init_z_pos).tolist()[0])
a_pos = tuple(move_matrix.dot(init_a_pos).tolist()[0])


def apply_position():
    x_sphere.translate.set(x_pos)
    y_sphere.translate.set(y_pos)
    z_sphere.translate.set(z_pos)
    a_sphere.translate.set(a_pos)

#apply_position()

points = [
    [0.784, 0.0, -0.784],
    [0.0, 0.0, -1.108],
    [-0.784, 0.0, -0.784],
    [-1.108, 0.0, -0.0],
    [-0.784, -0.0, 0.784],
    [-0.0, -0.0, 1.108],
    [0.784, -0.0, 0.784],
    [1.108, -0.0, 0.0]
]

new_points = [move_matrix.dot(p).tolist()[0] for p in points]