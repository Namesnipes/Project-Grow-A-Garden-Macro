from datetime import datetime
import logging
import pyautogui
import pydirectinput
from pytweening import easeOutCirc
import sys
from time import sleep
import json
import os
import functools
from .WindowManager import WindowManager
import pygetwindow as gw

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def ensure_roblox_active(func):
    """
    A decorator to ensure the 'Roblox' window is active before executing the decorated function.
    Attempts to activate 'Roblox' if it's not currently active.
    """
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        # Get the window from the instance
        roblox_window = getattr(self, 'window', None) or getattr(self.window_manager, 'window', None)
        
        if roblox_window is None:
            logging.error("No Roblox window found in instance")
            return False
        
        is_active = gw.getActiveWindow() == roblox_window
        if not is_active:
            window_title = getattr(roblox_window, 'title', 'Roblox')
            logging.info(
                f"Pre-check: Window '{window_title}' is NOT active for '{func.__name__}'."
            )
            exit()

        logging.debug(f"Executing '{func.__name__}' for Roblox window...")
        return func(self, *args, **kwargs)

    return wrapper


class GAGMacro:
    def __init__(self, config_path="config.json"):
        self.os_name = sys.platform
        self.asset_path = os.path.join("templates")
        self.config = self._load_config(config_path)

        pyautogui.PAUSE = (
            0  # Removing the built-in delay completely bcs we won't use this for inputs
        )
        pydirectinput.PAUSE = 0.05  # Lowering the built-in delay, but leaving a small one so the clicks and movements register

        self.window_manager = WindowManager(config_path)
        self.game_actions = GameActions(self)

    def _load_config(self, config_path):
        """
        Load configuration from a JSON file.
        """
        try:
            with open(config_path, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
            return {}

    @ensure_roblox_active
    def click(self, x, y):
        """
        Clicks at x, y in CLIENT coordinates (ignores window title bar and border).
        """
        # convert to client coordinates
        x = x + self.window_manager.xOffset
        y = y + self.window_manager.yOffset
        if self.os_name == "win32":
            pydirectinput.moveTo(x, y)
            pydirectinput.moveRel(1, 1)
            pydirectinput.moveRel(-1, -1)
            pydirectinput.click()
        else:
            pyautogui.moveTo(x, y)
            pyautogui.click()
    
    @ensure_roblox_active
    def click_abs(self, x, y):
        """
        Clicks at x, y in CLIENT coordinates (ignores window title bar and border).
        """
        if self.os_name == "win32":
            pydirectinput.moveTo(x, y)
            pydirectinput.moveRel(1, 1)
            pydirectinput.moveRel(-1, -1)
            pydirectinput.click()
        else:
            pyautogui.moveTo(x, y)
            pyautogui.click()

    @ensure_roblox_active
    def move(self, x, y):
        """
        Clicks at x, y in CLIENT coordinates (ignores window title bar and border).
        """
        # convert to client coordinates
        x = x + self.window_manager.xOffset
        y = y + self.window_manager.yOffset
        if self.os_name == "win32":
            pydirectinput.moveTo(x, y)
            pydirectinput.moveRel(1, 1)
            pydirectinput.moveRel(-1, -1)
        else:
            pyautogui.moveTo(x, y)

    @ensure_roblox_active
    def drag(self, start_x, start_y, end_x, end_y):
        """
        Drags the mouse from (start_x, start_y) to (end_x, end_y) in CLIENT coordinates.
        """
        # convert to client coordinates
        start_x += self.window_manager.xOffset
        start_y += self.window_manager.yOffset
        end_x += self.window_manager.xOffset
        end_y += self.window_manager.yOffset

        if self.os_name == "win32":
            pydirectinput.moveTo(start_x, start_y)
            sleep(0.1)
            pydirectinput.mouseDown(button="left")
            sleep(0.1)
            pydirectinput.moveTo(end_x, end_y)
            sleep(0.1)
            pydirectinput.mouseUp(button="left")
        else:
            pyautogui.moveTo(start_x, start_y)
            pyautogui.dragTo(end_x, end_y)

    @ensure_roblox_active
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

    def click_image(self, image_name, confidence=0.9, debug_string=None):
            """
            Finds and clicks the center of a given image on the screen.
            This is the preferred method for clicking buttons.
            
            Returns:
                bool: True if the image was found and clicked, False otherwise.
            """
            image_path = os.path.join(self.asset_path, image_name)
            if not os.path.exists(image_path):
                logging.error(f"Image asset not found at '{image_path}'")
                return False

            try:
                # The region to search in
                search_region = self.window.box if self.window else None

                location = pyautogui.locateCenterOnScreen(
                    image_path, confidence=confidence, region=search_region
                )

                if location:
                    logging.info(f"Found '{image_name}' at {location}. Clicking...")
                    self.click_abs(*location)
                    return True
                else:
                    logging.warning(f"Could not find '{image_name}' on screen with confidence {confidence}.")
                    
                    if debug_string:
                        try:
                            screenshot = pyautogui.screenshot(region=search_region)
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                            filename = f"{debug_string}_{image_name}_{timestamp}.png"
                            screenshot.save(os.path.join("debug", filename))
                            logging.info(f"Saved debug screenshot to '{filename}'")
                        except Exception as e:
                            logging.error(f"Failed to save debug screenshot: {e}")
                    
                    return False

            except pyautogui.PyAutoGUIException as e:
                logging.info(f"Could not find '{image_name}'")
                return False

    def find_image(self, image_name, confidence=0.9):
        """
        Checks if an image is on the screen.
        """

        if not os.path.exists(image_name):
            print(f"Error: Image asset not found at '{image_name}'")
            return False

        try:
            pyautogui.locateOnScreen(
                image_name, confidence=confidence, region=self.window.box if self.window else None
            )
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
        self.game_elements = self.macro.config.get("game_elements")

    def goto_seeds(self):
        """
        Navigates to the Seed shop.
        """
        seed_coords = self.game_elements.get("seed_button")
        return self.macro.click(*seed_coords)
    
    def goto_gear_shop(self):
        """
        Navigates to the Gear shop.
        """
        keybinds = self.macro.config.get("keybinds", {})
        wrench_keybind = keybinds.get("recall_wrench", '2')

        pydirectinput.press(wrench_keybind)
        sleep(0.5) 

        logging.info("Using recall wrench to teleport...")
        self.macro.click_center() 
        sleep(0.2) 
        pydirectinput.click(button="left")
        sleep(0.5) 

    def goto_garden(self):
        """
        Navigates to the Garden.
        """
        print(self.game_elements)
        garden_coords = self.game_elements.get("garden_button")
        return self.macro.click(*garden_coords)

    def goto_sell(self):
        """
        Navigates to the Sell shop.
        """
        sell_coords = self.game_elements.get("sell_button")
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
        pyautogui.scroll(1000000)  # Going first person
        sleep(0.2)

        # Looking up. (windows only)
        pydirectinput.PAUSE = (
            0.002  # Temporarely, because this part would be too slow otherwise
        )
        for i in range(1, 100):
            pydirectinput.moveRel(
                0, int(200 * easeOutCirc(i / 100))
            )  # A fucking genius way of bypassing what I think is Roblox trying to prevent robotic mouse movement
        pydirectinput.PAUSE = 0.05

        sleep(0.3)
        pyautogui.scroll(-2500)  # Going third person

        toggle_follow_mode()
        sleep(0.5)
        pyautogui.scroll(-3000)
        sleep(0.2)
        pydirectinput.PAUSE = (
            0  # Temporarely, because this part would be too slow otherwise
        )
        for i in range(0, 6):  # Abusing the follow camera mode to align the camera
            self.goto_seeds()
            sleep(0.05)
            self.goto_sell()
            sleep(0.05)
        pydirectinput.PAUSE = 0.05

        toggle_follow_mode()
        print("Camera and settings complete!")
        sleep(0.5)

    def sell_inventory(self):
        print("Selling inventory... ")
        self.goto_sell()
        sleep(0.2)
        pydirectinput.press("e")
        sleep(2)
        self.macro.click(*self.game_elements.get("sell_inventory"))
        sleep(1)

    def put_recall_wrench_in_hotbar(self):
        """
        Puts the recall wrench in the hotbar using pydirectinput.

        Opens the backpack (`), selects backpackSearchBar, types "recall" and
        presses enter, then drags the mouse from topLeftItemSlot to itemSlotTwo.
        """
        pydirectinput.press("`")  # Open the backpack
        sleep(0.5)
        self.macro.click(
            *self.game_elements.get("backpack_search_bar")
        )  # Move to the search bar and click
        self.macro.click(
            *self.game_elements.get("backpack_search_bar")
        ) 
        sleep(0.5)
        # Send ctrl+a then delete to clear the search bar
        pydirectinput.press("delete")
        sleep(0.2)
        pydirectinput.write("recall")  # Type the search term
        sleep(0.2)
        pydirectinput.press("enter")  # Press enter to search
        sleep(0.5)

        # Drag the recall wrench from the top left item slot to item slot two
        # pydirectinput's drag is a two-step process: move to start, then drag to end
        self.macro.drag(*self.game_elements.get("top_left_item_slot"), *self.game_elements.get("item_slot_two"))
        sleep(0.5)
        self.macro.click_center()
        sleep(0.5)
        pydirectinput.press("`")  # Close the backpack
        sleep(0.5)
    
    def buy_from_egg_shop(self):
        """
        Automatically buys items from the Egg Shop.
        """
        self.goto_gear_shop()
        confirm_image = "money_symbol.png"

        logging.info("Walking to the first egg...")
        sleep(0.8)
        pydirectinput.keyDown('w')
        sleep(0.9)
        pydirectinput.keyUp('w')
        sleep(0.75)

        for i in range(3):
            log_prefix = f"[Egg {i+1}/{3}]"

            if i > 0:
                logging.info(f"{log_prefix} Nudging forward to next egg...")
                pydirectinput.keyDown('w')
                sleep(0.2)
                pydirectinput.keyUp('w')
                sleep(0.75)

            logging.info(f"{log_prefix} Interacting with egg...")
            pydirectinput.press('e')
            sleep(0.5) 

            logging.info(f"{log_prefix} Looking for '{confirm_image}' to confirm purchase...")
            self.macro.click_image(confirm_image, confidence=0.85, debug_string="egg_purchase")
            sleep(0.5)
    
    def close_gui(self, button_image_name, confidence=0.85):
        """
        Closes a GUI by finding and double-clicking a specified close button.
        """
        logging.info(f"Attempting to close GUI by double-clicking: '{button_image_name}'")

        if self.macro.click_image(button_image_name, confidence=confidence):
            logging.info("First click successful. Performing second click.")
            sleep(0.5) 
            self.macro.click_image(button_image_name, confidence=confidence)

            self.macro.click_center()
            logging.info("GUI close sequence completed.")
            return True
