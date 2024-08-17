import random
from random import randint
class Board:
    def __init__(self, size, hid = False):
        self.ships = []
        self.false_coord = []
        self.size = size
        self.board = [['0' for i in range(size)] for i in range(size)]
        self.count = 0
        self.hid = hid

    def draw_board(self):
        board_str = "  | " + " | ".join(str(i + 1) for i in range(self.size)) + " |\n"
        for i in range(self.size):
            board_str += f"{i + 1} | " + " | ".join(self.board[i]) + " |\n"

        if self.hid:
            board_str = board_str.replace('■','0')
        return board_str

    def set_ship(self, ship):
        for i in ship.get_coordinates():
            if self.is_out(i):
                raise ExceptionOutOfBoard('Точка за пределами доски')
        if not self.is_free(ship):
            raise ExceptionEnterDot('Точка занята')
        for i in ship.get_coordinates():
            self.board[i.x][i.y] = '■'
        self.ships.append(ship)
        self.contur(ship)

    def contur(self, ship, show=False):
        for x in range(-1, 2):
            for y in range(-1, 2):
                for xy in ship.get_coordinates():
                    new_dot = Coordinates(xy.x + x, xy.y + y)
                    if not self.is_out(new_dot):
                        self.false_coord.append(new_dot)
                        if show:
                            if self.board[new_dot.x][new_dot.y] == 'X':
                                pass
                            else:
                                self.board[new_dot.x][new_dot.y] = '*'

    def is_out(self, coord):
        return self.size <= coord.x or self.size <= coord.y or coord.x < 0 or coord.y < 0

    def shooten(self, reg_hits):
        return reg_hits in self.false_coord

    def reg_hits(self, shoot_dot):
        if self.is_out(shoot_dot):
            raise ExceptionOutOfBoard('Точка за пределами доски')
        if shoot_dot in self.false_coord:
            raise ExceptionEnterDot('Точка занята')

        self.false_coord.append(shoot_dot)

        for ship in self.ships:
            if shoot_dot in ship.get_coordinates():
                ship.get_hit()
                self.board[shoot_dot.x][shoot_dot.y] = 'X'
                if ship.get_crash():
                    self.count += 1
                    self.contur(ship, True)
                    print('Корабль потоплен')
                    return True
                else:
                    print('Корабль ранен')
                    return True
        self.board[shoot_dot.x][shoot_dot.y] = '*'
        print('Мимо')
        return False

    def is_free(self, ship):
        for i in ship.get_coordinates():
            if i in self.false_coord:
                return False
        return True

    def remove(self):
        self.false_coord = []


class Ship:
    def __init__(self, size, orientation, pozition):
        self.size = size
        self.orientation = orientation
        self.pozition = pozition
        self.hits = 0

    def get_coordinates(self):
        coordinates = []
        row, col = self.pozition.x, self.pozition.y
        for i in range(self.size):
            if self.orientation == 'H':
                coordinates.append(Coordinates(row, col + i))
            elif self.orientation == 'V':
                coordinates.append(Coordinates(row + i, col))
        return coordinates

    def get_hit(self):
        self.hits += 1

    def get_crash(self):
        return self.hits >= self.size


class Coordinates:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y


class GameException(Exception):
    pass


class ExceptionOutOfBoard(GameException):
    pass


class ExceptionEnterDot(GameException):
    pass

class BoardWrongShipException(GameException):
    pass

class Player:
    def __init__(self, board, board_PC):
        self.board_PC = board_PC
        self.board = board

    def ask(self):
        raise NotImplementedError()

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.board_PC.reg_hits(target)
                return repeat
            except GameException as e:
                print(e)

class AI(Player):
    def ask(self):
        d = Coordinates(randint(0,5), randint(0, 5))
        print(f"Ход компьютера: {d.x+1} {d.y+1}")
        return d


class User(Player):
    def ask(self):
        while True:
            cords = input("Ваш ход: ").split()

            if len(cords) != 2:
                print(" Введите 2 координаты! ")
                continue

            x, y = cords

            if not (x.isdigit()) or not (y.isdigit()):
                print(" Введите числа! ")
                continue

            x, y = int(x), int(y)

            return Coordinates(x - 1, y - 1)

class Game:
    def __init__(self, size=6):
        self.size = size
        pl = self.random_board()
        co = self.random_board()
        co.hid = True

        self.ai = AI(co, pl)
        self.us = User(pl, co)

    def random_board(self):
        board = None
        while board is None:
            board = self.random_place()
        return board

    def random_place(self):
        lens = [3, 2, 2, 1, 1, 1, 1]
        board = Board(size=self.size)
        attempts = 0
        while len(board.ships) < len(lens):
            attempts += 1
            if attempts > 2000:
                return None
            ship = Ship(lens[len(board.ships)], random.choice(['H', 'V']),
                        Coordinates(randint(0, self.size - 1), randint(0, self.size - 1)))
            try:
                board.set_ship(ship)
            except (ExceptionOutOfBoard, ExceptionEnterDot):
                continue
        board.remove()
        return board

    def greet(self):
        print("-------------------")
        print("  Приветсвуем Вас  ")
        print("      в игре       ")
        print("    морской бой    ")
        print("-------------------")
        print(" формат ввода: x y ")
        print(" x - номер строки  ")
        print(" y - номер столбца ")

    def loop(self):
        num = 0
        while True:
            print("-" * 20)
            print("Доска пользователя:")
            print(self.us.board.draw_board())
            print("-" * 20)
            print("Доска компьютера:")
            print(self.ai.board.draw_board())
            if num % 2 == 0:
                print("-" * 20)
                print("Ходит пользователь!")
                repeat = self.us.move()
            else:
                print("-" * 20)
                print("Ходит компьютер!")
                repeat = self.ai.move()
            if repeat:
                num -= 1

            if self.ai.board.count == 7:
                print("-" * 20)
                print("Пользователь выиграл!")
                break

            if self.us.board.count == 7:
                print("-" * 20)
                print("Компьютер выиграл!")
                break
            num += 1

    def start(self):
        self.greet()
        self.loop()


g = Game(6)
g.start()