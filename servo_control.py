import RPi.GPIO as GPIO
import time

servoPIN = 13
GPIO.setmode(GPIO.BCM)
GPIO.setup(servoPIN, GPIO.OUT)

p = GPIO.PWM(servoPIN, 50) # GPIO 13 for PWM with 50Hz

# 伺服馬達角度控制函數
def set_servo_angle(angle):
    """
    設定伺服馬達角度
    angle: 0-180度
    """
    # 將角度轉換為duty cycle
    # 0度 = 2.5%, 90度 = 7.5%, 180度 = 12.5%
    duty_cycle = 2.5 + (angle / 180.0) * 10
    p.ChangeDutyCycle(duty_cycle)
    time.sleep(0.1)  # 給馬達時間移動

# 馬達置中函數
def center_servo():
    """將伺服馬達設定為置中位置 (90度)"""
    print("設定馬達置中位置 (90度)...")
    set_servo_angle(90)
    time.sleep(1)  # 等待馬達到達位置
    print("馬達已置中！")

# 初始化並置中
p.start(7.5)  # 從置中位置開始 (90度)
print("伺服馬達初始化...")
time.sleep(1)

# 先設定馬達置中
center_servo()

try:
    print("開始馬達測試...")
    print("按 Ctrl+C 停止程式")
    
    while True:
        # 測試動作：左-中-右-中
        print("移動到 0度...")
        set_servo_angle(0)
        time.sleep(1)
        
        print("移動到 90度 (置中)...")
        set_servo_angle(90)
        time.sleep(1)
        
        print("移動到 180度...")
        set_servo_angle(185)
        time.sleep(1)
        
        print("回到 90度 (置中)...")
        set_servo_angle(90)
        time.sleep(1)
        
        print("---")
        
except KeyboardInterrupt:
    print("\n程式被中斷")
finally:
    print("馬達回到置中位置...")
    center_servo()  # 結束前先置中
    p.stop()
    GPIO.cleanup()
    print("清理完成")