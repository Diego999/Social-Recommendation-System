from numpy import zeros


class Matrix:
    def __init__(self, list_rows, list_cols, type, fill_val=None):
        self.rows = list_rows
        self.rows_index = self.create_dict_index(self.rows)
        self.cols = list_cols
        self.cols_index = self.create_dict_index(self.cols)
        self.matrix = zeros(shape=(len(list_rows), len(list_cols)), dtype=type)
        if fill_val is not None:
            self.matrix.fill(fill_val)

    @staticmethod
    def create_dict_index(list):
        return {list[i]: i for i in range(0, len(list))}

    def get_rows(self):
        return self.rows

    def get_cols(self):
        return self.cols

    def __getitem__(self, pos):
        return self.matrix[self.rows_index[pos[0]], self.cols_index[pos[1]]]

    def __setitem__(self, pos, value):
        self.matrix[self.rows_index[pos[0]], self.cols_index[pos[1]]] = value

    def __str__(self):
        out = ''
        for r in self.rows:
            for c in self.cols:
                out += str(self[r, c]) + ' '
            out += '\n'
        return out
