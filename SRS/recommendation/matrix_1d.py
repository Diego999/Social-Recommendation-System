from numpy import zeros


class Matrix1D:
    """
    Matrix 1D with the index with objects
    """
    def __init__(self, list_rows, type, fill_val=None):
        self.rows = list_rows
        self.rows_index = Matrix1D.create_dict_index(self.rows)
        self.matrix = zeros(shape=len(list_rows), dtype=type)
        if fill_val is not None:
            self.matrix.fill(fill_val)

    @staticmethod
    def create_dict_index(list):
        """
        Create a dictionnary of index which represent objects
        """
        return {list[i]: i for i in range(0, len(list))}

    def get_rows(self):
        return self.rows

    def __getitem__(self, pos):
        return self.matrix[self.rows_index[pos]]

    def __setitem__(self, pos, value):
        self.matrix[self.rows_index[pos]] = value

    def __str__(self):
        return " ".join([str(self[r]) for r in self.rows])
