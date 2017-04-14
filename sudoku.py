# -*- coding:utf-8 -*-
# __author__ = 'L'

from sudoku_main import main
import os

if __name__ == '__main__':
    _con = True
    _in = ''
    while _con:
        _in = input('Filename of input:\n').strip()
        if os.path.exists(_in):
            _con = False
        else:
            print('File does not exist.')
    _out = input('Filename of output (or blank):\n').strip()
    main(_in=_in, _out=_out, show=False, randomly=True)
