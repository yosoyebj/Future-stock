import sys
import time

def loading_animation():
    #printing reading data with some loading animation
    print("loading .", end="", flush =True)
    for _ in range(30):  # 30 is used to display 3 sec to get 0.1 sec intervals
        time.sleep(0.1)  # Wait 0.1 sec
        sys.stdout.write(".")  # Print a dot
        sys.stdout.flush()  # Immediately show the dot

    sys.stdout.write("\r" + " " * (30 +10) + "\r")
    sys.stdout.flush()
    