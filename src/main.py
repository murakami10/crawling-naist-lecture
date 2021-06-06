import logging

from crawling_naist_syllabus.gui import GUI

# logの出力設定
formating = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(format=formating)
logging.getLogger("crawling_naist_syllabus").setLevel(level=logging.WARNING)

if __name__ == "__main__":
    gui = GUI()
    gui.loop()
