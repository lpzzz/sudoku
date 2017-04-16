# -*- coding:utf-8 -*-
# __author__ = 'L'

from typing import List, Dict, Tuple, Set, Any
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
        self.num = len(self.selection)
        self.coor: List[Tuple[int, int]] = []
        for i, j in itertools.product(range(self.size), repeat=2):
            self.coor.append((i, j))
        self.table: Matrix = [[0] * self.size for _ in range(self.size)]
        self.box: Matrix = [[0] * self.size for _ in range(self.size)]
        s = int(self.size ** 0.5)
        for i, j in self.coor:
            self.box[i][j] = i // s * s + j // s
        self.choice: Matrix = ()
        self.initialized = False
        self.confirmed = False

        if table is not ():
            if self.ismatrix(table):
                for i, j in self.coor:
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
        if v is 0:
            v = self[i][j]
            if v is not 0:
                self[i][j] = 0
                self.initialize_(show=show)
        else:
            self[i][j] = v
            if self.initialized:
                for _i, _j in self.neighbour(i, j, v):
                    self.choice[_i][_j].remove(v)
                self.choice[i][j] = set()
        if show:
            print('(%s, %s) = %s' % (i, j, self.selection[v]))
            print(self)

    def neighbour(self, i: int, j: int, v: int, *, area='choice', stats=False):
        _neighbour: Points = set()
        row, col, box = -1, -1, -1
        for _i in range(self.size):
            if area is 'choice' and v in self.choice[_i][j]:
                _neighbour.add((_i, j))
                row += 1
            elif area is 'table' and self[_i][j] is v:
                _neighbour.add((_i, j))

        for _j in range(self.size):
            if area is 'choice' and v in self.choice[i][_j]:
                _neighbour.add((i, _j))
                col += 1
            elif area is 'table' and self[i][_j] is v:
                _neighbour.add((i, _j))

        b = self.box[i][j]
        for _i, _j in self.coor:
            if self.box[_i][_j] is b:
                if area is 'choice' and v in self.choice[_i][_j]:
                    _neighbour.add((_i, _j))
                    box += 1
                elif area is 'table' and self[_i][_j] is v:
                    _neighbour.add((_i, _j))

        if stats:
            return _neighbour, row, col, box
        else:
            return _neighbour

    def makechoice(self, *, randomly=False, show=False):
        candidate: List[Tuple[int, int, int]] = []
        qualified = 1
        while len(candidate) is 0:
            qualified += 1
            for i, j in self.coor:
                if len(self.choice[i][j]) is qualified:
                    for v in range(1, self.num):
                        if v in self.choice[i][j]:
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
        for i, j in self.coor:
            self.choice[i][j] = set()
            for v in range(1, self.num):
                self.choice[i][j].add(v)
        for i, j in self.coor:
            if self[i][j] is not 0:
                v = self[i][j]
                self.choice[i][j] = set()
                _neighbour = self.neighbour(i, j, 0, area='table')
                for _i, _j in _neighbour:
                    if v in self.choice[_i][_j]:
                        self.choice[_i][_j].remove(v)
        
        if show:
            print('CHOICES:', self.choice_(detail=True), sep='\n')

    def simplfy(self, *, show=True):
        _flag = True
        while _flag:
            _flag = False
            for i, j in self.coor:
                if len(self.choice[i][j]) is 1:
                    _flag = True
                    v = list(self.choice[i][j])[0]
                    self.set_(i, j, v, show=show)

            for v in range(1, self.num):
                for i, j in self.coor:
                    if v in self.choice[i][j]:
                        _neighbour, row, col, box = self.neighbour(i, j, v, stats=True)
                        if row * col * box is 0:
                            _flag = True
                            self.set_(i, j, v, show=show)
            
        if show:
            print('simplied SODUKU:', self, sep='\n')
            print('CHOICES:', self.choice_(), sep='\n')

    def solve(self, *, randomly, show):
        guess: List[Tuple] = []
        loop: int = 0
        while True:
            if not self.initialized:
                if self.islegal:
                    self.initialize_(show=show)
                else:
                    raise SudokuIsIllegal
                self.initialized = True
            self.simplfy(show=show)

            if self.iscompleted:
                print('  ' * (len(guess) - 1), 'completed: ', loop, sep='')
                raise SudokuIsCompleted

            elif self.islegal:
                if not self.confirmed:
                    print('CONFIRMED:', self, sep='\n')
                    self.confirmed = True
                # guess
                bestchoice = self.makechoice(randomly=randomly, show=show)
                backup = copy.deepcopy((self.table, self.choice))
                guess.append((backup, *bestchoice))
                _choice = (bestchoice[0], bestchoice[1], self.selection[bestchoice[2]])
                print('> ' * (len(guess) - 1), 'guess: ', _choice, sep='')
                loop += 1
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
                self.table, self.choice = copy.deepcopy(backup)
                self.choice[wrongi][wrongj].remove(wrongv)
                if show:
                    print('BACKUP:')
                    print(self)
                    # print('FLAGS:', self.flag_, sep='\n')
                    print('CHOICES:', self.choice_(), sep='\n')

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
                if len(self.choice[i][j]) is not 0:
                    p = '%-2d' % len(self.choice[i][j])
                else:
                    p = '- '
                _str += p
            _str += '\n'
        if detail:
            for v in range(1, self.num):
                _str += 'choice of %d:\n' % v
                for i in range(self.size):
                    for j in range(self.size):
                        if v not in self.choice[i][j]:
                            p = '-'
                        else:
                            p = self.selection[v]
                        _str += p + ' '
                    _str += '\n'
        return _str

    @property
    def count(self) -> List[int]:
        _count = [0] * self.num
        for i, j in self.coor:
            _count[self[i][j]] += 1
        return _count

    @property
    def islegal(self) -> bool:
        if not self.initialized:
            for i, j in self.coor:
                if self[i][j] is not 0 and len(self.neighbour(i, j, self[i][j], area='table')) > 1:
                    return False
        else:
            for i, j in self.coor:
                if self[i][j] is 0 and len(self.choice[i][j]) is 0:
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
    code = 2
    randomly = False
    show = True
    main(_in='sudoku.in%d.txt' % code, size=size, selection=selection, randomly=randomly, show=show, )
