#!/usr/bin/env python
# encoding: utf-8

import pool_core
import argparse
import sys

# CURRENT_ITEM_GETTER_MAP = {
#'base16-shell': pool_core.current_base16_shell_scheme,
#'zsh_prompt_theme': pool_core.current_zsh_prompt_theme,
#}

ACTION_MAP = {
    'like': pool_core.pool.like,
    'ban': pool_core.pool.ban,
    'free': pool_core.pool.free,
    'list': pool_core.pool.list,
    'info': pool_core.pool.info,
    'pick': pool_core.pool.pick,
    'current': pool_core.pool.current,
    'white_list': pool_core.pool.white_list,
    'free_list': pool_core.pool.free_list,
    'black_list': pool_core.pool.black_list,
}

POOL_FACTORY_MAP = {
    'b': pool_core.pool.base16_shell_theme_pool,
    'base16': pool_core.pool.base16_shell_theme_pool,
    'z': pool_core.pool.zsh_prompt_theme_pool,
    'zsh_prompt': pool_core.pool.zsh_prompt_theme_pool,
}

# command interface
cmd = argparse.ArgumentParser(
    prog='pool',
    description='favorite pool utility',
    epilog='this is epilog',
    formatter_class=argparse.ArgumentDefaultsHelpFormatter
)

cmd.add_argument(
    'what',
    choices=['b', 'base16', 'z', 'zsh_prompt'],
    help='kind of the pool to manage'
)

cmd.add_argument(
    'action',
    choices=ACTION_MAP.keys() + ['reset'],
    nargs='?',
    default='info',
    help='action to apply onto the item')

cmd.add_argument(
    'item',
    nargs='*',
    help='the target item'
)

cmd.add_argument(
    '-r',
    '--rights',
    nargs=2,
    help='change white/free item rights'
)

cmd.add_argument(
    '-x',
    action='store_true',
    help='test argpase code'
)

ns = cmd.parse_args()
if ns.x:
    print(ns)
    sys.exit()

if ns.action == 'reset':
    _map = {
        'b': 'base16',
        'base16': 'base16',
        'z': 'zsh_prompt',
        'zsh_prompt': 'zsh_prompt',
    }

    pool_core.pool.reset(_map[ns.what])

    sys.exit()

obj = POOL_FACTORY_MAP[ns.what]()

# if '-r, --rights' is given, change rights and exit
if ns.rights:
    obj.set_rights(*ns.rights, dump=True)
    sys.exit()

method = ACTION_MAP[ns.action]

if ns.action in (
        'list',
        'info',
        'pick',
        'current',
        'white_list',
        'free_list',
        'black_list'):
    method(obj)
elif ns.action in ('like', 'ban', 'free'):
    method(obj, ns.item)
    pass
else:
    print('* unhandled command action: {} *'.format(ns.action))
