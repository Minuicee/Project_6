from PyQt5.QtWidgets import QHBoxLayout, QLineEdit, QMainWindow, QApplication, QLabel, QGridLayout, QWidget, QVBoxLayout, QPushButton, QColorDialog, QSlider
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor, QPixmap
import sys

 

class MainWindow(QMainWindow):
    
    def __init__(self):
        super().__init__()
        
        #! Changeable Variables
        self.pixels = 150 #(should be square number) amount of pixels used for picture (n²)
        self.brush_size = 5 #standard brush size (formula for "brush_size -> pixel" included in /brush_size_info.png)
        self.frame_size = 600 #size of frame (squared)
        self.color = "gray" #standard color
        
        #*init variables
        self.Settingswindow_isShown = False
        self.mousePressed = False
        self.method_isLoading = False
        self.brush_activated = True
        self.pressed_keys = set()
        self.undo_version = 1
        self.undo_stack = []
        self.pixel_labels = {}
        self.last_save = {}
        
        self.app = app #make it usuable for everything in MainWindow 
        self.initUI()     
            
    def initUI(self):
        self.setWindowTitle("Draw")
        
        #*init layout
        self.setFixedSize(self.frame_size, self.frame_size)
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.grid_layout = QGridLayout()
        self.grid_layout.setContentsMargins(0,0,0,0)
        self.grid_layout.setSpacing(0)
        self.central_widget.setLayout(self.grid_layout)
        
        #*init pixels
        for i in range(self.pixels):
            for j in range(self.pixels):
                label = QLabel(self)
                self.grid_layout.addWidget(label, i, j)
                self.pixel_labels[(i, j)] = label
                self.last_save[(i, j, self.undo_version)] = label.styleSheet() 
                
                
        #*init settingswindow
        self.Settingswindow = QMainWindow()
        self.Settingswindow.setFixedSize(500,300)
        self.Settingswindow.setWindowFlag(Qt.FramelessWindowHint)
        self.central_widget_Settingswindow = QWidget() #layout
        self.Settingswindow.setCentralWidget(self.central_widget_Settingswindow)
        self.layout_Settingswindow = QVBoxLayout()
        self.central_widget_Settingswindow.setLayout(self.layout_Settingswindow)
        
        #*init savewindow
        self.Savewindow = QMainWindow()
        self.Savewindow.setFixedSize(500,300)
        self.central_widget_Savewindow = QWidget() #layout
        self.Savewindow.setCentralWidget(self.central_widget_Savewindow)
        self.layout_Savewindow = QHBoxLayout()
        self.central_widget_Savewindow.setLayout(self.layout_Savewindow)
        
        #*submit button for savewindow
        self.close_Savewindow_button = QPushButton("Save")
        self.layout_Savewindow.addWidget(self.close_Savewindow_button)
        self.close_Savewindow_button.setStyleSheet("background-color: green;font-family: Times New Roman;border-radius: 5px;")
        self.close_Savewindow_button.clicked.connect(self.check_file_name)
        self.close_Savewindow_button.setFixedSize(50,50)
        
        #*savewindow info
        self.savewindow_info = QLabel("Set file name ->")
        self.layout_Savewindow.addWidget(self.savewindow_info)
        self.savewindow_info.setStyleSheet("color: gray;font-family: Times New Roman;font-size: 25px;")
        
        #*Lineedit for savewindow
        self.saveDirectory_lineedit = QLineEdit()
        self.layout_Savewindow.addWidget(self.saveDirectory_lineedit)
        self.saveDirectory_lineedit.setFixedSize(200,50)
        self.saveDirectory_lineedit.setStyleSheet("font-family: Times New Roman;font-size: 25px;")
        self.saveDirectory_lineedit.setAlignment(Qt.AlignCenter)
        
        #*savewindow info for the fileending = .png
        self.savewindow_info_fileending = QLabel(".png")
        self.layout_Savewindow.addWidget(self.savewindow_info_fileending)
        self.savewindow_info_fileending.setFixedSize(50,50)
        self.savewindow_info_fileending.setStyleSheet("color: gray;font-family: Times New Roman;font-size: 25px;")
        
        #*close button for settingswindow
        self.close_Settingswindow_button = QPushButton("X")
        self.layout_Settingswindow.addWidget(self.close_Settingswindow_button)
        self.close_Settingswindow_button.setStyleSheet("background-color: red;font-family: Times New Roman;")
        self.close_Settingswindow_button.clicked.connect(self.close_Settingswindow)
        self.close_Settingswindow_button.setFixedSize(50,50)
        
        #*open color picker button
        self.open_color_picker = QPushButton("Change brush-color")
        self.layout_Settingswindow.addWidget(self.open_color_picker)
        self.open_color_picker.setStyleSheet(f"background-color: {self.color};font-family: Times New Roman;font-size: 35px;border-radius: 15px;border: 2px solid black;") 
        self.open_color_picker.setFixedSize(450,75)
        self.open_color_picker.clicked.connect(self.change_brush_color)
        
        #*brush size info
        self.brush_size_info = QLabel("Brush-size: 5")
        self.layout_Settingswindow.addWidget(self.brush_size_info)
        self.brush_size_info.setStyleSheet("color: black;font-family: Times New Roman;font-size: 35px;")
        
        #*brush size slider
        self.brush_size_slider = QSlider(Qt.Horizontal)
        self.brush_size_slider.setMinimum(1)
        self.brush_size_slider.setMaximum(25)
        self.brush_size_slider.setValue(5)
        self.brush_size_slider.valueChanged.connect(self.update_brush_size)
        self.layout_Settingswindow.addWidget(self.brush_size_slider)
        self.brush_size_slider.setFixedSize(450,50)
        self.brush_size_slider.setStyleSheet("border-radius: 5px;")
    
    def show_Savewindow(self):
            self.pressed_keys.remove(83)       # ↓
            self.pressed_keys.remove(16777249) #somehow needed due to keys not getting removed after this functtion
            self.Savewindow.hide()
            self.Savewindow.show()
        
    def change_brush_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.change_color_picker_button_color(color.name()) #! ↓ Function must be called before ↓
            self.color = color.name() #get string so it can be used for style sheet
            
    def change_color_picker_button_color(self, color):
        #*Function needed so styleSheet doesn't get too long
        
        oldBackground = self.open_color_picker.styleSheet().find(f"background-color: {self.color};")
        #saves new color + everything in style sheet except old color
        newStyleSheet =  self.open_color_picker.styleSheet()[:oldBackground] + self.open_color_picker.styleSheet()[(oldBackground + len(f"background-color: {self.color};")):] + f"background-color: {color};"
        self.open_color_picker.setStyleSheet(newStyleSheet)
        
    def update_brush_size(self, val):
        self.brush_size = val
        self.brush_size_info.setText(f"Brush-size: {val}")
    
    def close_Settingswindow(self):
        self.Settingswindow.hide()
        self.Settingswindow_isShown = False
        
    def show_Settingswindow(self):
        #*Show settingswindow
        if not self.Settingswindow_isShown:
            self.Settingswindow.show()
            self.Settingswindow_isShown = True
    
    def closeEvent(self, event):
        #* Close everything if MainWindow is closed
        self.app.quit()
        self.Settingswindow.close()
    
    def keyPressEvent(self, event):
        key = event.key()
        self.pressed_keys.add(key)
        
        if key == Qt.Key_T:
            if not self.Settingswindow_isShown:
                self.show_Settingswindow()
            else:
                self.close_Settingswindow() #close and open to put it on top of screen again
                self.show_Settingswindow()
                
        elif Qt.Key_Z in self.pressed_keys and Qt.Key_Control in self.pressed_keys:
            if not self.method_isLoading:
                self.method_isLoading = True
                self.undo()
                self.method_isLoading = False
              
        elif Qt.Key_Q in self.pressed_keys and Qt.Key_Control in self.pressed_keys:
            if not self.method_isLoading:
                self.method_isLoading = True
                self.empty_canva()
                self.method_isLoading = False
            
        elif Qt.Key_S in self.pressed_keys and Qt.Key_Control in self.pressed_keys:
            if not self.method_isLoading:
                self.method_isLoading = True
                self.show_Savewindow()
                self.method_isLoading = False
            
        elif Qt.Key_R in self.pressed_keys and Qt.Key_Control in self.pressed_keys:
            if not self.method_isLoading:
                self.method_isLoading = True
                self.rotateImg()
                self.method_isLoading = False
                
        elif Qt.Key_B in self.pressed_keys:
            if not self.brush_activated:
                self.brush_activated = True
        
        elif Qt.Key_E in self.pressed_keys:
            if self.brush_activated:
                self.brush_activated = False
            else:
                self.brush_activated = True
        
    def save(self, filename):
        saved_image = QPixmap(self.size())
        self.render(saved_image)
        saved_image.save(f"{filename}.png")
        
        self.Savewindow.hide()
    
    def check_file_name(self):
        filename = self.saveDirectory_lineedit.text()
        if len(filename) < 1:
            self.warn_invalid_file_name("null")
            return #if theres no character return
        
        if len(filename) > 255: 
            self.warn_invalid_file_name("length")
            return #if file name is longer than 255 characters return
         
        invalid_characters = ["\\", "/", ":", "*", "?", "\"", "<", ">", "|", " "]   
        for character in filename: #look for invalid characters
            if character in invalid_characters:
                self.warn_invalid_file_name("invalid", character)
                return
                
        self.save(filename) #if file name is ok, save file
                  
    def warn_invalid_file_name(self, reason, char=""):
        if reason == "length":
            self.savewindow_info.setText("Too long")
        elif reason == "invalid":
            self.savewindow_info.setText(f"Cant contain {char}")
        else: #else is called if the length of the file name is lower than 1
            self.savewindow_info.setText(f"Atleast 1 char")
      
    def empty_canva(self):
        self.save_current_state()
        for (row, col), pixels in self.pixel_labels.items():
            self.pixel_labels[(row,col)].setStyleSheet("")    
                
    def undo(self):
        #* Undo last thing drawn
        if self.undo_stack:
            last_state = self.undo_stack.pop()
            for (row, col), style in last_state.items():
                self.pixel_labels[(row, col)].setStyleSheet(style)
                
    def save_current_state(self):
        #* Save current drawing
        current_state = {key: pixel.styleSheet() for key, pixel in self.pixel_labels.items()}
        self.undo_stack.append(current_state)
        
    def keyReleaseEvent(self, event):
        self.pressed_keys.discard(event.key())
    
    def mousePressEvent(self, event):
        if not self.mousePressed:
            self.save_current_state()        
            self.draw()
            self.startDrawing = QtCore.QTimer()
            self.startDrawing.timeout.connect(self.draw)
            self.startDrawing.start(0)
            self.mousePressed = True
        
    def mouseReleaseEvent(self, event):
        if self.mousePressed:
            self.startDrawing.stop()
            self.mousePressed = False
        
    def draw(self):
        local_pos = self.central_widget.mapFromGlobal(QCursor.pos())
        pixel_size_x = self.width() // self.pixels
        pixel_size_y = self.height() // self.pixels
        
        row = local_pos.y() // pixel_size_y
        col = local_pos.x() // pixel_size_x
        
        if self.brush_activated:
            color = self.color
        else:
            color = "white"
        
        #*right pixels
        for i in range(self.brush_size-1): 
            y_coordinate = col + (self.brush_size-1 - i) 
            needed_pixels = i * 2 + 1
            side_pixels = (needed_pixels - 1) // 2

            for j in range(side_pixels):
                if 0 <= row - side_pixels + j < self.pixels and 0 <= y_coordinate < self.pixels:
                    self.pixel_labels[(row - side_pixels + j, y_coordinate)].setStyleSheet(f"background-color: {color};")
                if 0 <= row + 1 + j < self.pixels and 0 <= y_coordinate < self.pixels:
                    self.pixel_labels[(row + 1 + j, y_coordinate)].setStyleSheet(f"background-color: {color};")

            if 0 <= row < self.pixels and 0 <= y_coordinate < self.pixels:
                self.pixel_labels[(row, y_coordinate)].setStyleSheet(f"background-color: {color};")

        #*middle pixels
        for i in range((self.brush_size-1)*2+1):
            if 0 <= row - (self.brush_size-1) + i < self.pixels and 0 <= col < self.pixels:
                self.pixel_labels[(row - (self.brush_size-1) + i, col)].setStyleSheet(f"background-color: {color};")

        #*left pixels
        for i in range(self.brush_size-1):
            y_coordinate = col - (self.brush_size-1 - i) 
            needed_pixels = i * 2 + 1
            side_pixels = (needed_pixels - 1) // 2

            for j in range(side_pixels):
                if 0 <= row - side_pixels + j < self.pixels and 0 <= y_coordinate < self.pixels:
                    self.pixel_labels[(row - side_pixels + j, y_coordinate)].setStyleSheet(f"background-color: {color};")
                if 0 <= row + 1 + j < self.pixels and 0 <= y_coordinate < self.pixels:
                    self.pixel_labels[(row + 1 + j, y_coordinate)].setStyleSheet(f"background-color: {color};")

            if 0 <= row < self.pixels and 0 <= y_coordinate < self.pixels:
                self.pixel_labels[(row, y_coordinate)].setStyleSheet(f"background-color: {color};")

    def rotateImg(self):
        self.save_current_state()
        
        #*Make a copy of current image
        tmp = {key: pixel.styleSheet() for key, pixel in self.pixel_labels.items()}
        self.undo_stack.append(tmp)
        
        size = self.pixels #sidelenght of matrix
        
        #*Make tmp be equal to the rotated image
        for col in range(size):
            for row in range(size):
                tmp[row,col] = self.pixel_labels[size-col-1,row].styleSheet()
        
        #*update image to tmp
        for col in range(size):
            for row in range(size):
                self.pixel_labels[row,col].setStyleSheet(tmp[row,col])
                
                

if __name__ == "__main__":
    app = QApplication(sys.argv)
    Mainwindow = MainWindow()
    Mainwindow.show()
    sys.exit(app.exec())
