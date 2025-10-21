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

# 個別角度的微調參數 (servo 值偏移量)
angle_adjustments = {
    0: 0.0,    # 0度的微調值
    45: 0.0,   # 45度的微調值
    90: 0.0,   # 90度的微調值
    135: 0.0,  # 135度的微調值
    180: 0.0   # 180度的微調值
}

def angle_to_servo_value(angle):
    """將角度轉換為 gpiozero Servo 的值 - 修正方向並支援個別微調"""
    # 修正方向：0度 -> +1 (右邊), 90度 -> 0 (中間), 180度 -> -1 (左邊)
    servo_value = 1 - (angle / 180.0) * 2
    
    # 套用個別角度的微調
    if angle in angle_adjustments:
        servo_value += angle_adjustments[angle]
    
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

def adjust_individual_angles(servo):
    """個別調整各角度的參數"""
    print("\n🎯 個別角度微調")
    print("=" * 50)
    
    while True:
        print(f"\n📋 當前角度微調值:")
        for angle in TEST_ANGLES:
            adjustment = angle_adjustments[angle]
            servo_value = angle_to_servo_value(angle)
            print(f"  {angle:3d}° -> 微調: {adjustment:+6.3f} -> 最終servo值: {servo_value:+6.3f}")
        
        print(f"\n選擇要調整的角度:")
        for i, angle in enumerate(TEST_ANGLES, 1):
            print(f"{i}. {angle}度")
        print("6. 測試當前設定")
        print("7. 重置所有微調")
        print("8. 返回主選單")
        
        choice = input("\n請選擇 (1-8): ").strip()
        
        if choice in ['1', '2', '3', '4', '5']:
            angle_index = int(choice) - 1
            angle = TEST_ANGLES[angle_index]
            adjust_single_angle(servo, angle)
        elif choice == '6':
            test_current_adjustments(servo)
        elif choice == '7':
            reset_all_adjustments()
        elif choice == '8':
            break
        else:
            print("❌ 請選擇 1-8")

def adjust_single_angle(servo, angle):
    """調整單一角度的參數"""
    print(f"\n🔧 調整 {angle}° 的參數")
    current_adjustment = angle_adjustments[angle]
    current_servo_value = angle_to_servo_value(angle)
    
    print(f"當前微調值: {current_adjustment:+6.3f}")
    print(f"當前servo值: {current_servo_value:+6.3f}")
    
    # 先測試當前位置
    print(f"\n📍 測試當前 {angle}° 位置...")
    test_angle(servo, angle)
    
    while True:
        print(f"\n⚙️ {angle}° 微調選項:")
        print("1. 增加 +0.01 (順時針微調)")
        print("2. 增加 +0.05 (順時針調整)")
        print("3. 減少 -0.01 (逆時針微調)")
        print("4. 減少 -0.05 (逆時針調整)")
        print("5. 手動輸入數值")
        print("6. 測試當前位置")
        print("7. 重置此角度")
        print("8. 完成調整")
        
        choice = input(f"\n調整 {angle}° (1-8): ").strip()
        
        if choice == '1':
            angle_adjustments[angle] += 0.01
        elif choice == '2':
            angle_adjustments[angle] += 0.05
        elif choice == '3':
            angle_adjustments[angle] -= 0.01
        elif choice == '4':
            angle_adjustments[angle] -= 0.05
        elif choice == '5':
            try:
                new_adjustment = float(input("輸入新的微調值 (-1.0 到 +1.0): "))
                if -1.0 <= new_adjustment <= 1.0:
                    angle_adjustments[angle] = new_adjustment
                else:
                    print("❌ 微調值必須在 -1.0 到 +1.0 之間")
                    continue
            except ValueError:
                print("❌ 請輸入有效的數值")
                continue
        elif choice == '6':
            pass  # 直接測試
        elif choice == '7':
            angle_adjustments[angle] = 0.0
            print(f"✅ {angle}° 微調值已重置")
        elif choice == '8':
            break
        else:
            print("❌ 請選擇 1-8")
            continue
        
        # 限制範圍並測試
        angle_adjustments[angle] = max(-1.0, min(1.0, angle_adjustments[angle]))
        new_servo_value = angle_to_servo_value(angle)
        
        print(f"🔄 新的微調值: {angle_adjustments[angle]:+6.3f}")
        print(f"🔄 新的servo值: {new_servo_value:+6.3f}")
        test_angle(servo, angle)

def test_current_adjustments(servo):
    """測試當前所有角度的微調設定"""
    print(f"\n🧪 測試當前微調設定")
    print("=" * 50)
    
    for angle in TEST_ANGLES:
        adjustment = angle_adjustments[angle]
        servo_value = angle_to_servo_value(angle)
        print(f"\n測試 {angle}° (微調: {adjustment:+6.3f}, servo值: {servo_value:+6.3f})")
        servo.value = servo_value
        time.sleep(2.5)  # 較長的等待時間以便觀察
    
    print("\n✅ 完成所有微調測試")

def reset_all_adjustments():
    """重置所有角度的微調值"""
    for angle in TEST_ANGLES:
        angle_adjustments[angle] = 0.0
    print("✅ 所有角度微調值已重置為 0")

def save_adjustments_to_file():
    """將微調值儲存到檔案"""
    try:
        with open("servo_adjustments.txt", "w", encoding="utf-8") as f:
            f.write("# 伺服馬達角度微調參數\n")
            f.write(f"# 脈波範圍: {current_min_pulse:.1f}ms - {current_max_pulse:.1f}ms\n")
            f.write("angle_adjustments = {\n")
            for angle in TEST_ANGLES:
                f.write(f"    {angle}: {angle_adjustments[angle]:.6f},\n")
            f.write("}\n")
        print("✅ 微調參數已儲存到 servo_adjustments.txt")
    except Exception as e:
        print(f"❌ 儲存失敗: {e}")

def load_adjustments_from_file():
    """從檔案載入微調值"""
    try:
        with open("servo_adjustments.txt", "r", encoding="utf-8") as f:
            content = f.read()
            # 簡單的解析 (這裡可以用更安全的方法)
            if "angle_adjustments = {" in content:
                exec(content.split("angle_adjustments = ")[1].split("}")[0] + "}")
                print("✅ 微調參數已從 servo_adjustments.txt 載入")
                return True
    except FileNotFoundError:
        print("📝 沒有找到儲存的微調檔案")
    except Exception as e:
        print(f"❌ 載入失敗: {e}")
    return False

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
    print("=" * 60)
    print(f"GPIO Pin: {servoPIN}")
    print(f"脈波範圍: {current_min_pulse:.1f}ms - {current_max_pulse:.1f}ms")
    print(f"測試角度: {', '.join(map(str, TEST_ANGLES))}°")
    print(f"方向設定: 0°=右邊, 90°=中間, 180°=左邊")
    
    print("\n角度映射與微調:")
    print("角度  微調值    最終servo值  脈波寬度")
    print("-" * 45)
    for angle in TEST_ANGLES:
        adjustment = angle_adjustments[angle]
        servo_value = angle_to_servo_value(angle)
        pulse_width = calculate_pulse_width(servo_value, current_min_pulse, current_max_pulse)
        print(f"{angle:3d}°  {adjustment:+7.3f}  {servo_value:+8.3f}  {pulse_width:7.3f}ms")

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
        
        # 嘗試載入儲存的微調值
        if load_adjustments_from_file():
            print("🔄 是否要使用載入的微調值？(y/n)")
            if input().strip().lower() == 'y':
                print("✅ 使用載入的微調值")
            else:
                reset_all_adjustments()
                print("✅ 使用預設值")
        
        while True:
            print("\n" + "="*60)
            print("📋 測試選單:")
            print("1. 測試所有關鍵角度 (0, 45, 90, 135, 180)")
            print("2. 互動角度測試")
            print("3. 掃描測試 (0° - 180°)")
            print("4. 🎯 個別角度微調 (NEW!)")
            print("5. 調整脈波寬度參數")
            print("6. 顯示當前參數")
            print("7. 儲存微調參數")
            print("8. 載入微調參數")
            print("9. 重新初始化伺服")
            print("0. 結束程式")
            
            choice = input("\n請選擇 (0-9): ").strip()
            
            if choice == '1':
                test_all_angles(servo)
            elif choice == '2':
                interactive_angle_test(servo)
            elif choice == '3':
                sweep_test(servo)
            elif choice == '4':
                adjust_individual_angles(servo)
            elif choice == '5':
                if servo:
                    servo.close()
                adjust_pulse_width()
                servo = create_servo()
                print("✅ 伺服重新初始化完成")
            elif choice == '6':
                show_parameter_info()
            elif choice == '7':
                save_adjustments_to_file()
            elif choice == '8':
                load_adjustments_from_file()
            elif choice == '9':
                if servo:
                    servo.close()
                servo = create_servo()
                print("✅ 伺服重新初始化完成")
                test_angle(servo, 90)
            elif choice == '0':
                break
            else:
                print("❌ 請選擇 0-9")
    
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