# -*- coding:utf-8 -*-
# __author__ = 'L'

from typing import List, Dict, Tuple, Set, Any
from io import StringIO
import copy
import codecs
import random

Matrix = List[List[Any]]
Points = Set[Tuple[int, int]]


class Sudoku:
    map = {'r': 'Row', 'c': 'Column', 'b': 'Box'}

    def __init__(self, *, size: int=9, selection: str='', name: str='', table: Matrix=(), box: Matrix=()):
        self.size = size
        self.name = name
        self.selection = selection
        self.table: Matrix = [[0] * self.size for _ in range(self.size)]
        self.box: Matrix = [[0] * self.size for _ in range(self.size)]
        s = int(self.size ** 0.5)
        for i in range(self.size):
            for j in range(self.size):
                self.box[i][j] = i // s * s + j // s
        self.flag: Dict[str, Matrix] = {}
        for index in Sudoku.map:
            self.flag[index] = [None] * self.size
            for i in range(self.size):
                self.flag[index][i] = [0] * len(self.selection)
        self.choice: Matrix = ()
        self.initialized = False
        self.confirmed = False

        if table is not ():
            if self.ismatrix(table):
                for i in range(self.size):
                    for j in range(self.size):
                        self.set_(i, j, table[i][j])
            else:
                for line in table:
                    print(line)
                raise ValueError

        if box is not ():
            if self.ismatrix(box):
                self.box = box
            else:
                for line in box:
                    print(line)
                raise ValueError

    def __getitem__(self, sequence) -> List:
        return self.table[sequence]

    def __setitem__(self, sequence, value):
        raise IndexError

    def set_(self, i: int, j: int, v: int, *, show=False):
        b = self.box[i][j]
        if v is 0:
            v = self[i][j]
            if v is not 0:
                self[i][j] = 0
                self.flag['r'][i][v] -= 1
                self.flag['c'][j][v] -= 1
                self.flag['b'][b][v] -= 1
            self.initialize_(show=show)
        else:
            self[i][j] = v
            self.flag['r'][i][v] += 1
            self.flag['c'][j][v] += 1
            self.flag['b'][b][v] += 1
            if self.initialized:
                for _i, _j in self.neighbour(i, j, v):
                    self.choice[_i][_j][0] -= 1
                    self.choice[_i][_j][v] = 0
                self.choice[i][j] = [0] * len(self.selection)
        if show:
            print('(%s, %s) = %s' % (i, j, self.selection[v]))
            print(self)

    def neighbour(self, i: int, j: int, v: int = 0) -> Points:
        _neighbour: Points = set()
        for _i in range(self.size):
            if not v or self.choice[_i][j][v]:
                _neighbour.add((_i, j))
        for _j in range(self.size):
            if not v or self.choice[i][_j][v]:
                _neighbour.add((i, _j))
        b = self.box[i][j]
        for _i in range(self.size):
            for _j in range(self.size):
                if self.box[_i][_j] is b:
                    if not v or self.choice[_i][_j][v]:
                        _neighbour.add((_i, _j))
        return _neighbour

    def makechoice(self, *, randomly=False, failure: Tuple[int, int]=(), show=False):
        candidate: List[Tuple[int, int, int]] = []
        qualified = 1
        while len(candidate) is 0:
            qualified += 1
            for i in range(self.size):
                for j in range(self.size):
                    if self.choice[i][j][0] is qualified:
                        for v in range(1, len(self.selection)):
                            if self.choice[i][j][v]:
                                candidate.append((i, j, v))
        if show:
            print('standard:', qualified)
            print('among:', )
            site: Dict[Tuple[int, int], List[int]] = {}
            for i, j, v in candidate:
                if (i, j) not in site:
                    site[(i, j)] = []
                site[(i, j)].append(v)
            for _site in site:
                print(_site, ':', end=' ')
                for _v in site[_site]:
                    print(self.selection[_v], end=' ')
                print()

        if failure is not () and self.choice[failure[0]][failure[1]][0] > 1:
            print(self, self.choice_(), sep='\n')
            _i, _j = failure
            print('failure: (%d, %d)' % (_i, _j))
            candidate = []
            for v in range(1, len(self.selection)):
                candidate.append((_i, _j, v))

        if randomly:
            return random.choice(candidate)
        else:
            _i, _j, _v, _n = self.size, self.size, 0, 0
            for i, j, v in candidate:
                _neighbour = self.neighbour(i, j, v)
                if _n is 0 or len(_neighbour) > _n:
                    _i, _j, _v, _n = i, j, v, len(_neighbour)
                elif len(_neighbour) == _n and random.choice((False, True)):
                    _i, _j, _v = i, j, v
        return _i, _j, _v

    def initialize_(self, *, show=False):
        self.choice = [[None] * self.size for _ in range(self.size)]
        for i in range(self.size):
            for j in range(self.size):
                self.choice[i][j] = [0] * len(self.selection)
                if self[i][j] is 0:
                    for v in range(1, len(self.selection)):
                        b = self.box[i][j]
                        if self.flag['r'][i][v] + self.flag['c'][j][v] + self.flag['b'][b][v] is 0:
                            self.choice[i][j][v] = 1  # 1 = True
                            self.choice[i][j][0] += 1  # counter
        if show:
            print('FLAGS:', self.flag_, sep='\n')
            print('CHOICES:', self.choice_(detail=True), sep='\n')

    def simplfy(self, *, show=True):
        _flag = True
        while _flag:
            _flag = False
            for i in range(self.size):
                for j in range(self.size):
                    if self.choice[i][j][0] is 1:
                        _flag = True
                        v = 1
                        while self.choice[i][j][v] is 0:
                            v += 1
                        self.set_(i, j, v, show=show)

            for v in range(1, len(self.selection)):
                assessed: Matrix = [[False] * self.size for _ in range(self.size)]
                for i in range(self.size):
                    for j in range(self.size):
                        if not assessed[i][j] and self.choice[i][j][v]:
                            _neighbour = self.neighbour(i, j)
                            if len(_neighbour) > 1:
                                for _i, _j in _neighbour:
                                    assessed[_i][_j] = True
                            else:
                                _flag = True
                                self.set_(i, j, v, show=show)

        if show:
            print('simplied SODUKU:', self, sep='\n')
            print('CHOICES:', self.choice_(), sep='\n')

    def solve(self, *, randomly, show):
        guess: List[Tuple] = []
        failure: Tuple[int, int] = ()
        count: int = 0
        while True:
            if not self.initialized:
                if self.islegal:
                    self.initialize_(show=show)
                else:
                    raise SudokuIsIllegal
                self.initialized = True
            self.simplfy(show=show)

            if self.iscompleted:
                print('  ' * (len(guess) - 1), 'completed: ', count, sep='')
                raise SudokuIsCompleted

            elif self.islegal:
                if not self.confirmed:
                    print('CONFIRMED:', self, sep='\n')
                    self.confirmed = True
                # guess
                bestchoice = self.makechoice(randomly=randomly, failure=failure, show=show)
                backup = copy.deepcopy((self.table, self.flag, self.choice))
                guess.append((backup, *bestchoice))
                _choice = (bestchoice[0], bestchoice[1], self.selection[bestchoice[2]])
                print('> ' * (len(guess) - 1), 'guess: ', _choice, sep='')
                count += 1
                if show:
                    print()
                self.set_(*bestchoice, show=show)

            elif len(guess) is 0:
                print('illegal!')
                raise SudokuIsIllegal

            else:
                [backup, wrongi, wrongj, wrongv] = guess[-1]
                _choice = (wrongi, wrongj, self.selection[wrongv])
                print('  ' * (len(guess) - 2) + '< ', 'wrong: ', _choice, sep='')
                del guess[-1]
                self.table, self.flag, self.choice = copy.deepcopy(backup)
                self.choice[wrongi][wrongj][wrongv] = 0
                self.choice[wrongi][wrongj][0] -= 1
                if show:
                    print('BACKUP:')
                    print(self)
                    # print('FLAGS:', self.flag_, sep='\n')
                    print('CHOICES:', self.choice_(), sep='\n')
                    failure = (wrongi, wrongj)

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
                p = self.selection[self[i][j]]
                if self[i][j] is 0:
                    p = '-'
                q = ' '
                _str += p + q
            _str += '\n'
        # _str = _str[:-1]
        return _str

    def choice_(self, *, detail=False) -> str:
        _str: str = ''
        for i in range(self.size):
            for j in range(self.size):
                if self.choice[i][j][0] is not 0:
                    p = '%3d' % self.choice[i][j][0]
                else:
                    p = '  -'
                _str += p
            _str += '\n'
        if detail:
            for v in range(1, len(self.selection)):
                _str += 'choice of %d:\n' % v
                for i in range(self.size):
                    for j in range(self.size):
                        if self.choice[i][j][v] is 0:
                            p = '-'
                        elif self.choice[i][j][v] is 1:
                            p = self.selection[v]
                        else:
                            p = '+'
                        _str += p + ' '
                    _str += '\n'
        return _str

    @property
    def flag_(self) -> str:
        _str: str = ''
        for index in Sudoku.map:
            _str = _str + Sudoku.map[index] + ':\n'
            for sequence in self.flag[index]:
                for v in range(1, len(self.selection)):
                    if sequence[v] is 0:
                        p = '-'
                    elif sequence[v] is 1:
                        p = self.selection[v]
                    else:
                        p = '+'
                    _str += p + ' '
                _str += '\n'
        # _str = _str[:-1]
        return _str

    @property
    def islegal(self) -> bool:
        if self.choice is ():
            for index in Sudoku.map:
                for sequence in self.flag[index]:
                    for number in sequence[1:]:
                        if number > 1:
                            return False
        else:
            for i in range(self.size):
                for j in range(self.size):
                    if self[i][j] + self.choice[i][j][0] is 0:
                        return False
        return True

    @property
    def iscompleted(self) -> bool:
        for i in range(self.size):
            for j in range(self.size):
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
    code = 6
    size = 16
    selection = '-0123456789ABCDEF'
    randomly = False
    show = False
    main(_in='sudoku.in%d.txt' % code, size=size, selection=selection, randomly=randomly, show=show)
