from gtts import gTTS
from playsound import playsound
import sys
import os

fname = 'data_tts/TTS'

def break_ko_en(text) -> list:
    msg = []
    tmp = ''
    if ord('a') <= ord(text[0].lower()) <= ord('z'):
        lang = ['en']
    else:
        lang = ['ko']
    msg.append(lang)
    for c in text:
        pre_lang = lang
        if ord('가') <= ord(c) <= ord('힣'):
            lang = ['ko']
        elif ord('a') <= ord(c.lower()) <= ord('z'):
            lang = ['en']
        if pre_lang == lang:
            tmp += c
            continue
        if tmp:
            msg[-1].append(tmp)
            tmp = c
        msg.append(lang)
    msg[-1].append(tmp)
    return msg


def text2speech(text) -> None:
    for fidx in range(1,12):
        if not os.path.isfile(fname + str(fidx) + '.mp3'):
            fidx -= 1
            break
    if fidx > 9:
        os.remove(fname + str(fidx) + '.mp3')
        fidx -= 1

    while fidx > 0:
        os.rename(fname + str(fidx) + '.mp3', fname + str(fidx + 1) + '.mp3')
        fidx = fidx - 1
    msg = break_ko_en(text)
    with open(fname + '1.mp3', 'wb') as f:
        for t in msg:
            tts = gTTS(text=t[1], lang=t[0])
            tts.write_to_fp(f)
    playsound(fname + '1.mp3')