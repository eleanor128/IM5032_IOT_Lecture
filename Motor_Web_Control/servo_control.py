import RPi.GPIO as GPIO
import time

# 伺服馬達設定
servoPIN = 14
# LED 設定
ledPIN = 26

GPIO.setmode(GPIO.BCM)
GPIO.setup(servoPIN, GPIO.OUT)
GPIO.setup(ledPIN, GPIO.OUT)

p = GPIO.PWM(servoPIN, 50)  # GPIO 14, 50Hz

print("硬體初始化完成:")
print(f"伺服馬達: GPIO {servoPIN}")
print(f"LED 燈: GPIO {ledPIN}")

# 伺服馬達角度控制函數
def set_servo_angle(angle):
    """設定伺服馬達角度 (0-180度)"""
    # 反轉角度：0度在左邊，180度在右邊
    reversed_angle = 180 - angle
    duty_cycle = 2.5 + (reversed_angle / 180.0) * 10
    p.ChangeDutyCycle(duty_cycle)
    print(f"馬達轉到 {angle}度 (左0°-右180°)")
    time.sleep(1)

# LED 控制函數
def led_on():
    """開啟 LED"""
    GPIO.output(ledPIN, GPIO.HIGH)
    print("LED 開啟")

def led_off():
    """關閉 LED"""
    GPIO.output(ledPIN, GPIO.LOW)
    print("LED 關閉")

def led_blink(times=3, delay=0.5):
    """LED 閃爍"""
    print(f"LED 閃爍 {times} 次")
    for i in range(times):
        led_on()
        time.sleep(delay)
        led_off()
        time.sleep(delay)

# 初始化
p.start(7.5)  # 90度開始
print("伺服馬達初始化完成")
time.sleep(1)

try:
    print("測試馬達角度和 LED...")
    
    # 先測試 LED
    print("\n=== LED 測試 ===")
    led_blink(3)
    time.sleep(1)
    
    print("\n=== 馬達測試 ===")
    # 測試各個角度，每次移動時閃爍 LED
    angles = [0, 45, 90, 135, 180]
    
    for angle in angles:
        led_on()  # 移動時點亮 LED
        set_servo_angle(angle)
        led_off()  # 移動完成後關閉 LED
        time.sleep(1)
    
    # 回到90度
    led_on()
    set_servo_angle(90)
    led_off()
    print("測試完成")
        
except KeyboardInterrupt:
    print("\n程式被中斷")
finally:
    print("清理中...")
    led_off()  # 確保 LED 關閉
    set_servo_angle(90)  # 馬達回到中心位置
    time.sleep(1)
    p.stop()
    GPIO.cleanup()
    print("清理完成")