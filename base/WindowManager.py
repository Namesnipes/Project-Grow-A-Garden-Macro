import json
import os
import sys
from time import sleep
import pyautogui


class WindowManager:
    def __init__(self, config_path='config.json'):
        self.config = self._load_config(config_path)
        self.os_name = sys.platform

        self.window = None
        self.yOffset = self.config['title_bar_offsets'].get(self.os_name, 30)
        self.xOffset = self.config['border_offsets'].get(self.os_name, 5)


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
        
        # get window containing only "Roblox"
        windows = [w for w in windows if self.config['window_title_contains'] in w.title]
        self.window = windows[0]
        try:
            self.window.activate()
            sleep(0.3)
            self.window.maximize()
            sleep(0.3)
            self.window.moveTo(0, 0)
            sleep(0.3)
            self.window.resizeTo(self.config['standard_width'], self.config['standard_height'])
            sleep(0.5)
            # get client offset
            location = pyautogui.locateCenterOnScreen(
                "templates/seeds.png",
                region=self.window.box,
                confidence=0.95
            )

            self.xOffset = location.x - self.config.get("game_elements").get("seed_button")[0]
            self.yOffset = location.y - self.config.get("game_elements").get("seed_button")[1]
            print(f"Height and width of top bar/sidebar: {self.xOffset}, y: {self.yOffset}")

        except Exception as e:
            print(f"Error standardizing window: {e}")
            return False
            
        print("Window setup complete!")
        return True

    def get_center_coordinates(self):
        """Returns the center coordinates of the current window."""
        if not self.window:
            print("Error: Window not set up. Call setup_window() first.")
            return None
        
        center_x = self.window.left + self.window.width // 2
        center_y = self.window.top + self.window.height // 2
        return (center_x, center_y)