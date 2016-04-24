"""
Grid
"""
EMPTY = 0


def empty_grid(rows, cols):
    """
    Return an empty gird.
    """
    return [[EMPTY for _ in range(cols)]
            for _ in range(rows)]


class Grid:
    """
    2D grid.
    """
    def __init__(self, rows, cols):
        """
        Initialize a 2D grid.
        """
        self.rows = rows
        self.cols = cols
        self.cells = empty_grid(rows, cols)

    def __len__(self):
        """
        Return the total number of cells.
        """
        return self.rows * self.cols

    def __iter__(self):
        """
        Iterate through every cell.
        """
        for row in range(self.rows):
            for col in range(self.cols):
                yield row, col

    def reset(self):
        """
        Set all cells empty.
        """
        self.cells = empty_grid(self.rows, self.cols)

    def get_rows(self):
        """
        Return the number of rows.
        """
        return self.rows

    def get_cols(self):
        """
        Return the number of columns.
        """
        return self.cols

    def get_row(self, row):
        """
        Return cells in given row.
        """
        return [(row, col) for col in range(self.cols)]

    def get_col(self, col):
        """
        Returns cells in given column.
        """
        return [(row, col) for row in range(self.rows)]

    def get_tile(self, row, col):
        """
        Return the tile at given cell.
        """
        return self.cells[row][col]

    def set_tile(self, row, col, tile):
        """
        Set a tile at given cell.
        """
        self.cells[row][col] = tile

    def pop_tile(self, row, col):
        """
        Remove a tile and return it.
        """
        tile = self.get_tile(row, col)
        self.set_tile(row, col, EMPTY)
        return tile

    def get_tiles(self, cells):
        """
        Return tiles at given cells.
        """
        return [self.get_tile(row, col) for row, col in cells]

    def set_tiles(self, cells, tiles):
        """
        Set tiles at given cells.
        """
        for (row, col), tile in zip(cells, tiles):
            self.set_tile(row, col, tile)

    def pop_tiles(self, cells):
        """
        Remove tiles and return them.
        """
        return [self.pop_tile(row, col) for row, col in cells
                if self.get_tile(row, col)]

    def is_valid(self, row, col):
        """
        Return true if given cell is in grid.
        """
        return (0 <= col < self.cols and
                0 <= row < self.rows)

    def is_empty(self, row, col):
        """
        Return true if given cell is empty.
        """
        if self.is_valid(row, col):
            return self.get_tile(row, col) is EMPTY
        return False

    def empty_cells(self):
        """
        Return all empty cells in grid.
        """
        return [(row, col)
                for row in range(self.rows)
                for col in range(self.cols)
                if self.is_empty(row, col)]
