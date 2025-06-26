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
        time.sleep(1)
        #game_actions.goto_garden()
        time.sleep(1)
        #game_actions.goto_seeds()
        time.sleep(1)
        #game_actions.goto_sell()
        