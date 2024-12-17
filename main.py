import sys
from math import cos, pi, sin

import matplotlib.pyplot as plt
import numpy as np
import qdarktheme
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from mpl_toolkits.mplot3d import Axes3D
from numpy import array
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QDoubleValidator
from PyQt5.QtWidgets import (
    QApplication,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QFileDialog,
)

from object_3d import Model3D

###### Crie suas funções de translação, rotação, criação de referenciais, plotagem de setas e qualquer outra função que precisar


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Add arrow size variables
        self.world_arrow_size = 1.5
        self.camera_arrow_size = 1.5
        
        # definindo as variaveis
        self.set_variables()
        # Ajustando a tela
        self.setWindowTitle("Grid Layout")
        self.setGeometry(100, 100, 1280, 720)
        self.setup_ui()
        self.setFocusPolicy(Qt.StrongFocus)

    def set_variables(self):
        self.objeto_original = None
        self.objeto = None
        self.cam_original = self.init_cam()
        self.cam = self.cam_original
        self.px_base = 1280
        self.px_altura = 720
        self.dist_foc = 50
        self.stheta = 0
        self.ox = self.px_base / 2
        self.oy = self.px_altura / 2
        self.ccd = [36, 24]
        self.projection_matrix = []

    def setup_ui(self):
        # Apply dark theme with custom accent color
        style_sheet = """
            QMainWindow {
                background-color: #2b2b2b;
            }
            QGroupBox {
                border: 2px solid #404040;
                border-radius: 8px;
                margin-top: 1em;
                font-weight: bold;
                color: #e0e0e0;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QLineEdit {
                padding: 5px;
                border: 1px solid #404040;
                border-radius: 4px;
                background-color: #333333;
                color: #e0e0e0;
            }
            QLabel {
                color: #e0e0e0;
            }
            QPushButton {
                background-color: #0d47a1;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1565c0;
            }
            QPushButton:pressed {
                background-color: #0a3d91;
            }
        """
        self.setStyleSheet(style_sheet)

        # Criar o layout de grade
        qdarktheme.setup_theme()
        grid_layout = QGridLayout()

        # Criar os widgets
        line_edit_widget1 = self.create_world_widget("Ref mundo")
        line_edit_widget2 = self.create_cam_widget("Ref camera")
        line_edit_widget3 = self.create_intrinsic_widget("params instr")

        self.canvas = self.create_matplotlib_canvas()

        # Adicionar os widgets ao layout de grade
        grid_layout.addWidget(line_edit_widget1, 0, 0)
        grid_layout.addWidget(line_edit_widget2, 0, 1)
        grid_layout.addWidget(line_edit_widget3, 0, 2)
        grid_layout.addWidget(self.canvas, 1, 0, 1, 3)

        # Criar um widget para agrupar o botão de reset
        reset_widget = QWidget()
        reset_layout = QHBoxLayout()
        reset_widget.setLayout(reset_layout)

        # Create file open button
        file_button = QPushButton("Open STL File")
        file_button.clicked.connect(self.open_stl_file)
        
        # Add the button to reset_layout (before adding reset_button)
        reset_layout.addWidget(file_button)

        # Criar o botão de reset vermelho
        reset_button = QPushButton("Reset")
        reset_button.setFixedSize(80, 35)
        reset_style = """
            QPushButton {
                background-color: #c62828;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
            QPushButton:pressed {
                background-color: #b71c1c;
            }
        """
        reset_button.setStyleSheet(reset_style)
        reset_button.clicked.connect(self.reset_canvas)

        # Adicionar o botão de reset ao layout
        reset_layout.addWidget(reset_button)

        # Adicionar o widget de reset ao layout de grade
        grid_layout.addWidget(reset_widget, 2, 0, 1, 3)

        # Criar um widget central e definir o layout de grade como seu layout
        central_widget = QWidget()
        central_widget.setLayout(grid_layout)

        # Definir o widget central na janela principal
        self.setCentralWidget(central_widget)

    def create_intrinsic_widget(self, title):
        # Criar um widget para agrupar os QLineEdit
        line_edit_widget = QGroupBox(title)
        line_edit_layout = QVBoxLayout()
        line_edit_widget.setLayout(line_edit_layout)

        # Criar um layout de grade para dividir os QLineEdit em 3 colunas
        grid_layout = QGridLayout()

        line_edits = []
        labels = [
            "n_pixels_base:",
            "n_pixels_altura:",
            "ccd_x:",
            "ccd_y:",
            "dist_focal:",
            "sθ:",
            "World arrows:",
            "Camera arrows:",
        ]

        # Adicionar widgets QLineEdit com caixa de texto ao layout de grade
        for i in range(1, 9):
            line_edit = QLineEdit()
            label = QLabel(labels[i - 1])
            validator = QDoubleValidator()  # Validador numérico
            line_edit.setValidator(validator)  # Aplicar o validador ao QLineEdit
            grid_layout.addWidget(label, (i - 1) // 2, 2 * ((i - 1) % 2))
            grid_layout.addWidget(line_edit, (i - 1) // 2, 2 * ((i - 1) % 2) + 1)
            line_edits.append(line_edit)

        # Criar o botão de atualização
        update_button = QPushButton("Atualizar")
        clear_button = QPushButton("Limpar")

        ##### Você deverá criar, no espaço reservado ao final, a função self.update_params_intrinsc ou outra que você queira
        # Conectar a função de atualização aos sinais de clique do botão
        update_button.clicked.connect(lambda: self.update_params_intrinsc(line_edits))
        clear_button.clicked.connect(lambda: self.clear_fields(line_edits))
        # Adicionar os widgets ao layout do widget line_edit_widget
        line_edit_layout.addLayout(grid_layout)
        line_edit_layout.addWidget(update_button)
        line_edit_layout.addWidget(clear_button)

        # Retornar o widget e a lista de caixas de texto
        return line_edit_widget

    def create_world_widget(self, title):
        # Criar um widget para agrupar os QLineEdit
        line_edit_widget = QGroupBox(title)
        line_edit_layout = QVBoxLayout()
        line_edit_widget.setLayout(line_edit_layout)

        # Criar um layout de grade para dividir os QLineEdit em 3 colunas
        grid_layout = QGridLayout()

        line_edits = []
        labels = [
            "X(move):",
            "X(angle):",
            "Y(move):",
            "Y(angle):",
            "Z(move):",
            "Z(angle):",
        ]  # Texto a ser exibido antes de cada QLineEdit

        # Adicionar widgets QLineEdit com caixa de texto ao layout de grade
        for i in range(1, 7):
            line_edit = QLineEdit()
            label = QLabel(labels[i - 1])
            validator = QDoubleValidator()  # Validador numérico
            line_edit.setValidator(validator)  # Aplicar o validador ao QLineEdit
            grid_layout.addWidget(label, (i - 1) // 2, 2 * ((i - 1) % 2))
            grid_layout.addWidget(line_edit, (i - 1) // 2, 2 * ((i - 1) % 2) + 1)
            line_edits.append(line_edit)

        # Criar o botão de atualização
        update_button = QPushButton("Atualizar")
        clear_button = QPushButton("Limpar")
        ##### Você deverá criar, no espaço reservado ao final, a função self.update_world ou outra que você queira
        # Conectar a função de atualização aos sinais de clique do botão
        update_button.clicked.connect(lambda: self.update_world(line_edits))
        clear_button.clicked.connect(lambda: self.clear_fields(line_edits))
        # Adicionar os widgets ao layout do widget line_edit_widget
        line_edit_layout.addLayout(grid_layout)
        line_edit_layout.addWidget(update_button)
        line_edit_layout.addWidget(clear_button)

        # Retornar o widget e a lista de caixas de texto
        return line_edit_widget

    def create_cam_widget(self, title):
        # Criar um widget para agrupar os QLineEdit
        line_edit_widget = QGroupBox(title)
        line_edit_layout = QVBoxLayout()
        line_edit_widget.setLayout(line_edit_layout)

        # Criar um layout de grade para dividir os QLineEdit em 3 colunas
        grid_layout = QGridLayout()

        line_edits = []
        labels = [
            "X(move):",
            "X(angle[°]):",
            "Y(move):",
            "Y(angle[°]):",
            "Z(move):",
            "Z(angle[°]):",
        ]  # Texto a ser exibido antes de cada QLineEdit

        # Adicionar widgets QLineEdit com caixa de texto ao layout de grade
        for i in range(1, 7):
            line_edit = QLineEdit()
            label = QLabel(labels[i - 1])
            validator = QDoubleValidator()  # Validador numérico
            line_edit.setValidator(validator)  # Aplicar o validador ao QLineEdit
            grid_layout.addWidget(label, (i - 1) // 2, 2 * ((i - 1) % 2))
            grid_layout.addWidget(line_edit, (i - 1) // 2, 2 * ((i - 1) % 2) + 1)
            line_edits.append(line_edit)

        # Criar o botão de atualização
        update_button = QPushButton("Atualizar")
        clear_button = QPushButton("Limpar")

        ##### Você deverá criar, no espaço reservado ao final, a função self.update_cam ou outra que você queira
        # Conectar a função de atualização aos sinais de clique do botão
        update_button.clicked.connect(lambda: self.update_cam(line_edits))
        clear_button.clicked.connect(lambda: self.clear_fields(line_edits))
        # Adicionar os widgets ao layout do widget line_edit_widget
        line_edit_layout.addLayout(grid_layout)
        line_edit_layout.addWidget(update_button)
        line_edit_layout.addWidget(clear_button)

        # Retornar o widget e a lista de caixas de texto
        return line_edit_widget

    def clear_fields(self, line_edits):
        for line_edit in line_edits:
            line_edit.clear()

    def create_matplotlib_canvas(self):
        # Criar um widget para exibir os gráficos do Matplotlib
        canvas_widget = QWidget()
        canvas_layout = QHBoxLayout()
        canvas_widget.setLayout(canvas_layout)

        # Criar um objeto FigureCanvas para exibir o gráfico 2D
        self.fig1, self.ax1 = plt.subplots()
        self.ax1.set_title("Camera View", pad=20, fontsize=12, fontweight="bold")
        self.ax1.set_xlabel("X (pixels)", fontsize=10)
        self.ax1.set_ylabel("Y (pixels)", fontsize=10)
        self.ax1.grid(True, linestyle="--", alpha=0.3)
        self.canvas1 = FigureCanvas(self.fig1)

        ##### Falta acertar os limites do eixo X
        self.ax1.set_xlim(0, self.px_base)
        ##### Falta acertar os limites do eixo Y
        self.ax1.set_ylim(0, self.px_altura)

        ##### Você deverá criar a função de projeção
        if self.objeto is not None:
            object_2d = self.projection_2d()
            self.ax1.plot(object_2d[0, :], object_2d[1, :], "r-")

        self.ax1.grid("True")
        self.ax1.set_aspect("equal")
        canvas_layout.addWidget(self.canvas1)

        # Criar um objeto FigureCanvas para exibir o gráfico 3D
        self.fig2 = plt.figure()
        self.ax2 = self.fig2.add_subplot(111, projection="3d")
        self.ax2.set_title("3D Scene", pad=20, fontsize=12, fontweight="bold")
        self.ax2.set_xlabel("X", fontsize=10)
        self.ax2.set_ylabel("Y", fontsize=10)
        self.ax2.set_zlabel("Z", fontsize=10)
        self.ax2.grid(True, linestyle="--", alpha=0.3)

        self.draw_arrows(self.cam[:, -1], self.cam[:, 0:3], self.ax2)  # rotation matrix
        self.draw_arrows(self.cam_original[:, -1], self.cam_original[:, 0:3], self.ax2)

        ##### Falta plotar o seu objeto 3D e os referenciais da câmera e do mundo
        if self.objeto is not None:
            self.ax2.plot(self.objeto[0, :], self.objeto[1, :], self.objeto[2, :], "r-")

        self.ax2.plot(self.cam[0, :], self.cam[1, :], self.cam[2, :], "g-")
        self.ax2.plot(
            self.cam_original[0, :],
            self.cam_original[1, :],
            self.cam_original[2, :],
            "b-",
        )
        self.canvas2 = FigureCanvas(self.fig2)
        canvas_layout.addWidget(self.canvas2)

        # Retornar o widget de canvas
        return canvas_widget

    ##### Você deverá criar as suas funções aqui
    def reset_plot(self):
        # Clear both axes
        self.ax1.clear()
        self.ax2.clear()

        # Redraw 2D plot
        self.ax1.set_title("Camera View", pad=20, fontsize=12, fontweight="bold")
        self.ax1.set_xlabel("X (pixels)", fontsize=10)
        self.ax1.set_ylabel("Y (pixels)", fontsize=10)
        self.ax1.grid(True, linestyle="--", alpha=0.3)
        self.ax1.set_xlim(0, self.px_base)
        self.ax1.set_ylim(0, self.px_altura)
        if self.objeto is not None:
            object_2d = self.projection_2d()
            self.ax1.plot(object_2d[0, :], object_2d[1, :], "r-")
        self.ax1.grid(True)
        self.ax1.set_aspect("equal")

    # adding quivers to the plot
    def draw_arrows(self, point, base, axis, length=1.5):
        # The object base is a matrix, where each column represents the vector
        # of one of the axis, written in homogeneous coordinates (ax,ay,az,0)

        # Plot vector of x-axis
        axis.quiver(
            point[0],
            point[1],
            point[2],
            base[0, 0],
            base[1, 0],
            base[2, 0],
            color="red",
            pivot="tail",
            length=length,
        )
        # Plot vector of y-axis
        axis.quiver(
            point[0],
            point[1],
            point[2],
            base[0, 1],
            base[1, 1],
            base[2, 1],
            color="green",
            pivot="tail",
            length=length,
        )
        # Plot vector of z-axis
        axis.quiver(
            point[0],
            point[1],
            point[2],
            base[0, 2],
            base[1, 2],
            base[2, 2],
            color="blue",
            pivot="tail",
            length=length,
        )

        return axis

    def move(self, dx, dy, dz):
        T = np.eye(4)
        T[0, -1] = dx
        T[1, -1] = dy
        T[2, -1] = dz
        return T

    def z_rotation(self, angle):
        rotation_matrix = np.array(
            [
                [cos(angle), -sin(angle), 0, 0],
                [sin(angle), cos(angle), 0, 0],
                [0, 0, 1, 0],
                [0, 0, 0, 1],
            ]
        )
        return rotation_matrix

    def x_rotation(self, angle):
        rotation_matrix = np.array(
            [
                [1, 0, 0, 0],
                [0, cos(angle), -sin(angle), 0],
                [0, sin(angle), cos(angle), 0],
                [0, 0, 0, 1],
            ]
        )
        return rotation_matrix

    def y_rotation(self, angle):
        rotation_matrix = np.array(
            [
                [cos(angle), 0, sin(angle), 0],
                [0, 1, 0, 0],
                [-sin(angle), 0, cos(angle), 0],
                [0, 0, 0, 1],
            ]
        )
        return rotation_matrix

    def update_params_intrinsc(self, line_edits):
        self.px_base = (
            float(line_edits[0].text())
            if not line_edits[0].text() == ""
            else self.px_base
        )
        self.px_altura = (
            float(line_edits[1].text())
            if not line_edits[1].text() == ""
            else self.px_altura
        )
        self.ccd[0] = (
            float(line_edits[2].text())
            if not line_edits[2].text() == ""
            else self.ccd[0]
        )
        self.ccd[1] = (
            float(line_edits[3].text())
            if not line_edits[3].text() == ""
            else self.ccd[1]
        )
        self.dist_foc = (
            float(line_edits[4].text())
            if not line_edits[4].text() == ""
            else self.dist_foc
        )
        self.stheta = (
            float(line_edits[5].text())
            if not line_edits[5].text() == ""
            else self.stheta
        )
        self.world_arrow_size = (
            float(line_edits[6].text())
            if not line_edits[6].text() == ""
            else self.world_arrow_size
        )
        self.camera_arrow_size = (
            float(line_edits[7].text())
            if not line_edits[7].text() == ""
            else self.camera_arrow_size
        )

        print("\n=== Intrinsic Parameters Updated ===")
        print(f"Resolution: {self.px_base}x{self.px_altura} pixels")
        print(f"CCD Sensor: {self.ccd[0]}x{self.ccd[1]} mm")
        print(f"Focal Distance: {self.dist_foc} mm")
        print(f"Skew: {self.stheta}")
        print(f"World Arrow Size: {self.world_arrow_size}")
        print(f"Camera Arrow Size: {self.camera_arrow_size}")
        print("================================\n")
        self.update_canvas()

    def update_world(self, line_edits):
        dx = float(line_edits[0].text()) if not line_edits[0].text() == "" else 0
        dy = float(line_edits[2].text()) if not line_edits[2].text() == "" else 0
        dz = float(line_edits[4].text()) if not line_edits[4].text() == "" else 0
        angle_x = (
            np.deg2rad(float(line_edits[1].text()))
            if not line_edits[1].text() == ""
            else 0
        )
        angle_y = (
            np.deg2rad(float(line_edits[3].text()))
            if not line_edits[3].text() == ""
            else 0
        )
        angle_z = (
            np.deg2rad(float(line_edits[5].text()))
            if not line_edits[5].text() == ""
            else 0
        )

        Rx, Ry, Rz = [], [], []
        T = np.eye(4)

        T = self.move(dx, dy, dz)
        Rx = self.x_rotation(angle_x)
        Ry = self.y_rotation(angle_y)
        Rz = self.z_rotation(angle_z)
        R = Rz @ Ry @ Rx
        self.cam = (self.cam_original @ R @ T) @ self.cam
        self.update_canvas()

    def update_cam(self, line_edits):
        dx = float(line_edits[0].text()) if not line_edits[0].text() == "" else 0
        dy = float(line_edits[2].text()) if not line_edits[2].text() == "" else 0
        dz = float(line_edits[4].text()) if not line_edits[4].text() == "" else 0

        angle_x = (
            np.deg2rad(float(line_edits[1].text()))
            if not line_edits[1].text() == ""
            else 0
        )
        angle_y = (
            np.deg2rad(float(line_edits[3].text()))
            if not line_edits[3].text() == ""
            else 0
        )
        angle_z = (
            np.deg2rad(float(line_edits[5].text()))
            if not line_edits[5].text() == ""
            else 0
        )

        Rx, Ry, Rz = [], [], []
        T = np.eye(4)

        T = self.move(dx, dy, dz)

        Rx = self.x_rotation(angle_x)
        Ry = self.y_rotation(angle_y)
        Rz = self.z_rotation(angle_z)

        R = Rz @ Ry @ Rx

        # Combine translation and rotation
        self.cam = self.cam @ R @ T

        self.update_canvas()

    def projection_2d(self):
        print("\n=== Projection Matrix Info ===")
        print("Computing projection matrix...")

        intrinsic_params = self.generate_intrinsic_params_matrix()
        print("\nIntrinsic Parameters Matrix:")
        print(intrinsic_params)

        extrinsic_params = np.linalg.inv(self.cam)
        print("\nExtrinsic Parameters Matrix:")
        print(extrinsic_params)

        matrix_pi = np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0]])
        self.projection_matrix = intrinsic_params @ matrix_pi @ extrinsic_params

        print("\nFinal Projection Matrix:")
        print(self.projection_matrix)
        print("==========================\n")

        projected_points = self.projection_matrix @ self.objeto
        # Normalize homogeneous coordinates
        projected_points = projected_points / projected_points[2, :]
        return projected_points[:2, :]  # Return only x,y coordinates

    def generate_intrinsic_params_matrix(self):
        dist_foc = self.dist_foc
        dx = dist_foc * self.px_base / self.ccd[0]
        dy = dist_foc * self.px_altura / self.ccd[1]

        print(f"dx: {dx}, dy: {dy}")

        intrinsic_params = np.array(
            [
                [dx, -dx * self.stheta, self.ox],
                [0, dy, self.oy],
                [0, 0, 1],
            ]
        )

        return intrinsic_params

    def update_canvas(self):
        self.reset_plot()

        # Redraw 3D plot with different arrow sizes for world and camera
        self.draw_arrows(self.cam[:, -1], self.cam[:, 0:3], self.ax2, length=self.camera_arrow_size)
        self.draw_arrows(self.cam_original[:, -1], self.cam_original[:, 0:3], self.ax2, length=self.world_arrow_size)
        if self.objeto is not None:
            self.ax2.plot(self.objeto[0, :], self.objeto[1, :], self.objeto[2, :], "r-")
        self.ax2.plot(self.cam[0, :], self.cam[1, :], self.cam[2, :], "g-")
        self.ax2.plot(
            self.cam_original[0, :],
            self.cam_original[1, :],
            self.cam_original[2, :],
            "b-",
        )

        self.canvas1.draw()
        self.canvas2.draw()

    def reset_canvas(self):
        # Keep the original object but reset its position
        if self.objeto_original is not None:
            self.objeto = self.objeto_original.copy()
        
        # Reset all other parameters
        self.cam_original = self.init_cam()
        self.cam = self.cam_original
        self.px_base = 1280
        self.px_altura = 720
        self.dist_foc = 50
        self.stheta = 0
        self.ox = self.px_base / 2
        self.oy = self.px_altura / 2
        self.ccd = [36, 24]
        self.projection_matrix = []
        self.world_arrow_size = 1.5  # Reset arrow sizes
        self.camera_arrow_size = 1.5
        
        self.reset_plot()
        self.update_canvas()

    def init_cam(self):
        # Create the camera matrix directly as a numpy array
        cam = np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]])

        return cam

    def keyPressEvent(self, event):
        # Define movement speed
        move_speed = 0.5
        angle_speed = 5  # in degrees

        # Create a list to simulate the line_edits input for update_cam
        # Format: [x_move, x_angle, y_move, y_angle, z_move, z_angle]
        line_edits = ["0", "0", "0", "0", "0", "0"]

        # Handle arrow key movements
        if event.key() == Qt.Key_Left:
            line_edits[0] = str(-move_speed)
        elif event.key() == Qt.Key_Right:
            line_edits[0] = str(move_speed)
        elif event.key() == Qt.Key_Up:
            line_edits[2] = str(move_speed)
        elif event.key() == Qt.Key_Down:
            line_edits[2] = str(-move_speed)
        elif event.key() == Qt.Key_PageUp:
            line_edits[4] = str(move_speed)
        elif event.key() == Qt.Key_PageDown:
            line_edits[4] = str(-move_speed)
        # Handle rotation keys
        elif event.key() == Qt.Key_W:
            line_edits[1] = str(angle_speed)
        elif event.key() == Qt.Key_S:
            line_edits[1] = str(-angle_speed)
        elif event.key() == Qt.Key_A:
            line_edits[3] = str(angle_speed)
        elif event.key() == Qt.Key_D:
            line_edits[3] = str(-angle_speed)
        elif event.key() == Qt.Key_Q:
            line_edits[5] = str(angle_speed)
        elif event.key() == Qt.Key_E:
            line_edits[5] = str(-angle_speed)

        # Create mock QLineEdit objects with the text values
        class MockLineEdit:
            def __init__(self, text):
                self._text = text

            def text(self):
                return self._text

        mock_line_edits = [MockLineEdit(text) for text in line_edits]
        self.update_cam(mock_line_edits)

    def open_stl_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open STL File",
            "",
            "STL Files (*.stl);;All Files (*.*)"
        )
        if file_path:
            self.objeto_original = Model3D(file_path).model
            self.objeto = self.objeto_original
            self.update_canvas()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
