from time import sleep
from pynput import keyboard
from pyautogui import moveTo, click as mouse_click, screenshot, alert  # type: ignore
import pytesseract
from PIL import Image, ImageEnhance
import numpy as np
import cv2
from rapidfuzz import fuzz


DESIRED_CARDS = ["dropkick"]


def click(x, y, delay=0.5):
    moveTo(x, y, duration=0.1)
    mouse_click()
    sleep(delay)


def find_color(x0, y0, x1, y1, color, margin=3):
    """
    Find the first pixel in the specified region that matches the given color.
    Returns the coordinates of the pixel if found, otherwise returns None.
    """
    img = screenshot(region=(x0, y0, x1 - x0, y1 - y0))
    for y in range(img.height):
        for x in range(img.width):
            r, g, b, a = img.getpixel((x, y))  # type: ignore
            # print(r, g, b)
            cr, cg, cb = color
            if (
                abs(r - cr) <= margin
                and abs(g - cg) <= margin
                and abs(b - cb) <= margin
            ):
                return (x + x0, y + y0)
    return None


def get_text(x, y, width, height, save=False):
    """
    Capture a screenshot of the specified region and extract text from it.
    Returns the extracted text.
    """
    img = screenshot(region=(x, y, width, height)).convert("L")
    img = img.resize((img.width * 4, img.height * 4), resample=Image.Resampling.LANCZOS)
    img = ImageEnhance.Sharpness(img).enhance(10.0)
    _, cv_img = cv2.threshold(np.array(img), 180, 255, cv2.THRESH_BINARY)

    contours, hierarchy = cv2.findContours(
        cv_img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE
    )
    hierarchy = hierarchy[0]
    cv_img = np.zeros_like(img)

    for i, cnt in enumerate(contours):
        parent = hierarchy[i][3]
        if parent == -1:
            area = cv2.contourArea(cnt)
            if 70 < area < 800:
                cv2.drawContours(cv_img, contours, i, 255, -1)  # type: ignore
                for j, h in enumerate(hierarchy):
                    if h[3] == i:
                        cv2.drawContours(cv_img, contours, j, 0, -1)  # type: ignore

    img = Image.fromarray(cv_img)
    if save:
        img.save("screenshot.png")
    text = pytesseract.image_to_string(
        img,
        config='-c preserve_interword_spaces=1 -c tessedit_char_whitelist="ABCDEFGHIJKLMNOPQRSTUVWXYZ abcdefghijklmnopqrstuvwxyz" --psm 7',
    )
    return " ".join(text.lower().strip().split())


def restart_run():
    click(1140, 260)  # Click on the "Settings" button
    click(950, 330)  # Click on the "Abandon Run" button
    click(660, 530)  # Click on the "Yes" button to confirm
    click(720, 600)  # Click on the "Continue" button
    click(720, 620, delay=5.0)  # Click on the "Main Menu" button


def start_run():
    click(360, 500)  # Click on the "Play" button
    click(540, 450)  # Click on the "Standard" button
    click(590, 560)  # Click on the "Ironclad" button
    click(1120, 580, delay=2.0)  # Click on the "Embark" button
    click(400, 620, delay=0.3)  # Click on the "Talk" button
    click(400, 590, delay=0.7)  # Click on the "1 HP" button
    click(400, 620, delay=0.3)  # Click on the "Leave" button

    mob_location = find_color(480, 560, 910, 580, (35, 50, 55), margin=20)
    while not mob_location:
        sleep(0.5)
        mob_location = find_color(480, 560, 910, 580, (35, 50, 55), margin=20)
    click(mob_location[0] + 8, mob_location[1] + 8, delay=3.0)  # Click on the mob

    health_bar = find_color(780, 500, 950, 560, (185, 41, 30))
    while not health_bar:
        sleep(0.5)
        health_bar = find_color(780, 500, 950, 560, (185, 41, 30))
    while health_bar:
        strike = find_color(530, 600, 900, 640, (224, 160, 65))
        if strike is None:
            restart_run()
            start_run()
            return
        click(strike[0], strike[1], delay=0.5)
        click(health_bar[0] + 30, health_bar[1] - 30, delay=0.5)  # Click on the mob
        health_bar = find_color(780, 500, 950, 560, (185, 41, 30))

    sleep(1.0)  # Wait for the battle to finish
    for i in range(3):  # Claim rewards
        click(720, 400)
    sleep(0.5)

    click(600, 500)
    card_one = get_text(540, 395, 95, 15)

    click(720, 500)
    card_two = get_text(675, 395, 95, 15)

    click(850, 500)
    card_three = get_text(810, 395, 95, 15)

    cards = (
        card_one,
        card_two,
        card_three,
    )

    print("Cards found:", cards)

    for card in cards:
        for desired_card in DESIRED_CARDS:
            if fuzz.ratio(card, desired_card) > 80:
                print(f"Found desired card: {card}")
                alert(
                    title="Card found!",
                    text=f"The card '{desired_card}' has been detected!",
                )
                return

    sleep(5.0)
    restart_run()
    start_run()


def on_press(key):
    try:
        if key.char == "\\":
            start_run()
        elif key.char == "]":
            restart_run()
        elif key.char == "1":
            print(get_text(540, 395, 95, 15, save=True))
        elif key.char == "2":
            print(get_text(675, 395, 95, 15, save=True))
        elif key.char == "3":
            print(get_text(810, 395, 95, 15, save=True))
    except AttributeError:
        pass


with keyboard.Listener(on_press=on_press) as listener:
    listener.join()
