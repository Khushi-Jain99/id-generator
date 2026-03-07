from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QFormLayout,
                             QLineEdit, QPushButton, QLabel, QSpacerItem,
                             QSizePolicy, QMessageBox)
from PIL import Image, ImageDraw, ImageFont
import random
import os
import datetime
import qrcode
import cv2
import sys
import numpy as np


class IDCardGenerator(QMainWindow):
    """Modern Professional ID Card Generator Application"""

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        """Initialize and setup the user interface with modern design"""
        # Main window properties
        self.setWindowTitle("Professional ID Card Generator")
        self.setGeometry(100, 100, 900, 650)
        self.center_window()
        self.setMinimumSize(900, 650)

        # Apply global stylesheet
        self.setStyleSheet(self.get_global_stylesheet())

        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(0)

        # Create title
        title = self.create_title()
        main_layout.addWidget(title)
        main_layout.addSpacing(15)

        # Create card container with modern styling
        card_widget = QWidget()
        card_widget.setObjectName("cardContainer")
        card_layout = QVBoxLayout(card_widget)
        card_layout.setContentsMargins(40, 40, 40, 40)
        card_layout.setSpacing(20)

        # Add form layout
        form_layout = self.create_form_layout()
        card_layout.addLayout(form_layout)

        # Add button layout
        button_layout = self.create_button_layout()
        card_layout.addLayout(button_layout)

        # Add spacer
        spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        card_layout.addItem(spacer)

        main_layout.addWidget(card_widget)

    def create_title(self):
        """Create title label"""
        title = QLabel("ID Card Generator")
        title_font = QFont("Segoe UI", 28)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #1a73e8; font-weight: bold;")
        return title

    def create_form_layout(self):
        """Create form layout for input fields"""
        form_layout = QFormLayout()
        form_layout.setSpacing(18)
        form_layout.setHorizontalSpacing(30)

        # Set label properties
        label_font = QFont("Segoe UI", 11)
        label_font.setBold(True)

        # Company Name
        company_label = QLabel("Company Name:")
        company_label.setFont(label_font)
        company_label.setStyleSheet("color: #202124; padding-right: 10px;")
        self.lineEdit = self.create_input_field()
        form_layout.addRow(company_label, self.lineEdit)

        # Full Name
        fullname_label = QLabel("Full Name:")
        fullname_label.setFont(label_font)
        fullname_label.setStyleSheet("color: #202124; padding-right: 10px;")
        self.lineEdit_2 = self.create_input_field()
        form_layout.addRow(fullname_label, self.lineEdit_2)

        # Gender
        gender_label = QLabel("Gender:")
        gender_label.setFont(label_font)
        gender_label.setStyleSheet("color: #202124; padding-right: 10px;")
        self.lineEdit_3 = self.create_input_field()
        form_layout.addRow(gender_label, self.lineEdit_3)

        # Address
        address_label = QLabel("Address:")
        address_label.setFont(label_font)
        address_label.setStyleSheet("color: #202124; padding-right: 10px;")
        self.lineEdit_4 = self.create_input_field()
        form_layout.addRow(address_label, self.lineEdit_4)

        # Phone Number
        phone_label = QLabel("Phone Number:")
        phone_label.setFont(label_font)
        phone_label.setStyleSheet("color: #202124; padding-right: 10px;")
        self.lineEdit_5 = self.create_input_field()
        form_layout.addRow(phone_label, self.lineEdit_5)

        return form_layout

    def create_input_field(self):
        """Create a styled input field"""
        input_field = QLineEdit()
        input_field.setMinimumHeight(40)
        input_field.setFont(QFont("Segoe UI", 11))
        input_field.setObjectName("inputField")
        return input_field

    def create_button_layout(self):
        """Create button layout"""
        button_layout = QVBoxLayout()
        button_layout.setSpacing(12)

        # Capture Image button
        self.pushButton = QPushButton("Capture Image")
        self.pushButton.setMinimumHeight(45)
        self.pushButton.setFont(QFont("Segoe UI", 11, QFont.Bold))
        self.pushButton.setObjectName("primaryButton")
        self.pushButton.clicked.connect(self.capture)
        button_layout.addWidget(self.pushButton)

        # Generate ID Card button
        self.pushButton_2 = QPushButton("Generate ID Card")
        self.pushButton_2.setMinimumHeight(45)
        self.pushButton_2.setFont(QFont("Segoe UI", 11, QFont.Bold))
        self.pushButton_2.setObjectName("primaryButton")
        self.pushButton_2.clicked.connect(self.generate_idcard)
        button_layout.addWidget(self.pushButton_2)

        return button_layout

    @staticmethod
    def get_global_stylesheet():
        """Return global stylesheet for modern SaaS design"""
        return """
        QMainWindow {
            background: qlineargradient(
                x1: 0, y1: 0, x2: 1, y2: 1,
                stop: 0 #f0f4ff,
                stop: 1 #e8f0fe
            );
        }

        #cardContainer {
            background-color: #ffffff;
            border-radius: 12px;
            border: none;
        }

        #inputField {
            background-color: #f8f9fa;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            padding: 8px 12px;
            color: #202124;
            selection-background-color: #1a73e8;
        }

        #inputField:focus {
            border: 2px solid #1a73e8;
            background-color: #ffffff;
        }

        #inputField::placeholder {
            color: #9aa0a6;
        }

        #primaryButton {
            background-color: #1a73e8;
            color: #ffffff;
            border: none;
            border-radius: 8px;
            font-weight: bold;
            padding: 10px 20px;
        }

        #primaryButton:hover {
            background-color: #1765cc;
        }

        #primaryButton:pressed {
            background-color: #1557b0;
        }

        QLabel {
            color: #202124;
        }
        """

    def center_window(self):
        """Center the window on screen"""
        screen = QtWidgets.QApplication.primaryScreen()
        if screen:
            screen_geometry = screen.geometry()
            window_geometry = self.geometry()
            x = (screen_geometry.width() - window_geometry.width()) // 2
            y = (screen_geometry.height() - window_geometry.height()) // 2
            self.move(x, y)

    def capture(self):
        """Capture image from camera with improved UI and instructions"""
        camera = cv2.VideoCapture(0)
        camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        
        if not camera.isOpened():
            QMessageBox.warning(self, "Camera Error", "Unable to open camera. Please check your camera connection.")
            return
        
        captured = False
        
        while True:
            ret, frame = camera.read()
            if not ret:
                break
            
            # Flip frame for mirror effect
            frame = cv2.flip(frame, 1)
            
            # Add instruction text
            cv2.putText(frame, "Press C to Capture | Press Q to Quit", (20, 40),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            # Draw capture area rectangle
            height, width = frame.shape[:2]
            start_row, start_col = int(height * 0.25), int(width * 0.25)
            end_row, end_col = int(height * 0.80), int(width * 0.80)
            cv2.rectangle(frame, (start_col, start_row), (end_col, end_row), (0, 255, 0), 2)
            cv2.putText(frame, "Position face within the rectangle", (20, 80),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            
            # Display frame
            cv2.imshow('ID Card Camera - Capture Image', frame)
            
            # Capture on 'C' key, Quit on 'Q' key
            key = cv2.waitKey(1) & 0xFF
            if key == ord('c') or key == ord('C'):
                try:
                    cropped_img = frame[start_row:end_row, start_col:end_col]
                    cv2.imwrite('person.jpg', cropped_img)
                    captured = True
                    QMessageBox.information(self, "Success", "Image captured successfully!")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to save image: {str(e)}")
                break
            elif key == ord('q') or key == ord('Q'):
                break
        
        camera.release()
        cv2.destroyAllWindows()

    def get_font(self, size):
        """Get font with fallback support"""
        font_paths = [
            'arial.ttf',
            'C:\\Windows\\Fonts\\arial.ttf',
            '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
            '/System/Library/Fonts/Arial.ttf'
        ]
        
        for font_path in font_paths:
            try:
                if os.path.exists(font_path):
                    return ImageFont.truetype(font_path, size=size)
            except Exception:
                continue
        
        # Fallback to default font
        return ImageFont.load_default()

    def generate_idcard(self):
        """Generate ID card with captured image and error handling"""
        try:
            # Check if required fields are filled
            if not self.lineEdit_2.text().strip():
                QMessageBox.warning(self, "Missing Field", "Please enter Full Name.")
                return
            
            # Check if person.jpg exists
            if not os.path.exists('person.jpg'):
                QMessageBox.warning(self, "Missing Image", "Please capture an image first using 'Capture Image' button.")
                return
            
            # Load captured person image
            person_image = Image.open('person.jpg')
            
            # Generating Blank White Image
            image = Image.new('RGB', (1000, 900), (255, 255, 255))
            draw = ImageDraw.Draw(image)
            
            # Get fonts with fallback
            font_80 = self.get_font(80)
            font_60 = self.get_font(60)
            font_45 = self.get_font(45)
            
            date = datetime.datetime.now()
            
            # Company Name
            (x, y) = (50, 50)
            message = self.lineEdit.text() or "Company"
            company = message
            color = 'rgb(0, 0, 0)'
            draw.text((x, y), message, fill=color, font=font_80)
            
            # ID Number
            (x, y) = (50, 350)
            id_no = random.randint(1000000, 9000000)
            message = f'ID {id_no}'
            color = 'rgb(255, 0, 0)'
            draw.text((x, y), message, fill=color, font=font_60)
            
            # Full Name
            (x, y) = (50, 250)
            message = self.lineEdit_2.text()
            name = message
            color = 'rgb(0, 0, 0)'
            draw.text((x, y), message, fill=color, font=font_45)
            
            # Gender
            (x, y) = (50, 550)
            message = self.lineEdit_3.text() or "N/A"
            color = 'rgb(0, 0, 0)'
            draw.text((x, y), message, fill=color, font=font_45)
            
            # Phone Number
            (x, y) = (50, 650)
            message = self.lineEdit_5.text() or "N/A"
            color = 'rgb(0, 0, 0)'
            draw.text((x, y), message, fill=color, font=font_45)
            
            # Address
            (x, y) = (50, 750)
            message = self.lineEdit_4.text() or "N/A"
            color = 'rgb(0, 0, 0)'
            draw.text((x, y), message, fill=color, font=font_45)
            
            # Paste person image directly onto the card
            image.paste(person_image, (600, 75))
            
            # Save final ID card with clean filename
            output_filename = f"{name}_IDCard.png"
            image.save(output_filename)
            
            # Delete temporary person.jpg file
            if os.path.exists('person.jpg'):
                os.remove('person.jpg')
            
            # Show success message
            QMessageBox.information(self, "Success", f"ID Card generated successfully!\n\nSaved as: {output_filename}")
            
        except FileNotFoundError as e:
            QMessageBox.critical(self, "File Error", f"File not found: {str(e)}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate ID card: {str(e)}")


def main():
    """Main entry point for the application"""
    app = QtWidgets.QApplication(sys.argv)
    window = IDCardGenerator()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()