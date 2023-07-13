class Matrix:

    def __init__(self, *args, **kwargs):
        self.data = []

    def x_vector(self):
        return [self.data[0][i] for i in range(3)]

    def y_vector(self):
        return [self.data[1][i] for i in range(3)]

    def z_vector(self):
        return [self.data[2][i] for i in range(3)]

    def row_count(self):
        return len(self.data)

    def column_count(self):
        return len(self.data[0])

    @classmethod
    def compose_from_vectors(cls, position, aim_vector, up_vector, rotate_order='xyz'):
        working_y_vector = up_vector
        z_vector = aim_vector
        x_vector = working_y_vector.cross_product(z_vector)
        y_vector = x_vector.cross_product(z_vector)
        matrix_entries = []
        vector_dictionary = dict(x=x_vector, y=y_vector, z=z_vector)
        vector_list = [v for v in rotate_order]
        for i in range(3):
            matrix_entries.extend(vector_dictionary[vector_list[i]].unit().data)
            matrix_entries.append(0.0)
        matrix_entries.extend([0.0, 0.0, 0.0, 1.0])
        return Matrix(matrix_entries)
