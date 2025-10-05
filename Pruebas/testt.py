from PyQt5 import QtCore, QtGui, QtWidgets


class ImageViewer(QtWidgets.QGraphicsView):
    def __init__(self, parent=None):
        super(ImageViewer, self).__init__(parent)
        self.scene = QtWidgets.QGraphicsScene(self)
        self.setScene(self.scene)

        # Configuración para alta calidad
        self.setRenderHint(QtGui.QPainter.Antialiasing, True)
        self.setRenderHint(QtGui.QPainter.SmoothPixmapTransform, True)
        self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)
        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.scale_factor = 1.0

    def load_image(self, image_path):
        """Carga una imagen TIFF con máxima calidad"""
        image = QtGui.QImage(image_path)
        if image.isNull():
            QtWidgets.QMessageBox.warning(self, "Error", f"No se pudo abrir la imagen:\n{image_path}")
            return

        pixmap = QtGui.QPixmap.fromImage(image)
        self.scene.clear()
        self.scene.addPixmap(pixmap)
        self.fitInView(self.scene.itemsBoundingRect(), QtCore.Qt.KeepAspectRatio)
        self.scale_factor = 1.0

    def wheelEvent(self, event):
        """Zoom con la rueda del ratón"""
        zoom_in_factor = 1.25
        zoom_out_factor = 1 / zoom_in_factor

        if event.angleDelta().y() > 0:
            zoom_factor = zoom_in_factor
        else:
            zoom_factor = zoom_out_factor

        self.scale(zoom_factor, zoom_factor)
        self.scale_factor *= zoom_factor


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.setEnabled(True)
        MainWindow.resize(1226, 704)
        MainWindow.setTabShape(QtWidgets.QTabWidget.Rounded)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setStyleSheet("background-color:rgb(40,40,35)")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)

        # ----- Barra superior -----
        self.frameSuperior = QtWidgets.QFrame(self.centralwidget)
        self.frameSuperior.setStyleSheet("background-color: rgb(24, 24, 24);")
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout(self.frameSuperior)

        self.lblTitulo = QtWidgets.QLabel("STELLAR PIXELS", self.frameSuperior)
        self.lblTitulo.setStyleSheet("color:white; font-size:18pt; font-weight:bold;")
        self.horizontalLayout_6.addWidget(self.lblTitulo)

        self.lineEdit = QtWidgets.QLineEdit(self.frameSuperior)
        self.lineEdit.setPlaceholderText("Buscar...")
        self.lineEdit.setStyleSheet("background-color:white;")
        self.horizontalLayout_6.addWidget(self.lineEdit)

        self.verticalLayout.addWidget(self.frameSuperior)

        # ----- Panel principal -----
        self.framePaneles = QtWidgets.QFrame(self.centralwidget)
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.framePaneles)

        # Panel central (visor)
        self.panelCentral = QtWidgets.QFrame(self.framePaneles)
        self.verticalLayout_6 = QtWidgets.QVBoxLayout(self.panelCentral)

        # Controles superiores
        self.controles = QtWidgets.QFrame(self.panelCentral)
        self.horizontalLayout_9 = QtWidgets.QHBoxLayout(self.controles)
        self.zoom_label = QtWidgets.QLabel("100%")
        self.zoom_label.setStyleSheet("color:white;")
        self.horizontalLayout_9.addWidget(self.zoom_label)
        self.verticalLayout_6.addWidget(self.controles)

        # Visor de imagen
        self.imagen = QtWidgets.QFrame(self.panelCentral)
        self.verticalLayout_7 = QtWidgets.QVBoxLayout(self.imagen)
        self.viewer = ImageViewer()  # Aquí integramos el visor
        self.verticalLayout_7.addWidget(self.viewer)
        self.verticalLayout_6.addWidget(self.imagen)

        self.horizontalLayout.addWidget(self.panelCentral)
        self.verticalLayout.addWidget(self.framePaneles)

        MainWindow.setCentralWidget(self.centralwidget)
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        # Cargar imagen TIFF automáticamente
        self.viewer.load_image("imagen.tif")

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "STELLAR PIXELS"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
