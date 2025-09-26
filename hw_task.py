import time
import threading
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

def show_digits():
    for n in range(10):

        show_dp = (n % 2 == 0 and n > 0)
            
        show_digit(1, n, dp=show_dp)
        show_digit(2, n)             
            
        # 每5個數字亮一次LED
        if n % 5 == 0:
            led_on()
        else:
            led_off()  # 修正錯誤：ed_off() -> led_off()

        time.sleep(0.5)  # 每個數字顯示 0.5 秒

    all_off()          # 間隔前先全部熄滅
    led_off()          # 關閉LED
    time.sleep(1)

def validate_input(user_input):
    """驗證用戶輸入是否有效"""
    try:
        # 檢查輸入是否包含小數點
        if '.' in user_input:
            # 小數處理
            num = float(user_input)
            # 檢查小數範圍：0.1~9.9
            if 0.1 <= num <= 9.9:
                return True, user_input  # 返回原始字串，保持小數點格式
            else:
                return False, None
        else:
            # 整數處理
            num = int(user_input)
            # 檢查整數範圍：0~99
            if 0 <= num <= 99:
                return True, num  # 返回整數
            else:
                return False, None
            
    except ValueError:
        return False, None

def display_number(number):
    """在七段顯示器上顯示數字"""
    all_off()  # 先清空顯示
    
    # 判斷是否為小數（檢查原始輸入字串）
    if isinstance(number, str) and '.' in number:
        # 小數處理 (例如: "1.5", "3.7")
        parts = number.split('.')
        digit1 = int(parts[0])  # 整數部分
        digit2 = int(parts[1][0])  # 小數第一位
        
        show_digit(1, digit1, dp=True)   # 第一個顯示器顯示整數部分並點亮小數點
        show_digit(2, digit2, dp=False)  # 第二個顯示器顯示小數部分
        
        print(f"顯示: {digit1}.{digit2}")
        
    else:
        # 整數處理
        number = int(number)
        if number < 10:
            # 單位數 (0~9) - 只在右邊顯示器顯示，左邊保持關閉
            set_segments(1, 0, 0, 0, 0, 0, 0, 0, False)  # 第一個顯示器關閉
            show_digit(2, number, dp=False)  # 第二個顯示器顯示數字
            print(f"顯示: {number}")
        else:
            # 兩位數 (10~99)
            tens = number // 10
            units = number % 10
            show_digit(1, tens, dp=False)    # 第一個顯示器顯示十位數
            show_digit(2, units, dp=False)   # 第二個顯示器顯示個位數
            print(f"顯示: {tens}{units}")

import threading

# 全域變數來控制自動清空
last_display_time = 0
clear_display_flag = True

def auto_clear_display():
    """5秒後自動清空顯示器"""
    global last_display_time, clear_display_flag
    
    current_time = time.time()
    last_display_time = current_time
    
    def clear_after_delay():
        time.sleep(5)  # 等待5秒
        # 檢查是否在這5秒內有新的顯示
        if time.time() - last_display_time >= 4.9 and clear_display_flag:
            all_off()      # 清空顯示器
            print("\n顯示已自動清空")
            print("請輸入數字: ", end="", flush=True)  # 重新顯示輸入提示
    
    # 啟動背景執行緒來處理自動清空
    clear_thread = threading.Thread(target=clear_after_delay)
    clear_thread.daemon = True  # 設為daemon，程式結束時會自動停止
    clear_thread.start()
    
    return clear_thread

def input_display_system():
    """主要的輸入顯示系統"""
    global clear_display_flag
    
    print("=" * 50)
    print("🔢 互動小遊戲")
    print("=" * 50)
    print("請輸入數字，讓它顯示在顯示器上")
    print("支援範圍:")
    print("  - 整數: 0~99")
    print("  - 小數: 0.1~9.9")
    print("注意: 顯示5秒後會自動清空")
    print("=" * 50)
    
    current_timer = None  # 追蹤當前的計時器
    
    while True:
        try:
            user_input = input("\n請輸入數字: ").strip()

            # 驗證輸入
            is_valid, number = validate_input(user_input)
            
            if is_valid:
                # 輸入正確，顯示數字
                led_off()  # 確保LED關閉
                display_number(number)
                print("✅ 輸入正確!")
                print("(5秒後自動清空...)")
                
                # 停止之前的計時器（如果存在）
                if current_timer and current_timer.is_alive():
                    # 無法直接停止thread，但我們可以重新開始計時
                    pass
                
                # 啟動新的自動清空計時器
                current_timer = auto_clear_display()
                
            else:
                # 輸入錯誤，亮起LED並顯示錯誤訊息
                led_on()
                all_off()  # 清空顯示器
                print("   請輸入 0~99 的整數或 0.1~9.9 的小數")
                time.sleep(2)  # LED亮2秒
                led_off()
                
        except KeyboardInterrupt:
            print("\n程式被中斷")
            break
        except Exception as e:
            print(f"發生錯誤: {e}")
            led_on()
            time.sleep(1)
            led_off()
    
    # 退出時停止自動清空
    clear_display_flag = False


# 主程式區塊
try:

    print("測試中...")
    led_on()
    segment_walk(0.3)
    time.sleep(0.3)
    led_off()
    show_digits()
    print("測試完成!\n")
    
    # 啟動輸入顯示系統
    input_display_system()


# 捕捉 Ctrl+C 中斷，做清理
except KeyboardInterrupt:
    print("\n程式被中斷")
finally:
    all_off()        # 關掉所有段位
    led_off()        # 關閉LED
    GPIO.cleanup()   # 清理 GPIO 狀態
    print("GPIO清理完成")