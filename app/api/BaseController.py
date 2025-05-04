from core.config import get_settings, Settings
import os


class BaseController:
    def __init__(self):
        self.app_settings: Settings = get_settings()
        self.base_dir = os.path.dirname(os.path.dirname(__file__))
        self.file_dir = os.path.join(self.base_dir, 'assets/files')

        # print(f"Base directory: {self.base_dir}")
        # print(f"File directory: {self.file_dir}")
