import numpy as np
from stl import mesh


class Model3D:
    def __init__(self, stl_file_path):
        # Load the STL file
        self.mesh = mesh.Mesh.from_file(stl_file_path)
        
        # Get the x, y, z coordinates from the mesh
        x = self.mesh.x.flatten()
        y = self.mesh.y.flatten()
        z = self.mesh.z.flatten()
        
        # Create the object using homogeneous coordinates
        self.model = np.array([x.T, y.T, z.T, np.ones(x.size)])
