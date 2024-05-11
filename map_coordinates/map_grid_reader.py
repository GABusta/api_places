import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use the non-GUI Agg backend
import matplotlib.pyplot as plt
import os


def correct_quad_orientation(elements, node_coords):
    """
    Adjust the orientation of quadrilateral elements to counterclockwise order.
    :param elements: Array of arrays, where each sub-array has indices to 'node_coords',
                     the first item in each sub-array is the element ID, the next four are node indices.
    :param node_coords: Array of coordinates, where each sub-array contains [x, y, z] for each node.
    :return: Array of corrected node indices for each element.
    """
    corrected_elements = []

    for element in elements:
        node_indices = np.array(element[1:5])
        coords = np.array([node_coords[index - 1][:2] for index in node_indices])

        center = np.mean(coords, axis=0)
        angles = np.arctan2(coords[:, 1] - center[1], coords[:, 0] - center[0])

        sorted_indices = node_indices[np.argsort(angles)]
        corrected_elements.append(np.concatenate(([element[0]], sorted_indices)))

    return np.array(corrected_elements)


class Mesh:
    """
    Mesh Structure
    """
    def __init__(self):
        self.physical_entities = {}
        self.geometry = {}
        self.meshing = {}

    def read_gmsh_file(self, file, tipo, dim=2):
        """
        how to read the msh file here -->  http://gmsh.info/dev/doc/texinfo/gmsh.pdf
        \n
        :param file: location of the msh file
        :param tipo:
        :param dim: 1 or 2 dimensions
        :return: mesh object
        """
        with open(file) as input_file:
            read_file = input_file.readlines()
            read_file = [line.rstrip("\n") for line in read_file]

            # --- splitting the file ---
            physical_idx, entities_idx, nodes_idx, elements_idx = Mesh._splitting_file(
                read_file
            )

            # --- physical entities ---
            Mesh._physical_entities(self, read_file, physical_idx)

            # --- Entities ---
            Mesh._entities(self, read_file, entities_idx)

            # --- Nodes ---
            Mesh._nodes(self, read_file, nodes_idx)

            # --- Elements ---
            Mesh._elements(self, read_file, elements_idx)

        return self

    @staticmethod
    def _splitting_file(read_file):
        physical_idx = [
            read_file.index("$PhysicalNames"),
            read_file.index("$EndPhysicalNames"),
        ]
        entities_idx = [
            read_file.index("$Entities"),
            read_file.index("$EndEntities"),
        ]
        nodes_idx = [read_file.index("$Nodes"), read_file.index("$EndNodes")]
        elements_idx = [
            read_file.index("$Elements"),
            read_file.index("$EndElements"),
        ]

        return physical_idx, entities_idx, nodes_idx, elements_idx

    def _physical_entities(self, read_file, physical_idx):
        total_physical_entities = int(read_file[physical_idx[0] + 1])
        for idx in range(total_physical_entities):
            read_line = read_file[physical_idx[0] + 2 + idx].split(" ")
            # lines
            if int(read_line[0]) == 1:
                self.physical_entities.contour_idxs.append(int(read_line[1]))
                self.physical_entities.contour_tag.append(read_line[2].replace('"', ""))
            # surfaces
            else:
                self.physical_entities.surface_idxs.append(int(read_line[1]))
                self.physical_entities.surface_tag.append(read_line[2])

        self.physical_entities.contours_number = len(
            self.physical_entities.contour_idxs
        )
        self.physical_entities.surfaces_number = len(
            self.physical_entities.surface_idxs
        )
        return self

    def _entities(self, read_file, entities_idx):
        entities = read_file[entities_idx[0] + 1].split(" ")
        n_points = int(entities[0])
        n_curves = int(entities[1])
        n_surfaces = int(entities[2])
        self.geometry.points.points_number = n_points
        self.geometry.curves.curves_number = n_curves
        self.geometry.surfaces.surfaces_number = n_surfaces

        for idx in range(n_points):
            read_line = read_file[entities_idx[0] + 2 + idx].split(" ")
            self.geometry.points.point.append(int(read_line[0]))
            self.geometry.points.point_coord.append(
                list(map(int, [read_line[1], read_line[2]]))
            )

        for idx in range(n_curves):
            read_line = read_file[entities_idx[0] + 2 + idx + n_points].split(" ")
            self.geometry.curves.curve_tag.append(int(read_line[0]))
            self.geometry.curves.curve_coord.append(
                list(map(int, [coord for coord in read_line[1:7]]))
            )

            count_physical = int(read_line[7])
            self.geometry.curves.physical_tags_number.append(count_physical)
            self.geometry.curves.physical_tags.append(
                list(map(int, (tag for tag in read_line[8 : 8 + count_physical])))
            )

            count = int(read_line[8 + count_physical])
            self.geometry.curves.bounding_curves_number.append(count)
            self.geometry.curves.bounding_curves.append(
                list(map(int, [curve for curve in read_line[10 : 10 + count]]))
            )

        for idx in range(n_surfaces):
            read_line = read_file[
                entities_idx[0] + 2 + idx + n_points + n_curves
            ].split(" ")
            self.geometry.surfaces.surfaces_tag.append(int(read_line[0]))
            self.geometry.surfaces.surfaces_coord.append(
                list(map(int, [coord for coord in read_line[1:7]]))
            )

            count_physical = int(read_line[7])
            self.geometry.surfaces.physical_tags_number.append(count_physical)
            self.geometry.surfaces.physical_tags.append(
                list(map(int, (tag for tag in read_line[8 : 8 + count_physical])))
            )
            count = int(read_line[8 + count_physical])
            self.geometry.surfaces.bounding_curves_number.append(count)
            self.geometry.surfaces.curves_tags.append(
                list(map(int, [tag for tag in read_line[10 : 10 + count]]))
            )

        return self

    def _nodes(self, read_file, nodes_idx):
        read_line = read_file[nodes_idx[0] + 1].split(" ")
        self.meshing.nodes_number = int(read_line[3])
        idx = nodes_idx[0] + 1
        while idx < nodes_idx[1] - 1:
            read_line = read_file[idx + 1].split(" ")
            entity_dim = int(read_line[0])
            entity_tag = int(read_line[1])
            nodes_in_block = int(read_line[3])

            initial = idx + 2
            end = initial + nodes_in_block
            node_tags = read_file[initial:end]
            node_coords = read_file[end : end + nodes_in_block]

            # if entity_dim == 0:
            #    idx += nodes_in_block * 2 + 1
            #    continue

            for tag in node_tags:
                # node_id, entity_dimension, entity_id
                self.meshing.nodes_entities_tag.append(
                    [int(tag), entity_dim, entity_tag]
                )

            for coord in node_coords:
                coordinate = coord.split(" ")
                self.meshing.nodes_coord.append(
                    list(map(float, [value for value in coordinate]))
                )
            idx = end + nodes_in_block - 1

        return self

    def _elements(self, read_file, elements_idx):
        read_line = read_file[elements_idx[0] + 1].split(" ")
        self.meshing.elements_number = int(read_line[1])
        idx = 1
        while idx < self.meshing.elements_number - 1:
            read_line = read_file[elements_idx[0] + 1 + idx].split(" ")
            entity_dim = int(read_line[0])
            entity_tag = int(read_line[1])
            element_type = int(read_line[2])
            elements_in_block = int(read_line[3])

            # only use the 2D elements
            if element_type != 3:
                idx += elements_in_block + 1
                continue

            initial = elements_idx[0] + 2 + idx
            end = initial + elements_in_block
            elements_tags = read_file[initial:end]

            for element in elements_tags:
                nodes = element.split(" ", maxsplit=4)
                self.meshing.elements_connection.append(
                    list(map(int, [node.strip() for node in nodes]))
                )
            idx += elements_in_block + 1
        self.meshing.elements_number = len(self.meshing.elements_connection)

        return self


class MeshRead:
    """
    Mesh Read from .msh file
    """
    def __init__(
        self,
        geometry_points=np.array(
            [
                [0.0, 0.0],
                [40.0, 0.0],
                [40.0, 40.0],
                [25.0, 40.0],
                [25.0, 20.0],
                [15.0, 20.0],
                [15.0, 40.0],
                [5.0, 40.0],
                [5.0, 10.0],
                [3.0, 7.0],
                [0.0, 7.0],
            ]
        ),
        model_name="default_model",
        path="./mesh_files/default_geom.msh",
        mesh_file_name="default_geom.msh",
        element_size=2.0,
        tipo=1,
        dim=2,
    ):
        """
        Read the mesh file, or generate the mesh file if it is not created \n
        :param geometry_points: points of the external geometry
        :param model_name:
        :param mesh_file_name: name with the root path
        :param element_size: size of the finite element used
        :param tipo: type of study
        :param dim: number of dimensions
        :return self
        """
        self.mesh_data = []

        try:
            self.mesh_data = MeshRead.read_gmsh_file(path=path, tipo=tipo, dim=dim)

        except Exception:
            self.mesh_data = MeshRead.generation_read_gmsh_file(
                geometry_points=geometry_points,
                path=path,
                model_name=model_name,
                mesh_file_name=mesh_file_name,
                element_size=element_size,
                tipo=tipo,
                dim=dim,
            )

    @staticmethod
    def read_gmsh_file(path, tipo, dim):
        mesh_file_path = os.path.abspath(path)
        return Mesh().read_gmsh_file(file=mesh_file_path, tipo=tipo, dim=dim)

    @staticmethod
    def generation_read_gmsh_file(
        geometry_points, path, model_name, mesh_file_name, element_size, tipo, dim
    ):
        MeshRead.generation_gmsh_file(
            geometry_points, model_name, path, mesh_file_name, element_size
        )
        return MeshRead.read_gmsh_file(path, tipo, dim)


    def correct_quad_orientation(self):
        """
        Adjust the orientation of quadrilateral elements to counterclockwise order.
        :param elements: Array of arrays, where each sub-array has indices to 'node_coords',
                        the first item in each sub-array is the element ID, the next four are node indices.
        :param node_coords: Array of coordinates, where each sub-array contains [x, y, z] for each node.
        :return: Array of corrected node indices for each element.
        """
        corrected_elements = []
        elements = self.mesh_data.meshing.elements_connection
        node_coords = self.mesh_data.meshing.nodes_coord

        for element in elements:
            node_indices = np.array(element[1:5])
            coords = np.array([node_coords[index - 1][:2] for index in node_indices])

            center = np.mean(coords, axis=0)
            angles = np.arctan2(coords[:, 1] - center[1], coords[:, 0] - center[0])

            sorted_indices = node_indices[np.argsort(angles)]
            corrected_elements.append(np.concatenate(([element[0]], sorted_indices)))

        self.mesh_data.meshing.elements_connection = np.array(corrected_elements)
        return self
