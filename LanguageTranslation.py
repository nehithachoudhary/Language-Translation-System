import tkinter as tk
import numpy as np
from tkinter import ttk, END, messagebox
from PIL import Image, ImageTk
import cv2
from googletrans import Translator, LANGUAGES

class AutocompleteCombobox(ttk.Combobox):
    def set_completion_list(self, completion_list):
        self._completion_list = sorted(completion_list, key=str.lower)  # sorted case-insensitive
        self._hits = []
        self._hit_index = 0
        self.position = 0
        self.bind('<KeyRelease>', self.handle_keyrelease)
        self['values'] = self._completion_list

    def autocomplete(self, delta=0):
        if delta:
            self.delete(self.position, tk.END)
        else:
            self.position = len(self.get())
        _hits = []
        for item in self._completion_list:
            if item.lower().startswith(self.get().lower()):
                _hits.append(item)
        if _hits != self._hits:
            self._hit_index = 0
            self._hits = _hits
        if _hits:
            self._hit_index = (self._hit_index + delta) % len(_hits)
            self.delete(0, tk.END)
            self.insert(0, _hits[self._hit_index])
            self.select_range(self.position, tk.END)

    def handle_keyrelease(self, event):
        if event.keysym == 'BackSpace':
            self.delete(self.index(tk.INSERT), tk.END)
            self.position = self.index(tk.END)
        if event.keysym == 'Left':
            if self.position < self.index(tk.END):  # delete the selection
                self.delete(self.position, tk.END)
            else:
                self.position -= 1  # delete one character
                self.delete(self.position, tk.END)
        if event.keysym == 'Right':
            self.position = self.index(tk.END)  # go to end (no selection)
        if len(event.keysym) == 1:
            self.autocomplete()


class LanguageTranslatorApp:
    def __init__(self, window, video_source):
        self.window = window
        self.window.title("Language Translator")
        self.video_source = video_source
        self.cap = cv2.VideoCapture(self.video_source)
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.aspect_ratio = self.width / self.height
        self.canvas_width = 1250
        self.canvas_height = int(self.canvas_width / self.aspect_ratio)
        self.canvas = tk.Canvas(window, width=self.canvas_width, height=self.canvas_height)
        self.canvas.pack()

        # Create the input text widget
        self.inputEntry = tk.Text(window, width=35, height=9, font=('Microsoft Yahei UI Light', 11, 'bold'), bd=0, fg='black')
        self.inputEntry.place(x=135, y=320)
        self.inputEntry.configure(bg='slateBlue3', highlightthickness=0)  # Set transparent background

        # Create the output text widget
        self.outputEntry = tk.Text(window, width=35, height=9, font=('Microsoft Yahei UI Light', 11, 'bold'), bd=0, fg='black')
        self.outputEntry.place(x=830, y=320)
        self.outputEntry.configure(bg='slateBlue3', highlightthickness=0)  # Set transparent background

        # Create the combo box with search feature
        languages = list(LANGUAGES.values())
        self.language_combo = AutocompleteCombobox(window, width=17, font=('Microsoft Yahei UI Light', 11, 'bold'))
        self.language_combo.set_completion_list(languages)
        self.language_combo.place(x=545, y=230)
        self.language_combo.set("Choose Language")  # Set default value
        self.language_combo.bind("<FocusIn>", self.on_combobox_focus)

        # Create the translate button
        self.translate_button = tk.Button(window, text='TRANSLATE', font=('Open Sans', 12, 'bold'), bd=3,
                                           bg='slateBlue3', fg='black', cursor='hand2', activebackground='black',
                                           activeforeground='cyan', width=15, command=self.translate)
        self.translate_button.place(x=550, y=500)

        # Create the clear button
        self.clear_button = tk.Button(window, text='CLEAR', font=('Open Sans', 10, 'bold'), bd=3,
                                       bg='slateBlue3', fg='black', cursor='hand2', activebackground='black',
                                       activeforeground='cyan', width=7, command=self.clear)
        self.clear_button.place(x=370, y=460)

        self.update()

    def update(self):
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.resize(frame, (self.canvas_width, self.canvas_height))
            self.photo = ImageTk.PhotoImage(image=Image.fromarray(frame))
            self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)
        self.window.after(10, self.update)

    def load_gif(self, file):
        self.gif_frames = []
        self.gif_index = 0
        gif_info = Image.open(file)
        self.gif_frames = [tk.PhotoImage(file=file, format=f"gif -index {i}") for i in range(gif_info.n_frames)]
        self.show_next_frame()

    def show_next_frame(self):
        if hasattr(self, 'gif_label') and self.gif_index < len(self.gif_frames):
            self.gif_label.config(image=self.gif_frames[self.gif_index])
            self.gif_index = (self.gif_index + 1) % len(self.gif_frames)
            self.window.after(50, self.show_next_frame)
        else:
            # If the gif_label widget does not exist or the index is out of range, stop the animation
            self.gif_index = 0
    def load_gif_frames(self):
        try:
            while True:
                self.gif_frames.append(self.gif.copy())
                self.gif.seek(len(self.gif_frames))
        except EOFError:
            pass
    def update_video(self):
        frame = self.gif_frames[self.current_frame_index]
        photo = ImageTk.PhotoImage(frame)
        self.video_label.configure(image=photo)
        self.video_label.image = photo
        self.current_frame_index = (self.current_frame_index + 1) % len(self.gif_frames)
        self.window.after(30, self.update_video)
    def ok(self):
        self.subwindow_frame.destroy()
    def translate(self):
        dest = self.language_combo.get()
        text = self.inputEntry.get("1.0", "end-1c")  # Get text from the Text widget
        if text == '':
            self.subwindow_frame=tk.Toplevel(self.window,bg="black")
            self.subwindow_frame.title("ERROR")
            self.subwindow_frame.geometry("500x250")
            screen_width = self.window.winfo_screenwidth()
            screen_height = self.window.winfo_screenheight()
            frame_width = 500
            frame_height = 250
            x_coordinate = (screen_width - frame_width) // 2
            y_coordinate = (screen_height - frame_height) // 2
            self.subwindow_frame.geometry(f"{frame_width}x{frame_height}+{x_coordinate}+{y_coordinate}")
            # Video display
            self.video_label = tk.Label(self.subwindow_frame, bg="black")
            self.video_label.place(x=10, y=10, width=200, height=200)
            # Video display
            self.video_label = tk.Label(self.subwindow_frame, bg="black")
            self.video_label.place(x=10, y=10, width=200, height=200)
            # Text display
            self.text_label1 = tk.Label(self.subwindow_frame, text="Hey!!", font=("Helvetica", 18), bg="black", fg="white")  # Set text background color to black and text color to white
            self.text_label1.place(x=250, y=80)
            self.text_label = tk.Label(self.subwindow_frame, text="You didn't enter the text", font=("Helvetica", 16), bg="black", fg="white")  # Set text background color to black and text color to white
            self.text_label.place(x=250, y=110)
            self.gif_path = "sad1.gif"
            self.gif = Image.open(self.gif_path)
            self.gif_frames = []
            self.load_gif_frames()
            self.current_frame_index = 0
            # Play GIF
            self.update_video()
            self.ok_button = tk.Button(self.subwindow_frame,text='OK', font=('Open Sans', 12, 'bold'), bd=3,
                                           bg='white', fg='black', cursor='hand2', activebackground='black',
                                           activeforeground='cyan', width=10, command=self.ok)
            self.ok_button.place(x=360, y=200)
        elif dest == 'Choose Language' or dest == '':
            #messagebox.showinfo("ERROR", "Please select the language")
            self.subwindow_frame=tk.Toplevel(self.window,bg="black")
            self.subwindow_frame.title("ERROR")
            self.subwindow_frame.geometry("500x250")
            screen_width = self.window.winfo_screenwidth()
            screen_height = self.window.winfo_screenheight()
            frame_width = 500
            frame_height = 250
            x_coordinate = (screen_width - frame_width) // 2
            y_coordinate = (screen_height - frame_height) // 2
            self.subwindow_frame.geometry(f"{frame_width}x{frame_height}+{x_coordinate}+{y_coordinate}")
            # Video display
            self.video_label = tk.Label(self.subwindow_frame, bg="black")
            self.video_label.place(x=10, y=10, width=200, height=200)
            # Text display
            self.text_label1 = tk.Label(self.subwindow_frame, text="OOPS!!", font=("Helvetica", 18), bg="black", fg="white")  # Set text background color to black and text color to white
            self.text_label1.place(x=250, y=65)
            self.text_label = tk.Label(self.subwindow_frame, text="You forgot to select the ", font=("Helvetica", 16), bg="black", fg="white")
            self.text_label.place(x=250, y=100)
            self.text_label1 = tk.Label(self.subwindow_frame, text="language", font=("Helvetica", 16), bg="black", fg="white")  # Set text background color to black and text color to white
            self.text_label1.place(x=300, y=130)
            # Video display
            self.video_label = tk.Label(self.subwindow_frame, bg="black")
            self.video_label.place(x=10, y=10, width=200, height=200) 
            self.gif_path = "sad1.gif"
            self.gif = Image.open(self.gif_path)
            self.gif_frames = []
            self.load_gif_frames()
            self.current_frame_index = 0
            # Play GIF
            self.update_video()
            self.ok_button = tk.Button(self.subwindow_frame,text='OK', font=('Open Sans', 12, 'bold'), bd=3,
                                           bg='white', fg='black', cursor='hand2', activebackground='black',
                                           activeforeground='cyan', width=10, command=self.ok)
            self.ok_button.place(x=360, y=200)
        else:
            try:
                translator = Translator()
                translated = translator.translate(text, dest)
                self.Label1 = tk.Label(self.window, text='The Given Text is Translated', font=('Microsoft Yahei UI Light', 12, 'bold'), bg='black', fg='slateBlue3')
                self.Label1.place(x=515, y=420)
                self.Label2 = tk.Label(self.window, width =22, text='into  ' + dest, font=('Microsoft Yahei UI Light', 12, 'bold'), bg='black', fg='slateBlue3')
                self.Label2.place(x=520, y=450)
                # Load GIF image
                self.gif_label = tk.Label(root)
                self.gif_label.place(x=555, y=300)
                self.load_gif("arrow.gif")
                self.outputEntry.delete(1.0, END)
                self.outputEntry.insert(END, translated.text)
            except ValueError as e:
                #messagebox.showinfo("ERROR", "Please select the correct language")
                self.subwindow_frame=tk.Toplevel(self.window,bg="black")
                self.subwindow_frame.title("ERROR")
                self.subwindow_frame.geometry("500x250")
                screen_width = self.window.winfo_screenwidth()
                screen_height = self.window.winfo_screenheight()
                frame_width = 500
                frame_height = 250
                x_coordinate = (screen_width - frame_width) // 2
                y_coordinate = (screen_height - frame_height) // 2
                self.subwindow_frame.geometry(f"{frame_width}x{frame_height}+{x_coordinate}+{y_coordinate}")
                # Video display
                self.video_label = tk.Label(self.subwindow_frame, bg="black")
                self.video_label.place(x=10, y=10, width=200, height=200)
                # Text display
                self.text_label1 = tk.Label(self.subwindow_frame, text="OOPS!!", font=("Helvetica", 16), bg="black", fg="white")  # Set text background color to black and text color to white
                self.text_label1.place(x=250, y=65)
                self.text_label1 = tk.Label(self.subwindow_frame, text="you have selected", font=("Helvetica", 16), bg="black", fg="white")
                self.text_label1.place(x=250, y=90)
                self.text_label = tk.Label(self.subwindow_frame, text="incorrect language ", width=20,font=("Helvetica", 16), bg="black", fg="white")
                self.text_label.place(x=250,y=115)
                # Video display
                self.video_label = tk.Label(self.subwindow_frame, bg="black")
                self.video_label.place(x=10, y=10, width=200, height=200)
                self.gif_path = "sad1.gif"
                self.gif = Image.open(self.gif_path)
                self.gif_frames = []
                self.load_gif_frames()
                self.current_frame_index = 0
                # Play GIF
                self.update_video()
                self.ok_button = tk.Button(self.subwindow_frame,text='OK', font=('Open Sans', 12, 'bold'), bd=3,
                                               bg='white', fg='black', cursor='hand2', activebackground='black',
                                               activeforeground='cyan', width=10, command=self.ok)
                self.ok_button.place(x=360, y=200)


    def clear(self):
        self.inputEntry.delete(1.0, END)
        self.outputEntry.delete(1.0, END)
        self.gif_label.destroy()
        self.Label1.destroy()
        self.Label2.destroy()

    def on_combobox_focus(self, event):
        if self.language_combo.get() == "Choose Language":
            self.language_combo.set("")

root = tk.Tk()
video_source = 'bg.mp4'
app = LanguageTranslatorApp(root, video_source)
root.mainloop()
