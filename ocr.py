import os
import pytesseract
from PIL import Image
from pytesseract import Output


def find_last_snap(host):
    column = Image.open(f'{host}-screen.png')
    gray = column.convert('L')
    bw = gray.point(lambda x: 0 if x > 200 else 255, '1')
    data = pytesseract.image_to_data(bw, output_type=Output.DICT)
    x, y, recents_y = -1, -1, -1
    for i in range(len(data['text'])):
        if data['text'][i] == "Last":
            x, y = data['left'][i], data['top'][i]
        elif data['text'][i] == "Recents":
            recents_y = data['top'][i]
    os.remove(f'{host}-screen.png')
    return x, y, recents_y
