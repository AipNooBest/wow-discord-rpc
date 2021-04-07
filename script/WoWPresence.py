import sys
import rpc
import time
import json
import os
import ast
from PIL import Image, ImageGrab
import win32gui

# localisation variables. Change them for your preferences.
inMainMenu = "In main menu"

# these are internal use variables, don't touch them
decoded = ''
wow_hwnd = None
rpc_obj = None
lastZone = None
lastPlayerLevel = None
lastPlayerName = None
lastPlayerInfo = None
lastEngClass = None
lastPlayerState = None
lastMapID = None
timePlayed = None
dir_path = os.path.dirname(os.path.realpath(__file__))
f = open(dir_path + '/zones.txt')
zones = ast.literal_eval(f.read())


def callback(hwnd, extra):
    global wow_hwnd
    if (win32gui.GetWindowText(hwnd) == 'World of Warcraft' and
            win32gui.GetClassName(hwnd).startswith('GxWindowClass')):
        wow_hwnd = hwnd


def read_squares(hwnd):
    global decoded
    rect = win32gui.GetWindowRect(hwnd)
    new_rect = (rect[0], rect[1], rect[2], 1)
    try:
        im = ImageGrab.grab(new_rect)
    except Image.DecompressionBombError:
        print('DecompressionBombError')
        return 0

    r, g, b = im.getpixel((0, 0))
    r2, g2, b2 = im.getpixel((1, 0))
    if not r == g == b == 36 and not r2 == g2 == b2 == 0:
        return 1

    read = []
    duplicate = False
    for square_idx in range(int(im.width)):
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
        print('Error decoding the pixels: %s.' % exc)
        return 0
    parts = decoded.replace('$$$', '').split('|')

    # sanity check
    if (len(parts) != 7 or
            not decoded.endswith('$$$') or
            not decoded.startswith('$$$')):
        return 0

    return parts


def connect_to_discord():
    global rpc_obj
    if not rpc_obj:
        print('Not connected to Discord, connecting...')
        while True:
            try:
                rpc_obj = (rpc.DiscordIpcClient
                           .for_platform("827272838771507210"))
            except Exception as exc:
                print("I couldn't connect to Discord (%s). It's "
                      'probably not running. I will try again in 5 '
                      'sec.' % str(exc))
                time.sleep(5)
                pass
            else:
                break
        print('Connected to Discord.')


def update_activity(activity):
    global rpc_obj
    global lastZone, lastPlayerLevel, lastPlayerName, lastPlayerInfo, lastEngClass, lastState
    try:
        rpc_obj.set_activity(activity)
    except Exception as exc:
        print('Looks like the connection to Discord was broken (%s). '
              'I will try to connect again in 5 sec.' % str(exc))
        lastZone, lastPlayerLevel, lastPlayerName, lastPlayerInfo, lastEngClass, lastState = None, None, None, None, None, None
        rpc_obj = None


while True:
    wow_hwnd = None
    win32gui.EnumWindows(callback, None)

    if win32gui.GetForegroundWindow() == wow_hwnd:
        lines = read_squares(wow_hwnd)

        if not lines:
            time.sleep(1)
            continue
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
            print("Setting activity: %s" % inMainMenu)
            update_activity(activity)
        else:
            zoneName, playerLevel, playerName, playerInfo, engClass, playerState, mapID = lines

            if zoneName != lastZone or playerState != lastPlayerState:
                # there has been an update, so send it to discord
                lastZone = zoneName
                lastPlayerLevel = playerLevel
                lastPlayerName = playerName
                lastPlayerInfo = playerInfo
                lastEngClass = engClass
                lastPlayerState = playerState
                lastMapID = mapID

                connect_to_discord()

                print('Setting new activity: %s - %s - %s - %s - %s - %s - %s' % (
                    zoneName, playerLevel, playerName, playerInfo, engClass, playerState, mapID))

                if timePlayed is None:
                    timePlayed = {'start': round(time.time())}
                if mapID in zones.keys():
                    zone = zones[str(mapID)]
                else:
                    zone = "wow-icon"
                    print("The zone is not in the list: %s [ID: %s]" % (zoneName, mapID))
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
        print('WoW no longer exists, terminating...')
        rpc_obj.close()
        sys.exit()
    time.sleep(5)
