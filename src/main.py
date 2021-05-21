import logging

from croning_naist_syllabus.gui import GUI

logger = logging.getLogger()

if __name__ == "__main__":
    gui = GUI()
    window = gui.start_display()

    while True:
        event, values = window.read()
        logger.debug(event, values)
        if event == None:
            break
        elif event == "display_lecture":
            window.close()
            window = gui.display_lectures(values)
        elif event == "display_detail":
            window.close()
            window = gui.display_details(values)
        elif event == "refetch_details":
            window.close()
            window = gui.display_details(values, True)

    window.close()
