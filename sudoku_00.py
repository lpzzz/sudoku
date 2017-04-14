# -*- coding: utf8 -*-
import copy

N = 3
FILENAME = 'sudoku.in%s.txt' % N
print(FILENAME)
with open(FILENAME, 'r') as f:
    STR = f.read()

FOUT = []

FORM = list('╔═══════════╤═══════════╤═══════════╗\n'
            '║ X   X   X │ X   X   X │ X   X   X ║\n'
            '║           │           │           ║\n'
            '║ X   X   X │ X   X   X │ X   X   X ║\n'
            '║           │           │           ║\n'
            '║ X   X   X │ X   X   X │ X   X   X ║\n'
            '╟───────────┼───────────┼───────────╢\n'
            '║ X   X   X │ X   X   X │ X   X   X ║\n'
            '║           │           │           ║\n'
            '║ X   X   X │ X   X   X │ X   X   X ║\n'
            '║           │           │           ║\n'
            '║ X   X   X │ X   X   X │ X   X   X ║\n'
            '╟───────────┼───────────┼───────────╢\n'
            '║ X   X   X │ X   X   X │ X   X   X ║\n'
            '║           │           │           ║\n'
            '║ X   X   X │ X   X   X │ X   X   X ║\n'
            '║           │           │           ║\n'
            '║ X   X   X │ X   X   X │ X   X   X ║\n'
            '╚═══════════╧═══════════╧═══════════╝')
INDEX = []
for i in range(len(FORM)):
    if FORM[i] == 'X':
        INDEX.append(i)

BINDEX = ((0, 0, 0, 1, 1, 1, 2, 2, 2),
          (0, 0, 0, 1, 1, 1, 2, 2, 2),
          (0, 0, 0, 1, 1, 1, 2, 2, 2),
          (3, 3, 3, 4, 4, 4, 5, 5, 5),
          (3, 3, 3, 4, 4, 4, 5, 5, 5),
          (3, 3, 3, 4, 4, 4, 5, 5, 5),
          (6, 6, 6, 7, 7, 7, 8, 8, 8),
          (6, 6, 6, 7, 7, 7, 8, 8, 8),
          (6, 6, 6, 7, 7, 7, 8, 8, 8))


class point(object):
    def __init__(self, i, j, value=0):
        self.value = value
        self.i = i
        self.j = j

    def print(self):
        prin('(%s,%s)=%s ' % (self.i, self.j, self.value))
        return


class sudoku(object):
    def __init__(self, name=''):
        self.name = name
        self.table = [None] * 9
        for i in range(9):
            self.table[i] = [0] * 9

    def print(self):
        global form
        if self.name != '':
            prin(self.name + ':\n')
        for i in range(81):
            form = FORM
            form[INDEX[i]] = str(self.table[i // 9][i % 9])
        for c in form:
            if c == '0':
                prin(' ')
            else:
                prin(c)
        prin('\n')
        return

    def check(self, i, j, delete=False, sui=False):
        flag = [[], False, False, False]
        n = self.table[i][j]
        if n == 0:
            return [[], True, True, True]
        else:
            for k in range(9):
                if k != i and self.table[k][j] == n:
                    flag[2] = True
                    flag[0].append(point(k, j, n))
                    if delete:
                        self.table[k][j] = 0
                if k != j and self.table[i][k] == n:
                    flag[1] = True
                    flag[0].append(point(i, k, n))
                    if delete:
                        self.table[i][k] = 0
            b = BINDEX[i][j]
            b1 = b // 3 * 3
            b2 = b % 3 * 3
            for k in range(b1, b1 + 3):
                for l in range(b2, b2 + 3):
                    if k == i and l == j:
                        pass
                    elif self.table[k][l] == n:
                        flag[3] = True
                        flag[0].append(point(k, l, n))
                        if delete:
                            self.table[k][l] = 0
            if sui:
                self.table[i][j] = 0
                flag[0].append(point(i, j, n))

        return flag


class part(object):
    def __init__(self, name=''):
        self.name = name
        self.table = [None] * 9
        for i in range(9):
            self.table[i] = [False] * 10
        self.index = [None] * 9
        for i in range(9):
            self.index[i] = [0] * 9

    def print(self):
        if self.name != '':
            prin(self.name + ':\n')
        for i in range(9):
            for j in range(1, 10):
                if self.table[i][j]:
                    prin('%s ' % j)
                else:
                    prin('  ')
            prin('\n')


def prin(string=None):
    FOUT.append(str(string))
    print(str(string),end='')
    return


def set(i, j, n):
    sdk.table[i][j] = n
    box.table[box.index[i][j]][n] = True
    row.table[i][n] = True
    col.table[j][n] = True
    return



def input():
    i = 0
    j = 0
    l = len(STR)
    while i < 81 and j < l:
        while not str.isdigit(STR[j]):
            j = j + 1
        set(i // 9, i % 9, int(STR[j]))
        i += 1
        j += 1
    return


def solve(what, which, option):
    k = 0
    for i in range(9):
        for j in range(9):
            k += option[0].table[i][j]
    print(k)
    if k == 0:
        return which
    return which


#==================
# Start from here
#==================

sdk = sudoku('ANSWER')
row = part('Row')
col = part('Column')
box = part('Box')

input()
SDK = sudoku('QUESTION')
SDK.table = copy.deepcopy(sdk.table)
for i in range(9):
    for j in range(9):
        row.index[i][j] = i
        col.index[i][j] = j
box.index = copy.deepcopy(BINDEX)

left = [9] * 10
left[0] = 81



opt = [None] * 10
for i in range(10):
    opt[i] = sudoku('option for %s' % i)


for k in range(1, 10):
    for i in range(9):
        for j in range(9):
            if row.table[i][k] or col.table[j][k] or box.table[box.index[i][j]][k] or sdk.table[i][j] > 0:
                pass
            else:
                opt[k].table[i][j] = k
                opt[0].table[i][j] += 1


flag = True
while flag:
    flag = False
    lis = []
    clis = []

    for i in range(9):
        for j in range(9):
            if opt[0].table[i][j] == 1:
                for k in range(1, 10):
                    if opt[k].table[i][j] == k:
                        flag = True
                        lis.append(point(i, j, k))

    for k in range(1, 10):
        for i in range(9):
            for j in range(9):
                clis = []
                clis = opt[k].check(i, j)
                if clis[1] and clis[2] and clis[3]:
                    pass
                else:
                    flag = True
                    lis.append(point(i, j, k))

    for p in lis:
        print('(%s,%s)=%s' % (p.i, p.j, p.value), end=' ')
        set(p.i, p.j, p.value)
    print()

    opt[0].print()

    while len(lis) > 0:

        clis = []
        clis = opt[lis[-1].value].check(lis[-1].i, lis[-1].j, True, True)
        for p in clis[0]:
            # p.print()
            opt[0].table[p.i][p.j] -= 1
        for k in range(1, 10):
            if opt[k].table[lis[-1].i][lis[-1].j] != 0:
                opt[k].table[lis[-1].i][lis[-1].j] = 0
                opt[0].table[lis[-1].i][lis[-1].j] -= 1

        # print(len(lis),end=' left: ')
        # print('(%s,%s)=%s'%(lis[-1].iter_index,lis[-1].j,lis[-1].value),end=' ')

        lis.pop()


sdk = solve([], sdk, opt)

SDK.print()
sdk.print()
row.print()
col.print()
box.print()

for i in range(10):
    opt[i].print()

with open('sudoku.out.txt', 'w') as f:
    for string in FOUT:
        f.write(string)
        # print(string,end='')
