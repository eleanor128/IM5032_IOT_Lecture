
import time
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)

# a 紅色線
# d 綠色線
# c 咖啡色線
# d 紫色線
# e 黃色線
# f 白色線
# g 橘色線


# 定義七段顯示器 a~g 七個段位對應到的 GPIO 腳位
SEG_PINS = {
    'a': 11,   # GPIO11 控制 a 段
    'b': 0,    # GPIO0 控制 b 段
    'c': 5,
    'd': 6,
    'e': 13,
    'f': 19,
    'g': 26,
}

# 初始化所有段位腳為輸出模式，預設 LOW（共陰極：LOW=熄滅）
for pin in SEG_PINS.values():
    GPIO.setup(pin, GPIO.OUT, initial=GPIO.LOW)

# 定義 0~9 的段碼資料，每個元組代表 a~g 七段的亮滅狀態
# True/1 = 點亮，False/0 = 熄滅（共陰極：HIGH=亮）
DIGITS = {
    0: (1,1,1,1,1,1,0),  # 顯示 0
    1: (0,1,1,0,0,0,0),  # 顯示 1
    2: (1,1,0,1,1,0,1),  # 顯示 2
    3: (1,1,1,1,0,0,1),  # 顯示 3
    4: (0,1,1,0,0,1,1),  # 顯示 4
    5: (1,0,1,1,0,1,1),  # 顯示 5
    6: (1,0,1,1,1,1,1),  # 顯示 6
    7: (1,1,1,0,0,0,0),  # 顯示 7
    8: (1,1,1,1,1,1,1),  # 顯示 8
    9: (1,1,1,1,0,1,1),  # 顯示 9
}

# 控制每一段 a~g 是否要點亮
def set_segments(a,b,c,d,e,f,g):
    # 建立一個 dict 將每段對應到狀態
    states = {'a':a,'b':b,'c':c,'d':d,'e':e,'f':f,'g':g}
    # 對每一段的腳位設定 HIGH（亮）或 LOW（滅）
    for seg, val in states.items():
        GPIO.output(SEG_PINS[seg], GPIO.HIGH if val else GPIO.LOW)

# 顯示某個數字 (0~9)
def show_digit(n):
    pattern = DIGITS.get(n, (0,0,0,0,0,0,0))  # 取出對應段碼，預設全部熄滅
    set_segments(*pattern)  # 解包元組並傳給 set_segments

# 熄滅所有段位（全部 LOW）
def all_off():
    set_segments(0,0,0,0,0,0,0)

# 每段依序點亮，用來測試段是否正常
def segment_walk(delay=0.25):
    for seg in ['a','b','c','d','e','f','g']:
        all_off()  # 每次先全部熄滅
        GPIO.output(SEG_PINS[seg], GPIO.HIGH)  # 點亮當前這一段（共陰極：HIGH=亮）
        time.sleep(delay)  # 停留一段時間再換下一段
    all_off()

# 主程式區塊
try:
    segment_walk(0.3)  # 先跑一次每段測試（每段亮 0.3 秒）

    while True:
        # 依序顯示 0 到 9
        for n in range(10):
            show_digit(n)  # 顯示當前數字
            time.sleep(0.8)  # 每個數字顯示 0.8 秒
        all_off()          # 間隔前先全部熄滅
        time.sleep(0.3)

# 捕捉 Ctrl+C 中斷，做清理
except KeyboardInterrupt:
    pass
finally:
    all_off()        # 關掉所有段位
    GPIO.cleanup()   # 清理 GPIO 狀態
