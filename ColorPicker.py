from PyQt5.QtWidgets import QApplication, QMainWindow, QLineEdit, QScrollArea, QPushButton, QFileDialog
from PyQt5.QtGui import  QImage, QKeyEvent
from PyQt5.QtCore import QThread, pyqtSignal, Qt, QSettings
from PyQt5 import uic
import os, sys

from Imageview import ImageView


from requests import get as request_get

class ScreenShotThread(QThread):
    screenshot_complete = pyqtSignal(QImage)
    def __init__(self,orient,url):
        super().__init__()
        self.orient = str(orient)
        self.url = url

    def run(self) -> None:
        try:
            data = request_get(self.url + "/snapshot?ext=png&compress=1&orient=" + self.orient)
        except Exception:
            # self.screenshot_complete.emit(None)
            print("错误")
            return

        qimg = QImage.fromData(data.content)
        self.screenshot_complete.emit(qimg)


class MainWindow(QMainWindow):
    imageview: ImageView
    text1: QPushButton
    text2: QPushButton
    text3: QPushButton
    text4: QPushButton
    pathEdit: QLineEdit
    scrollArea: QScrollArea
    pathButton: QPushButton
    setting = QSettings("com.ayogg","colorpicker")
    path: str = None

    def __init__(self, *args, **kwargs):
        super().__init__( *args, **kwargs)
        if getattr(sys, 'frozen', False):
            basedir = sys._MEIPASS
            uic.loadUi(os.path.join(basedir,"resource/ui_color_picker.ui"), self)
        else:
            basedir = "/Users/ayogg/Code/autotouch_colorpicker"
            uic.loadUi(os.path.join(basedir,"resource/ui_color_picker.ui"), self)


        self.imageview = ImageView()
        self.scrollArea.setWidget(self.imageview)
        self.scrollArea.setWidgetResizable(True)
        self.setAcceptDrops(True)

        self.path = self.setting.value("path", "", type=str)
        self.pathButton.setText("保存路径" + self.path)

    def screenshot(self):
        self.clear_all()
        url = self.ip_edit.text()
        orient = self.orient_edit.text()
        self.thread = ScreenShotThread(orient, "http://" + url)
        self.thread.screenshot_complete.connect(self.imageview.set_img)
        self.thread.start()
        self.statusBar().showMessage("截图")

    def generate(self):
        self.statusBar().showMessage("生成")
        color_text = ""
        region_text = ""

        region = self.imageview.get_region()
        x1, y1, x2, y2 = 0,0,0,0
        if region is not None:
            x1, y1, x2, y2 = region
            region_text = "{%d, %d, %d, %d}"%(x1,y1,x2,y2)
        else:
            region_text = None

        if len(self.imageview.point_list) > 0:
            color_text = "{"
            #{color={{139,50,0xf5e6a7},{1561,120,0x32211c},{1211,718,0xd1c1b1},{1393,725,0xf3b25e}}, region={37,150,1469,717}}
            for p in self.imageview.point_list:
                x, y, c = p[0],p[1],p[2]
                color_text = color_text + "{%d, %d, %s}, "%(x,y,c)
            color_text = color_text[:-2] + "}"

        color_compare = "if multiColor(%s, 95) then"%(color_text)
        fuzzy_find = ""
        mask = ""

        if region:
            mask = "{color=%s, region=%s}"%(color_text,region_text)
            fuzzy_find = "local x,y=findMultiColorInRegionFuzzyByTable(%s,95,%d,%d,%d,%d)" % (color_text,x1,y1,x2,y2)
        else:
            mask = "{color=%s}"%(color_text)
            fuzzy_find = "local x,y=findMultiColorInRegionFuzzyByTable(%s,95,0,0,9999,9999)" % color_text

        self.text1.setText(mask)
        self.text2.setText(color_compare)
        self.text3.setText(fuzzy_find)

        if region:
            self.text4.setText("%d, %d, %d, %d"%(x1,y1,x2,y2))

    def get_save_path(self):
        self.path = QFileDialog.getExistingDirectory(self,"选择截图保存路径")
        self.setting.setValue("path", self.path)
        self.pathButton.setText("保存路径" + self.path)

    def save_img(self):
        if (not os.path.exists(self.path)) or self.path is None:
            self.get_save_path()

        if self.imageview.save_img(self.path):
            self.statusBar().showMessage("保存成功")
        else:
            self.statusBar().showMessage("保存失败")


    def clear_all(self):
        self.imageview.clear_point()
        self.text1.setText("")
        self.text2.setText("")
        self.text3.setText("")
        self.text4.setText("")

    def copy_text(self):
        w: QPushButton = self.sender()
        clipboard = QApplication.clipboard()
        clipboard.setText(w.text())
        

    def keyReleaseEvent(self, e: QKeyEvent) -> None:
        if e.key() == Qt.Key_Q:
            self.screenshot()
        elif e.key() == Qt.Key_E:
            self.generate()
        elif e.key() == Qt.Key_W:
            self.clear_all()
        elif e.key() == Qt.Key_S:
            self.save_img()
        elif e.key() == Qt.Key_1:
            self.imageview.scale_down()
        elif e.key() == Qt.Key_2:
            self.imageview.scale_up()

    def dragEnterEvent(self, event):
        event.accept()

    def dropEvent(self, event):
        path: str = event.mimeData().urls()[0].toLocalFile().lower()
        if path.endswith(".png") or path.endswith(".jpg"):
            self.clear_all()
            self.imageview.set_img(QImage(path))



if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = MainWindow()

    mainWindow.show()


    sys.exit(app.exec_())


