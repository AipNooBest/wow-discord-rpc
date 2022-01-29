import sys
import rpc
import time
import json
import os
import ast
from PIL import Image, ImageGrab
import win32gui
import win32api
import win32con
import logging

# localisation variables. Change them for your preferences.
inMainMenu = "In main menu"

# these are internal use variables, don't touch them, unless you know what you're doing.
logging.basicConfig(filename='log.txt', filemode='w', encoding='utf-8', level=logging.INFO)
decoded = ''
wow_hwnd = None
rpc_obj = None
timePlayed = None
dir_path = os.path.dirname(os.path.realpath(__file__))
f = open(dir_path + '/zones.txt')
zones = ast.literal_eval(f.read())
print("The script is running!\n"
      "Now you can minimize the window and play WoW.\n"
      "The script will terminate automatically when you exit the game.\n"
      "Check log.txt if you need detailed information.")


def callback(hwnd, extra):
    global wow_hwnd
    if (win32gui.GetWindowText(hwnd) == 'World of Warcraft' and
            win32gui.GetClassName(hwnd).startswith('GxWindowClass')):
        wow_hwnd = hwnd


def getImage(rect, offsetX, offsetY, iter):
    new_rect = (rect[0] + offsetX, rect[1] + offsetY, rect[2], rect[1] + offsetY + 2)
    logging.debug("Window rectangle: %s; Iteration %s", str(new_rect), iter)
    try:
        im = ImageGrab.grab(new_rect, all_screens=True)
        logging.debug("Pixel at position 0,0: " + str(im.getpixel((0, 0))))
        # Firstly try to get pixels at absolute position 0, 0 - if the game is running in borderless mode.
        if im.getpixel((0, 0)) == (36, 36, 36):
            return im
        # If 0, 0 coordinates are wrong, the game is probably running in windowed mode with borders.
        else:
            if iter == 0:
                # Getting height of the windows border (this may vary depending on DWM scaling, so hard-coding is bad).
                height = (win32api.GetSystemMetrics(win32con.SM_CYCAPTION) +
                          win32api.GetSystemMetrics(win32con.SM_CYBORDER) * 4 +
                          win32api.GetSystemMetrics(win32con.SM_CYEDGE) * 2)
                logging.debug("Window border height: %s" % height)
                # Check if the game is running fullscreen-windowed mode with borders, so we apply only Y offset.
                return getImage(rect, offsetX, height, 1)
            elif iter == 1:
                # The last option - the game is running in pure windowed mode, so we apply both offsets.
                return getImage(rect, 8, offsetY, 2)
            # If neither of the above options are true, the pixel array is probably does not exist.
            return False
    except Image.DecompressionBombError:
        logging.error('DecompressionBombError')
        return False


def read_squares(hwnd):
    global decoded
    rect = win32gui.GetWindowRect(hwnd)
    im = getImage(rect, 0, 0, 0)
    if im is False:
        return 1

    # Check if there's a message at the top left corner.
    # If there's none, then we're either in main menu or addon is not working.
    # Sometimes addon moves 1 px to the right, so we check if that is the case.
    offset = 0
    if im.getpixel((1, 0)) == (0, 0, 0):
        logging.debug("Pixels are 1x1 starting at position 0")
    # Second pixel also can be duplicated due to resizing.
    elif im.getpixel((1, 0)) == (36, 36, 36) and (im.getpixel((2, 0)) == (0, 0, 0) or im.getpixel((2, 0)) == (36, 36, 36)):
        logging.debug("Pixels are more than 1x1 or they start at position 1")
        offset += 1
    else:
        logging.info("Could not find pixel array. You're either in main menu or addon is not working")
        return 1

    read = []
    duplicate = False
    for square_idx in range(offset, int(im.width)):
        r, g, b = im.getpixel((square_idx, 0))

        if r == g == b == 255:
            break

        if r == g == b == 0:
            duplicate = False
            continue

        if not duplicate:
            read.append(r)
            read.append(g)
            read.append(b)
            duplicate = True

    try:
        decoded = bytes(read).decode('utf-8').rstrip('\0')
    except Exception as exc:
        logging.error('Error decoding the pixels: %s.' % exc)
        print('Something is overlapping information pixels, or the game is running in full-screen. '
              'If it so, change the mode to windowed or borderless.')
        return 0
    parts = decoded.replace('$$$', '').split('|')

    # sanity check
    if (not decoded.endswith('$$$') or not decoded.startswith('$$$')):
        return 0

    return parts


def connect_to_discord():
    global rpc_obj
    if not rpc_obj:
        logging.info('Not connected to Discord, connecting...')
        while True:
            try:
                rpc_obj = (rpc.DiscordIpcClient
                           .for_platform("827272838771507210"))
            except Exception as exc:
                logging.warning("I couldn't connect to Discord (%s). It's "
                                'probably not running. I will try again in 5 '
                                'sec.' % str(exc))
                time.sleep(5)
                pass
            else:
                break


def update_activity(activity):
    global rpc_obj
    try:
        rpc_obj.set_activity(activity)
    except Exception as exc:
        logging.warning('Looks like the connection to Discord was broken (%s). '
                        'I will try to connect again in 5 sec.' % str(exc))
        rpc_obj = None


while True:
    wow_hwnd = None
    win32gui.EnumWindows(callback, None)

    if win32gui.GetForegroundWindow() == wow_hwnd:
        lines = read_squares(wow_hwnd)

        if not lines:  # Something went wrong
            time.sleep(5)
            continue

        # We know that we're either in main menu or addon is not working
        elif lines == 1:
            connect_to_discord()
            if timePlayed is None:
                timePlayed = {'start': round(time.time())}
            activity = {
                'details': inMainMenu,
                'timestamps': timePlayed,
                'assets': {
                    'large_image': "wow-icon"
                }
            }
            logging.info("Setting activity: %s" % inMainMenu)
            update_activity(activity)
            time.sleep(3)
            continue
        else:
            zoneName, playerLevel, playerName, playerInfo, engClass, playerState, mapID = lines
            connect_to_discord()

            logging.info('Setting new activity: %s - %s - %s - %s - %s - %s - %s' % (
                zoneName, playerLevel, playerName, playerInfo, engClass, playerState, mapID))

            if timePlayed is None:
                timePlayed = {'start': round(time.time())}
            if mapID in zones.keys():
                zone = zones[str(mapID)]
            else:
                zone = "wow-icon"
                logging.warning("The zone is not in the list: %s [ID: %s]" % (zoneName, mapID))
            activity = {
                'details': "%s [%s LVL]" % (playerName, playerLevel),
                'state': playerState,
                'assets': {
                    'large_image': zone,
                    'large_text': zoneName,
                    'small_image': engClass.lower(),
                    'small_text': playerInfo
                },
                'timestamps': timePlayed
            }
            update_activity(activity)

    elif not wow_hwnd and rpc_obj:
        logging.info('WoW no longer exists, terminating...')
        rpc_obj.close()
        sys.exit()
    time.sleep(5)
