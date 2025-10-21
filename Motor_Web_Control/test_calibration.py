#!/usr/bin/env python3
"""
測試校準後的伺服馬達精度
"""

import RPi.GPIO as GPIO
import time

# GPIO 設定
servoPIN = 13  # 改為 GPIO 13
GPIO.setmode(GPIO.BCM)
GPIO.setup(servoPIN, GPIO.OUT)

# 伺服馬達校準表
SERVO_CALIBRATION = {
    0: 12.60,
    45: 11.00,
    90: 7.30,
    135: 4.50,
    180: 2.20,
}

def get_calibrated_duty_cycle(target_angle):
    """根據校準資料獲取角度對應的 duty cycle"""
    if target_angle in SERVO_CALIBRATION:
        return SERVO_CALIBRATION[target_angle]

    # 線性插值
    angles = sorted(SERVO_CALIBRATION.keys())

    if target_angle <= angles[0]:
        return SERVO_CALIBRATION[angles[0]]
    if target_angle >= angles[-1]:
        return SERVO_CALIBRATION[angles[-1]]

    # 找到相鄰的兩個校準點
    for i in range(len(angles) - 1):
        if angles[i] <= target_angle <= angles[i + 1]:
            angle1, angle2 = angles[i], angles[i + 1]
            duty1, duty2 = SERVO_CALIBRATION[angle1], SERVO_CALIBRATION[angle2]

            # 線性插值
            ratio = (target_angle - angle1) / (angle2 - angle1)
            return duty1 + ratio * (duty2 - duty1)

    return 7.30  # 預設值

def set_calibrated_angle(angle):
    """使用校準資料設定角度"""
    duty_cycle = get_calibrated_duty_cycle(angle)
    p.ChangeDutyCycle(duty_cycle)
    print(f"🎯 設定角度 {angle}° (PWM: {duty_cycle:.2f}%)")
    time.sleep(1.5)

def test_precision():
    """測試校準精度"""
    print("🎯 校準精度測試")
    print("=" * 40)
    
    # 測試所有校準點
    print("📍 測試直接校準點:")
    for angle in sorted(SERVO_CALIBRATION.keys()):
        duty_cycle = SERVO_CALIBRATION[angle]
        print(f"角度 {angle:3d}° -> PWM {duty_cycle:5.2f}%")
        set_calibrated_angle(angle)
        time.sleep(2)
    
    print("\n📐 測試插值角度:")
    # 測試插值角度
    test_angles = [15, 30, 60, 75, 105, 120, 150, 165]
    for angle in test_angles:
        duty_cycle = get_calibrated_duty_cycle(angle)
        print(f"角度 {angle:3d}° -> PWM {duty_cycle:5.2f}% (插值)")
        set_calibrated_angle(angle)
        time.sleep(2)

def sweep_test():
    """掃描測試"""
    print("\n🔄 平滑掃描測試")
    print("從 0° 到 180°，每 10° 一步")
    
    for angle in range(0, 181, 10):
        duty_cycle = get_calibrated_duty_cycle(angle)
        print(f"角度 {angle:3d}° -> PWM {duty_cycle:5.2f}%")
        set_calibrated_angle(angle)
        time.sleep(1)
    
    # 回到中心
    print("回到中心位置 (90°)")
    set_calibrated_angle(90)

def compare_calibration():
    """比較校準前後的差異"""
    print("\n📊 校準前後比較")
    print("=" * 60)
    print("角度   標準PWM   校準PWM   差異")
    print("-" * 60)
    
    for angle in sorted(SERVO_CALIBRATION.keys()):
        # 標準計算 (舊方法)
        reversed_angle = 180 - angle
        standard_pwm = 2.5 + (reversed_angle / 180.0) * 10
        
        # 校準值
        calibrated_pwm = SERVO_CALIBRATION[angle]
        
        # 差異
        difference = calibrated_pwm - standard_pwm
        
        print(f"{angle:3d}°   {standard_pwm:6.2f}%   {calibrated_pwm:6.2f}%   {difference:+6.2f}%")

def interactive_test():
    """互動測試模式"""
    print("\n🎮 互動測試模式")
    print("輸入角度 (0-180) 進行測試")
    print("輸入 'quit' 退出")
    
    while True:
        try:
            user_input = input("\n輸入角度: ").strip()
            
            if user_input.lower() == 'quit':
                break
            
            angle = int(user_input)
            if 0 <= angle <= 180:
                set_calibrated_angle(angle)
            else:
                print("❌ 角度必須在 0-180 之間")
        
        except ValueError:
            print("❌ 請輸入有效的數字")
        except KeyboardInterrupt:
            print("\n⚡ 退出互動模式")
            break

def main():
    """主程式"""
    global p
    
    try:
        # 初始化 PWM
        p = GPIO.PWM(servoPIN, 50)
        p.start(get_calibrated_duty_cycle(90))
        
        print("🎯 伺服馬達校準測試程式")
        print("📍 GPIO Pin: 13")  # 更新為 GPIO 13
        print("⚙️  使用校準資料進行精確控制")
        
        # 初始化到中心位置
        print("\n🏠 馬達初始化到中心位置...")
        set_calibrated_angle(90)
        time.sleep(2)
        
        while True:
            print("\n" + "="*40)
            print("📋 測試選單:")
            print("1. 精度測試 (所有角度)")
            print("2. 掃描測試 (平滑移動)")
            print("3. 校準前後比較")
            print("4. 互動測試")
            print("5. 結束程式")
            
            choice = input("\n請選擇 (1-5): ").strip()
            
            if choice == '1':
                test_precision()
            elif choice == '2':
                sweep_test()
            elif choice == '3':
                compare_calibration()
            elif choice == '4':
                interactive_test()
            elif choice == '5':
                break
            else:
                print("❌ 請選擇 1-5")
    
    except KeyboardInterrupt:
        print("\n⚡ 程式被中斷")
    
    finally:
        # 清理
        print("\n🧹 清理 GPIO...")
        if 'p' in globals():
            set_calibrated_angle(90)  # 回到中心
            time.sleep(1)
            p.stop()
        GPIO.cleanup()
        print("✅ 清理完成")

if __name__ == '__main__':
    main()