import os, sys
try:
    from msvcrt import getch
    def _get_key():
        char = getch()
        # Arrow keys are returned as two bytes, starting with 224.
        if ord(char) == 224:
            name_by_second_byte = {b'H': 'up',b'P': 'down',
                                   b'M': 'right', b'K': 'left'}
            return name_by_second_byte[getch()]
        else:
            return char.decode('utf-8')

    def _display(text):
        os.system('cls')
        sys.stdout.write(text)
        sys.stdout.flush()
        return True

except ImportError:
    import curses, atexit
    window = curses.initscr()
    window.keypad(True)
    curses.noecho()
    curses.cbreak()

    # Without this the program works fine, but the terminal remains borked
    # after exit. If this happens to you, run `reset` to restore (just type and
    # press enter, even if you don't see the text).
    atexit.register(curses.endwin)
    atexit.register(curses.nocbreak)
    atexit.register(curses.echo)

    special_keys = {
        259: 'up', 258: 'down',
        261: 'right', 260: 'left',
        263: 'backspace',
        265: 'f1',
        266: 'f2',
    }

    # Note: window.getch() returns int, not str.
    def _get_key():
        keycode = window.getch()
        if keycode > 256:
            return special_keys[keycode]
        else:
            return chr(keycode)

    def _display(text):
        max_height, max_width = window.getmaxyx()
        lines = text.split('\n')
        clipped_lines = [line[:max_width] for line in lines][:max_height]
        clipped_text = '\n'.join(clipped_lines)
        window.addstr(0, 0, clipped_text)
        window.clrtobot()
        window.refresh()
        return text == clipped_text


current_text = ''

def to_str(text):
    """
    Forces a conversion of the given text to type `str`.
    Support lists of lines, matrices, bytes, numbers, etc.
    """
    if isinstance(text, list):
        if len(text) and isinstance(text[0], list):
            # Display matrices.
            return '\n'.join(''.join(map(to_str, line)) for line in text)
        else:
            # Display list of lines.
            return '\n'.join(map(to_str, text))

    if isinstance(text, bytes):
        # Decode bytes.
        return text.decode('utf-8')
    
    # General conversions to string.
    return str(text)


def display(text):
    """
    Clears the screen and refills it with the given text.

    Returns True if the console managed to print all text without clipping and
    false otherwise (Linux only, Windows always returns True).
    """
    text = to_str(text)

    # Remember text set to use in set_display.
    global current_text
    current_text = text

    return _display(text)


def set_display(x, y, text):
    """
    Changes only a portion of the display, keeping the rest constant.

    This function assumes the display has been set by the function `display`.
    Multi-character replacements are supported, but multi-line ones not.
    """
    text = to_str(text)
    lines = current_text.split('\n')
    lines[y] = lines[y][:x] + text + lines[y][x + len(text):]
    display(lines)


"""
Map of keys and functions. Every time one of these keys is pressed, the
respective function will be called. The pressed key is not returned by
get_key() or similar.
"""
hotkeys = {}

def get_key():
    """
    Waits for user keyboard input and returns the character typed, or special
    key such as "up".
    """
    while True:
        key = _get_key()
        if key in hotkeys:
            hotkeys[key]()
            continue
        else:
            return key

def get_valid_key(expected_keys):
    """
    Waits until the user presses one of the keys in `expected_keys` and returns
    it.
    """
    while True:
        key = get_key()
        if key in expected_keys:
            return key

def get_option(option_by_key):
    """
    Given a map key -> option, waits until the user selects a valid key and
    then returns the associated option.
    """
    return option_by_key[get_valid_key(option_by_key)]

def process_input(function_by_key):
    """
    Given a map key -> function, loops receiving user input and invoking the
    respective functions. Unknown keys are ignored.

    To exit the loop, raise an exception from the invoked function.
    """
    while True:
        get_option(function_by_key)()

if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.DEBUG, filename='error_log.txt')
    try:
        display('\n' * 30)
        while True:
            key = get_key()
            display(key)
            if key == 'q':
                exit()
    except Exception as e:
        logging.exception('Error!')
