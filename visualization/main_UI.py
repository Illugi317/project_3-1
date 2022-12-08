from tkinter import *
from PIL import ImageTk, Image
from tkinter import filedialog
from accel import detect_throws_from_data
import os
import cv2, numpy as np


def makeBasic():
    """
    This Initializes the UI, making all the basic boxes and mapping out what is where
    """
    global root, main_array, image_box, white_image, LeftBox, white, current_array
    current_throws = []
    root = Tk()
    root.title("IMU data throw analyzer app!")
    root.config(bg="#A0A882")
    root.resizable(width=NO, height=NO)
    image_box = Label()
    white = np.ones([720, 1080, 3]).astype(np.uint8) * 255
    main_array = white
    white_image = ImageTk.PhotoImage(Image.fromarray(white))
    LeftBox = Canvas(root)
    LeftBox.grid(row=1, column=0, columnspan=6)
    text = Text(LeftBox, width=60,height=20)
    text.pack()
    text.insert(INSERT, "Load IMU data to begin!")
    text.config(state=DISABLED)
    give_legend()
    """
    RightBox = Canvas(root)
    RightBox.grid(row=1, column=6, columnspan=3)
    StartText = Text(LeftBox, width=30)
    StartText.insert(INSERT, "To start, load an image")
    StartText.config(state=DISABLED)
    StartText.pack()
    StartText = Text(RightBox, width=30)
    StartText.insert(INSERT, "To start, load an image")
    StartText.config(state=DISABLED)
    StartText.pack()
    """
    buttonFilePick = Button(root, text="Load new IMU data!", command=lambda: load_file())
    buttonFilePick.config(bg="#CFCF2F")
    buttonFilePick.grid(row=2, column=7, columnspan=4)
    current_array = main_array


def give_list():
    """
    This method returns a nice OptionMenu where the user can choose which throw to inspect
    """
    global current_throws, var, LeftBox
    mylist = []
    for i in range(1, len(current_throws) + 1):
        mylist.append(f"Throw_{i}")
    var = StringVar(LeftBox)
    var.set(mylist[0])
    var.trace("w", update_left_text)
    w = OptionMenu(LeftBox, var, *mylist)
    return w


def update_left(*args):
    """
    This method updates the left column when loading a new data file
    """
    global var, LeftBox, main_array, white, current_throws, left_text
    if main_array is not white:
        LeftBox.grid_forget()
        LeftBox = Canvas(width=200, height=700)
        LeftTop = Label(text="Select the throw to inspect!")
        LeftTop.config(bg="#CFCF2F")
        LeftTop.grid(row=0, column=0, columnspan=6)
        List = give_list()
        List.config(bg="#CFCF2F")
        List.pack()
        LeftBox.grid(row=1, column=0, columnspan=6)
        text = Text(LeftBox, width=60,height=20)
        text.pack()
        current_throw_title = var.get()
        current_throw = current_throws[int(current_throw_title[-1]) - 1]
        throw_data = give_left_text(current_throw)
        text.insert(INSERT, throw_data)
        text.config(state=DISABLED)
        left_text = text
        give_legend()

def give_legend():
    global LeftBox
    picture_legend = Text(LeftBox, width=60, height=10, wrap=WORD)
    picture_legend.pack()
    legend = "How to interpret the plotted image? \n" \
             "The 'X' points are located at the time of each detected throw \n" \
             "The lines at height 100 are highlighting the times when we detected that the die was flying\n" \
             "The lines at height 50 are highlighting the times when we detected that the die was not moving, " \
             "most probably laying on the floor \n"
    picture_legend.insert(INSERT, legend)
def give_left_text(current_throw):
    """
    This method returns the text containing all data we have on a throw
    """
    throw_data = f"The throw happened at time index {current_throw.time} \n" \
                 f"The maximal acceleration value achieved was {current_throw.peak_val} \n" \
                 f"The throw {'did' if current_throw.THROW_ON_FLOOR else 'did not'} land on the floor \n" \
                 f"The time of flight was equal to {current_throw.tof} timesteps \n"
    return throw_data


def update_left_text(*args):
    """
    This method updates the text on the left column when changing the currently inspected throw
    :param args:
    :return:
    """
    global left_text, var
    current_throw_title = var.get()
    current_throw = current_throws[int(current_throw_title[-1]) - 1]
    throw_data = give_left_text(current_throw)
    left_text.config(state=NORMAL)
    left_text.delete("1.0", "end")
    left_text.insert(INSERT, throw_data)
    left_text.config(state=DISABLED)


def load_image(name):
    """
    This short method loads an image, reading it essentially
    """
    image = cv2.imread(name)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    return image


def setWhite():
    """
    This method sets the current image to the blank white image
    """
    global image_box, white_image, white
    image_box.grid_forget()
    image_box = Label(image=white_image)
    image_box.grid(row=1, column=7, columnspan=3)
    updateCurrent(white)


def updateCurrent(image):
    """
    Updates the current image array with given image
    """
    global current_array
    current_array = image


def update_image(image):
    """
    Updates the current image with the given image
    """
    global image_box, MainImage
    image_box.grid_forget()
    MainImage = ImageTk.PhotoImage(Image.fromarray(image))
    image_box = Label(image=MainImage)
    image_box.grid(row=1, column=7, columnspan=3)
    if image.all() == None:
        setWhite()
    updateCurrent(image)


def resizing(image, width, height):
    """
    Resizing method for images
    """
    newSize = (width, height)
    return cv2.resize(image, newSize, interpolation=cv2.INTER_NEAREST)


def update_main_image(filename):
    """
    Updates the main image with the given image   BTW ALL OF THESE IMAGE UPDATES ARE FROM PAST PROJECT,
     WE WILL ONLY HAVE ONE OF THESE RN IM TOO LAZY TO REFACTOR THEM SORRY
    """
    global main_array
    main_array = cv2.imread(filename)
    main_array = cv2.cvtColor(main_array, cv2.COLOR_BGR2RGB)
    main_array = resizing(main_array, 1080, 720)
    update_image(main_array)
    update_left()


def load_file():
    """
    Loads the IMU data and plots everything
    """
    global current_throws
    filename = filedialog.askopenfilename(title="Select the IMU data csv!")
    image_path, throws = detect_throws_from_data(filename, "throw_data")
    current_throws = throws
    update_main_image(image_path)
    os.remove(image_path)


def main():
    """
    Main app loop start
    """
    global root
    makeBasic()
    setWhite()
    root.mainloop()


if __name__ == "__main__":
    main()