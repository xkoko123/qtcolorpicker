from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QPen, QColor, QPixmap, QImage
import time, os

class ImageView(QLabel):
    press_x = -1
    press_y = -1
    point_list = []
    img:QImage= None
    scale = 1.8

    region_x1, region_y1, region_x2, region_y2 = -1, -1, -1, -1
    x = -1
    y = -1

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setMouseTracking(True)

    def paintEvent(self, e):
        super().paintEvent(e)
        qp = QPainter()
        pen = QPen(QColor(255, 0, 0))
        pen.setWidth(2)

        qp.begin(self)
        qp.setPen(pen)
        for point in self.point_list:
            x,y,c = point
            qp.drawPoint(x/self.scale, y/self.scale)
        qp.drawText(self.x+10,self.y+10,"%d,%d"%(self.x * self.scale,self.y* self.scale))

        if self.region_x1 != -1 and self.region_x2 != -1:
            qp.drawRect(self.region_x1/self.scale,
                        self.region_y1/self.scale,
                        self.region_x2/self.scale - self.region_x1/self.scale,
                        self.region_y2/self.scale - self.region_y1/self.scale
                        )
        if self.press_x != -1 :
            qp.drawRect(self.press_x, self.press_y, self.x - self.press_x, self.y - self.press_y)

        qp.end()

    def mouseMoveEvent(self, e) -> None:
        self.x, self.y = e.x(), e.y()
        self.update()

    def mousePressEvent(self, e):
        self.press_x, self.press_y = e.x(), e.y()


    def mouseReleaseEvent(self, e) -> None:
        x, y = e.x(), e.y()
        if abs(self.press_x - x)<5 and abs(self.press_y - y)<5 :
            self.point_list.append([x * self.scale, y * self.scale, self.color_at(x * self.scale, y * self.scale)])
        else:
            self.region_x2, self.region_y2 = x * self.scale, y * self.scale
            self.region_x1, self.region_y1 = self.press_x * self.scale, self.press_y * self.scale
        self.press_x = -1
        self.press_y = -1
        self.update()


    def set_img(self, img:QImage):
        if img is None:
            return
        self.img = img
        w, h = img.width(), img.height()
        print(self.height())
        self.scale = max(w/self.width() , h/self.height())
        nimg = self.img.scaled(w / self.scale, h / self.scale)
        self.setPixmap(QPixmap.fromImage(nimg))
        self.setFixedSize(nimg.width(), nimg.height())
        self.point_list.clear()
        self.update()

    def clear_point(self):
        self.point_list.clear()
        self.region_x1, self.region_y1, self.region_x2, self.region_y2 = -1, -1, -1, -1
        self.update()

    def color_at(self, x,y):
        if self.img is None:
            return -1
        color:QColor = self.img.pixelColor(x, y)
        return "0x%.2x%.2x%.2x" % (color.red(), color.green(), color.blue())

    def get_region(self):
        if self.region_x1 == -1:
            return None
        else:
            return (self.region_x1,
                    self.region_y1,
                    self.region_x2,
                    self.region_y2)

    def save_img(self, path):
        if self.img:
            return self.img.save(os.path.join(path,"screenshot-%d.png"%(time.time()) ) )
        return False

    def scale_up(self):
        if self.img:
            self.scale = self.scale - 0.5
            w, h = self.img.width(), self.img.height()
            nimg = self.img.scaled(w / self.scale, h / self.scale)
            self.setPixmap(QPixmap.fromImage(nimg))
            self.setFixedSize(nimg.width(), nimg.height())
            self.update()

    def scale_down(self):
        if self.img:
            self.scale = self.scale + 0.5
            w, h = self.img.width(), self.img.height()
            nimg = self.img.scaled(w / self.scale, h / self.scale)
            self.setPixmap(QPixmap.fromImage(nimg))
            self.setFixedSize(nimg.width(), nimg.height())
            self.update()
