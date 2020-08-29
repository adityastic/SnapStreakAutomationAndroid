import threading
import time

from ppadb.client import Client as AdbClient
from ppadb.device import Device

client = AdbClient(host="127.0.0.1", port=5037)


def sleep_after_exec(func):
    def wrapper(*args, **kwargs):
        func(*args, **kwargs)
        time.sleep(0.5)

    return wrapper


def get_resolution(device):
    return tuple(
        [int(x) for x in str(device.shell("wm size")).split(" ")[2].replace("\n", "").split("x")])


def log(string):
    print(f'[{time.strftime("%H:%M:%S:%s", time.localtime())}]: {string}')


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
    device.input_swipe(x, y, x, y, 5000)


@sleep_after_exec
def send_picture(width, height, device):
    x = width - width / 16
    y = height - height / 16
    log(f"{device.get_serial_no()}: Clicking Send at {x},{y}")
    device.input_tap(x, y)


@sleep_after_exec
def click_last_snap(width, height, device):
    x = width - width / 2
    y = height / 2 + height / 8
    log(f"{device.get_serial_no()}: Clicking Last Send at {x},{y}")
    device.input_tap(x, y)


def capture_screen(device):
    result = device.screencap()
    with open(f"{device.get_serial_no()}-screen.png", "wb") as fp:
        fp.write(result)


def streak_on_device(picture, device: Device):
    dev_width, dev_height = get_resolution(device)
    open_snapchat(device)
    if picture:
        click_picture(dev_width, dev_height, device)
    else:
        click_video(dev_width, dev_height, device)

    send_picture(dev_width, dev_height, device)

    capture_screen(device)
    click_last_snap(dev_width, dev_height, device)
    send_picture(dev_width, dev_height, device)
    go_to_homepage(device)


def streak_call(picture: bool):
    for device in client.devices():
        log(f"Working on {device}")
        threading.Thread(target=streak_on_device, args=(picture, device)).start()


if __name__ == "__main__":
    streak_call(picture=True)
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
