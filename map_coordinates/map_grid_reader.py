import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use the non-GUI Agg backend
import matplotlib.pyplot as plt
import os


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
