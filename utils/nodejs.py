# -*- coding: utf-8 -*-
import subprocess
import os

from utils import utils

PROJ_PATH = utils.get_path_with_base_file(__file__, '..')
TMP_PATH = utils.get_path_with_base_file(__file__, '../tmp')


class CmdError(Exception):
    pass


def run_nodejs(script_path, args, input_text):
    input_text = input_text or ''
    args = args or []
    result = ''

    if os.path.exists(TMP_PATH):
        os.remove(TMP_PATH)
    with open(TMP_PATH, 'wt', encoding='utf-8') as fd:
        fd.write(input_text)

    command = ['node', '--experimental-modules']
    command.append(script_path)
    command.extend(args)
    command.append(TMP_PATH)
    ret = subprocess.call(command, shell=True, cwd=PROJ_PATH)
    if ret != 0:
        cmd_str = command
        if isinstance(command, list):
            cmd_str = ' '.join(command)
        message = "Error running command: %s", cmd_str
        raise CmdError(message)

    with open(TMP_PATH, 'rt', encoding='utf-8') as fd:
        result = fd.read()
    if os.path.exists(TMP_PATH):
        os.remove(TMP_PATH)
    return result
