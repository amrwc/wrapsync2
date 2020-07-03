"""
Common utitilies.
"""

from datetime import datetime
from sys import exit, stdout


def raise_error(message, cmd=[]):
    """
    Prints the given error message and exits with a non-zero code.
    @param message: error message
    """
    print_coloured(f"[{get_time()}] ", 'white')
    print_coloured('ERROR: ', 'red', 'bold')
    if cmd:
        print_coloured(f"{message}\n", 'red')
        print_cmd(cmd)
        print('')
    else:
        print_coloured(f"\n{message}\n\n", 'red')
    usage()
    exit(1)


def usage():
    """
    Prints usage instructions.
    """
    print_coloured('Usage:\n', 'white', 'bold')
    print_coloured('$ ./wrapsync2.py ', 'white')
    print_coloured('<push/pull> <dir_name/all> [rsync_options]\n', 'yellow', 'bold')


def print_cmd(cmd):
    """
    Prints the given `rsync` command to the console.
    @param cmd: rsync command in a list form
    """
    print_coloured(f"{' '.join(cmd)}\n", 'grey')


def get_time():
    """
    Returns current time.
    @return: time in HH:MM:SS format
    """
    return datetime.now().strftime('%H:%M:%S')


def print_coloured(text, colour, effect=''):
    """
    Prints the given text in the given colour and effect.
    @param text: message to print out
    @param colour: display colour
    @param effect: (optional) effect to use, such as 'bold' or 'underline'
    """
    text_effect = get_text_effect(effect)
    stdout.write(
        f"{text_effect}{get_colour(colour)}{text}{get_text_effect('reset')}")


def get_colour(colour):
    """
    Returns an ANSI escape sequence for the given colour.
    @param colour: name of the colour
    @return: escape sequence for the given colour
    """
    sequence_base = '\033['
    colours = {
        'red': '31m',
        'yellow': '33m',
        'green': '32m',
        'grey': '37m',
        'white': '97m'
    }
    return f"{sequence_base}{colours[colour]}"


def get_text_effect(effect):
    """
    Returns an ASCII escape sequence for a text effect, such as 'bold'.
    @param effect: name of the effect
    @return: escape sequence for the given effect
    """
    sequence_base = '\033['
    effects = {
        '': '',
        'reset': '0m',
        'bold': '1m',
        'underline': '4m'
    }
    return f"{sequence_base}{effects[effect]}"
