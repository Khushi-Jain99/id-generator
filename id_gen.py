from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QFont, QPixmap, QImage
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QPushButton, QLabel, QSpacerItem, QSizePolicy,
    QMessageBox, QDialog, QFileDialog, QGraphicsDropShadowEffect,
    QGraphicsOpacityEffect,
)
from PIL import Image, ImageDraw, ImageFont
import random
import os
import datetime
import qrcode
import cv2
import sys

# ─── Card dimension constants (standard ID at 300 DPI) ────
CARD_W, CARD_H = 1012, 638
HEADER_H = 120
ACCENT_H = 4
FOOTER_H = 84
CORNER_R = 24
PHOTO_W, PHOTO_H = 200, 250
PHOTO_BORDER = 3

# ─── Colour palette ───────────────────────────────────────
C_PRIMARY = (13, 71, 161)
C_ACCENT = (255, 193, 7)
C_WHITE = (255, 255, 255)
C_DARK = (33, 33, 33)
C_GRAY = (117, 117, 117)
C_LIGHT_GRAY = (245, 245, 245)
C_RED = (183, 28, 28)
C_HEADER_SUB = (187, 222, 251)


# ─── Font helper with caching ─────────────────────────────
_font_cache = {}


def get_font(size, bold=False):
    key = (size, bold)
    if key in _font_cache:
        return _font_cache[key]
    candidates = []
    if bold:
        candidates += [
            "C:\\Windows\\Fonts\\arialbd.ttf",
            "C:\\Windows\\Fonts\\segoeuib.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        ]
    candidates += [
        "C:\\Windows\\Fonts\\arial.ttf",
        "C:\\Windows\\Fonts\\segoeui.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/System/Library/Fonts/Arial.ttf",
        "arial.ttf",
    ]
    for p in candidates:
        try:
            if os.path.exists(p):
                f = ImageFont.truetype(p, size=size)
                _font_cache[key] = f
                return f
        except Exception:
            continue
    f = ImageFont.load_default()
    _font_cache[key] = f
    return f


# ─── Helper: round corners on a PIL image ─────────────────
def round_corners(img, radius):
    img = img.convert("RGBA")
    mask = Image.new("L", img.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle(
        [(0, 0), (img.width - 1, img.height - 1)], radius, fill=255
    )
    img.putalpha(mask)
    return img


# ─── Helper: RGBA → RGB on white background ───────────────
def rgba_to_rgb(img):
    bg = Image.new("RGB", img.size, (255, 255, 255))
    if img.mode == "RGBA":
        bg.paste(img, mask=img.split()[3])
    else:
        bg.paste(img)
    return bg


# ─── Helper: monogram circle ──────────────────────────────
def monogram_circle(letter, diameter, bg_col, fg_col, font):
    img = Image.new("RGBA", (diameter, diameter), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse([(0, 0), (diameter - 1, diameter - 1)], fill=bg_col)
    bbox = d.textbbox((0, 0), letter, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    d.text(
        ((diameter - tw) / 2, (diameter - th) / 2 - 2),
        letter, fill=fg_col, font=font,
    )
    return img


# ═══════════════════════════════════════════════════════════
#  Preview Dialog
# ═══════════════════════════════════════════════════════════
class IDCardPreview(QDialog):
    """Shows the generated front & back cards with download buttons."""

    def __init__(self, front_pil, back_pil, default_name, parent=None):
        super().__init__(parent)
        self.front_pil = front_pil
        self.back_pil = back_pil
        self.default_name = default_name
        self.setWindowTitle("ID Card Preview")
        self.setMinimumSize(1100, 720)
        self._build_ui()

    # ── UI ──────────────────────────────────────────────────
    def _build_ui(self):
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                    stop:0 #e8eaf6, stop:1 #e3f2fd);
            }
            QLabel#cardLabel { background: transparent; border: none; }
            QPushButton#dlBtn {
                background-color: #0D47A1; color: white;
                border: none; border-radius: 8px;
                font-weight: bold; font-size: 13px;
                padding: 12px 28px;
            }
            QPushButton#dlBtn:hover { background-color: #1565C0; }
            QPushButton#closeBtn {
                background-color: #757575; color: white;
                border: none; border-radius: 8px;
                font-weight: bold; font-size: 13px;
                padding: 12px 28px;
            }
            QPushButton#closeBtn:hover { background-color: #616161; }
            QLabel#heading { color: #0D47A1; font-size: 22px; font-weight: bold; }
            QLabel#sideLabel { color: #424242; font-size: 14px; font-weight: bold; }
        """)

        root = QVBoxLayout(self)
        root.setContentsMargins(30, 20, 30, 20)
        root.setSpacing(16)

        heading = QLabel("Generated ID Card")
        heading.setObjectName("heading")
        heading.setAlignment(Qt.AlignCenter)
        root.addWidget(heading)

        # ── Cards side by side ──
        cards = QHBoxLayout()
        cards.setSpacing(40)
        cards.setAlignment(Qt.AlignCenter)

        for label_text, pil_img in [("Front", self.front_pil),
                                     ("Back", self.back_pil)]:
            col = QVBoxLayout()
            lbl = QLabel(label_text)
            lbl.setObjectName("sideLabel")
            lbl.setAlignment(Qt.AlignCenter)
            col.addWidget(lbl)

            card_lbl = QLabel()
            card_lbl.setObjectName("cardLabel")
            card_lbl.setAlignment(Qt.AlignCenter)
            pixmap = self._pil_to_pixmap(pil_img).scaled(
                480, 302, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            card_lbl.setPixmap(pixmap)

            shadow = QGraphicsDropShadowEffect()
            shadow.setBlurRadius(25)
            shadow.setOffset(0, 4)
            shadow.setColor(QtGui.QColor(0, 0, 0, 80))
            card_lbl.setGraphicsEffect(shadow)
            col.addWidget(card_lbl)
            cards.addLayout(col)

        root.addLayout(cards)
        root.addSpacing(10)

        # ── Buttons ──
        btn_row = QHBoxLayout()
        btn_row.setAlignment(Qt.AlignCenter)
        btn_row.setSpacing(16)

        for text, slot, obj_name in [
            ("Download as PNG", self._save_png, "dlBtn"),
            ("Download as PDF", self._save_pdf, "dlBtn"),
            ("Close", self.accept, "closeBtn"),
        ]:
            btn = QPushButton(text)
            btn.setObjectName(obj_name)
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(slot)
            btn_row.addWidget(btn)

        root.addLayout(btn_row)

        # ── Fade-in animation ──
        opacity = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(opacity)
        anim = QPropertyAnimation(opacity, b"opacity", self)
        anim.setDuration(400)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.setEasingCurve(QEasingCurve.OutCubic)
        anim.start()
        self._anim = anim  # prevent GC

    # ── Conversions ─────────────────────────────────────────
    @staticmethod
    def _pil_to_pixmap(pil_img):
        img = pil_img.convert("RGBA")
        data = img.tobytes("raw", "RGBA")
        qimg = QImage(data, img.width, img.height, QImage.Format_RGBA8888)
        return QPixmap.fromImage(qimg)

    def _combined_image(self):
        gap = 30
        w = max(self.front_pil.width, self.back_pil.width)
        h = self.front_pil.height + gap + self.back_pil.height
        combined = Image.new("RGBA", (w, h), (255, 255, 255, 255))
        combined.paste(self.front_pil, (0, 0), self.front_pil)
        combined.paste(self.back_pil, (0, self.front_pil.height + gap),
                       self.back_pil)
        return combined

    # ── Save handlers ───────────────────────────────────────
    def _save_png(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Save ID Card as PNG",
            os.path.join(os.path.expanduser("~"), "Desktop",
                         f"{self.default_name}_IDCard.png"),
            "PNG Image (*.png)",
        )
        if path:
            rgba_to_rgb(self._combined_image()).save(path, "PNG")
            QMessageBox.information(self, "Saved", f"ID card saved to:\n{path}")

    def _save_pdf(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Save ID Card as PDF",
            os.path.join(os.path.expanduser("~"), "Desktop",
                         f"{self.default_name}_IDCard.pdf"),
            "PDF File (*.pdf)",
        )
        if path:
            front_rgb = rgba_to_rgb(self.front_pil)
            back_rgb = rgba_to_rgb(self.back_pil)
            front_rgb.save(path, "PDF", save_all=True,
                           append_images=[back_rgb])
            QMessageBox.information(self, "Saved", f"ID card saved to:\n{path}")


# ═══════════════════════════════════════════════════════════
#  Main Window
# ═══════════════════════════════════════════════════════════
class IDCardGenerator(QMainWindow):
    """Professional ID Card Generator Application"""

    def __init__(self):
        super().__init__()
        self._build_ui()

    # ── Window setup ────────────────────────────────────────
    def _build_ui(self):
        self.setWindowTitle("Professional ID Card Generator")
        self.setGeometry(100, 100, 920, 760)
        self._center()
        self.setMinimumSize(920, 760)
        self.setStyleSheet(_MAIN_STYLE)

        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(0)

        # Title
        title = QLabel("ID Card Generator")
        title.setObjectName("appTitle")
        title.setAlignment(Qt.AlignCenter)
        root.addWidget(title)
        root.addSpacing(18)

        # Card container
        card = QWidget()
        card.setObjectName("cardContainer")
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setOffset(0, 4)
        shadow.setColor(QtGui.QColor(0, 0, 0, 45))
        card.setGraphicsEffect(shadow)

        card_lay = QVBoxLayout(card)
        card_lay.setContentsMargins(44, 36, 44, 36)
        card_lay.setSpacing(22)
        card_lay.addLayout(self._create_form())
        card_lay.addLayout(self._create_buttons())
        card_lay.addItem(
            QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding)
        )

        root.addWidget(card)

    # ── Form fields ─────────────────────────────────────────
    def _create_form(self):
        form = QFormLayout()
        form.setSpacing(16)
        form.setHorizontalSpacing(28)

        lbl_font = QFont("Segoe UI", 11)
        lbl_font.setBold(True)

        fields = [
            ("Company / College:", "lineEdit"),
            ("Full Name:", "lineEdit_2"),
            ("Department / Role:", "lineEdit_dept"),
            ("Gender:", "lineEdit_3"),
            ("Address:", "lineEdit_4"),
            ("Phone Number:", "lineEdit_5"),
        ]
        for text, attr in fields:
            lbl = QLabel(text)
            lbl.setFont(lbl_font)
            lbl.setStyleSheet("color: #202124;")
            inp = QLineEdit()
            inp.setMinimumHeight(42)
            inp.setFont(QFont("Segoe UI", 11))
            inp.setObjectName("inputField")
            setattr(self, attr, inp)
            form.addRow(lbl, inp)

        return form

    # ── Buttons ─────────────────────────────────────────────
    def _create_buttons(self):
        lay = QVBoxLayout()
        lay.setSpacing(12)

        self.pushButton = self._btn("Capture Image", self.capture)
        self.pushButton_2 = self._btn("Generate ID Card", self.generate_idcard)
        lay.addWidget(self.pushButton)
        lay.addWidget(self.pushButton_2)
        return lay

    @staticmethod
    def _btn(text, slot):
        btn = QPushButton(text)
        btn.setMinimumHeight(48)
        btn.setFont(QFont("Segoe UI", 11, QFont.Bold))
        btn.setObjectName("primaryButton")
        btn.setCursor(Qt.PointingHandCursor)
        btn.clicked.connect(slot)
        return btn

    # ── Centre on screen ────────────────────────────────────
    def _center(self):
        scr = QtWidgets.QApplication.primaryScreen()
        if scr:
            sg = scr.geometry()
            wg = self.geometry()
            self.move((sg.width() - wg.width()) // 2,
                      (sg.height() - wg.height()) // 2)

    # ── Camera capture ──────────────────────────────────────
    def capture(self):
        cam = cv2.VideoCapture(0)
        cam.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

        if not cam.isOpened():
            QMessageBox.warning(self, "Camera Error",
                                "Unable to open camera. Check your connection.")
            return

        while True:
            ret, frame = cam.read()
            if not ret:
                break
            frame = cv2.flip(frame, 1)

            h, w = frame.shape[:2]
            r1, c1 = int(h * 0.15), int(w * 0.30)
            r2, c2 = int(h * 0.90), int(w * 0.70)
            cv2.rectangle(frame, (c1, r1), (c2, r2), (0, 255, 0), 2)
            cv2.putText(frame, "Press C to Capture | Q to Quit",
                        (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.9,
                        (0, 255, 0), 2)
            cv2.putText(frame, "Position face within the rectangle",
                        (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                        (0, 255, 0), 2)
            cv2.imshow("ID Card Camera", frame)

            key = cv2.waitKey(1) & 0xFF
            if key in (ord("c"), ord("C")):
                cv2.imwrite("person.jpg", frame[r1:r2, c1:c2])
                QMessageBox.information(self, "Done",
                                        "Image captured successfully!")
                break
            if key in (ord("q"), ord("Q")):
                break

        cam.release()
        cv2.destroyAllWindows()

    # ── Generate ID Card ────────────────────────────────────
    def generate_idcard(self):
        name = self.lineEdit_2.text().strip()
        if not name:
            QMessageBox.warning(self, "Missing Field",
                                "Please enter Full Name.")
            return
        if not os.path.exists("person.jpg"):
            QMessageBox.warning(self, "Missing Image",
                                "Please capture an image first.")
            return

        company = self.lineEdit.text().strip() or "Organization"
        department = self.lineEdit_dept.text().strip() or "General"
        gender = self.lineEdit_3.text().strip() or "N/A"
        address = self.lineEdit_4.text().strip() or "N/A"
        phone = self.lineEdit_5.text().strip() or "N/A"
        id_no = str(random.randint(1_000_000, 9_999_999))

        now = datetime.datetime.now()
        issue_date = now.strftime("%d %b %Y")
        valid_date = (now + datetime.timedelta(days=365)).strftime("%d %b %Y")

        photo = Image.open("person.jpg")

        front = self._render_front(
            company, name, id_no, department, gender, phone,
            photo, issue_date, valid_date,
        )
        back = self._render_back(
            company, name, id_no, department, address, phone,
            issue_date, valid_date,
        )

        try:
            os.remove("person.jpg")
        except OSError:
            pass

        dlg = IDCardPreview(front, back, name, parent=self)
        dlg.exec_()

    # ═══════════════════════════════════════════════════════
    #  FRONT CARD
    # ═══════════════════════════════════════════════════════
    def _render_front(self, company, name, id_no, dept, gender,
                      phone, photo, issue_date, valid_date):
        card = Image.new("RGB", (CARD_W, CARD_H), C_WHITE)
        d = ImageDraw.Draw(card)

        # ── Header bar ──
        d.rectangle([(0, 0), (CARD_W, HEADER_H)], fill=C_PRIMARY)
        d.rectangle([(0, HEADER_H), (CARD_W, HEADER_H + ACCENT_H)],
                    fill=C_ACCENT)

        # Monogram logo
        mono = monogram_circle(
            company[0].upper(), 70, C_WHITE, C_PRIMARY,
            get_font(36, bold=True),
        )
        card.paste(mono, (40, 25), mono)

        # Company name + subtitle
        d.text((125, 30), company,
               fill=C_WHITE, font=get_font(32, bold=True))
        d.text((125, 72), "IDENTITY CARD",
               fill=C_HEADER_SUB, font=get_font(16))

        # ── Photo with border ──
        body_top = HEADER_H + ACCENT_H
        px, py = 55, body_top + 25
        inner_w = PHOTO_W - 2 * PHOTO_BORDER
        inner_h = PHOTO_H - 2 * PHOTO_BORDER
        ph = photo.resize((inner_w, inner_h), Image.LANCZOS)

        d.rectangle(
            [(px - PHOTO_BORDER, py - PHOTO_BORDER),
             (px + inner_w + PHOTO_BORDER, py + inner_h + PHOTO_BORDER)],
            fill=C_PRIMARY,
        )
        card.paste(ph, (px, py))

        # ── Vertical accent divider ──
        divider_x = 275
        d.line([(divider_x, body_top + 25),
                (divider_x, CARD_H - FOOTER_H - 10)],
               fill=C_ACCENT, width=2)

        # ── Info fields ──
        ix = 300
        iy = body_top + 30
        label_font = get_font(15)
        value_font = get_font(22, bold=True)
        name_font = get_font(28, bold=True)
        gap = 58

        # Name
        d.text((ix, iy), "NAME", fill=C_GRAY, font=label_font)
        d.text((ix, iy + 20), name, fill=C_DARK, font=name_font)
        iy += gap + 14

        # ID number (red accent)
        d.text((ix, iy), "ID NUMBER", fill=C_GRAY, font=label_font)
        d.text((ix, iy + 20), id_no, fill=C_RED, font=value_font)
        iy += gap

        # Department
        d.text((ix, iy), "DEPARTMENT", fill=C_GRAY, font=label_font)
        d.text((ix, iy + 20), dept, fill=C_DARK, font=value_font)
        iy += gap

        # Gender
        d.text((ix, iy), "GENDER", fill=C_GRAY, font=label_font)
        d.text((ix, iy + 20), gender, fill=C_DARK, font=value_font)
        iy += gap

        # Phone
        d.text((ix, iy), "PHONE", fill=C_GRAY, font=label_font)
        d.text((ix, iy + 20), phone, fill=C_DARK, font=value_font)

        # ── Footer ──
        fy = CARD_H - FOOTER_H
        d.rectangle([(0, fy), (CARD_W, CARD_H)], fill=C_LIGHT_GRAY)
        d.line([(0, fy), (CARD_W, fy)], fill=(224, 224, 224), width=1)

        foot = get_font(16)
        foot_b = get_font(16, bold=True)
        d.text((55, fy + 18), "Issue Date:", fill=C_GRAY, font=foot)
        d.text((170, fy + 18), issue_date, fill=C_DARK, font=foot_b)
        d.text((55, fy + 46), "Valid Until:", fill=C_GRAY, font=foot)
        d.text((170, fy + 46), valid_date, fill=C_DARK, font=foot_b)

        # Bottom accent bar
        d.rectangle([(0, CARD_H - 6), (CARD_W, CARD_H)], fill=C_PRIMARY)

        return round_corners(card, CORNER_R)

    # ═══════════════════════════════════════════════════════
    #  BACK CARD
    # ═══════════════════════════════════════════════════════
    def _render_back(self, company, name, id_no, dept, address,
                     phone, issue_date, valid_date):
        card = Image.new("RGB", (CARD_W, CARD_H), C_WHITE)
        d = ImageDraw.Draw(card)

        # ── Header ──
        d.rectangle([(0, 0), (CARD_W, 80)], fill=C_PRIMARY)
        d.rectangle([(0, 80), (CARD_W, 84)], fill=C_ACCENT)

        comp_font = get_font(28, bold=True)
        tw = d.textlength(company, font=comp_font)
        d.text(((CARD_W - tw) / 2, 24), company,
               fill=C_WHITE, font=comp_font)

        # ── Info section ──
        y = 110
        lf = get_font(15)
        vf = get_font(20)

        d.text((55, y), "ADDRESS", fill=C_GRAY, font=lf)
        d.text((55, y + 24), address, fill=C_DARK, font=vf)
        y += 75

        d.text((55, y), "PHONE", fill=C_GRAY, font=lf)
        d.text((55, y + 24), phone, fill=C_DARK, font=vf)
        y += 75

        d.text((55, y), "DEPARTMENT", fill=C_GRAY, font=lf)
        d.text((55, y + 24), dept, fill=C_DARK, font=vf)

        # ── QR code ──
        qr_data = f"Name: {name}\nID: {id_no}\nDept: {dept}\nPhone: {phone}"
        qr_img = qrcode.make(
            qr_data, box_size=5, border=2
        ).resize((180, 180)).convert("RGB")
        card.paste(qr_img, (CARD_W - 235, 110))

        # ── Divider ──
        y = 380
        d.line([(55, y), (CARD_W - 55, y)], fill=(224, 224, 224), width=1)

        # ── Terms ──
        y += 15
        tf = get_font(13)
        d.text((55, y),
               "This card is the property of the issuing organization.",
               fill=C_GRAY, font=tf)
        d.text((55, y + 22),
               "If found, please return to the address above.",
               fill=C_GRAY, font=tf)

        # ── Signature line ──
        y += 65
        d.text((55, y), "Authorized Signature", fill=C_GRAY,
               font=get_font(14))
        d.line([(55, y + 24), (300, y + 24)], fill=C_DARK, width=1)

        # ── Footer ──
        fy = CARD_H - FOOTER_H
        d.rectangle([(0, fy), (CARD_W, CARD_H)], fill=C_LIGHT_GRAY)
        d.line([(0, fy), (CARD_W, fy)], fill=(224, 224, 224))

        note = ("This card is non-transferable and must be "
                "returned upon request.")
        nw = d.textlength(note, font=get_font(13))
        d.text(((CARD_W - nw) / 2, fy + 20), note,
               fill=C_GRAY, font=get_font(13))

        validity = f"Valid: {issue_date}  \u2014  {valid_date}"
        vw = d.textlength(validity, font=get_font(14, bold=True))
        d.text(((CARD_W - vw) / 2, fy + 48), validity,
               fill=C_DARK, font=get_font(14, bold=True))

        # Bottom accent bar
        d.rectangle([(0, CARD_H - 6), (CARD_W, CARD_H)], fill=C_PRIMARY)

        return round_corners(card, CORNER_R)


# ─── Global stylesheet ────────────────────────────────────
_MAIN_STYLE = """
QMainWindow {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #f0f4ff, stop:1 #e8f0fe);
}
#appTitle {
    color: #0D47A1;
    font-size: 28px;
    font-weight: bold;
    font-family: 'Segoe UI';
}
#cardContainer {
    background: #ffffff;
    border-radius: 14px;
}
#inputField {
    background: #f8f9fa;
    border: 2px solid #e0e0e0;
    border-radius: 8px;
    padding: 8px 14px;
    color: #202124;
    selection-background-color: #1a73e8;
}
#inputField:focus {
    border: 2px solid #1a73e8;
    background: #ffffff;
}
#primaryButton {
    background-color: #0D47A1;
    color: #ffffff;
    border: none;
    border-radius: 8px;
    padding: 10px 20px;
}
#primaryButton:hover {
    background-color: #1565C0;
}
#primaryButton:pressed {
    background-color: #0D47A1;
}
QLabel {
    color: #202124;
}
"""


# ─── Entry Point ──────────────────────────────────────────
def main():
    app = QtWidgets.QApplication(sys.argv)
    window = IDCardGenerator()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
