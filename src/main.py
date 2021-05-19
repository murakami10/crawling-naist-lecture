from croning_naist_syllabus.GUI import GUI

if __name__ == "__main__":
    gui = GUI()
    window = gui.start_display()

    while True:
        event, values = window.read()
        print(event, values)
        if event == None:
            break
        elif event == "start_display":
            window.close()
            window = gui.request_lectures()
        elif event == "request_lectures":
            window.close()
            window = gui.display_lecture(values)
        elif event == "detail":
            window.close()
            window = gui.display_details(values)

    window.close()
