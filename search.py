#!/usr/bin/python3

import argparse
import pdb

help_msg = '''
Given two files:
  (1) a rectagular letter grid (i.e. word-search puzzle), and
  (2) a list of words, one per line
Print each word with one or more "origins", or "False" if not found.
Each word origin is {row}_{column}_{direction}, e.g. "12_5_UL", where
"UL" means the upper-left diagonal starting from (12,5).
'''

# 2019-05 Mark Beutnagel
#
# - NB: To avoid spurious duplication, all single-letter "strings" are
# recorded with 'X' representing a null direction: "X marks the spot".
# This will prevent the word "A" from appearing 8 times at the same coordinate,
# each with a different direction.

##-----------------------------------------------------------------------
## Constants

# Directions within letter grid are the cap-letter abbreviations of
#   Right, Left, Up, Down, UpRight, UpLeft, DownRight, DownLeft
# The table values are (row, column) increments to index the next character
# in a row, column, or diagonal. Special non-direction X applies only to
# single-characters, and is used to prevent the single-character work "A"
# from being recorded with 8 different directions.

# TODO? for 'X' we could replace (None,None) with (MAXINT, MAXINT).
# One step in any direction is outside the puzzle and no further logic
# is needed to prevent use.


DIRECTIONS = {
    'U':  (-1, 0), 
    'UR': (-1, +1),
    'R':  (0, +1),
    'DR': (+1, +1),
    'D':  (+1, 0),
    'DL': (+1, -1),
    'L':  (0, -1),
    'UL': (-1, -1),
    'X':  (None, None)
}

WORD_ORIGIN = 'WordOrigin'

# TODO? Create a TrieNode class rather than use a special key?
# Keep a list of word-start locations in each node, for now just by
# using a non-letter key within the letter dictionary. Example: if
# the word "atom" apears twice in the puzzle, and "atomic" appears once,
# the trie might contain
#    ... {'o': {'m': {'WORD_ORIGIN': [(3,6,'DR'),(12,8,'U')], 'i': {...},
# So, "atom" apears at row 3, column 6 going down-right and at row 12, column 3
# straight up. Note that the 'm' node contains both the origin info and
# the continuation of the word 'atomic'. Also note that every node leading
# down to atomic will include the same origin info for that word, so e.g.
# the word "at" will include the same origin, and perhaps many others.

##-----------------------------------------------------------------------
## Utility Functions

def populate_trie(trie, grid, nrows, ncols, env):
    '''For every starting point and every direction, scan that string into the trie.'''
    if env['verbose']: print(grid)
    for row in range(nrows):
        if env['verbose']: print(f'processing row {row}')
        for col in range(ncols):
            if env['verbose']: print(f'processing column {col}')
            for d in DIRECTIONS:
                if d in ['X']:
                    continue
                r_step, c_step = DIRECTIONS[d]
                if env['verbose']: print(f'processing direction {d}')
                # first level uses the 'X' to collapse directions for single-letters
                multi_character = False
                origin_x = f'{row}_{col}_X'
                origin = f'{row}_{col}_{d}'
                # temporary vars for loop below
                r, c, t = row, col, trie
                while r>=0 and r<nrows and c>=0 and c<ncols:
                    letter = grid[r][c]
                    if env['verbose']: print(f'letter: {letter} at ({r},{c})')
                    if not letter in t:
                        # uses set() to collapse multiple 'X' origin entries
                        t[letter] = {WORD_ORIGIN: set()}
                    t = t[letter]
                    t[WORD_ORIGIN].add(origin if multi_character else origin_x)
                    multi_character = True
                    if env['verbose']: print(r,c,letter)
                    r += r_step
                    c += c_step

##-----------------------------------------------------------------------
## Classes

# Class Puzzle, constructed from the 2-D letter array

class Puzzle(object):

    def __init__(self, list_of_strings, env):
        self.nrows = 0
        self.ncols = 0
        self.trie = {}
        self.env = env
        if list_of_strings:
            self.ingest(list_of_strings)

    def search(self, word):
        t = self.trie
        for ch in word:
            if ch not in t:
                return False
            t = t[ch]
        return t[WORD_ORIGIN]

    def ingest(self, lofs):
        if self.trie:
            raise Exception('This object has already been initialized.')
        # validate list of strings; init number of rows & columns
        grid = []
        if not lofs:
            raise Exception('Input cannot be empty')
        if type(lofs) not in [list, tuple]:
            raise Exception('Input must be a list or tuple of strings')
        for s in lofs:
            self.nrows += 1
            if not self.ncols:
                self.ncols = len(s)
            elif self.ncols != len(s):
                raise Exception(f'Expected #columns {self.ncols}, but row {self.nrows} has {len(s)}')
            grid.append(s)
        populate_trie(self.trie, grid, self.nrows, self.ncols, self.env)


##-----------------------------------------------------------------------
## MAIN

parser = argparse.ArgumentParser(description=help_msg)
parser.add_argument('--words', type=argparse.FileType('r'), required=True, help='Filename of the word list')
parser.add_argument('--puzzle', type=argparse.FileType('r'), required=True, help='Filename of the puzzle grid')
parser.add_argument('--verbose', '-v', dest='verbose', action='store_true', default=False)

args = parser.parse_args()
puzzle = [line.strip() for line in args.puzzle]
puzzle = [line for line in puzzle if line]
words = [line.strip() for line in args.words]
words = [line for line in words if line]

env = {'verbose': args.verbose}
p = Puzzle(puzzle, env)
for w in words:
    print(w, p.search(w))

