# Braille Printer PC SW
## Brief
이 프로그램은 자체 제작한 점자 프린터의 HW를 지원하는 PC SW입니다.<br>
텍스트 편집, 자동 한글->점자 변환기, TTS, OCR 기능이 포함되어 있습니다.<br>
<br>
점자 프린터는 ARM Cortex-M4 프로세서가 사용 되었으며, SW는 mbed-os 2.0을 기반으로 제작되었습니다.<br>
<a href="https://github.com/d2h10s/pybraille/tree/main/mbed"><img src="http://img.shields.io/badge/-Go to MBED Code-A8B9CC?style=flat-square&logo=c%2b%2b&logoColor=white"></a>

## SW Manual
<img src="img/manual_v1_3.png">
이 매뉴얼의 버전은 1.3로 최신 매뉴얼은 1.4입니다.<br>
차후 업데이터 예정입니다.

## Dependancy
<p align="center">
    <img src="https://img.shields.io/badge/python-3.8.5-002299">
    <img src="https://img.shields.io/badge/numpy-1.19.5-002299">
    <img src="https://img.shields.io/badge/pyserial-3.5-AA3355">
    <img src="https://img.shields.io/badge/requests-2.25.1-0000DD">
    <img src="https://img.shields.io/badge/playsound-1.2.2-0000DD">
    <img src="https://img.shields.io/badge/pyinstaller-4.2-DDDDDD">
    <br>
    <img src="https://img.shields.io/badge/pyqt5-5.15.2-009922">
    <img src="https://img.shields.io/badge/opencv-4.5.1.48-005555">
    <img src="https://img.shields.io/badge/pytesseract-0.3.7-002299">
    <img src="https://img.shields.io/badge/gtts-2.2.1-DD2299"> 
<p>
    
## Debugging
본 프로그램에는 디버깅용 콘솔이 포함되어 있으며 통신 상황을 모니터링 할 수 있습니다.
<img src="img/debugging.png">

## 점역 알고리즘
<img src="img/braille_translate_algorithm.png">

## 점자 유니코드 serialization 알고리즘
<img src="img/braille_to_dot_algorithm.png">

## Serial 장치 자동 탐색 알고리즘
<img src="img/serial_algorithm.png">

## 통신 프로토콜 프레임
<img src="img/protocol_base.png">

## Shape
<p align="center">
    <img src="img/isometric.png" ><br>
    Isometric
</p>

## Parts
### View
<p align="center">
    <img src="img/exploded_view.png">
    <img src="img/parts_table.png">
</p>

### Step Motor Resolution
<img src="img/select_resolution.png">

### Calculating Step Motor Speed
#### 
<img src="img/cal_dynamics.png">
<img src="img/cal_dynamics2.png">

## Schematic
<p align="center">
    <img src="img/schematic.png">
</p>
