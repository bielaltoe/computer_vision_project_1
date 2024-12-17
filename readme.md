# 3D Camera Visualization Tool

This project is part of the Computational Vision classes at UFES, guided by Professor Raquel Frizera Vassallo. It is a PyQt5-based application designed for visualizing 3D objects and camera transformations. The tool allows users to load STL files, manipulate camera positions, and view both 3D and 2D projections in real-time.

## Features

- **Load and Visualize 3D STL Files:** Import and explore 3D models with ease.
- **Real-time 3D Scene Manipulation:** Adjust the scene dynamically with immediate visual feedback.
- **Interactive Camera Positioning:** Move and rotate the camera to explore different perspectives.
- **2D Camera View Projection:** View the 2D projection of the 3D scene from the camera's perspective.
- **Adjustable Coordinate System Visualization:** Customize the size of coordinate vectors for better clarity.
- **Keyboard and UI Controls for Transformations:** Use intuitive controls to modify the scene.

## Installation

To set up the application, follow these steps:

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/bielaltoe/computer_vision_project_1.git
   ```

2. **Create and Activate a Virtual Environment (Optional but Recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Required Packages:**
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. **Run the Application:**
   ```bash
   python main.py
   ```

2. **Controls:**

   - **Keyboard Navigation:**
     - **Arrow Keys:** Move the camera position in the X/Y plane.
     - **Page Up/Down:** Move the camera position along the Z axis.
     - **W/S:** Rotate the camera around the X axis.
     - **A/D:** Rotate the camera around the Y axis.
     - **Q/E:** Rotate the camera around the Z axis.

3. **Parameters:**

   - **World Reference:** Adjust transformations of the world coordinate system.
   - **Camera Reference:** Modify the camera's position and orientation.
   - **Intrinsic Parameters:** Change camera properties and visualization settings.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---
