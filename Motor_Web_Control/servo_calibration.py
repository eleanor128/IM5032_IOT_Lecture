#!/usr/bin/env python3
"""
伺服馬達 PWM 校準程式
找出每個角度的最適合 PWM 值
"""

import RPi.GPIO as GPIO
import time
import json
from datetime import datetime

# GPIO 設定
servoPIN = 13  # 改為 GPIO 13
GPIO.setmode(GPIO.BCM)
GPIO.setup(servoPIN, GPIO.OUT)

# PWM 設定
p = GPIO.PWM(servoPIN, 50)
p.start(7.5)

# 校準資料儲存
calibration_data = {}

def set_pwm_duty_cycle(duty_cycle):
    """設定 PWM duty cycle"""
    p.ChangeDutyCycle(duty_cycle)
    time.sleep(1.5)  # 給馬達充足時間到達位置

def interactive_calibration():
    """互動式校準每個角度"""
    print("🎯 伺服馬達 PWM 校準程式")
    print("=" * 50)
    print("📍 GPIO Pin: 13")  # 更新為 GPIO 13
    print("🔊 PWM 頻率: 50Hz")
    print("⚙️  標準範圍: 2.5% - 12.5% duty cycle")
    print("=" * 50)
    
    # 要校準的角度
    angles_to_calibrate = [0, 15, 30, 45, 60, 75, 90, 105, 120, 135, 150, 165, 180]
    
    print("📋 校準步驟:")
    print("1. 觀察馬達是否到達正確角度")
    print("2. 如果不準確，輸入調整後的 duty cycle")
    print("3. 如果準確，直接按 Enter 確認")
    print("4. 輸入 'skip' 跳過該角度")
    print("5. 輸入 'quit' 結束校準")
    print()
    
    for angle in angles_to_calibrate:
        print(f"\n🎯 校準角度: {angle}°")
        print("-" * 30)
        
        # 計算標準 duty cycle (反轉角度)
        reversed_angle = 180 - angle
        standard_duty = 2.5 + (reversed_angle / 180.0) * 10
        
        print(f"📊 標準計算值: {standard_duty:.2f}%")
        
        # 設定到標準值
        set_pwm_duty_cycle(standard_duty)
        print(f"✅ 已設定 PWM 為 {standard_duty:.2f}%")
        
        while True:
            try:
                user_input = input(f"角度 {angle}° 是否正確？(Enter=確認 / 數字=調整 / skip=跳過 / quit=退出): ").strip()
                
                if user_input.lower() == 'quit':
                    print("🛑 校準被中斷")
                    return False
                
                elif user_input.lower() == 'skip':
                    print(f"⏭️  跳過角度 {angle}°")
                    break
                
                elif user_input == '':
                    # 確認當前值
                    calibration_data[angle] = standard_duty
                    print(f"✅ 角度 {angle}° 校準完成: {standard_duty:.2f}%")
                    break
                
                else:
                    # 嘗試解析為 duty cycle
                    custom_duty = float(user_input)
                    
                    if 1.0 <= custom_duty <= 15.0:  # 合理範圍
                        set_pwm_duty_cycle(custom_duty)
                        print(f"🔧 已調整為 {custom_duty:.2f}%")
                        
                        confirm = input("此角度正確嗎？(y/n): ").strip().lower()
                        if confirm in ['y', 'yes', '']:
                            calibration_data[angle] = custom_duty
                            print(f"✅ 角度 {angle}° 校準完成: {custom_duty:.2f}%")
                            break
                    else:
                        print("❌ Duty cycle 應在 1.0-15.0 之間")
            
            except ValueError:
                print("❌ 請輸入有效的數字或指令")
            except KeyboardInterrupt:
                print("\n⚡ 校準被中斷")
                return False
    
    return True

def fine_tune_calibration():
    """精細調整校準"""
    print("\n🔧 精細調整模式")
    print("輸入格式: <角度> <duty_cycle>")
    print("例如: 90 7.3")
    print("輸入 'done' 完成調整")
    
    while True:
        try:
            user_input = input("\n輸入角度和 duty cycle: ").strip()
            
            if user_input.lower() == 'done':
                break
            
            parts = user_input.split()
            if len(parts) == 2:
                angle = int(parts[0])
                duty_cycle = float(parts[1])
                
                if 0 <= angle <= 180 and 1.0 <= duty_cycle <= 15.0:
                    set_pwm_duty_cycle(duty_cycle)
                    calibration_data[angle] = duty_cycle
                    print(f"✅ 角度 {angle}° 更新為 {duty_cycle:.2f}%")
                else:
                    print("❌ 角度範圍: 0-180，duty cycle 範圍: 1.0-15.0")
            else:
                print("❌ 格式錯誤，請使用: <角度> <duty_cycle>")
        
        except ValueError:
            print("❌ 請輸入有效的數字")
        except KeyboardInterrupt:
            print("\n⚡ 精細調整結束")
            break

def test_calibration():
    """測試校準結果"""
    if not calibration_data:
        print("❌ 沒有校準資料可測試")
        return
    
    print("\n🧪 測試校準結果")
    print("按任意鍵開始測試，Ctrl+C 停止")
    input()
    
    try:
        sorted_angles = sorted(calibration_data.keys())
        
        for angle in sorted_angles:
            duty_cycle = calibration_data[angle]
            print(f"🎯 測試角度 {angle}° (PWM: {duty_cycle:.2f}%)")
            set_pwm_duty_cycle(duty_cycle)
            time.sleep(2)
    
    except KeyboardInterrupt:
        print("\n⚡ 測試結束")

def save_calibration():
    """儲存校準資料"""
    if not calibration_data:
        print("❌ 沒有校準資料可儲存")
        return
    
    # 準備儲存資料
    save_data = {
        'timestamp': datetime.now().isoformat(),
        'servo_pin': servoPIN,
        'pwm_frequency': 50,
        'calibration_data': calibration_data,
        'notes': '校準資料：角度 -> PWM duty cycle (%)'
    }
    
    # 儲存到檔案
    filename = f"servo_calibration_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(save_data, f, indent=2, ensure_ascii=False)
    
    print(f"💾 校準資料已儲存至: {filename}")
    
    # 顯示校準結果摘要
    print("\n📊 校準結果摘要:")
    print("-" * 40)
    sorted_angles = sorted(calibration_data.keys())
    
    for angle in sorted_angles:
        duty_cycle = calibration_data[angle]
        pulse_width = (duty_cycle / 100) * 20  # 計算脈衝寬度 (ms)
        print(f"角度 {angle:3d}° -> PWM {duty_cycle:5.2f}% -> 脈衝 {pulse_width:.2f}ms")

def generate_code():
    """產生程式碼"""
    if not calibration_data:
        print("❌ 沒有校準資料可產生程式碼")
        return
    
    print("\n💻 產生的程式碼:")
    print("=" * 50)
    
    # 產生校準表
    print("# 伺服馬達校準表")
    print("SERVO_CALIBRATION = {")
    sorted_angles = sorted(calibration_data.keys())
    
    for angle in sorted_angles:
        duty_cycle = calibration_data[angle]
        print(f"    {angle}: {duty_cycle:.2f},")
    
    print("}")
    print()
    
    # 產生插值函數
    print("""
def get_calibrated_duty_cycle(target_angle):
    \"\"\"根據校準資料獲取角度對應的 duty cycle\"\"\"
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
    
    return 7.5  # 預設值

def set_calibrated_angle(angle):
    \"\"\"使用校準資料設定角度\"\"\"
    duty_cycle = get_calibrated_duty_cycle(angle)
    p.ChangeDutyCycle(duty_cycle)
    print(f"設定角度 {angle}° (PWM: {duty_cycle:.2f}%)")
""")

def main():
    """主程式"""
    try:
        print("🎯 伺服馬達 PWM 校準工具")
        print("請確保馬達已正確連接到 GPIO 13")  # 更新為 GPIO 13
        input("按 Enter 開始校準...")
        
        # 馬達置中
        print("\n🏠 馬達置中...")
        set_pwm_duty_cycle(7.5)
        time.sleep(2)
        
        while True:
            print("\n" + "="*50)
            print("📋 校準選單:")
            print("1. 開始角度校準")
            print("2. 精細調整")
            print("3. 測試校準結果")
            print("4. 儲存校準資料")
            print("5. 產生程式碼")
            print("6. 結束程式")
            
            choice = input("\n請選擇 (1-6): ").strip()
            
            if choice == '1':
                success = interactive_calibration()
                if not success:
                    continue
            
            elif choice == '2':
                fine_tune_calibration()
            
            elif choice == '3':
                test_calibration()
            
            elif choice == '4':
                save_calibration()
            
            elif choice == '5':
                generate_code()
            
            elif choice == '6':
                break
            
            else:
                print("❌ 請選擇 1-6")
    
    except KeyboardInterrupt:
        print("\n⚡ 程式被中斷")
    
    finally:
        # 清理
        print("\n🧹 清理 GPIO...")
        set_pwm_duty_cycle(7.5)  # 回到中心
        time.sleep(1)
        p.stop()
        GPIO.cleanup()
        print("✅ 清理完成")

if __name__ == '__main__':
    main()