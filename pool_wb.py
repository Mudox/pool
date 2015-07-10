#!/usr/bin/env python
# encoding: utf-8

import random
import pickle
import json
import os
import textwrap
import glob
import re
import time

import pickers


class pool(object):

    data_files = {
        'zsh_prompt': os.path.expanduser('~/.mdx_zsh_prompt_theme_pool'),
        'base16': os.path.expanduser('~/.mdx_base16_shell_theme_pool'),
    }

    @classmethod
    def reset(self, what):
        """
        remove data file then the next instantiation of the pool class could
        create a reseted instance.
        """

        data_file_path = self.data_files[what]

        # backup previous data file first, if any.
        if os.path.exists(data_file_path):
            backup_file_path = '{}.old.{}'.format(
                data_file_path,
                time.strftime('%Y%m%d-%H%M%S')
            )

            os.rename(data_file_path, backup_file_path)

    def __init__(
            self,
            name,
            file,
            current_item_getter,
            full_set_getter,
    ):
        """
        by default, the possibility of black set items being picked is 0.0.
        you can elevate it by adjusting white_right or free_right, making the
        sum of them less than 1.0, the remaining if the right of black set
        items

        'name': a descriptive name of the pool

        'file': the file path to hold pool persistent data.

        'current_item_getter': a function receiving no arguments to returning
            current item.

        'full_set_getter': is a function receiving no arguments returning a
            frozenset of all available items.
        """

        self._name = name

        # initialize file path for saving & loading persistent datas
        self._data_file_path = file

        # initialize sets
        self._current_item_getter = current_item_getter
        self._full_set_getter = full_set_getter

        self.json_load()

    def check_rights(self):
        """
        check the rights
        """

        try:
            # validate & initialize rights
            if self._free_right >= self._white_right:
                raise ValueError(
                    "right of free items should less than white set items")

            if self._white_right + self._free_right > 100:
                raise ValueError(
                    "invalid right combinations, sum of rights should be 1.0")

            if self._black_right >= self._free_right:
                raise ValueError(
                    "right of black set items should less than free items")
        except:
            print('white: {}   free: {}   black: {}'.format(
                self._white_right,
                self._free_right,
                self._black_right,
            ))
            raise

    def set_rights(self, white_right, free_right, dump=False):
        """
        the right value should be integer number between(0, 100), float number
        will be truncated into integer before storing.
        """

        self._white_right = int(white_right)
        self._free_right = int(free_right)

        self.check_rights()

        if dump:
            self.json_dump()

    def current(self):
        print(self._current_item)

    def check_sets(self):
        if not self._full_set:
            raise RuntimeError("empty full set")

        if not self._black_set.isdisjoint(self._white_set):
            raise RuntimeError("black & white set intersects")

        if self._black_set >= self._full_set:
            raise RuntimeError("blacked all items")

        if self._white_set >= self._full_set:
            raise RuntimeError("whited all items")

    def free_list(self):
        for item in self._free_set:
            print(item)

    def black_list(self):
        for item in self._black_set:
            print(item)

    def white_list(self):
        for item in self._white_set:
            print(item)

    @property
    def _black_right(self):
        return 100 - self._white_right - self._free_right

    @property
    def _current_item(self):
        return self._current_item_getter()

    @property
    def _full_set(self):
        return self._full_set_getter()

    @property
    def _free_set(self):
        """set of items from full_set, that is neither in white set nor black set"""
        self.check_sets
        return self._full_set - self._white_set - self._black_set

    def ban(self, items):
        """
        move item into black set, so it will not get picked up or get picked up
        with a low possibility
        """

        self.json_load()
        self.check_sets()

        if len(items) == 0:
            items = (self._current_item, )

        for item in items:
            if not item in self._full_set:
                print("* item name '{}' not exists *".format(item))
            else:
                self._black_set.add(item)

            self._white_set.discard(item)

        self.json_dump()

    def free(self, items):
        """move item out of black set or white set, so it become free again"""

        self.json_load()
        self.check_sets()

        if len(items) == 0:
            items = (self._current_item, )

        for item in items:
            if not item in self._full_set:
                print("* item name '{}' not exists *".format(item))

            self._black_set.discard(item)
            self._white_set.discard(item)

        self.json_dump()

    def like(self, items):
        """
        move item into white set, so it will get picked up with the highest
        posssibility
        """

        self.json_load()
        self.check_sets()

        if len(items) == 0:
            items = (self._current_item, )

        for item in items:
            if not item in self._full_set:
                print("* item name '{}' not exists *".format(item))
            else:
                self._white_set.add(item)

            self._black_set.discard(item)

        self.json_dump()

    def random_pick_from(self, sets):
        '''random pick from first non-empty list'''

        non_empty_sets = [s for s in sets if s]
        if not non_empty_sets:
            raise RuntimeError("* alll 3 sets are empty *")

        # set can not be indexed, so it needs to be converted into list first.
        return random.choice(list(non_empty_sets[0]))

    def pick(self):
        """pick an item according to their possibility"""

        self.check_sets()

        dice = random.randrange(100)

        if dice < self._white_right:
            # pick an item from white set
            picked = self.random_pick_from([
                self._white_set,
                self._free_set,
                self._black_set,
            ])
        elif dice < self._white_right + self._free_right:
            # pick an item from free set
            picked = self.random_pick_from([
                self._free_set,
                self._white_set,
                self._black_set,
            ])
        else:
            # pick an item from black set
            picked = self.random_pick_from([
                self._black_set,
                self._free_set,
                self._white_set,
            ])

        if picked != self._current_item:
            print(picked)
        else:
            self.pick()

    def list(self):
        for item in self._full_set:
            print(item)

    def info(self):
        print(self)

    current_data_model_version = 1

    def json_dump(self):
        """
        convert self object as json compatible list, and write to the data file.
        """
        with open(self._data_file_path, mode='w') as json_file:
            to_dump = [
                pool.current_data_model_version,
                list(self._white_set),
                list(self._black_set),
                self._white_right,
                self._free_right,
            ]
            json.dump(to_dump, json_file)

    def json_load(self):

        loaded = False

        if os.path.exists(self._data_file_path):
            with open(self._data_file_path, mode='r') as json_file:
                json_obj = json.load(json_file)

                # check version
                if pool.current_data_model_version == json_obj[0]:
                    self._white_set = set(json_obj[1])
                    self._black_set = set(json_obj[2])

                    self.set_rights(json_obj[3], json_obj[4])

                    loaded = True
                else:
                    print(
                        "* invalid data file version detected, reset with old"
                        " file renamed...*")

        if not loaded:
            self.reset_instance()

    def reset_instance(self):

        self._white_right = 80
        self._free_right = 20

        self._white_set = set()
        self._black_set = set()

    def __str__(self):

        line_width = 70

        template = '''\

        {}

        current item: {}

        white item weight: {}  free item weight: {}   black item weight: {}

        \x1b[33m{}\x1b[0m

        {}
        '''

        template = textwrap.dedent(template)

        def columnize(cells, width=70):
            if len(cells) == 0:
                return 'empty set ?'

            max_cell_width = max(map(len, cells))
            cells_per_line = (width + 1) / max_cell_width
            sep_spaces = (
                width - cells_per_line * max_cell_width) / (cells_per_line - 1)

            if cells_per_line == 0:
                raise RuntimeError(
                    "cell width: {} too long".format(max_cell_width))

            result_lines = ''
            for i, text in enumerate(cells):
                cell = text.ljust(max_cell_width + sep_spaces)
                result_lines += cell
                if (i + 1) % cells_per_line == 0:
                    result_lines += '\n'

            return result_lines

        full_list_text = columnize(self._full_set)

        tw = textwrap.TextWrapper()
        tw.width = line_width
        full_list_tex = tw.fill(full_list_text)

        white_item_sgr = '\x1b[1;4;35m'
        white_item_repl = white_item_sgr + '\g<0>\x1b[0m'
        for item in self._white_set:
            full_list_text = re.sub(item.strip(), white_item_repl, full_list_text)

        black_item_sgr = '\x1b[2m'
        black_item_repl = black_item_sgr + '\g<0>\x1b[0m'
        for item in self._black_set:
            full_list_text = re.sub(item.strip(), black_item_repl, full_list_text)

        list_head = ' \x1b[0mnormal | {}white\x1b[0m | {}black\x1b[0m'.format(white_item_sgr, black_item_sgr).rjust(line_width + 25, '-')

        text = template.format(
            '== {} =='.format(self._name.upper()).center(line_width + 15),
            '\x1b[1;34m{}\x1b[0m'.format(self._current_item),
            self._white_right,
            self._free_right,
            self._black_right,
            list_head,
            full_list_text,
        )

        return text

    @classmethod
    def base16_shell_theme_pool(self):
        '''create and return a pool to manage base16 shell color schemes'''

        def get_available_themes():
            root_dir = os.path.expandvars('$MDX_REPOS_ROOT/base16-shell/')
            pattern = os.path.join(root_dir, 'base16*.sh')
            items = glob.glob(pattern)

            # extract basename with prefixing 'base16-' & suffixing '.sh'
            # stripped
            items = [os.path.basename(p)[7:-3] for p in items]

            return frozenset(items)

        def get_current_item():
            return os.environ.get('MDX_BASE_COLOR', '')

        data_file = self.data_files['base16']

        return pool('base16 shell color scheme pool',
                    data_file,
                    get_current_item,
                    get_available_themes)

    @classmethod
    def zsh_prompt_theme_pool(self):
        '''create and return a pool to manage zsh prompt themes'''

        def get_available_themes():
            root_dir = os.path.expandvars('$ZSH/themes')
            pattern = os.path.join(root_dir, '*.zsh-theme')
            items = glob.glob(pattern)
            items = [os.path.basename(p)[:-10] for p in items]
            return frozenset(items)

        def get_current_item():
            return os.environ.get('MDX_ZSH_THEME', '')

        data_file = self.data_files['zsh_prompt']

        return pool('zsh prompt theme pool',
                    data_file,
                    get_current_item,
                    get_available_themes)

    #@staticmethod
    # def vim_color_scheme_pool():
        #'''create and return a pool to manage vim color schemes'''

        # def available_schemes():
        # schemes = []

        # schemes under vim-config/neobundle/*/colors
        # root_dir = os.path.expandvars(
        #'$MDX_REPOS_ROOT/vim-config/neobundle/')
        # pattern = os.path.join(root_dir, '*', 'colors', '*.vim')
        # items = glob.glob(pattern)
        # items = [os.path.basename(p)[:-4] for p in items]
        # schemes += items

        # schemes under vim-config/colors
        # root_dir = os.path.expandvars('$MDX_REPOS_ROOT/vim-config/colors/')
        # pattern = os.path.join(root_dir, '*.vim')
        # items = glob.glob(pattern)
        # items = [os.path.basename(p)[:-4] for p in items]
        # schemes += items

        # return frozenset(schemes)

        # file = os.path.expanduser('~/.mdx_vim_color_scheme_pool')
        # return pool('vim color scheme pool', file, available_schemes)
