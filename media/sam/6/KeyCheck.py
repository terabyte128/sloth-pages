#! /usr/bin/python

from Tkinter import *

root = Tk()

root.attributes('-fullscreen', True)

label_text = StringVar()
label_text.set("Press any key to test.")

def quit():
	root.destroy()

text = Label(root, height=200, textvariable=label_text, font=("Arial", 20, "bold"))
close_button = Button(root, text="Close Program", command=quit)

def keyPressed(event):
    label_text.set("PRESSED: " + str(event.keysym))

def keyReleased(event):
    label_text.set("RELEASED: " + str(event.keysym))

root.bind("<KeyPress>", keyPressed)
root.bind("<KeyRelease>", keyReleased)

close_button.pack()
text.pack()

root.mainloop()
