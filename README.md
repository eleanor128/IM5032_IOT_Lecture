# HW1 - Raspberry Pi & 7-Segment Display

## Wiring

<div align="center">
<img height="540" alt="image" src="wiring.jpg" />
</div>


## Task 1 - Display & Read Input

The source code is in **hw_task.py** (ssd_rpigpio.py) , using RPi.GPIO  
Identified the two 7-segment dislay are both **Common Cathode (CC)**.  

<div align="center">
<img width="240" height="" alt="image" src="CC.jpg"/>
</div>

Demo video: https://youtube.com/shorts/FcWIsOccVfQ?feature=share
* Stage 1: display + LED demo
* Stage 2: input + output  
=> input 7,  output 7  
=> input 999,  invalid so LED on  
=> input 84, output 84  
=> input 3.5, output 3.5



## Task 2 - Stretch Ideas - Find The Numbers (Multiplication Game)

The source code is in **little_game.py** , using RPi.GPIO  
Demo video: https://youtu.be/1HFVEPgfIn8 

### How to Play:
1. **Start**: Press Enter to begin the game
2. **Random Display**: The two seven-segment displays will continuously show random numbers (0-9) with random decimal points
3. **Stop**: Press Enter again to stop and freeze the display
4. **Challenge**: Input two numbers that multiply to equal the displayed number
5. **Feedback**: 
   - **Correct Answer**: LED flashes in *short-long-short-long* pattern (3 times)
   - **Wrong Answer**: LED flashes in *long-long* pattern (3 times)

### Game Features:

- Supports both integers (0~99) and decimals (X.Y format)
- Only the first display will show decimal point
- Allows decimal inputs for multiplication
- Continuous gameplay until user exits

### Example Gameplay:
- Display shows: `3.7` → Input: `3.7 × 1 = 3.7` ✅
- Display shows: `24` → Input: `4 × 6 = 24` ✅  
- Display shows: `1.5` → Input: `1.5 × 2 = 3.0` ❌


