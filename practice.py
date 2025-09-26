import time
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)

# 定義第一個七段顯示器 a~g 對應到的 GPIO 腳位 (左邊那個)
SEG_PINS_1 = {
    'a': 11,   # 紅色線
    'b': 0,    # 綠色線
    'c': 5,    # 咖啡色線
    'd': 6,    # 紫色線
    'e': 13,   # 黃色線
    'f': 19,   # 白色線
    'g': 26,   # 橘色線
    'dp': 21,  # 灰色線，控制小數點
}

# 定義第二個七段顯示器 a~g 對應到的 GPIO 腳位 (右邊那個)
SEG_PINS_2 = {
    'a': 25,   # 藍色線
    'b': 8,   # 綠色線
    'c': 7,   # 咖啡色線
    'd': 1,   # 紫色線
    'e': 12,  # 黃色線
    'f': 16,  # 白色線
    'g': 20,  # 橘色線
}

# 定義LED的GPIO腳位
LED_PIN = 14  # LED接在GPIO14


# 初始化所有段位腳為輸出模式，預設 LOW（共陰極：LOW=熄滅）
for pin in SEG_PINS_1.values():
    GPIO.setup(pin, GPIO.OUT, initial=GPIO.LOW)

for pin in SEG_PINS_2.values():
    GPIO.setup(pin, GPIO.OUT, initial=GPIO.LOW)

# 初始化LED為輸出模式
GPIO.setup(LED_PIN, GPIO.OUT, initial=GPIO.LOW) 


# 定義 0~9 ，每個元組代表 a~g 七段的亮滅狀態
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

# 控制七顯示器每一段 a~g 是否要點亮
def set_segments(monitor_number,a,b,c,d,e,f,g,dp):
    # 建立一個 dict 將每段對應到狀態
    states_1 = {'a':a,'b':b,'c':c,'d':d,'e':e,'f':f,'g':g, 'dp':dp}
    states_2 = {'a':a,'b':b,'c':c,'d':d,'e':e,'f':f,'g':g}

    # 對每一段的腳位設定 HIGH（亮）或 LOW（滅）

    # 左邊的顯示器
    if monitor_number == 1: 
        for seg, val in states_1.items():
            GPIO.output(SEG_PINS_1[seg], GPIO.HIGH if val else GPIO.LOW)

    # 右邊的顯示器
    if monitor_number == 2: 
        for seg, val in states_2.items():
            GPIO.output(SEG_PINS_2[seg], GPIO.HIGH if val else GPIO.LOW)

# 顯示某個數字 (0~9)
def show_digit(monitor_number, n, dp=False):
    pattern = DIGITS.get(n, (0,0,0,0,0,0,0))  # 取出對應段碼，預設全部熄滅
    if monitor_number == 1:
        set_segments(1, *pattern, dp)  # 為monitor 1添加dp參數
    elif monitor_number == 2:
        set_segments(2, *pattern, False)  # monitor 2沒有dp，固定為False 

# 熄滅所有段位（全部 LOW）
def all_off():
    set_segments(1, 0, 0, 0, 0, 0, 0, 0, False)  # monitor 1，包含dp
    set_segments(2, 0, 0, 0, 0, 0, 0, 0, False)  # monitor 2，dp參數會被忽略

# LED控制函數
def led_on():
    GPIO.output(LED_PIN, GPIO.HIGH)

def led_off():
    GPIO.output(LED_PIN, GPIO.LOW)

def led_toggle():
    current_state = GPIO.input(LED_PIN)
    GPIO.output(LED_PIN, not current_state)

# 每段依序點亮，用來測試段是否正常
def segment_walk(delay=0.25):
    for seg in ['a','b','c','d','e','f','g']:
        all_off()  # 每次先全部熄滅
        GPIO.output(SEG_PINS_1[seg], GPIO.HIGH)
        GPIO.output(SEG_PINS_2[seg], GPIO.HIGH)
        time.sleep(delay)  # 停留一段時間再換下一段
    all_off()


# 主程式區塊
try:
    # 測試LED
    print("測試LED...")
    led_on()
    time.sleep(1)
    led_off()
    time.sleep(1)
    
    # 測試七段顯示器
    print("測試七段顯示器...")
    segment_walk(0.3)

    while True:
        # 依序顯示 0 到 99，使用兩位數顯示
        for n in range(100):
            tens = n // 10      # 十位數
            units = n % 10      # 個位數
            
            # 每10個數字顯示小數點（例如：1.0, 2.0, 3.0...）
            show_dp = (n % 10 == 0 and n > 0)
            
            show_digit(1, tens, dp=show_dp)  # 第一個顯示器顯示十位數，某些情況顯示小數點
            show_digit(2, units)             # 第二個顯示器顯示個位數
            
            # 每5個數字亮一次LED
            if n % 5 == 0:
                led_on()
            else:
                led_off()
                
            time.sleep(0.5)  # 每個數字顯示 0.5 秒
            
        all_off()          # 間隔前先全部熄滅
        led_off()          # 關閉LED
        time.sleep(1)

# 捕捉 Ctrl+C 中斷，做清理
except KeyboardInterrupt:
    print("\n程式被中斷")
finally:
    all_off()        # 關掉所有段位
    led_off()        # 關閉LED
    GPIO.cleanup()   # 清理 GPIO 狀態
    print("GPIO清理完成")