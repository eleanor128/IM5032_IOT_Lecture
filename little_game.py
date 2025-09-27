
import time
import random
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

# 初始化LED為輸出模式，預設 LOW（熄滅）
GPIO.setup(LED_PIN, GPIO.OUT, initial=GPIO.LOW) 


# 定義 0~9 的段碼資料，每個元組代表 a~g 七段的亮滅狀態
# True/1 = 點亮，False/0 = 熄滅
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

# 遊戲相關函數

# 全域變數控制遊戲狀態
game_running = False
current_digit1 = 0
current_digit2 = 0
current_dp1 = False
current_dp2 = False

def random_display():
    """持續隨機顯示數字和小數點"""
    global game_running, current_digit1, current_digit2, current_dp1, current_dp2
    while game_running:
        current_digit1 = random.randint(0, 9)
        current_digit2 = random.randint(0, 9)
        current_dp1 = random.choice([True, False])  # 只有第一個顯示器有小數點
        current_dp2 = False  # 第二個顯示器沒有小數點
        
        show_digit(1, current_digit1, current_dp1)  
        show_digit(2, current_digit2, current_dp2)  
        time.sleep(0.1)  # 快速變化

def get_displayed_number():
    """取得當前顯示的數字（考慮小數點位置）"""
    # 由於只有第一個顯示器有小數點功能
    if current_dp1:  # 第一個數字後有小數點: X.Y
        return current_digit1 + current_digit2 * 0.1
    else:  # 沒有小數點: XY
        return current_digit1 * 10 + current_digit2

def led_correct_pattern():
    """答對時的LED閃爍模式：短-長-短-長快速閃"""
    for _ in range(3):  # 重複3次
        # 短閃
        led_on()
        time.sleep(0.2)
        led_off()
        time.sleep(0.1)
        # 長閃
        led_on()
        time.sleep(0.5)
        led_off()
        time.sleep(0.1)
        # 短閃
        led_on()
        time.sleep(0.2)
        led_off()
        time.sleep(0.1)
        # 長閃
        led_on()
        time.sleep(0.5)
        led_off()
        time.sleep(0.2)

def led_wrong_pattern():
    """答錯時的LED閃爍模式：長-長"""
    for _ in range(3):  # 重複3次
        led_on()
        time.sleep(0.8)
        led_off()
        time.sleep(0.2)
        led_on()
        time.sleep(0.8)
        led_off()
        time.sleep(0.3)

def wait_for_enter():
    """等待 Enter 鍵按下"""
    print("按下 Enter 繼續...")
    try:
        input()
    except:
        pass

def multiplication_game():
    """主要的乘法遊戲"""
    global game_running
    
    print("=" * 50)
    print("🎮 數字乘法遊戲 🎮")
    print("=" * 50)
    print("遊戲規則:")
    print("按下 Enter 開始後兩個顯示器持續隨機顯示亂數，包含小數點也是隨機，再按下 Enter 之後就會馬上暫停留在剛剛顯示的數字")
    print("然後輸入兩個數字相乘等於此數(可以是小數)")
    print("=" * 50)
    
    wait_for_enter()
    
    # 開始隨機顯示
    game_running = True
    display_thread = threading.Thread(target=random_display)
    display_thread.daemon = True
    display_thread.start()
    
    print("🎲 數字正在隨機變化中...")
    print("再按一次 Enter 停止!")
    
    wait_for_enter()
    
    # 停止隨機顯示
    game_running = False
    time.sleep(0.2)  # 確保顯示停止
    
    # 顯示最終結果
    target_number = get_displayed_number()
    
    # 顯示當前數字的詳細資訊
    display_str = f"{current_digit1}"
    if current_dp1:
        display_str += "."
    display_str += f"{current_digit2}"
    # 第二個顯示器沒有小數點功能
    
    print("=" * 30)
    print("請輸入兩個數字相乘等於此數(可以是小數點):")
    
    try:
        num1 = float(input("第一個數字: "))
        num2 = float(input("第二個數字: "))
        result = num1 * num2
        
        print(f"\n你的答案: {num1} × {num2} = {result}")
        print(f"目標數字: {target_number}")
        
        # 檢查答案 (允許小誤差)
        if abs(result - target_number) < 0.01:
            print("🎉 答對了! 太棒了!")
            led_correct_pattern()
        else:
            print("❌ 答錯了，再接再厲!")
            led_wrong_pattern()
            
    except ValueError:
        print("❌ 輸入格式錯誤!")
        led_wrong_pattern()
    
    print("\n" + "=" * 50)

# 主程式區塊
try:
    # 先測試LED
    print("測試LED...")
    led_on()
    time.sleep(1)
    led_off()
    time.sleep(1)

    # 開始遊戲循環
    while True:
        try:
            multiplication_game()
            
            # 詢問是否繼續遊戲
            print("是否繼續遊戲? (按 Enter 繼續，輸入 'q' 退出)")
            choice = input().strip().lower()
            if choice == 'q':
                break
                
        except KeyboardInterrupt:
            break

# 捕捉 Ctrl+C 中斷，做清理
except KeyboardInterrupt:
    print("\n程式被中斷")
finally:
    all_off()        # 關掉所有段位
    led_off()        # 關閉LED
    GPIO.cleanup()   # 清理 GPIO 狀態
    print("GPIO清理完成")
