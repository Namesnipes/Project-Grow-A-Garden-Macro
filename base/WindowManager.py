import json
import sys
from time import sleep
import pyautogui
from screen_ocr import Reader


class WindowManager:
    def __init__(self, config_path='config.json'):
        self.config = self._load_config(config_path)
        self.os_name = sys.platform

        self.window = None
        self.yOffset = self.config['title_bar_offsets'].get(self.os_name, 30)
        self.xOffset = self.config['border_offsets'].get(self.os_name, 5)
        self.ocr_reader = Reader.create_quality_reader()

    def _load_config(self, path):
        """Loads the JSON configuration file."""
        with open(path, 'r') as f:
            return json.load(f)

    def setup_window(self):
        """Finds, activates, and standardizes the target window."""
        
        windows = pyautogui.getWindowsWithTitle(self.config['window_title']) # type: ignore
        if not windows:
            print("Error: Roblox window not found.")
            return False
        
        # get window containing only "Roblox"
        windows = [w for w in windows if self.config['window_title'] == w.title]
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
            if location:
                self.xOffset = location.x - self.config.get("game_elements").get("seed_button")[0]
                self.yOffset = location.y - self.config.get("game_elements").get("seed_button")[1]
                print(f"Height and width of top bar/sidebar: {self.xOffset}, y: {self.yOffset}")

        except Exception as e:
            print(f"Error standardizing window {e}")
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

    def get_words_in_bounding_box(self, bounding_box):
        """
        Performs OCR on a screen region and returns a list of lowercase text lines.
        
        Args:
            bounding_box: A tuple (left, top, right, bottom) defining the area.
            ocr_reader: An initialized screen_ocr.Reader instance.

        Returns:
            A list of tuples, where each tuple contains:
            - A lowercase string of the detected line of text.
            - A tuple (x, y) for the line's center coordinates.
        """
        result = self.ocr_reader.read_screen(bounding_box)
        
        output = []
        for line in result.result.lines:
            if not line.words:
                continue
                
            line_text = "".join(word.text + " " for word in line.words).strip().lower()
            
            first_word = line.words[0]
            last_word = line.words[-1]
            
            mid_y = int(first_word.top + (first_word.height / 2))
            mid_x = int((first_word.left + (last_word.left + last_word.width)) / 2)
            
            output.append((line_text, (mid_x, mid_y)))
            
        return output