# -*- coding:utf-8 -*-
# __author__ = 'L'

from typing import List, Tuple, Set, Any
from io import StringIO
import copy
import codecs
import random
import itertools

Matrix = List[List[Any]]
Points = Set[Tuple[int, int]]


class Sudoku:

    def __init__(self, *, size: int=9, selection: str='', name: str='', table: Matrix=(), box: Matrix=()):
        self.name = name
        self.size = size
        self.selection = selection
        self.n = len(self.selection)
        self.coor: List[Tuple[int, int]] = []
        for i, j in itertools.product(range(self.size), repeat=2):
            self.coor.append((i, j))
        self.table: Matrix = [[0] * self.size for _ in range(self.size)]
        self.box: Matrix = [[0] * self.size for _ in range(self.size)]
        self.mask: List[bool] = [True] * self.n
        self.map: Matrix = [[] for _ in range(self.size)]
        _sqrt = int(self.size ** 0.5)
        for i, j in self.coor:
            self.box[i][j] = i // _sqrt * _sqrt + j // _sqrt
        self.choice: Matrix = ()
        self.initialized: bool = False
        self.confirmed: bool = False
        self.show: bool = False

        if table is not ():
            if self.ismatrix(table):
                for i, j in self.coor:
                    self.set_(i, j, table[i][j])
            else:
                for line in table:
                    print(line)
                raise ValueError('\n\n\'table\' is not a \'Matrix\'')

        if box is not ():
            if self.ismatrix(box):
                self.box = box
            else:
                for line in box:
                    print(line)
                raise ValueError('\n\n\'box\' is not a \'Matrix\'')
        else:
            flag = True
            for i in range(_sqrt):
                _flag = flag
                for j in range(_sqrt):
                    b = self.box[i * _sqrt][j * _sqrt]
                    self.mask[b] = _flag
                    _flag = not _flag
                flag = not flag
        for i, j in self.coor:
            b = self.box[i][j]
            self.map[b].append((i, j))

    def __getitem__(self, sequence) -> List:
        return self.table[sequence]

    def __setitem__(self, sequence, value):
        raise IndexError

    def set_(self, i: int, j: int, v: int):
        if v is 0:
            v = self[i][j]
            if v is not 0:
                self[i][j] = 0
                self.initialize_()
        else:
            self[i][j] = v
            if self.initialized:
                for _i, _j in self.neighbour(i, j, v):
                    self.choice[_i][_j].remove(v)
                self.choice[i][j] = set()
        if self.initialized:
            if not self.islegal:
                raise SudokuIsIllegal

    def neighbour(self, i: int, j: int, v: int=0, *, area='choice', stats=False):
        _neighbour: Points = set()
        row, col, box = -1, -1, -1
        if area is 'choice':
            for _i in range(self.size):
                if v in self.choice[_i][j]:
                    _neighbour.add((_i, j))
                    row += 1

            for _j in range(self.size):
                if v in self.choice[i][_j]:
                    _neighbour.add((i, _j))
                    col += 1

            b = self.box[i][j]
            for _i, _j in self.map[b]:
                if v in self.choice[_i][_j]:
                    _neighbour.add((_i, _j))
                    box += 1

        elif area is 'table':
            for _i in range(self.size):
                if self[_i][j] is v:
                    _neighbour.add((_i, j))
            for _j in range(self.size):
                if self[i][_j] is v:
                    _neighbour.add((i, _j))
            b = self.box[i][j]
            for _i, _j in self.map[b]:
                if self[_i][_j] is v:
                    _neighbour.add((_i, _j))

        else:
            raise ValueError('\n\nArgument \'area\' should be \'choice\' or \'table\'')

        if stats:
            return _neighbour, row, col, box
        else:
            return _neighbour

    def makechoice(self, *, randomly=False):
        candidate: List[Tuple[int, int]] = []
        qualified = 1
        while len(candidate) is 0:
            qualified += 1
            for i, j in self.coor:
                if len(self.choice[i][j]) is qualified:
                    candidate.append((i, j))
        if self.show:
            print('standard:', qualified)
            print('among:')
            q = 0
            for i, j in candidate:
                q += 1
                print(f'{(i, j)} = ', end='')
                for v in self.choice[i][j]:
                    print(f'\'{self.selection[v]}\'', end=' ')
                print('    ', end='')
                if q % 5 is 0:
                    print()
            print()

        if randomly:
            _i, _j = random.choice(candidate)
            _v = random.choice(tuple(self.choice[_i][_j]))
            return _i, _j, _v
        else:
            _i, _j, _v, _n, _variety = self.size, self.size, 0, 0, 0
            for i, j in candidate:
                population: List[int, int] = [0] * self.n
                for v in self.choice[i][j]:
                    population[v] = len(self.neighbour(i, j, v))
                    population[0] += population[v] ** 2
                n = max(population[1:])
                v = random.choice([v for v in self.choice[i][j] if population[v] is n])
                variety = population[0] - n ** 2
                _flag = False
                if n > _n:
                    _flag = True
                elif n == _n:
                    if variety > _variety:
                        _flag = True
                    elif variety == _variety:
                        _flag = random.choice((False, True))
                if _flag:
                    _i, _j, _v, _n, _variety = i, j, v, n, variety
            if self.show:
                print(f'choose: {_i, _j} \'{self.selection[_v]}\' {_n, _variety}')
        return _i, _j, _v

    def initialize_(self):
        self.choice = [[None] * self.size for _ in range(self.size)]
        for i, j in self.coor:
            self.choice[i][j] = set()
            for v in range(1, self.n):
                self.choice[i][j].add(v)
        for i, j in self.coor:
            if self[i][j] is not 0:
                v = self[i][j]
                self.choice[i][j] = set()
                _neighbour = self.neighbour(i, j, area='table')
                for _i, _j in _neighbour:
                    if v in self.choice[_i][_j]:
                        self.choice[_i][_j].remove(v)

        if self.show:
            print('CHOICES:', self.choice_(), sep='\n')

    def simplfy(self):
        _flag = True
        q = 0
        while _flag:
            _flag = False
            for i, j in self.coor:
                if len(self.choice[i][j]) is 1:
                    v = list(self.choice[i][j])[0]
                    if self.show:
                        q += 1
                        print(f'{(i, j)} = \'{self.selection[v]}\'', end='    ')
                        if q % 5 is 0:
                            print()
                    self.set_(i, j, v)
                    _flag = True
            for v in range(1, self.n):
                for i, j in self.coor:
                    if v in self.choice[i][j]:
                        _neighbour, row, col, box = self.neighbour(i, j, v, stats=True)
                        if row * col * box is 0:
                            if self.show:
                                q += 1
                                print(f'{(i, j)} = \'{self.selection[v]}\'', end='    ')
                                if q % 5 is 0:
                                    print()
                            self.set_(i, j, v)
                            _flag = True
        if self.show:
            print('\nsimplied SODUKU:', self, sep='\n')
            print('CHOICES:', self.choice_(0), sep='\n')

    def solve(self, *, randomly, show=False):
        guess: List[Tuple] = []
        loop: int = 0
        self.show = show
        if self.islegal:
            self.initialize_()
        else:
            raise SudokuIsIllegal
        self.initialized = True
        while True:
            try:
                self.simplfy()
                
                if self.iscompleted:
                    print('  ' * (len(guess) - 1) + f'complete: {loop}')
                    raise SudokuIsCompleted
    
                else:
                    if not self.confirmed:
                        print('CONFIRMED:', self, sep='\n')
                        self.confirmed = True
                    bestchoice = self.makechoice(randomly=randomly)
                    backup = copy.deepcopy((self.table, self.choice))
                    guess.append((backup, *bestchoice))
                    _choice = (bestchoice[0], bestchoice[1], self.selection[bestchoice[2]])
                    loop += 1
                    print(f'> ' * (len(guess) - 1) + f'guess: {_choice}')
                    if self.show:
                        print()
                    self.set_(*bestchoice)
    
            except SudokuIsIllegal:
                if len(guess) is 0:
                    raise SudokuIsIllegal
    
                else:
                    [backup, wrongi, wrongj, wrongv] = guess[-1]
                    _choice = (wrongi, wrongj, self.selection[wrongv])
                    print('  ' * (len(guess) - 2) + f'< wrong: {_choice}')
                    del guess[-1]
                    self.table, self.choice = copy.deepcopy(backup)
                    self.choice[wrongi][wrongj].remove(wrongv)
                    if self.show:
                        print('BACKUP:')
                        print(self)
                        # print('FLAGS:', self.flag_, sep='\n')
                        print('CHOICES:', self.choice_(0), sep='\n')

    def ismatrix(self, suspect) -> bool:
        if len(suspect) != self.size:
            return False
        for sequence in suspect:
            if len(sequence) != self.size:
                return False
            for point in sequence:
                if type(point) is not int:
                    return False
                elif point < 0 or point > self.size:
                    return False
        return True

    def __str__(self) -> str:
        _str: str = ''
        for i in range(self.size):
            for j in range(self.size):
                if self[i][j] is not 0:
                    p = self.selection[self[i][j]]
                elif self.mask[self.box[i][j]]:
                    p = ' '
                else:
                    p = '-'
                _str += p + ' '
            _str += '\n'
        # _str = _str[:-1]
        return _str

    def choice_(self, *value) -> str:
        _str: str = ''
        if value is ():
            value = range(self.n)
        sub_str: str = ''
        _flag = False
        for i in range(self.size):
            for j in range(self.size):
                if len(self.choice[i][j]) is not 0:
                    p = f'{len(self.choice[i][j]):<2}'
                    _flag = True
                elif self.mask[self.box[i][j]]:
                    p = '  '
                else:
                    p = '- '
                sub_str += p
            sub_str += '\n'
        if not _flag:
            _str += '    None\n'
        else:
            if 0 in value:
                _str += sub_str
                value = list(value)
                value.pop(0)
            for v in value:
                sub_str: str = ''
                _flag = False
                sub_str += f'choice of {self.selection[v]}:\n'
                for i in range(self.size):
                    for j in range(self.size):
                        if self[i][j] is v:
                            p = self.selection[v]
                        elif v in self.choice[i][j]:
                            p = '#'
                            _flag = True
                        elif self.mask[self.box[i][j]]:
                            p = ' '
                        else:
                            p = '-'
                        sub_str += p + ' '
                    sub_str += '\n'
                if _flag:
                    _str += sub_str
        return _str

    @property
    def islegal(self) -> bool:
        if not self.initialized:
            for i, j in self.coor:
                if self[i][j] is not 0 and len(self.neighbour(i, j, self[i][j], area='table')) > 1:
                    return False
        else:
            for index in range(self.size):
                for v in range(1, self.n):
                    try:
                        i = 0
                        while v not in self.choice[i][index] and self[i][index] is not v:
                            i += 1
                        j = 0
                        while v not in self.choice[index][j] and self[index][j] is not v:
                            j += 1
                        b = 0
                        i, j = self.map[index][b]
                        while v not in self.choice[i][j] and self[i][j] is not v:
                            b += 1
                            i, j = self.map[index][b]
                    except IndexError:
                        if self.show:
                            print('\nILLEGAL:', self, sep='\n')
                            print(f'index = {index}')
                            print(self.choice_(v))
                        return False
        return True

    @property
    def iscompleted(self) -> bool:
        for i, j in self.coor:
            if self[i][j] is 0:
                return False
        return True


class SudokuIsIllegal(Exception):
    pass


class SudokuIsCompleted(Exception):
    pass


def fileinput(_in, *, size: int=0, selection: str='') -> Matrix:
    if size is 0:
        size = input('size: ')
    with codecs.open(_in, 'r', 'utf-8') as f:
        str_in = f.read()
    _table = [[0] * size for _ in range(size)]
    i, j = 0, 0
    while i < size ** 2 and j < len(str_in):
        while str_in[j] not in selection:
            j += 1
        _table[i // size][i % size] = selection.index(str_in[j])
        i += 1
        j += 1
    return _table


def main(*, _in: str='', _out: str='', size: int=0, selection: str='', randomly=False, show=False):
    if size != len(selection) - 1:
        raise ValueError
    _table: Matrix = fileinput(_in, size=size, selection=selection)
    fout = StringIO()
    question = Sudoku(name='QUESTION', size=size, selection=selection, table=_table)
    sudoku = Sudoku(name='ANSWER', size=size, selection=selection, table=_table)
    print('QUESTION:', question, sep='\n')
    print('QUESTION:', question, sep='\n', file=fout)

    try:
        sudoku.solve(randomly=randomly, show=show)
    except SudokuIsIllegal:
        print('\n>>>> Sudoku is illegal <<<<\n')
    except SudokuIsCompleted:
        print('ANSWER:', sudoku, sep='\n', file=fout)
        print('\n----------------------------\n')
        print(fout.getvalue())
        if _out is not '':
            with codecs.open(_out, 'w+', 'utf-8') as f:
                f.write(fout.getvalue())
                fout.close()

    return question, sudoku


if __name__ == '__main__':
    tuple_9 = (9, '0123456789')
    tuple_16 = (16, '-0123456789ABCDEF')
    size, selection = tuple_9
    code = 5
    randomly = False
    show = False
    main(_in=f'sudoku.in{code}.txt', size=size, selection=selection, randomly=randomly, show=show, )
