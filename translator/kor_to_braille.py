from . import map_kor_to_braille
import re


UNRECOGNIZED = '?'

open_quotes = True

BASE_CODE, CHOSUNG, JUNGSUNG = 44032, 588, 28

# 초성 리스트. 00 ~ 18
CHOSUNG_LIST = ['ㄱ', 'ㄲ', 'ㄴ', 'ㄷ', 'ㄸ', 'ㄹ', 'ㅁ',
                'ㅂ', 'ㅃ', 'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅉ',
                'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ']

# 중성 리스트. 00 ~ 20
JUNGSUNG_LIST = ['ㅏ', 'ㅐ', 'ㅑ', 'ㅒ', 'ㅓ', 'ㅔ', 'ㅕ',
                'ㅖ', 'ㅗ', 'ㅘ', 'ㅙ', 'ㅚ', 'ㅛ', 'ㅜ',
                'ㅝ', 'ㅞ', 'ㅟ', 'ㅠ', 'ㅡ', 'ㅢ', 'ㅣ']

# 종성 리스트. 00 ~ 27 + 1(1개 없음)
JONGSUNG_LIST = [' ', 'ㄱ', 'ㄲ', 'ㄳ', 'ㄴ', 'ㄵ', 'ㄶ', 'ㄷ',
                'ㄹ', 'ㄺ', 'ㄻ', 'ㄼ', 'ㄽ', 'ㄾ', 'ㄿ', 'ㅀ',
                'ㅁ', 'ㅂ', 'ㅄ', 'ㅅ','ㅆ', 'ㅇ', 'ㅈ', 'ㅊ',
                'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ']

def extract_words(string):
    words = string.split(" ")
    result = []
    for word in words:
        temp = word.split("\n")
        for item in temp:
            result.append(item)
    return result


def check_contraction(word, index, braille):
    for key, value in map_kor_to_braille.contractions.items():
        if word[index:].startswith(key):
            braille.append({'braille' : value, 'category' : '약어', 'original' : key})
            return len(key)
    return 0


def check_number(word, index, braille):
    if word[index].isdigit():
        if index is not 0:
            if word[index - 1].isdigit():
                value = map_kor_to_braille.numbers[word[index]]
                braille.append({'braille' : value, 'category' : '숫자', 'original' : word[index]})
            else:
                value = map_kor_to_braille.number_start + map_kor_to_braille.numbers[word[index]]
                braille.append({'braille' : value, 'category' : '숫자', 'original' : word[index]})
        else:
            value = map_kor_to_braille.number_start + map_kor_to_braille.numbers[word[index]]
            braille.append({'braille' : value, 'category' : '숫자', 'original' : word[index]})
        return True
    return False

def check_punctuation(word, index, braille):
    for key, value in map_kor_to_braille.punctuation.items():
        if key is word[index]:
            braille.append({'braille' : value, 'category' : '문장기호', 'original' : key})
            return True
    return False

def check_character(word, index, braille):
    key = word[index]
    if re.match('.*[ㄱ-ㅎㅏ-ㅣ가-힣]+.*', key) is not None:
        char = ord(key) - BASE_CODE
        char1 = int(char / CHOSUNG)
        char2 = int((char - (CHOSUNG * char1)) / JUNGSUNG)
        char3 = int((char - (CHOSUNG * char1) - (JUNGSUNG * char2)))
        braille.append({'braille' : map_kor_to_braille.CHOSUNG_letters.get(CHOSUNG_LIST[char1]), 'category' : '초성', 'original' : CHOSUNG_LIST[char1]})
        braille.append({'braille' : map_kor_to_braille.JUNGSUNG_letters.get(JUNGSUNG_LIST[char2]), 'category' : '중성', 'original' : JUNGSUNG_LIST[char2]})
        if char3 is not 0:
            braille.append({'braille' : map_kor_to_braille.JONGSUNG_letters.get(JONGSUNG_LIST[char3]), 'category' : '종성', 'original' : JONGSUNG_LIST[char3]})
        return True
    return False


def translate(string):
    words = extract_words(string)
    braille = []
    for word in words:
        i = 0
        while (i < len(word)):
            check_cont = check_contraction(word, i, braille)
            if check_cont:
                i += check_cont
                continue
            if check_number(word, i, braille):
                i += 1
                continue
            if check_punctuation(word, i, braille):
                i += 1
                continue
            check_character(word, i, braille)
            i += 1
        braille.append({'braille' : ' ', 'category' : 'space', 'original' : ' '})
    return braille


if __name__ == "__main__":
    print(translate("오늘 밤에도 별은 바람에 스치운다."))
