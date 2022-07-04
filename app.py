#Create app using with separating widget
from tkinter import *
import cv2
import os
from canvas_image import CanvasImage
from pcb import PCB
from xlsxwriter import Workbook
from yolov5.detectPCB import detect

# Advanced zoom for images of various types from small to huge up to several GB
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from tkinter import filedialog as fd


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        # App Title
        self.title("Defect Detection for PCB")
        self.iconbitmap("pcb_icon.ico")
        self.geometry("1000x550")
        self.resizable(0, 0)

        self.dict_pcb = {}

        self.listIndex = IntVar(
            self,
            name='listIndex',
            value=0
        )

        # String variables
        self.currentImgName = StringVar(
            self,
            name='currentImgName',
            value=''
        )

        # Menu
        self.menubar = Menu(self)

        file_menu = tk.Menu(self.menubar, tearoff=0)
        # Adding a open File button
        file_menu.add_command(label="Open Files", command=self.select_file)
        # Adding a open Folder button
        file_menu.add_command(label="Open Folder", command=self.select_folder)

        file_menu.add_separator()

        file_menu.add_command(label="Clear", command=self.clear_app)

        self.menubar.add_cascade(label="File", menu=file_menu)

        run_menu = tk.Menu(self.menubar, tearoff=0)
        # Adding a open Run
        run_menu.add_command(label="Run", command=self.defectDetectPCB)
        # Adding a open Run All
        run_menu.add_command(label="Run All", command=self.defectDetectPCBAll)

        self.menubar.add_cascade(label="Run", menu=run_menu)

        export_menu = tk.Menu(self.menubar, tearoff=0)

        export_menu.add_command(label="Report", command=self.export_report)

        export_menu.add_command(label="Images", command=self.save_image_predict)

        self.menubar.add_cascade(label="Export", menu=export_menu)

        self.menubar.add_command(label="Exit", command=self.quit)

        # Make the menubar the Main Menu
        self.config(menu=self.menubar)

        # Create Panedwindow
        panedwindow = ttk.Panedwindow(self, orient=HORIZONTAL)
        panedwindow.pack(fill=BOTH, expand=True)

        # Create Panedwindow_left
        panedwindow_left = ttk.Panedwindow(self, orient=VERTICAL)
        panedwindow_left.pack(fill=BOTH, expand=True)

        # Create Panedwindow_right
        panedwindow_right = ttk.Panedwindow(self, orient=VERTICAL)
        panedwindow_right.pack(fill=BOTH, expand=True)

        # Initialize style
        s = ttk.Style()
        # Create style used by default for all Frames
        s.configure('TFrame', background="#3C4043")

        # Add Frames to Panedwindow
        self.frame_lefttop = ttk.Frame(panedwindow_left, width=200, height=375, relief=SUNKEN, style="TFrame")
        self.frame_leftbottom = ttk.Frame(panedwindow_left, width=200, height=175, relief=SUNKEN, style="TFrame")
        panedwindow_left.add(self.frame_lefttop)
        panedwindow_left.add(self.frame_leftbottom)
        panedwindow.add(panedwindow_left)

        self.frame_rightbottom = ttk.Frame(panedwindow_right, width=800, height=550, relief=SUNKEN, style="TFrame")
        panedwindow_right.add(self.frame_rightbottom)
        panedwindow.add(panedwindow_right)

        # Create a Label Widget to display the text or Image
        panedwindow.update_idletasks()

        # List of files and folder
        self.list_files = Listbox(self.frame_lefttop, bg="#3C4043", font=('Arial 10'))
        self.list_files.grid(sticky='NSEW', column=0, row=0, ipadx=500, ipady=100)

        # List Accelerators
        self.list_files.bind('<Double-1>', self.changePathByClick)
        self.list_files.bind('<Return>', self.changePathByClick)

    def select_file(self):
        try:
            filetypes = [
                ('Image files', "*.jpg *.jpeg *.png")
            ]
            #fd.fd.askopenfilenames
            filenames = fd.askopenfilenames(
                title='Open file',
                initialdir='/',
                filetypes=filetypes)

            # Inserting the files and directories into the list
            for file in filenames:
                file_split = file.split("/")
                file_split.reverse()

                for index in range(0,len(file_split)):
                    if index == 0:
                        name = file_split[0]
                    else:
                        name = file_split[index] + "/" + name
                    if name in self.list_files.get(0, 'end'):
                        if file == self.dict_pcb[name].url_image:
                            break
                    else:
                        self.dict_pcb.update({name: PCB(name, file, self.listIndex.get())})
                        self.list_files.insert('end', name)
                        self.list_files.itemconfig(self.dict_pcb[name].id, {'fg': self.dict_pcb[name].getStatus()})
                        self.listIndex.set(self.listIndex.get() + 1)
                        break
        except:
            print("Exit file folder")

    def select_folder(self):
        try:
            foldername = fd.askdirectory(
                title='Open folder',
                initialdir='/')
            # Get all Files and Folders from the given Directory
            directory = os.listdir(foldername)

            # Clearing the list
            self.list_files.delete(0, END)
            imagetail = [".jpg", "jpeg", ".png"]
            # Inserting the files and directories into the list
            self.dict_pcb.clear()
            self.listIndex.set(0)
            for widget in self.frame_rightbottom.winfo_children():
                widget.destroy()
            for widget in self.frame_leftbottom.winfo_children():
                widget.destroy()
            for file in directory:
                if file[-4:].lower() in imagetail:
                    self.dict_pcb.update({file: PCB(file, os.path.join(foldername, file).replace('\\', '/'), self.listIndex.get())})
                    self.list_files.insert('end', file)
                    self.list_files.itemconfig(self.dict_pcb[file].id, {'fg': self.dict_pcb[file].getStatus()})
                    self.listIndex.set(self.listIndex.get() + 1)
        except:
            print("Exit directory")


    def export_report(self):
        try:
            path = fd.asksaveasfilename(defaultextension=".xlsx")
            workbook = Workbook(path)
            worksheet = workbook.add_worksheet()
            # sheet.write(row,col, data, style)
            worksheet.write(0, 0, 'Report of Defect Detection for PCB')
            worksheet.write(1, 0, 'No.')
            worksheet.write(1, 1, 'Name')
            worksheet.write(1, 2, 'Missing hole')
            worksheet.write(1, 3, 'Mouse bite')
            worksheet.write(1, 4, 'Open circuit')
            worksheet.write(1, 5, 'Short')
            worksheet.write(1, 6, 'Spur')
            worksheet.write(1, 7, 'Spurious copper')
            worksheet.write(1, 8, 'Status')

            count = 2
            num = 1
            for pcb in self.dict_pcb.values():
                if pcb.is_process:
                    defect = [0, 0, 0, 0, 0, 0]
                    coor = [[], [], [], [], [], []]
                    for label in pcb.getPCBLabel():
                        defect[label[0]] = defect[label[0]] + 1
                        coor[label[0]].append(str((label[2], label[3], label[4], label[5])))
                    if defect[1] != 0 or defect[2] != 0 or defect[3] !=0:
                        status = 'Damaged'
                    elif defect[0] !=0 or defect[4] !=0 or defect[5] !=0:
                        status = 'Confused'
                    else:
                        status = 'Good'
                    for index in range(len(coor)):
                        coor[index].insert(0, str(defect[index]))
                    worksheet.write(count, 0, num)
                    worksheet.write(count, 1, pcb.name)
                    worksheet.write(count, 2, '\n'.join(coor[0]))
                    worksheet.write(count, 3, '\n'.join(coor[1]))
                    worksheet.write(count, 4, '\n'.join(coor[2]))
                    worksheet.write(count, 5, '\n'.join(coor[3]))
                    worksheet.write(count, 6, '\n'.join(coor[4]))
                    worksheet.write(count, 7, '\n'.join(coor[5]))
                    worksheet.write(count, 8, status)
                    count = count + 1
                    num = num + 1

            workbook.close()
            messagebox.showinfo("Notification", "Report saved successfully!")

        except:
            return

    def save_image_predict(self):
        # try:
            foldername = fd.askdirectory(
                title='Save',
                initialdir='/')

            for pcb in self.dict_pcb.values():
                if pcb.is_process:
                    print(pcb.name)
                    new_filename = 'pred_' + pcb.name.replace('/', '_')
                    print(new_filename)
                    path = os.path.join(foldername, new_filename).replace('\\', '/')
                    cv2.imwrite(path, pcb.image_process)

            messagebox.showinfo("Notification", "Images saved successfully!")

        # except:
        #     print("Exit")

    def clear_app(self):
        self.list_files.delete(0, END)
        self.dict_pcb.clear()
        self.listIndex.set(0)
        self.currentImgName.set('')
        for widget in self.frame_rightbottom.winfo_children():
            widget.destroy()
        for widget in self.frame_leftbottom.winfo_children():
            widget.destroy()


    def defectDetectPCB(self):
        current_pick = self.currentImgName.get()
        if self.dict_pcb[current_pick].is_process == False:
            # get the complete path by joining the current path with the picked item
            image_detect, label_tensor = detect(source=self.dict_pcb[current_pick].url_image)
            self.dict_pcb[current_pick].image_process = image_detect
            self.dict_pcb[current_pick].label = label_tensor.tolist()
            self.dict_pcb[current_pick].is_process = True
            self.list_files.itemconfig(self.dict_pcb[current_pick].id, {'fg': self.dict_pcb[current_pick].getStatus()})
        canvas = CanvasImage(self.frame_rightbottom, self.dict_pcb[current_pick].image_process, 795, 530, is_url=False)  # create widget
        canvas.grid(row=0, column=0)  # show widget


    def defectDetectPCBAll(self):
        current_pick = self.currentImgName.get()
        for image_name in self.dict_pcb.keys():
            if self.dict_pcb[image_name].is_process == False:
                # get the complete path by joining the current path with the picked items
                image_detect, label_tensor = detect(source=self.dict_pcb[image_name].url_image)
                self.dict_pcb[image_name].image_process = image_detect
                self.dict_pcb[image_name].label = label_tensor.tolist()
                self.dict_pcb[image_name].is_process = True
                self.list_files.itemconfig(self.dict_pcb[image_name].id, {'fg': self.dict_pcb[image_name].getStatus()})
        messagebox.showinfo("Notification", "Completed prediction!")
        if current_pick != '':
            canvas = CanvasImage(self.frame_rightbottom, self.dict_pcb[current_pick].image_process, 795, 530, is_url=False)  # create widget
            canvas.grid(row=0, column=0)  # show widget

    def changePathByClick(self, event=None):
        try:
            # Get clicked item.
            current_pick = self.list_files.get(self.list_files.curselection()[0])
            canvas_originImg = CanvasImage(self.frame_leftbottom, self.dict_pcb[current_pick].url_image, 200, 150)  # create widget
            canvas_originImg.grid(row=0, column=0)  # show widget
            self.currentImgName.set(current_pick)
        except:
            print("List is Null")

        try:
            if self.dict_pcb[current_pick].is_process:
                # get the complete path by joining the current path with the picked item
                canvas = CanvasImage(self.frame_rightbottom, self.dict_pcb[current_pick].image_process, 795, 530, is_url=False)  # create widget
                canvas.grid(row=0, column=0)  # show widget
            else:
                for widget in self.frame_rightbottom.winfo_children():
                    widget.destroy()
        except:
            print("First canvas")
