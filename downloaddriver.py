import os
import shutil
from webdriver_manager.microsoft import EdgeChromiumDriverManager

def download_driver():
    driver_path = EdgeChromiumDriverManager().install()
    new_path = './edgedriver_win64'
    os.makedirs("./edgedriver_win64/", exist_ok=True)
    shutil.copy(driver_path, new_path)
