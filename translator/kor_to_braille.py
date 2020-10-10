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

Dot_LIST = {
    'ㄱ': [0,0,0,1,0,0],
    'ㄴ': [1,0,0,1,0,0],
    'ㄷ': [0,1,0,1,0,0],
    'ㄹ': [0,0,0,0,1,0],
    'ㅁ': [1,0,0,0,1,0],
    'ㅂ': [0,0,0,1,1,0],
    'ㅅ': [0,0,0,0,0,1],
    'ㅇ': [1,1,0,1,1,0],
    'ㅈ': [0,0,0,1,0,1],
    'ㅊ': [0,0,0,0,1,1],
    'ㅋ': [1,1,0,1,0,0],
    'ㅌ': [1,1,0,0,1,0],
    'ㅍ': [1,0,0,1,1,0],
    'ㅎ': [0,1,0,1,1,0],

    'ㄲ': [[0,0,0,0,0,1], [0,0,0,1,0,0]],
    'ㄸ': [[0,0,0,0,0,1], [0,1,0,1,0,0]],
    'ㅃ': [[0,0,0,0,0,1], [0,0,0,1,1,0]],
    'ㅆ': [[0,0,0,0,0,1], [0,0,0,0,0,1]],
    'ㅉ': [[0,0,0,0,0,1], [0,0,0,1,0,1]],

    'ㅏ': [1,1,0,0,0,1],
    'ㅑ': [0,0,1,1,1,0],
    'ㅓ': [0,1,1,1,0,0],
    'ㅕ': [1,0,0,0,1,1],
    'ㅗ': [1,0,1,0,0,1],
    'ㅛ': [0,0,1,1,0,1],
    'ㅜ': [1,0,1,1,0,0],
    'ㅠ': [1,0,0,1,0,1],
    'ㅡ': [0,1,0,1,0,1],
    'ㅣ': [1,0,1,0,1,0],
    'ㅐ': [1,1,1,0,1,0],
    'ㅔ': [1,0,1,1,1,0],
    'ㅒ': [[0,0,1,1,1,0], [1,1,1,0,1,0]],
    'ㅖ': [0,0,1,1,0,0],
    'ㅘ': [1,1,1,0,0,1],
    'ㅙ': [[1,1,1,0,0,1], [1,1,1,0,1,0]],
    'ㅚ': [1,0,1,1,1,1],
    'ㅝ': [1,1,1,1,0,0],
    'ㅞ': [[1,1,1,1,0,0], [1,1,1,0,1,0]],
    'ㅟ': [[1,0,1,1,0,0], [1,1,1,0,1,0]],
    'ㅢ': [0,1,0,1,1,1],

    'a': [1,0,0,0,0,0],
    'b': [1,1,0,0,0,0],
    'c': [1,0,0,1,0,0],
    'd': [1,0,0,1,1,0],
    'e': [1,0,0,0,1,0],
    'f': [1,1,0,1,0,0],
    'g': [1,1,0,1,1,0],
    'h': [1,1,0,0,1,0],
    'i': [0,1,0,1,0,0],
    'j': [0,1,0,1,1,0],
    'k': [1,0,1,0,0,0],
    'l': [1,1,1,0,0,0],
    'm': [1,0,1,1,0,0],
    'n': [1,0,1,1,1,0],
    'o': [1,0,1,0,1,0],
    'p': [1,1,1,1,0,0],
    'q': [1,1,1,1,1,0],
    'r': [1,1,1,0,1,0],
    's': [0,1,1,1,0,0],
    't': [0,1,1,1,1,0],
    'u': [1,0,1,0,0,1],
    'v': [1,1,1,0,0,1],
    'w': [0,1,1,1,1,1],
    'x': [1,0,1,1,0,1],
    'y': [1,0,1,1,1,1],
    'z': [1,0,1,0,1,1],

    'A': [[0,0,0,0,0,1], [1,0,0,0,0,0]],
    'B': [[0,0,0,0,0,1], [1,1,0,0,0,0]],
    'C': [[0,0,0,0,0,1], [1,0,0,1,0,0]],
    'D': [[0,0,0,0,0,1], [1,0,0,1,1,0]],
    'E': [[0,0,0,0,0,1], [1,0,0,0,1,0]],
    'F': [[0,0,0,0,0,1], [1,1,0,1,0,0]],
    'G': [[0,0,0,0,0,1], [1,1,0,1,1,0]],
    'H': [[0,0,0,0,0,1], [1,1,0,0,1,0]],
    'I': [[0,0,0,0,0,1], [0,1,0,1,0,0]],
    'J': [[0,0,0,0,0,1], [0,1,0,1,1,0]],
    'K': [[0,0,0,0,0,1], [1,0,1,0,0,0]],
    'L': [[0,0,0,0,0,1], [1,1,1,0,0,0]],
    'M': [[0,0,0,0,0,1], [1,0,1,1,0,0]],
    'N': [[0,0,0,0,0,1], [1,0,1,1,1,0]],
    'O': [[0,0,0,0,0,1], [1,0,1,0,1,0]],
    'P': [[0,0,0,0,0,1], [1,1,1,1,0,0]],
    'Q': [[0,0,0,0,0,1], [1,1,1,1,1,0]],
    'R': [[0,0,0,0,0,1], [1,1,1,0,1,0]],
    'S': [[0,0,0,0,0,1], [0,1,1,1,0,0]],
    'T': [[0,0,0,0,0,1], [0,1,1,1,1,0]],
    'U': [[0,0,0,0,0,1], [1,0,1,0,0,1]],
    'V': [[0,0,0,0,0,1], [1,1,1,0,0,1]],
    'W': [[0,0,0,0,0,1], [0,1,1,1,1,1]],
    'X': [[0,0,0,0,0,1], [1,0,1,1,0,1]],
    'Y': [[0,0,0,0,0,1], [1,0,1,1,1,1]],
    'Z': [[0,0,0,0,0,1], [1,0,1,0,1,1]],

    ',': [0,1,0,0,0,0],
    ';': [[0,0,0,0,1,1],[0,1,1,0,0,0]],
    ':': [[0,0,0,0,1,0],[0,1,0,0,0,0]],
    '.': [0,1,0,0,1,1],
    '-': [0,1,0,0,1,0],
    '?': [0,1,1,0,0,1],
    '_': [0,0,1,0,0,1],
    '!': [0,1,1,0,1,0],
    '(': [[0,1,1,0,0,1], [0,0,1,0,0,0]],
    ')': [[0,0,0,0,0,1], [0,0,1,0,1,1]],
    '“': [0,1,1,0,0,1],
    '”': [0,0,1,0,1,1],
    '/': [[0,0,0,1,1,1],[0,0,1,1,0,0]],

    '1': [[0,0,1,1,1,1], [1,0,0,0,0,0]],
    '2': [[0,0,1,1,1,1], [1,1,0,0,0,0]],
    '3': [[0,0,1,1,1,1], [1,0,0,1,0,0]],
    '4': [[0,0,1,1,1,1], [1,0,0,1,1,0]],
    '5': [[0,0,1,1,1,1], [1,0,0,0,1,0]],
    '6': [[0,0,1,1,1,1], [1,1,0,1,0,0]],
    '7': [[0,0,1,1,1,1], [1,1,0,1,1,0]],
    '8': [[0,0,1,1,1,1], [1,1,0,0,1,0]],
    '9': [[0,0,1,1,1,1], [0,1,0,1,0,0]],
    '0': [[0,0,1,1,1,1], [0,1,0,1,1,0]],

    '가': [1,1,0,1,0,1],
    '나': [1,0,0,1,0,0],
    '다': [0,1,0,1,0,0],
    '마': [1,0,0,0,1,0],
    '바': [0,0,0,1,1,0],
    '사': [1,1,1,0,0,0],
    '자': [0,0,0,1,0,1],
    '카': [1,1,0,1,0,0],
    '타': [1,1,0,0,1,0],
    '파': [1,0,0,1,1,0],
    '하': [0,1,0,1,1,0],
    '것': [[0,0,0,1,1,1], [0,1,1,1,0,0]],
    '억': [1,0,0,1,1,1],
    '언': [0,1,1,1,1,1],
    '얼': [0,1,1,1,1,0],
    '열': [1,1,0,0,1,1],
    '영': [1,1,0,1,1,1],
    '옥': [1,0,1,1,0,1],
    '온': [1,1,1,0,1,1],
    '옹': [1,1,1,1,1,1],
    '운': [1,1,0,1,1,0],
    '울': [1,1,1,1,0,1],
    '은': [1,0,1,0,1,1],
    '을': [0,1,1,1,0,1],
    '인': [1,1,1,1,1,0],
    '그래서': [[1,0,0,0,0,0],[0,1,1,1,0,0]],
    '그러나': [[1,0,0,0,0,0],[1,0,0,1,0,0]],
    '그러므로': [[1,0,0,0,0,0],[0,1,0,0,0,1]],
    '그러면': [[1,0,0,0,0,0],[0,1,0,0,1,0]],
    '그런데': [[1,0,0,0,0,0],[1,0,1,1,1,0]],
    '그리고': [[1,0,0,0,0,0],[1,0,1,0,0,1]],
    '그리하여': [[1,0,0,0,0,0],[1,0,0,0,1,1]],
}

JONGSUNG_DOT={
    'ㄱ': [1,0,0,0,0,0],
    'ㄴ': [0,1,0,0,1,0],
    'ㄷ': [0,0,1,0,1,0],
    'ㄹ': [0,1,0,0,0,0],
    'ㅁ': [0,1,0,0,0,1],
    'ㅂ': [1,1,0,0,0,0],
    'ㅅ': [0,0,1,0,0,0],
    'ㅇ': [0,1,1,0,1,1],
    'ㅈ': [1,0,1,0,0,0],
    'ㅊ': [0,1,1,0,0,0],
    'ㅋ': [0,1,1,0,1,0],
    'ㅌ': [0,1,1,0,0,1],
    'ㅍ': [0,1,0,0,1,1],
    'ㅎ': [0,0,1,0,1,1],

    'ㄲ': [[1,0,0,0,0,0], [1,0,0,0,0,0]],
    'ㄳ': [[1,0,0,0,0,0], [0,0,1,0,0,0]],
    'ㄵ': [[0,1,0,0,1,0], [1,0,1,0,0,0]],
    'ㄶ': [[0,1,0,0,1,0], [0,0,1,0,1,1]],
    'ㄺ': [[0,1,0,0,0,0], [1,0,0,0,0,0]],
    'ㄻ': [[0,1,0,0,0,0], [0,1,0,0,0,1]],
    'ㄼ': [[0,1,0,0,0,0], [1,1,0,0,0,0]],
    'ㄽ': [[0,1,0,0,0,0], [0,0,1,0,0,0]],
    'ㄾ': [[0,1,0,0,0,0], [0,1,1,0,0,1]],
    'ㄿ': [[0,1,0,0,0,0], [0,1,0,0,1,1]],
    'ㅀ': [[0,1,0,0,0,0], [0,0,1,0,1,1]],
    'ㅄ': [[1,1,0,0,0,0], [0,0,1,0,0,0]],
    'ㅆ': [0,0,1,1,0,0],
}
Dot_bit = []

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
            check_Dot(key)
            return len(key)
    return 0


def check_number(word, index, braille):
    if word[index].isdigit():
        if index is not 0:
            if word[index - 1].isdigit():
                value = map_kor_to_braille.numbers[word[index]]
                braille.append({'braille' : value, 'category' : '숫자', 'original' : word[index]})
                check_Dot(word[index])
            else:
                value = map_kor_to_braille.number_start + map_kor_to_braille.numbers[word[index]]
                braille.append({'braille' : value, 'category' : '숫자', 'original' : word[index]})
                check_Dot(word[index])
        else:
            value = map_kor_to_braille.number_start + map_kor_to_braille.numbers[word[index]]
            braille.append({'braille' : value, 'category' : '숫자', 'original' : word[index]})
            check_Dot(word[index])
        return True
    return False

def check_punctuation(word, index, braille):
    for key, value in map_kor_to_braille.punctuation.items():
        if key is word[index]:
            braille.append({'braille' : value, 'category' : '문장기호', 'original' : key})
            check_Dot(key)
            return True
    return False

def check_character(word, index, braille):
    key = word[index]
    if re.match('[a-zA-Z]', key) is not None:
        braille.append({'braille' : map_kor_to_braille.english.get(key), 'category' : '영어', 'original' : key})
        check_Dot(key)
    if re.match('.*[ㄱ-ㅎㅏ-ㅣ가-힣]+.*', key) is not None:
        char = ord(key) - BASE_CODE
        char1 = int(char / CHOSUNG)
        char2 = int((char - (CHOSUNG * char1)) / JUNGSUNG)
        char3 = int((char - (CHOSUNG * char1) - (JUNGSUNG * char2)))
        braille.append({'braille' : map_kor_to_braille.CHOSUNG_letters.get(CHOSUNG_LIST[char1]), 'category' : '초성', 'original' : CHOSUNG_LIST[char1]})
        check_Dot(CHOSUNG_LIST[char1])
        braille.append({'braille' : map_kor_to_braille.JUNGSUNG_letters.get(JUNGSUNG_LIST[char2]), 'category' : '중성', 'original' : JUNGSUNG_LIST[char2]})
        check_Dot(JUNGSUNG_LIST[char2])
        if char3 is not 0:
            braille.append({'braille' : map_kor_to_braille.JONGSUNG_letters.get(JONGSUNG_LIST[char3]), 'category' : '종성', 'original' : JONGSUNG_LIST[char3]})
            JONGSUNG_dummy=JONGSUNG_DOT.get(JONGSUNG_LIST[char3])
            check_dim(JONGSUNG_dummy)
        return True
    return False

def check_Dot(text):
    dot=Dot_LIST.get(text)
    check_dim(dot)

def check_dim(list):
    if len(list) == 2:
        dummy = list[0]
        dummy2= list[1]
        Dot_bit.extend(dummy)
        Dot_bit.extend(dummy2)
    else:
        Dot_bit.extend(list)

def translate(string):
    words = extract_words(string)
    braille = []
    if words =='':
        return ''

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
        Dot_bit.extend([0,0,0,0,0,0])
    return braille