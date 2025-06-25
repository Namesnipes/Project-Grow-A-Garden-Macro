import time

from macro import GAGMacro


if __name__ == '__main__':
    print("Starting macro in 3 seconds...")
    time.sleep(3)

    macro = GAGMacro()
    
    if macro.setup_window():
        time.sleep(1)
        macro.click_center()
        time.sleep(1)
        macro.click(477, 131)