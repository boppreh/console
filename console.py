import os, sys
try:
    from msvcrt import getch
    special_keys = {
        'H': 'up', 'P': 'down',
        'M': 'right', 'K': 'left',
    }

    def get_key():
        char = getch()
        # Arrow keys are returned as two bytes, starting with 224.
        if ord(char) == 224:
            return special_keys[getch()]
        else:
            return char

    def display(text):
        os.system('cls')
        sys.stdout.write(text)

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
    }

    # Note: window.getch() returns int, not str.
    def get_key():
        keycode = window.getch()
        if keycode > 256:
            return special_keys[keycode]
        else:
            return chr(keycode)

    def display(text):
        window.addstr(0, 0, text)
        window.clrtobot()
        window.refresh()

def get_valid_key(expected_keys):
    while True:
        key = get_key()
        if key in expected_keys:
            return key

if __name__ == '__main__':
    while True:
        key = get_key()
        print key
        if key == 'q':
            exit()
