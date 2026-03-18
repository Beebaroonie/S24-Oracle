import time
import os

if __name__ == '__main__':
    # This dummy service exists solely to satisfy Android 14's strict requirement
    # that a foreground service of type "mediaProjection" is actively running 
    # while the main app captures the screen.
    while True:
        time.sleep(1)