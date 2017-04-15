# -*- coding:utf-8 -*-
# __author__ = 'L'

from sudoku_main import main
import os
import codecs

if __name__ == '__main__':
    _in, size, selection = '', '', ''
    _con = True
    while _con:
        size = input('Size of sudoku(or nothing): \n').strip()
        if size is '':
            size = 9
            _con = False
        elif size.isdigit():
            size = int(size)
            _con = False
        else:
            print('>> Please input an integer.')
    print(f'    size = {size}\n')
    _con = True
    while _con:
        selection = input('Selectable letters(or nothing): \n').replace(' ', '')
        if selection is '':
            selection = '0123456789'
            _con = False
        elif len(selection) == len(set(selection)):
            _con = False
        else:
            print('    No repetition.')
    print(f'    selection = \'{selection}\'\n')
    _con = True
    _confirm = ''
    while _con:
        if _confirm is not '':
            _in, _confirm = _confirm, ''
        else:
            _in = input('Filename of input:\n').strip()
        if os.path.exists(_in):
            with codecs.open(_in, 'r', 'utf-8') as f:
                print(f.read(), '\n', sep='')
            _confirm = input('Press ENTER to confirm\n or input another file:\n')
            if _confirm is '':
                _con = False
        else:
            print('    File does not exist.')
    
    _out = input('Filename of output (or nothing):\n').strip()
    main(_in=_in, _out=_out,  size=size, selection=selection, show=False, randomly=True)
