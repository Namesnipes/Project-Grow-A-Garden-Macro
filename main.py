import time
from base.MacroManager import GAGMacro


if __name__ == '__main__':
    print("Starting macro in 3 seconds...")
    time.sleep(3)

    macro = GAGMacro()
    game_actions = macro.game_actions
    
    if macro.setup_window():
        time.sleep(0.5)
        game_actions.set_camera_and_settings()
        game_actions.sell_inventory()
        