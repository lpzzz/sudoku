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

    def __init__(self, *, name: str = '', table: Matrix = (), box: Matrix = ()):
        self.name = name
        self.table: Matrix = [[0] * 9 for _ in range(9)]
        self.box: Matrix = [[0, 0, 0, 1, 1, 1, 2, 2, 2],
                            [0, 0, 0, 1, 1, 1, 2, 2, 2],
                            [0, 0, 0, 1, 1, 1, 2, 2, 2],
                            [3, 3, 3, 4, 4, 4, 5, 5, 5],
                            [3, 3, 3, 4, 4, 4, 5, 5, 5],
                            [3, 3, 3, 4, 4, 4, 5, 5, 5],
                            [6, 6, 6, 7, 7, 7, 8, 8, 8],
                            [6, 6, 6, 7, 7, 7, 8, 8, 8],
                            [6, 6, 6, 7, 7, 7, 8, 8, 8]]
        self.flag: Dict[str, Matrix] = {}
        for index in Sudoku.map:
            self.flag[index] = [None] * 9
            for i in range(9):
                self.flag[index][i] = [0] * 10
        self.choice: Matrix = ()
        self.initialized = False
        self.confirmed = False

        if table is not ():
            if ismatrix(table):
                for i in range(9):
                    for j in range(9):
                        self.set_(i, j, table[i][j])
            else:
                raise ValueError

        if box is not ():
            if ismatrix(box):
                self.box = box
            else:
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
                self.choice[i][j] = [0] * 10
        if show:
            print('(%s, %s) = %s' % (i, j, v))
            print(self)

    def neighbour(self, i: int, j: int, v: int=0) -> Points:
        _neighbour: Points = set()
        for _i in range(9):
            if not v or self.choice[_i][j][v]:
                _neighbour.add((_i, j))
        for _j in range(9):
            if not v or self.choice[i][_j][v]:
                _neighbour.add((i, _j))
        b = self.box[i][j]
        for _i in range(9):
            for _j in range(9):
                if self.box[_i][_j] is b:
                    if not v or self.choice[_i][_j][v]:
                        _neighbour.add((_i, _j))
        return _neighbour

    def makechoice(self, *, randomly=False, failure: Tuple[int, int]=(), show=False):
        candidate: List[Tuple[int, int, int]] = []
        qualified = 1
        while len(candidate) is 0:
            qualified += 1
            for i in range(9):
                for j in range(9):
                    if self.choice[i][j][0] is qualified:
                        for v in range(1, 10):
                            if self.choice[i][j][v]:
                                candidate.append((i, j, v))
        if show:
            print('Standard:', qualified)
            print('among:',)
            site: Dict[Tuple[int, int], List[int]] = {}
            for i, j, v in candidate:
                if (i, j) not in site:
                    site[(i, j)] = []
                site[(i, j)].append(v)
            for s in site:
                print(s, ':', end=' ')
                for _candidate in site[s]:
                    print(_candidate, end=' ')
                print()

        if failure is not () and self.choice[failure[0]][failure[1]][0] > 1:
            print(self, self.choice_(), sep='\n')
            _i, _j = failure
            _v, _n = 0, 0
            for v in range(1, 10):
                _neighbour = self.neighbour(_i, _j, v)
                if _n is 0 or len(_neighbour) < _n:
                    _v, _n = v, len(_neighbour)
            print('Failure: (%d, %d)' % (_i, _j))
            return _i, _j, _v
        elif randomly:
            return random.choice(candidate)
        else:
            _i, _j, _v, _n = 9, 9, 0, 0
            for i, j, v in candidate:
                _neighbour = self.neighbour(i, j, v)
                if _n is 0 or len(_neighbour) < _n:
                    _i, _j, _v, _n = i, j, v, len(_neighbour)

        print('Loneliest:', _n)
        return _i, _j, _v

    def initialize_(self, *, show=False):
        self.choice = [[None] * 9 for _ in range(9)]
        for i in range(9):
            for j in range(9):
                self.choice[i][j] = [0] * 10
                if self[i][j] is 0:
                    for v in range(1, 10):
                        b = self.box[i][j]
                        if self.flag['r'][i][v] + self.flag['c'][j][v] + self.flag['b'][b][v] is 0:
                            self.choice[i][j][v] = 1    # 1 = True
                            self.choice[i][j][0] += 1   # counter
        if show:
            print('FLAGS:', self.flag_, sep='\n')
            print('CHOICES:', self.choice_(detail=True), sep='\n')

    def simplfy(self, *, show=True):
        _flag = True
        while _flag:
            _flag = False
            for i in range(9):
                for j in range(9):
                    if self.choice[i][j][0] is 1:
                        _flag = True
                        v = 1
                        while self.choice[i][j][v] is 0:
                            v += 1
                        self.set_(i, j, v, show=show)

            for v in range(1, 10):
                assessed: Matrix = [[False] * 9 for _ in range(9)]
                for i in range(9):
                    for j in range(9):
                        if not assessed[i][j] and self.choice[i][j][v]:
                            _neighbour = self.neighbour(i, j)
                            if len(_neighbour) > 1:
                                for _i, _j in _neighbour:
                                    assessed[_i][_j] = True
                            else:
                                _flag = True
                                self.set_(i, j, v, show=show)

        if show:
            print('Simplied SODUKU:', self, sep='\n')
            print('CHOICES:', self.choice_(), sep='\n')

    def solve(self, *, guess: List[Tuple]=None, failure: Tuple[int, int]=(), randomly, show):
        if not self.initialized:
            if self.islegal:
                self.initialize_(show=show)
            else:
                raise SudokuIsIllegal
            self.initialized = True
        self.simplfy(show=show)

        if self.iscompleted:
            raise SudokuIsCompleted

        elif self.islegal:
            if not self.confirmed:
                print('Confirmed:', self, sep='\n')
                self.confirmed = True
            # guess
            bestchoice = self.makechoice(randomly=randomly, failure=failure, show=show)
            if guess is None:
                guess = []
            backup = copy.deepcopy(self.table), copy.deepcopy(self.flag), copy.deepcopy(self.choice)
            guess.append((backup, *bestchoice))
            print('> ' * (len(guess) - 1), 'guess: ', bestchoice, sep='')
            if show:
                print()
            self.set_(*bestchoice, show=show)
            return self.solve(guess=guess, randomly=randomly, show=show)

        elif guess is None:
            raise SudokuIsIllegal

        else:
            print('  ' * (len(guess) - 2) + '< ', 'wrong: ', guess[-1][1:], sep='')
            [backup, wrongi, wrongj, wrongv] = guess[-1]
            del guess[-1]
            if len(guess) is 0:
                guess = None
            self.table = copy.deepcopy(backup[0])
            self.flag = copy.deepcopy(backup[1])
            self.choice = copy.deepcopy(backup[2])
            self.choice[wrongi][wrongj][wrongv] = 0
            self.choice[wrongi][wrongj][0] -= 1
            if show:
                print('backup:')
                print(self)
                # print('FLAGS:', self.flag_, sep='\n')
                print('CHOICES:', self.choice_(), sep='\n')
            return self.solve(guess=guess, failure=(wrongi, wrongj), randomly=randomly, show=show)

    def __str__(self):
        _str: str = ''
        for i in range(9):
            for j in range(9):
                p = str(self[i][j])
                if self[i][j] is 0:
                    p = '-'
                q = ' '
                _str = _str + p + q
            _str += '\n'
        # _str = _str[:-1]
        return _str

    @property
    def flag_(self) -> str:
        _str: str = ''
        for index in Sudoku.map:
            _str = _str + Sudoku.map[index] + ':\n'
            for sequence in self.flag[index]:
                for v in range(1, 10):
                    if sequence[v] is 0:
                        p = '-'
                    elif sequence[v] is 1:
                        p = str(v)
                    else:
                        p = '+'
                    _str = _str + p + ' '
                _str += '\n'
        # _str = _str[:-1]
        return _str

    def choice_(self, *, detail=False) -> str:
        _str: str = ''
        for i in range(9):
            for j in range(9):
                if self.choice[i][j][0] is not 0:
                    p = str(self.choice[i][j][0])
                else:
                    p = '-'
                _str = _str + p + ' '
            _str += '\n'
        if detail:
            for v in range(1, 10):
                _str += 'choice of %d:\n' % v
                for i in range(9):
                    for j in range(9):
                        if self.choice[i][j][v] is 0:
                            p = '-'
                        elif self.choice[i][j][v] is 1:
                            p = str(v)
                        else:
                            p = '+'
                        _str = _str + p + ' '
                    _str += '\n'
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
            for i in range(9):
                for j in range(9):
                    if self[i][j] + self.choice[i][j][0] is 0:
                        return False
        return True

    @property
    def iscompleted(self) -> bool:
        for i in range(9):
            for j in range(9):
                if self[i][j] is 0:
                    return False
        return True


class SudokuIsIllegal(Exception):
    pass


class SudokuIsCompleted(Exception):
    pass


def ismatrix(suspect) -> bool:
    _flag = True
    if len(suspect) == 9:
        for sequence in suspect:
            if len(sequence) != 9:
                _flag = False
            for point in sequence:
                if type(point) is not int:
                    _flag = False
                elif point < 0 or point > 9:
                    _flag = False
    else:
        _flag = False
    return _flag


def fileinput(_in) -> Matrix:
    if _in is '':
        _in = input('fileinput: ')
    with codecs.open('%s.txt' % _in, 'r', 'utf-8') as f:
        str_in = f.read()
    _table = [[0] * 9 for _ in range(9)]
    i = 0
    j = 0
    l = len(str_in)
    while i < 81 and j < l:
        while not str_in[j].isdigit():
            j = j + 1
        _table[i // 9][i % 9] = int(str_in[j])
        i += 1
        j += 1
    return _table


def main(*, _in: str = '', _out: str = '', randomly=False, show=False):
    _table: Matrix = fileinput(_in)
    fout = None
    if _out is not '':
        fout = StringIO()
    question = Sudoku(name='QUESTION', table=_table)
    sudoku = Sudoku(name='ANSWER', table=_table)
    print('QUESTION:', question, sep='\n', file=fout)

    try:
        sudoku.solve(randomly=randomly, show=show)
    except SudokuIsIllegal:
        print('\n>>>> Sudoku is illegal <<<<\n')
    except SudokuIsCompleted:
        print('ANSWER:', sudoku, sep='\n', file=fout)
        if fout is not None:
            with codecs.open('%s.txt' % _out, 'w+', 'utf-8') as f:
                print('\n----------------------------\n')
                print(fout.getvalue())
                f.write(fout.getvalue())
                fout.close()

    return question, sudoku


def test():
    pass


if __name__ == '__main__':
    code = 5
    randomly = True
    show = True
    main(_in='sudoku.in%d' % code, _out='sudoku.out%d' % code, randomly=randomly, show=show)
