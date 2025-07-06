from time import sleep
from base.MacroManager import GAGMacro


if __name__ == '__main__':
    print("Starting macro in 3 seconds...")
    sleep(3)

    macro = GAGMacro()
    game_actions = macro.game_actions
    
    if macro.setup_window():
        game_actions.goto_garden()
        sleep(0.5)
        game_actions.set_camera_and_settings()  
        sleep(0.5)  
        game_actions.put_recall_wrench_in_hotbar()
        sleep(0.5)
        game_actions.buy_from_gear_shop()