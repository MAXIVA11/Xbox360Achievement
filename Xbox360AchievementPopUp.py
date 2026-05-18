import sys
import os
import argparse

from PyQt5.QtCore import (
    Qt,
    QPropertyAnimation,
    QEasingCurve,
    QTimer,
    QUrl,
    QPoint,
    pyqtSignal,
    QRectF,
)

from PyQt5.QtGui import (
    QPixmap,
    QPainter,
    QColor,
    QPen,
    QFont,
    QFontMetrics,
    QPainterPath,
)

from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
)

from PyQt5.QtMultimedia import QSoundEffect


FONT_FAMILY = "Convection Regular"


class AchievementPopup(QWidget):
    closed = pyqtSignal()

    POPUP_WIDTH = 410
    POPUP_HEIGHT = 66

    def __init__(
        self, title, gamerscore, icon_path=None, sound_path=None, side="bottom-right"
    ):
        super().__init__()

        self.title = title
        self.gamerscore = gamerscore
        self.side = side

        if not icon_path:
            icon_path = "Icon/XboxIcon.png"

        self.setWindowFlags(
            Qt.FramelessWindowHint
            | Qt.WindowStaysOnTopHint
            | Qt.Tool
            | Qt.NoDropShadowWindowHint
        )

        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)

        self.setFixedSize(self.POPUP_WIDTH, self.POPUP_HEIGHT)

        # ================= SOUND =================
        self.sound = None

        if sound_path and os.path.exists(sound_path):
            self.sound = QSoundEffect()
            self.sound.setSource(QUrl.fromLocalFile(sound_path))
            self.sound.setVolume(1.0)

        self._build_ui(icon_path)

    # ================= UI =================
    def _build_ui(self, icon_path):

        # ================= ICON =================
        self.icon_label = QLabel(self)
        self.icon_label.setGeometry(6, 6, 54, 54)
        self.icon_label.setStyleSheet("background: transparent;")

        icon_pm = self._load_icon_pixmap(icon_path, 50)

        self.icon_label.setPixmap(icon_pm)
        self.icon_label.setAlignment(Qt.AlignCenter)

        # ================= TITLE =================
        self.label_title = QLabel("Achievement unlocked", self)

        self.label_title.setGeometry(70, 9, self.POPUP_WIDTH - 80, 22)

        self.label_title.setStyleSheet(
            """
            color: #E7E7E7;
            background: transparent;
        """
        )

        title_font = QFont(FONT_FAMILY)
        title_font.setPixelSize(15)
        title_font.setWeight(QFont.DemiBold)

        self.label_title.setFont(title_font)

        # ================= BODY =================
        self.label_name = QLabel(self)

        self.label_name.setGeometry(70, 29, self.POPUP_WIDTH - 78, 26)

        self.label_name.setStyleSheet(
            """
            color: #F0F0F0;
            background: transparent;
        """
        )

        body_font = QFont(FONT_FAMILY)
        body_font.setPixelSize(14)
        body_font.setWeight(QFont.Medium)
        body_font.setLetterSpacing(QFont.AbsoluteSpacing, 0.2)

        self.label_name.setFont(body_font)

        self._update_elided_name()

    # ================= BACKGROUND =================
    def paintEvent(self, event):
        p = QPainter(self)

        p.setRenderHint(QPainter.Antialiasing, True)

        rect = QRectF(self.rect().adjusted(1, 1, -1, -1))

        pill = QPainterPath()
        pill.addRoundedRect(rect, 32, 32)

        p.setPen(Qt.NoPen)
        p.setBrush(QColor("#2C2C2C"))

        p.drawPath(pill)

        p.end()

    # ================= TEXT =================
    def _update_elided_name(self):
        text = f"{self.gamerscore}G - {self.title}"

        metrics = QFontMetrics(self.label_name.font())

        elided = metrics.elidedText(text, Qt.ElideRight, self.label_name.width())

        self.label_name.setText(elided)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_elided_name()

    # ================= ICON =================
    def _load_icon_pixmap(self, icon_path, size):

        if os.path.exists(icon_path):
            pm = QPixmap(icon_path)

            if not pm.isNull():
                return self._make_round_pixmap(pm, size)

        return self._build_xbox_icon(size)

    def _make_round_pixmap(self, pixmap, size):

        canvas = QPixmap(size, size)
        canvas.fill(Qt.transparent)

        p = QPainter(canvas)

        p.setRenderHint(QPainter.Antialiasing)
        p.setRenderHint(QPainter.SmoothPixmapTransform)

        # outer circle
        p.setPen(QPen(QColor(0, 0, 0, 120), 2))
        p.setBrush(QColor("#2B2B2B"))

        p.drawEllipse(0, 0, size, size)

        # clip
        clip = QPainterPath()
        clip.addEllipse(2, 2, size - 4, size - 4)

        p.setClipPath(clip)

        scaled = pixmap.scaled(
            size, size, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation
        )

        x = (scaled.width() - size) // 2
        y = (scaled.height() - size) // 2

        cropped = scaled.copy(x, y, size, size)

        p.drawPixmap(0, 0, cropped)

        p.end()

        return canvas

    def _build_xbox_icon(self, size):

        pm = QPixmap(size, size)
        pm.fill(Qt.transparent)

        p = QPainter(pm)

        p.setRenderHint(QPainter.Antialiasing)

        p.setPen(QPen(QColor("#0F0F0F"), 2))
        p.setBrush(QColor("#1E1E1E"))

        p.drawEllipse(0, 0, size, size)

        font = QFont(FONT_FAMILY, int(size * 0.45), QFont.Bold)

        p.setFont(font)
        p.setPen(QColor("#7CFF36"))

        p.drawText(pm.rect(), Qt.AlignCenter, "X")

        p.end()

        return pm

    # ================= SHOW =================
    def show_popup(self):

        screen = QApplication.primaryScreen().availableGeometry()

        margin = 20

        # ================= POSITION =================
        if self.side == "bottom-right":

            target_x = screen.right() - self.width() - margin
            target_y = screen.bottom() - self.height() - margin

            start_x = screen.right() + self.width()
            start_y = target_y

        elif self.side == "bottom-left":

            target_x = screen.left() + margin
            target_y = screen.bottom() - self.height() - margin

            start_x = -self.width()
            start_y = target_y

        elif self.side == "top-right":

            target_x = screen.right() - self.width() - margin
            target_y = screen.top() + margin

            start_x = screen.right() + self.width()
            start_y = target_y

        elif self.side == "top-left":

            target_x = screen.left() + margin
            target_y = screen.top() + margin

            start_x = -self.width()
            start_y = target_y

        else:
            # fallback
            target_x = screen.right() - self.width() - margin
            target_y = screen.bottom() - self.height() - margin

            start_x = screen.right() + self.width()
            start_y = target_y

        self.move(start_x, start_y)

        self.show()

        if self.sound:
            self.sound.play()

        # ================= SLIDE IN =================
        self.slide_anim = QPropertyAnimation(self, b"pos")

        self.slide_anim.setDuration(170)

        self.slide_anim.setStartValue(QPoint(start_x, start_y))

        self.slide_anim.setEndValue(QPoint(target_x, target_y))

        self.slide_anim.setEasingCurve(QEasingCurve.OutCubic)

        self.slide_anim.finished.connect(lambda: QTimer.singleShot(4000, self.dismiss))

        self.slide_anim.start()

    # ================= DISMISS =================
    def dismiss(self):

        screen = QApplication.primaryScreen().availableGeometry()

        if "right" in self.side:
            end_x = screen.right() + self.width() + 30
        else:
            end_x = -self.width() - 30

        self.anim = QPropertyAnimation(self, b"pos")

        self.anim.setDuration(150)

        self.anim.setStartValue(self.pos())

        self.anim.setEndValue(QPoint(end_x, self.y()))

        self.anim.setEasingCurve(QEasingCurve.InCubic)

        self.anim.finished.connect(self.close)
        self.anim.finished.connect(self.closed.emit)

        self.anim.start()


# ================= CLI =================
def parse_args():

    parser = argparse.ArgumentParser(description="Xbox 360 Achievement Popup")

    parser.add_argument("--title", default="All Achievements Unlocked")

    parser.add_argument("--gamerscore", type=int, default=100)

    parser.add_argument("--icon", default="Icon/XboxIcon.png")

    parser.add_argument("--sound", default="Sound/achievement.wav")

    parser.add_argument(
        "--side",
        choices=["bottom-right", "bottom-left", "top-right", "top-left"],
        default="bottom-right",
        help="Popup screen position",
    )

    return parser.parse_args()


# ================= MAIN =================
if __name__ == "__main__":

    args = parse_args()

    app = QApplication(sys.argv)

    popup = AchievementPopup(
        title=args.title,
        gamerscore=args.gamerscore,
        icon_path=args.icon,
        sound_path=args.sound,
        side=args.side,
    )

    popup.closed.connect(app.quit)

    popup.show_popup()

    sys.exit(app.exec_())
