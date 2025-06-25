import pyautogui
import sys
import time
import json
import os

class GAGMacro:
    def __init__(self, config_path='config.json'):
        self.config = self._load_config(config_path)
        self.os_name = sys.platform
        
        self.asset_path = os.path.join('assets', self.os_name)

        self.window = None
        self.title_bar_height = self.config['title_bar_offsets'].get(self.os_name, 30)
        self.border_width = self.config['border_offsets'].get(self.os_name, 5)


    def _load_config(self, path):
        """Loads the JSON configuration file."""
        with open(path, 'r') as f:
            return json.load(f)

    def setup_window(self):
        """Finds, activates, and standardizes the target window."""
        
        windows = pyautogui.getWindowsWithTitle(self.config['window_title_contains'])
        if not windows:
            print("Error: Roblox window not found.")
            return False
        
        self.window = windows[0]
        try:
            self.window.activate()
            time.sleep(0.5)
            self.window.moveTo(0, 0)
            self.window.resizeTo(self.config['standard_width'], self.config['standard_height'])
            time.sleep(0.5)
            self.title_bar_height = self.config['standard_height'] - self.window.height
            self.border_width = self.config['standard_width'] - self.window.width
        except Exception as e:
            print(f"Error standardizing window: {e}")
            return False
            
        print("Window setup complete!")
        return True
    
    def click(self, x, y):
        pyautogui.click(x, y)
    
    def click_center(self):
        """
        Clicks the center of the current window.
        """
        if not self.window:
            return False
        
        center_x = self.window.left + self.window.width // 2
        center_y = self.window.top + self.window.height // 2
        pyautogui.click(center_x, center_y)
        print(f"Clicked at center: ({center_x}, {center_y})")
        return True

    def click_image(self, image_name, confidence=0.9):
        """
        Finds and clicks the center of a given image on the screen.
        This is the preferred method for clicking buttons.
        """
        if not self.window:
            print("Error: Window not set up. Call setup_window() first.")
            return False

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
            print(f"Error during image search. Ensure OpenCV is installed (`pip install opencv-python`). Details: {e}")
            return False