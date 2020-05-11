WHITE = 1
BLACK = 2


def opponent(color):
    if color == WHITE:
        return BLACK
    else:
        return WHITE


def sign(n):
    """Возвращает единицу с таким же знаком, как у аргумента"""
    if n:
        return n // abs(n)
    return n


def print_board(board):  # Распечатать доску в текстовом виде (см. скриншот)
    print('     +----+----+----+----+----+----+----+----+')
    for row in range(7, -1, -1):
        print(' ', row, end='  ')
        for col in range(8):
            print('|', board.cell(row, col), end=' ')
        print('|')
        print('     +----+----+----+----+----+----+----+----+')
    print(end='        ')
    for col in range(8):
        print(col, end='    ')
    print()


def correct_coords(row, col):
    """Функция проверяет, что координаты (row, col) лежат
    внутри доски"""
    return 0 <= row < 8 and 0 <= col < 8


class Board:
    def __init__(self):
        self.color = WHITE
        self.field = []
        for row in range(8):
            self.field.append([None] * 8)
        self.field[0] = [
            Rook(WHITE), Knight(WHITE), Bishop(WHITE), Queen(WHITE),
            King(WHITE), Bishop(WHITE), Knight(WHITE), Rook(WHITE)
        ]
        self.field[1] = [
            Pawn(WHITE), Pawn(WHITE), Pawn(WHITE), Pawn(WHITE),
            Pawn(WHITE), Pawn(WHITE), Pawn(WHITE), Pawn(WHITE)
        ]
        self.field[6] = [
            Pawn(BLACK), Pawn(BLACK), Pawn(BLACK), Pawn(BLACK),
            Pawn(BLACK), Pawn(BLACK), Pawn(BLACK), Pawn(BLACK)
        ]
        self.field[7] = [
            Rook(BLACK), Knight(BLACK), Bishop(BLACK), Queen(BLACK),
            King(BLACK), Bishop(BLACK), Knight(BLACK), Rook(BLACK)
        ]

    def current_player_color(self):
        return self.color

    def cell(self, row, col):
        """Возвращает строку из двух символов. Если в клетке (row, col)
        находится фигура, символы цвета и фигуры. Если клетка пуста,
        то два пробела."""
        piece = self.field[row][col]
        if piece is None:
            return '  '
        return ('w' if piece.get_color() == WHITE else 'b') + piece.char()

    def get_piece(self, row, col):
        if correct_coords(row, col):
            return self.field[row][col]
        else:
            return None

    def move_piece(self, row, col, row1, col1):
        """Переместить фигуру из точки (row, col) в точку (row1, col1).
        Если перемещение возможно, метод выполнит его и вернёт True.
        Если нет --- вернёт False"""

        if not correct_coords(row, col) or not correct_coords(row1, col1):
            return False
        if row == row1 and col == col1:
            return False  # нельзя пойти в ту же клетку
        piece = self.field[row][col]
        if piece is None:
            return False
        if piece.get_color() != self.color:
            return False
        if self.field[row1][col1] is None:
            if not piece.can_move(self, row, col, row1, col1):
                return False
        elif self.field[row1][col1].get_color() == opponent(piece.get_color()):
            if not piece.can_attack(self, row, col, row1, col1):
                return False
        else:
            return False
        self.field[row][col] = None  # Снять фигуру.
        self.field[row1][col1] = piece  # Поставить на новое место.

        self.color = opponent(self.color)
        if isinstance(self.field[row1][col1], Rook) or isinstance(self.field[row1][col1], King):
            self.field[row1][col1].rok = False
        return True

    def move_and_promote_pawn(self, row, col, row1, col1, char):
        piece = self.field[row][col]
        if not isinstance(piece, Pawn):
            return False
        if not (piece.get_color() == WHITE and row1 == 7 or
                piece.get_color() == BLACK and row1 == 0):
            return False
        if self.field[row1][col1] is None:
            if piece.can_move(self, row, col, row1, col1):
                self.field[row][col] = None
                self.field[row1][col1] = {'Q': Queen, 'R': Rook,
                                          'B': Bishop, 'N': Knight}[char](piece.get_color())
                return True
        else:
            if piece.can_attack(self, row, col, row1, col1) and \
                    self.field[row1][col1].get_color() != piece.get_color():
                self.field[row][col] = None
                self.field[row1][col1] = {'Q': Queen, 'R': Rook,
                                          'B': Bishop, 'N': Knight}[char](piece.get_color())
                return True
        return False

    def is_under_attack(self, row, col, color):
        for x in range(8):
            for y in range(8):
                if not self.field[x][y] is None:
                    if self.field[x][y].color == color:
                        if self.field[x][y].can_move(self, x, y, row, col):
                            return True

    def castling0(self):
        if self.color == WHITE:
            row = 0
        else:
            row = 7
        if isinstance(self.field[row][0], Rook) and isinstance(self.field[row][4], King):
            if self.field[row][0].rok and self.field[row][4].rok:
                if not any(self.field[row][1:4]):
                    self.field[row][2] = self.field[row][4]
                    self.field[row][4] = None
                    self.field[row][3] = self.field[row][0]
                    self.field[row][0] = None
                    self.color = opponent(self.color)
                    return True

        return False

    def castling7(self):
        if self.color == WHITE:
            row = 0
        else:
            row = 7
        if isinstance(self.field[row][7], Rook) and isinstance(self.field[row][4], King):
            if self.field[row][7].rok and self.field[row][4].rok:
                if not any(self.field[row][5:7]):
                    self.field[row][6] = self.field[row][4]
                    self.field[row][4] = None
                    self.field[row][5] = self.field[row][7]
                    self.field[row][7] = None
                    self.color = opponent(self.color)
                    return True
        return False


class Rook:
    """Класс ладьи"""

    def __init__(self, color):
        self.color = color
        self.rok = True

    def get_color(self):
        return self.color

    def char(self):
        return 'R'

    def can_move(self, board, row, col, row1, col1):
        # Невозможно сделать ход в клетку, которая не лежит в том же ряду
        # или столбце клеток.
        if row != row1 and col != col1:
            return False

        step = 1 if (row1 >= row) else -1
        for r in range(row + step, row1, step):
            # Если на пути по горизонтали есть фигура
            if not (board.get_piece(r, col) is None):
                return False

        step = 1 if (col1 >= col) else -1
        for c in range(col + step, col1, step):
            # Если на пути по вертикали есть фигура
            if not (board.get_piece(row, c) is None):
                return False

        return True

    def can_attack(self, board, row, col, row1, col1):
        return self.can_move(board, row, col, row1, col1)


class Pawn:
    """Класс пешки"""

    def __init__(self, color):
        self.color = color

    def get_color(self):
        return self.color

    def char(self):
        return 'P'

    def can_move(self, board, row, col, row1, col1):
        # Пешка может ходить только по вертикали
        # "взятие на проходе" не реализовано
        if col != col1:
            return False

        # Пешка может сделать из начального положения ход на 2 клетки
        # вперёд, поэтому поместим индекс начального ряда в start_row.
        if self.color == WHITE:
            direction = 1
            start_row = 1
        else:
            direction = -1
            start_row = 6

        # ход на 1 клетку
        if row + direction == row1:
            return True

        # ход на 2 клетки из начального положения
        if (row == start_row
                and row + 2 * direction == row1
                and board.field[row + direction][col] is None):
            return True

        return False

    def can_attack(self, board, row, col, row1, col1):
        direction = 1 if (self.color == WHITE) else -1
        return (row + direction == row1
                and (col + 1 == col1 or col - 1 == col1))


class Knight:
    """Класс коня"""

    def __init__(self, color):
        self.color = color

    def get_color(self):
        return self.color

    def char(self):
        return 'N'  # kNight, буква 'K' уже занята королём

    def can_move(self, board, row, col, row1, col1):
        if (abs(row - row1) == 2 and abs(col - col1) == 1 or
            abs(row - row1) == 1 and abs(col - col1) == 2) and \
                0 <= row1 < 8 and 0 <= col1 < 8:
            if board.get_piece(row1, col1) is not None:
                return board.get_piece(row1, col1) != self.color
            return True
        return False

    def can_attack(self, board, row, col, row1, col1):
        return self.can_move(board, row, col, row1, col1)


class King:
    """Класс короля"""

    def __init__(self, color):
        self.color = color
        self.rok = True

    def get_color(self):
        return self.color

    def char(self):
        return 'K'

    def can_move(self, board, row, col, row1, col1):
        if row1 - row in [-1, 0, 1] and col1 - col in [-1, 0, 1] and \
                not (row1 - row == col1 - col == 0):
            if board.get_piece(row1, col1) is not None:
                if board.get_piece(row1, col1) == self.color:
                    return False

            return not board.is_under_attack(row1, col1, opponent(self.color))
        return False

    def can_attack(self, board, row, col, row1, col1):
        return self.can_move(board, row, col, row1, col1)


class Queen:
    """Класс ферзя"""

    def __init__(self, color):
        self.color = color

    def get_color(self):
        return self.color

    def char(self):
        return 'Q'

    def can_move(self, board, row, col, row1, col1):
        if abs(row - row1) == abs(col - col1) or row == row1 or col == col1:
            dy, dx = row1 - row, col1 - col
            if dy == dx == 0:
                return False
            if board.field[row1][col1] is not None:
                if board.field[row1][col1].get_color() == self.color:
                    return False
            if dx == 0 or dy == 0:
                step = 1 if (row1 >= row) else -1
                for r in range(row + step, row1, step):
                    if not (board.get_piece(r, col) is None):
                        return False

                step = 1 if (col1 >= col) else -1
                for c in range(col + step, col1, step):
                    if not (board.get_piece(row, c) is None):
                        return False

            for d in range(1, abs(dx) + 1):
                if not (board.get_piece(row + d * sign(dy),
                                        col + d * sign(dx)) is None):
                    if board.get_piece(row + d * sign(dy),
                                       col + d * sign(dx)).get_color() != self.color:
                        return (row + d * sign(dy),
                                col + d * sign(dx)) == (row1, col1)
                    return False
            return True
        return False

    def can_attack(self, board, row, col, row1, col1):
        return self.can_move(board, row, col, row1 - 1 * sign(row1 - row),
                             col1 - 1 * sign(col1 - col)) and row != row1 and col != col1


class Bishop:
    """Класс слона"""

    def __init__(self, color):
        self.color = color

    def get_color(self):
        return self.color

    def char(self):
        return 'B'

    def can_move(self, board, row, col, row1, col1):
        if abs(row - row1) == abs(col - col1):
            dy, dx = row1 - row, col1 - col
            if dy == dx == 0:
                return False
            if board.field[row1][col1] is not None:
                if board.field[row1][col1].get_color() == self.color:
                    return False

            for d in range(1, abs(dx) + 1):
                if not (board.get_piece(row + d * sign(dy),
                                        col + d * sign(dx)) is None):
                    if board.get_piece(row + d * sign(dy),
                                       col + d * sign(dx)).get_color() != self.color:
                        return (row + d * sign(dy),
                                col + d * sign(dx)) == (row1, col1)
                    return False
            return True
        return False

    def can_attack(self, board, row, col, row1, col1):
        return self.can_move(board, row, col, row1, col1)

# def main():
#     # Создаём шахматную доску
#     board = Board()
#     # Цикл ввода команд игроков
#     while True:
#         # Выводим положение фигур на доске
#         print_board(board)
#         # Подсказка по командам
#         print('Команды:')
#         print('    exit                               -- выход')
#         print('    move <row> <col> <row1> <row1>     -- ход из клетки (row, col)')
#         print('                                          в клетку (row1, col1)')
#         # Выводим приглашение игроку нужного цвета
#         if board.current_player_color() == WHITE:
#             print('Ход белых:')
#         else:
#             print('Ход чёрных:')
#         command = input()
#         if command == 'exit':
#             break
#
#         move_type, row, col, row1, col1 = command.split()
#         row, col, row1, col1 = int(row), int(col), int(row1), int(col1)
#
#         if board.move_piece(row, col, row1, col1):
#             print('Ход успешен')
#         else:
#             print('Координаты некорректы! Попробуйте другой ход!')
#
#
# main()
