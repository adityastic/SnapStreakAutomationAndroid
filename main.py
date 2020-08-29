import random
import threading
import time
from datetime import datetime

from ppadb.client import Client as AdbClient
from ppadb.device import Device

from ocr import find_last_snap

client = AdbClient(host="127.0.0.1", port=5037)


def sleep_after_exec(func):
    def wrapper(*args, **kwargs):
        func(*args, **kwargs)
        time.sleep(0.9)

    return wrapper


def get_resolution(device):
    return tuple(
        [int(x) for x in str(device.shell("wm size")).split(" ")[2].replace("\n", "").split("x")])


def log(string):
    print(f'[{datetime.utcnow().strftime("%H:%M:%S.%f")[:-3]}]: {string}')


@sleep_after_exec
def open_snapchat(device):
    """
    used: adb shell pm dump PACKAGE_NAME | grep -A 1 MAIN to find the activity for com.snapchat.android
    """
    log(f"{device.get_serial_no()}: Opening Snapchat")
    device.shell("am start -n com.snapchat.android/.LandingPageActivity")


def go_to_homepage(device):
    log(f"{device.get_serial_no()}: Going Back Home")
    device.shell("am start -a android.intent.action.MAIN -c android.intent.category.HOME")


@sleep_after_exec
def click_picture(width, height, device):
    x = width / 2
    y = height - height / 8
    log(f"{device.get_serial_no()}: Clicking Camera at {x},{y}")
    device.input_tap(x, y)


@sleep_after_exec
def click_video(width, height, device):
    x = width / 2
    y = height - height / 8
    log(f"{device.get_serial_no()}: Clicking Video at {x},{y}")
    device.input_swipe(x, y, x, y, 10000)


@sleep_after_exec
def send_picture(width, height, device):
    x = width - width / 16
    y = height - height / 16
    log(f"{device.get_serial_no()}: Clicking Send at {x},{y}")
    device.input_tap(x, y)


@sleep_after_exec
def click_random_filter(width, device):
    if random.randint(1, 2) == 1:
        device.input_swipe(width - 100, 1700, 100, 1700, 100)
    else:
        device.input_swipe(100, 1700, width - 100, 1700, 100)


@sleep_after_exec
def click_last_snap(device, last_snap_x, last_snap_y):
    log(f"{device.get_serial_no()}: Clicking Last Send at {last_snap_x},{last_snap_y}")
    device.input_tap(last_snap_x, last_snap_y)


def capture_screen(device):
    result = device.screencap()
    with open(f"{device.get_serial_no()}-screen.png", "wb") as fp:
        fp.write(result)


#
# def click_all_people(dev_width, dev_height, device, recents_y):
#     x = 90
#     y = recents_y + 90
#     threshold = 45
#     log(f"{device.get_serial_no()}: Clicking All Recents from {100},{recents_y}")
#     for i in range(60):
#         log("Tap")
#         device.input_tap(x, y)
#         y += 90


def streak_on_device(picture, device: Device):
    dev_width, dev_height = get_resolution(device)
    open_snapchat(device)
    if picture:
        click_picture(dev_width, dev_height, device)
        click_random_filter(dev_width, device)
    else:
        click_video(dev_width, dev_height, device)

    send_picture(dev_width, dev_height, device)

    capture_screen(device)

    log(f"{device.get_serial_no()}: Finding Last Snap")
    (x, y, recents_y) = find_last_snap(device.get_serial_no())
    if x == -1:
        log(f"{device.get_serial_no()}: Last Snap NOT FOUND")
    else:
        log(f"{device.get_serial_no()}: Last Snap FOUND")
        click_last_snap(device, x, y)
        send_picture(dev_width, dev_height, device)
        go_to_homepage(device)


def streak_call(picture: bool):
    for device in client.devices():
        log(f"Working on {device}")
        threading.Thread(target=streak_on_device, args=(picture, device)).start()


if __name__ == "__main__":
    log("Press V for Video, C for Picture and Q for Quiting the tool")
    while True:
        listening_char = input()
        if listening_char == "V" or listening_char == "v":
            streak_call(picture=False)
        elif listening_char == "C" or listening_char == "c":
            streak_call(picture=True)
        elif listening_char == "Q" or listening_char == "q":
            exit()
        else:
            log("Wrong Entry! Try again")
