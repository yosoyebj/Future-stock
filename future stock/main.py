import time
import sys


print("reading", end="", flush=True)  # Print the message on the same line

for _ in range(3 * 10):  # Multiply by 10 to get 0.1 sec intervals
    time.sleep(0.1)  # Wait 0.1 sec
    sys.stdout.write(".")  # Print a dot
    sys.stdout.flush()  # Immediately show the dot

print("\nDone!")  # Move to the next line when finished


