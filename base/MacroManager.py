import pyautogui
import pydirectinput
from pytweening import easeOutCirc
import sys
from time import sleep
import json
import os
from .WindowManager import WindowManager

class GAGMacro:
    def __init__(self, config_path='config.json'):
        self.os_name = sys.platform
        self.asset_path = os.path.join('assets', self.os_name)
        self.config = self._load_config(config_path)

        pyautogui.PAUSE = 0 # Removing the built-in delay completely bcs we won't use this for inputs
        pydirectinput.PAUSE = 0.05 # Lowering the built-in delay, but leaving a small one so the clicks and movements register

        self.window_manager = WindowManager(config_path)
        self.game_actions = GameActions(self)
    
    def _load_config(self, config_path):
        """
        Load configuration from a JSON file.
        """
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
            return {}
    
    def click(self, x, y):
        """
            Clicks at x, y in CLIENT coordinates (ignores window title bar and border).
        """
        # convert to client coordinates
        x = x + self.window_manager.xOffset
        y = y + self.window_manager.yOffset
        if self.os_name == 'win32':
            pydirectinput.moveTo(x, y)
            pydirectinput.moveRel(1,1)
            pydirectinput.moveRel(-1,-1)
            pydirectinput.click()
        else:
            pyautogui.moveTo(x, y)
            pyautogui.click()

    def move(self, x, y):
        """
            Clicks at x, y in CLIENT coordinates (ignores window title bar and border).
        """
        # convert to client coordinates
        x = x + self.window_manager.xOffset
        y = y + self.window_manager.yOffset
        if self.os_name == 'win32':
            pydirectinput.moveTo(x, y)
            pydirectinput.moveRel(1,1)
            pydirectinput.moveRel(-1,-1)
        else:
            pyautogui.moveTo(x, y)

    def click_center(self):
        """
        Clicks the center of the current window.
        """
        
        coordinates = self.window_manager.get_center_coordinates()
        if coordinates is None:
            print("Error: Could not get center coordinates")
            return False
        
        center_x, center_y = coordinates
        self.click(center_x, center_y)
        return True

    def click_image(self, image_name, confidence=0.9):
        """
        Finds and clicks the center of a given image on the screen.
        This is the preferred method for clicking buttons.
        """

        image_path = os.path.join(self.asset_path, image_name)
        if not os.path.exists(image_path):
            print(f"Error: Image asset not found at '{image_path}'")
            return False

        try:
            location = pyautogui.locateCenterOnScreen(
                image_path,
                confidence=confidence,
                region=self.window.box
            )
            
            if location:
                print(f"Found '{image_name}' at {location}. Clicking...")
                pyautogui.click(location)
                return True
            else:
                print(f"Error: Could not find '{image_name}' on screen.")
                return False
        except pyautogui.PyAutoGUIException as e:
            print(f"Error during image search. Details: {e}")
            return False

    def find_image(self, image_name, confidence=0.9):
        """
        Checks if an image is on the screen.
        """

        if not os.path.exists(image_name):
            print(f"Error: Image asset not found at '{image_name}'")
            return False

        try:
            pyautogui.locateOnScreen(image_name, confidence=confidence, region=self.window.box)
            # If above succeeds, we can just return True, since it returns an exeption if it fails
            return True
        except pyautogui.ImageNotFoundException:
            return False
        except pyautogui.PyAutoGUIException as e:
            print(f"Error during image search. Details: {e}")
        
    def setup_window(self):
        """
        Sets up the window using the WindowManager.
        """
        success = self.window_manager.setup_window()
        if success:
            # Store a reference to the window for convenience
            self.window = self.window_manager.window
        return success
    
class GameActions:
    """
    A class to handle game-specific actions.
    """
    
    def __init__(self, macro):
        self.macro = macro
        self.game_elements = self.macro.config.get('game_elements')

    def goto_seeds(self):
        """
        Navigates to the Seed shop.
        """
        seed_coords = self.game_elements.get('seed_button')
        return self.macro.click(*seed_coords)

    def goto_garden(self):
        """
        Navigates to the Garden.
        """
        print(self.game_elements)
        garden_coords = self.game_elements.get('garden_button')
        return self.macro.click(*garden_coords)

    def goto_sell(self):
        """
        Navigates to the Sell shop.
        """
        sell_coords = self.game_elements.get('sell_button')
        return self.macro.click(*sell_coords)
    
    def set_camera_and_settings(self):
        """
        Consistently sets an optimal angle to walk around
        """
        def toggle_follow_mode():
            pydirectinput.press("esc")
            sleep(0.4)
            pydirectinput.press("tab")
            sleep(0.3)
            pydirectinput.press("down")
            sleep(0.3)
            pydirectinput.press("right")
            sleep(0.3)
            pydirectinput.press("right")
            sleep(0.3)
            pydirectinput.press("esc")
        self.macro.click_center()
        pyautogui.scroll(1000000) # Going first person
        sleep(0.2)

        # Looking up. (windows only)
        pydirectinput.PAUSE = 0.002 # Temporarely, because this part would be too slow otherwise
        for i in range(1, 100):
            pydirectinput.moveRel(0,int(200*easeOutCirc(i/100))) # A fucking genius way of bypassing what I think is Roblox trying to prevent robotic mouse movement
        pydirectinput.PAUSE = 0.05

        sleep(0.3)
        pyautogui.scroll(-2500) # Going third person
        print(f"Camera zoom set. Aligning... ")

        toggle_follow_mode()
        sleep(0.5)
        pyautogui.scroll(-3000)
        sleep(0.2)
        pydirectinput.PAUSE = 0 # Temporarely, because this part would be too slow otherwise
        for i in range(0,6): # Abusing the follow camera mode to align the camera
            self.goto_seeds()
            sleep(0.05)
            self.goto_sell()
            sleep(0.05)
        pydirectinput.PAUSE = 0.05
        
        toggle_follow_mode()
        print("Camera and settings complete!")
        sleep(0.5)
