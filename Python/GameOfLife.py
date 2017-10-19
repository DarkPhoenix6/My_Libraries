# a simple parser for python. use get_number() and get_word() to read
def parser():
    while 1:
        data = list(input().split(' '))
        for number in data:
            if len(number) > 0:
                yield (number)


input_parser = parser()


def get_word():
    global input_parser
    return next(input_parser)


def get_number():
    data = get_word()
    try:
        return int(data)
    except ValueError:
        return float(data)


# numpy and scipy are available for use
import numpy
import scipy


class Cell(object):
    def __init__(self, is_alive=False):
        self.is_alive = is_alive
        self.alive_count = 0
        self.next_alive = True

    def inc_counter(self):
        """
        :return: True if keep seeking for ajacent cells
        """
        self.alive_count += 1
        if self.alive_count <= 3:
            # self.alive_count += 1
            return True
        else:
            # self.alive_count += 1
            return False

    def reset_count(self):
        self.alive_count = 0

    def set_is_alive_next(self):
        if self.is_alive:
            if 1 < self.alive_count < 4:
                self.next_alive = True
            else:
                self.next_alive = False
        else:
            if self.alive_count == 3:
                self.next_alive = True
            else:
                self.next_alive = False

    def set_is_alive(self):
        self.is_alive = self.next_alive
        self.reset_count()


class TorusBoard(object):
    def __init__(self):

        self.rows = get_number()
        self.columns = get_number()
        self.turns = get_number()
        self.cells = self.generate_board()  # self.state[row][column]
        # self.print_board()

    def generate_board(self):
        columns, rows = self.columns, self.rows
        m = [[Cell() for x in range(rows)] for y in range(columns)]
        # board_list = []
        for i in range(rows):
            board_cell = get_word()
            for j in range(columns):

                # board_list.append(board_cell)
                if board_cell[j] == "*":
                    m[j][i].is_alive = True
                else:
                    m[j][i].is_alive = False
        return m

    def do_game(self):
        while self.turns > 0:
            self.do_turn()

    def do_turn(self):
        columns, rows = self.columns, self.rows
        self.turns -= 1
        for i in range(columns):
            for j in range(rows):
                self.check_adjacent_cells(j, i)

        for i in range(columns):
            for j in range(rows):
                self.cells[i][j].set_is_alive()
                # self.print_board()
                # print(" ")

    def check_adjacent_cells(self, row, column):
        i_left = column - 1
        i_right = column - self.columns + 1
        i_below = row - self.rows + 1
        i_top = row - 1
        keep_loop = True
        for i in [i_top, row, i_below]:

            for j in [i_left, column, i_right]:
                if i == row and j == column:
                    continue
                else:
                    if self.cells[j][i].is_alive:
                        keep_loop = self.cells[column][row].inc_counter()
                    if not keep_loop:
                        break
            if not keep_loop:
                break
        self.cells[column][row].set_is_alive_next()

    def print_board(self):
        columns, rows = self.columns, self.rows
        m = self.cells
        for i in range(rows):
            print_row = ""
            for j in range(columns):

                if m[j][i].is_alive:
                    print_row = print_row + "*"
                else:
                    print_row = print_row + "-"
            print(print_row)


b = TorusBoard()
b.do_game()
b.print_board()