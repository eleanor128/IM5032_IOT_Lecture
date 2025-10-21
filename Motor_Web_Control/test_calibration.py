#!/usr/bin/env python3
"""
gpiozero 伺服馬達參數微調測試程式
針對 0、45、90、135、180 度進行精確調整
"""

from gpiozero import Servo
import time
import sys

# GPIO 設定
servoPIN = 13

# 測試角度
TEST_ANGLES = [0, 45, 90, 135, 180]

# 當前測試的 pulse width 範圍 (可調整)
current_min_pulse = 0.5  # ms
current_max_pulse = 2.5  # ms

def angle_to_servo_value(angle):
    """將角度轉換為 gpiozero Servo 的值 - 直接映射法"""
    # 0度 -> -1 (左邊), 90度 -> 0 (中間), 180度 -> +1 (右邊)
    servo_value = -1 + (angle / 180.0) * 2
    return max(-1, min(1, servo_value))

def calculate_pulse_width(servo_value, min_pulse, max_pulse):
    """計算給定 servo 值的脈波寬度"""
    # servo_value 從 -1 到 +1
    # 對應 min_pulse 到 max_pulse
    normalized = (servo_value + 1) / 2  # 轉換到 0-1 範圍
    pulse_width = min_pulse + normalized * (max_pulse - min_pulse)
    return pulse_width

def test_angle(servo, angle):
    """測試特定角度"""
    servo_value = angle_to_servo_value(angle)
    pulse_width = calculate_pulse_width(servo_value, current_min_pulse, current_max_pulse)
    
    print(f"🎯 測試角度 {angle:3d}° -> servo值: {servo_value:+5.3f} -> 脈波: {pulse_width:.3f}ms")
    servo.value = servo_value
    time.sleep(2)  # 等待舵機移動到位

def test_all_angles(servo):
    """測試所有關鍵角度"""
    print(f"\n📐 測試所有關鍵角度 (脈波範圍: {current_min_pulse:.1f}ms - {current_max_pulse:.1f}ms)")
    print("=" * 70)
    
    for angle in TEST_ANGLES:
        test_angle(servo, angle)
    
    print("\n✅ 完成所有角度測試")

def interactive_angle_test(servo):
    """互動角度測試"""
    print("\n🎮 互動角度測試")
    print("輸入角度 (0-180) 或 'back' 返回主選單")
    
    while True:
        try:
            user_input = input("\n輸入角度: ").strip()
            
            if user_input.lower() == 'back':
                break
            
            angle = int(user_input)
            if 0 <= angle <= 180:
                test_angle(servo, angle)
            else:
                print("❌ 角度必須在 0-180 之間")
        
        except ValueError:
            print("❌ 請輸入有效的數字")
        except KeyboardInterrupt:
            print("\n⚡ 退出互動模式")
            break

def adjust_pulse_width():
    """調整脈波寬度參數"""
    global current_min_pulse, current_max_pulse
    
    print(f"\n⚙️ 當前脈波範圍: {current_min_pulse:.1f}ms - {current_max_pulse:.1f}ms")
    print("調整脈波寬度參數 (輸入 0 跳過)")
    
    try:
        min_input = input(f"新的最小脈波寬度 (當前: {current_min_pulse:.1f}ms): ").strip()
        if min_input and min_input != '0':
            new_min = float(min_input)
            if 0.1 <= new_min <= 1.0:
                current_min_pulse = new_min
                print(f"✅ 最小脈波寬度更新為: {current_min_pulse:.1f}ms")
            else:
                print("❌ 最小脈波寬度應在 0.1-1.0ms 之間")
        
        max_input = input(f"新的最大脈波寬度 (當前: {current_max_pulse:.1f}ms): ").strip()
        if max_input and max_input != '0':
            new_max = float(max_input)
            if 2.0 <= new_max <= 3.0:
                current_max_pulse = new_max
                print(f"✅ 最大脈波寬度更新為: {current_max_pulse:.1f}ms")
            else:
                print("❌ 最大脈波寬度應在 2.0-3.0ms 之間")
    
    except ValueError:
        print("❌ 請輸入有效的數值")

def create_servo():
    """創建伺服物件"""
    return Servo(servoPIN, min_pulse_width=current_min_pulse/1000, max_pulse_width=current_max_pulse/1000)

def sweep_test(servo):
    """掃描測試"""
    print("\n🔄 掃描測試 - 從 0° 到 180°")
    print("每個角度停留 1 秒")
    
    angles = list(range(0, 181, 15))  # 每 15 度一步
    for angle in angles:
        test_angle(servo, angle)
        time.sleep(0.5)  # 較短的等待時間
    
    # 回到中心
    print("\n🏠 回到中心位置 (90°)")
    test_angle(servo, 90)

def show_parameter_info():
    """顯示參數資訊"""
    print("\n📋 當前參數設定:")
    print("=" * 50)
    print(f"GPIO Pin: {servoPIN}")
    print(f"脈波範圍: {current_min_pulse:.1f}ms - {current_max_pulse:.1f}ms")
    print(f"測試角度: {', '.join(map(str, TEST_ANGLES))}°")
    print("\n角度映射:")
    for angle in TEST_ANGLES:
        servo_value = angle_to_servo_value(angle)
        pulse_width = calculate_pulse_width(servo_value, current_min_pulse, current_max_pulse)
        print(f"  {angle:3d}° -> servo值: {servo_value:+5.3f} -> 脈波: {pulse_width:.3f}ms")

def main():
    """主程式"""
    servo = None
    
    try:
        print("🎯 gpiozero 伺服馬達參數微調程式")
        print("=" * 50)
        show_parameter_info()
        
        # 初始化伺服
        servo = create_servo()
        print(f"\n✅ 伺服馬達初始化完成 (GPIO {servoPIN})")
        
        # 初始化到中心位置
        print("\n🏠 馬達初始化到中心位置...")
        test_angle(servo, 90)
        
        while True:
            print("\n" + "="*50)
            print("📋 測試選單:")
            print("1. 測試所有關鍵角度 (0, 45, 90, 135, 180)")
            print("2. 互動角度測試")
            print("3. 掃描測試 (0° - 180°)")
            print("4. 調整脈波寬度參數")
            print("5. 顯示當前參數")
            print("6. 重新初始化伺服")
            print("7. 結束程式")
            
            choice = input("\n請選擇 (1-7): ").strip()
            
            if choice == '1':
                test_all_angles(servo)
            elif choice == '2':
                interactive_angle_test(servo)
            elif choice == '3':
                sweep_test(servo)
            elif choice == '4':
                if servo:
                    servo.close()
                adjust_pulse_width()
                servo = create_servo()
                print("✅ 伺服重新初始化完成")
            elif choice == '5':
                show_parameter_info()
            elif choice == '6':
                if servo:
                    servo.close()
                servo = create_servo()
                print("✅ 伺服重新初始化完成")
                test_angle(servo, 90)
            elif choice == '7':
                break
            else:
                print("❌ 請選擇 1-7")
    
    except KeyboardInterrupt:
        print("\n⚡ 程式被中斷")
    
    except Exception as e:
        print(f"\n❌ 錯誤: {e}")
    
    finally:
        # 清理
        if servo:
            print("\n🏠 回到中心位置...")
            try:
                test_angle(servo, 90)
                time.sleep(1)
            except:
                pass
            servo.close()
        print("✅ 清理完成")

if __name__ == '__main__':
    main()