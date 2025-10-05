from PyQt5.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem
from PyQt5.QtGui import QPixmap, QImage, QPainter
from PyQt5.QtCore import Qt
from PIL import Image
import sys

class ImageViewer(QGraphicsView):
    def __init__(self, image_path):
        super().__init__()

        # Cargar imagen TIFF con Pillow
        pil_image = Image.open(image_path)
        pil_image = pil_image.convert("RGBA")  # asegura compatibilidad

        # Convertir a QImage
        data = pil_image.tobytes("raw", "RGBA")
        qimage = QImage(data, pil_image.width, pil_image.height, QImage.Format_RGBA8888)

        # Convertir a QPixmap
        pixmap = QPixmap.fromImage(qimage)

        # Crear escena y agregar imagen
        scene = QGraphicsScene()
        scene.addPixmap(pixmap)
        self.setScene(scene)

        # Configurar vista
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setRenderHint(QPainter.Antialiasing, True)  # 🔧 corrección aquí
        self.scale_factor = 1.25

    def wheelEvent(self, event):
        if event.angleDelta().y() > 0:
            self.scale(self.scale_factor, self.scale_factor)
        else:
            self.scale(1 / self.scale_factor, 1 / self.scale_factor)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = ImageViewer("imagen.tif")  # asegúrate de que el archivo esté en la misma carpeta
    viewer.show()
    sys.exit(app.exec_())

