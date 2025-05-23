from tkinter import Tk
from app import ImageCrawlerApp

if __name__ == "__main__":
    root = Tk()
    app = ImageCrawlerApp(root)
    root.mainloop() 

# pyinstaller --onefile --windowed main.py