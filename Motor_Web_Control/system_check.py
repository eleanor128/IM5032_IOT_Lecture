#!/usr/bin/env python3
"""
Raspberry Pi 4 + Raspbian Buster + SG90 系統檢查程式
"""

import sys
import subprocess
import platform

def check_system():
    """檢查系統環境"""
    print("🔍 系統環境檢查")
    print("=" * 50)
    
    # Python 版本
    python_version = sys.version
    print(f"🐍 Python 版本: {python_version}")
    
    # 作業系統資訊
    os_info = platform.platform()
    print(f"💻 作業系統: {os_info}")
    
    # 檢查是否為 Raspberry Pi
    try:
        with open('/proc/cpuinfo', 'r') as f:
            cpuinfo = f.read()
            if 'Raspberry Pi' in cpuinfo:
                print("✅ 確認為 Raspberry Pi")
                if 'Pi 4' in cpuinfo:
                    print("✅ 確認為 Raspberry Pi 4")
            else:
                print("❌ 非 Raspberry Pi 環境")
    except:
        print("❓ 無法確認硬體型號")

def check_libraries():
    """檢查必要函式庫"""
    print("\n📚 函式庫檢查")
    print("=" * 50)
    
    libraries = [
        ('gpiozero', 'GPIO 控制'),
        ('flask', 'Web 伺服器'),
        ('time', '時間控制'),
        ('threading', '多執行緒'),
        ('json', 'JSON 處理')
    ]
    
    for lib, description in libraries:
        try:
            __import__(lib)
            print(f"✅ {lib:12} - {description}")
        except ImportError:
            print(f"❌ {lib:12} - {description} (需要安裝)")

def check_gpio_access():
    """檢查 GPIO 存取權限"""
    print("\n🔌 GPIO 存取檢查")
    print("=" * 50)
    
    try:
        from gpiozero import Device
        print("✅ gpiozero 匯入成功")
        
        # 檢查 GPIO 存取權限
        try:
            from gpiozero import LED
            test_led = LED(26)
            test_led.close()
            print("✅ GPIO 26 存取正常")
        except Exception as e:
            print(f"❌ GPIO 存取錯誤: {e}")
            print("💡 建議: 確保以適當權限執行或加入 gpio 群組")
            
    except ImportError:
        print("❌ gpiozero 未安裝")
        print("💡 安裝命令: sudo apt update && sudo apt install python3-gpiozero")

def test_sg90_compatibility():
    """測試 SG90 相容性"""
    print("\n🎯 SG90 伺服馬達相容性測試")
    print("=" * 50)
    
    try:
        from gpiozero import Servo
        
        # SG90 規格測試
        print("📊 SG90 規格:")
        print("   • 脈衝寬度: 1ms - 2ms")
        print("   • 週期: 20ms (50Hz)")
        print("   • 角度範圍: 0° - 180°")
        print("   • 工作電壓: 4.8V - 6V")
        
        # 創建 SG90 伺服馬達物件
        servo = Servo(13, min_pulse_width=1/1000, max_pulse_width=2/1000)
        print("✅ SG90 伺服馬達物件創建成功")
        
        # 測試基本位置
        test_positions = [
            (-1, "0度"),
            (0, "90度"),
            (1, "180度")
        ]
        
        print("\n🧪 位置測試 (不會實際移動):")
        for position, description in test_positions:
            try:
                # 不實際移動，只測試設定
                print(f"   • {description}: servo.value = {position}")
            except Exception as e:
                print(f"   ❌ {description}: 錯誤 - {e}")
        
        servo.close()
        print("✅ SG90 測試完成")
        
    except Exception as e:
        print(f"❌ SG90 測試失敗: {e}")

def show_recommendations():
    """顯示建議設定"""
    print("\n💡 Raspbian Buster 建議設定")
    print("=" * 50)
    
    recommendations = [
        "確保 gpiozero 版本 >= 1.5.0",
        "使用 sudo 權限或加入 gpio 群組",
        "SG90 使用 4.8V-6V 電源（建議 5V）",
        "控制訊號線連接到 GPIO 13",
        "LED 連接到 GPIO 26 (限流電阻 220-330Ω)",
        "確保共同接地 (GND)"
    ]
    
    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. {rec}")

def check_buster_specific():
    """檢查 Buster 特定設定"""
    print("\n🐧 Raspbian Buster 特定檢查")
    print("=" * 50)
    
    try:
        # 檢查 OS 版本
        with open('/etc/os-release', 'r') as f:
            os_release = f.read()
            if 'buster' in os_release.lower():
                print("✅ 確認為 Raspbian Buster")
            else:
                print("❓ 可能非 Buster 版本")
                
        # 檢查 gpiozero 版本
        import gpiozero
        print(f"✅ gpiozero 版本: {gpiozero.__version__}")
        
        # 檢查 Python 版本相容性
        if sys.version_info >= (3, 6):
            print("✅ Python 版本相容")
        else:
            print("⚠️  Python 版本可能過舊")
            
    except Exception as e:
        print(f"❌ Buster 檢查錯誤: {e}")

def main():
    """主程式"""
    print("🤖 Raspberry Pi 4 + SG90 + gpiozero 系統檢查")
    print("適用於 Raspbian Buster")
    print("=" * 70)
    
    check_system()
    check_libraries()
    check_gpio_access()
    test_sg90_compatibility()
    check_buster_specific()
    show_recommendations()
    
    print("\n" + "=" * 70)
    print("🎯 檢查完成！")
    print("如有問題，請參考上方建議進行設定")

if __name__ == '__main__':
    main()