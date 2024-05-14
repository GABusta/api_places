import numpy as np
import gmsh
import warnings
import os
from typing import List

warnings.filterwarnings("ignore")
absolute_path = os.path.dirname(__file__)


def get_coordinates_from_file(model_name: str) -> List[List[float]]:
    coordinates = []
    boundaries_filename = f"map_coordinates/boundaries/{model_name}.txt"
    with open(boundaries_filename, "r") as file:
        for line in file:
            lat, lon = line.strip().split(",")
            coordinates.append([float(lon), float(lat)])
    return coordinates


def mesh_generation_file(model_name: str, size_element: float) -> None:
    """
    Generation of the mesh file
    :param size_element:
    :param model_name:
    :return:
    """
    filename = f"map_coordinates/msh_files/{model_name}.msh"
    geom_points = get_coordinates_from_file(model_name)

    gmsh.initialize()
    gmsh.option.setNumber("General.Terminal", 1)  # GMSH prints mgs into console
    gmsh.model.add(model_name)

    # --- Points
    # --> gmsh.model.geo.addPoint( x, y, z, size_element, tag )
    for id, points in enumerate(geom_points):
        gmsh.model.geo.addPoint(points[0], points[1], 0.0, size_element, id)

    # --- Lines
    # --> gmsh.model.geo.addLine( initial_point_id, final_point_id, tag)
    curves_id = []
    for id, points in enumerate(geom_points):
        curves_id.append(id + 1)
        if id < len(geom_points) - 1:
            gmsh.model.geo.addLine(id, id + 1, id + 1)

        else:
            gmsh.model.geo.addLine(id, 0, id + 1)

    # --- curve loops
    # outside curves --> gmsh.model.geo.addCurveLoop( curves_id (array), tag )
    curves_id = np.array(curves_id, dtype=int)
    gmsh.model.geo.addCurveLoop(curves_id[:], 21)

    # --- surface
    # --> gmsh.model.geo.addPlaneSurface( curve_Loops (array), tag )
    gmsh.model.geo.addPlaneSurface([21], 22)

    # --- Physical groups
    # per default, GMSH reports only the FE that belongs to a certain physical defined group.
    # --> gmsh.model.addPhysicalGroup( Dimension, entities lists, tag)
    gmsh.model.geo.synchronize()
    for curve in curves_id:
        gmsh.model.addPhysicalGroup(dim=1, tags=[curve], name=f"curve{curve}")

    gmsh.model.addPhysicalGroup(dim=2, tags=[22], name="surface")
    # ---Mesh
    gmsh.model.geo.synchronize()
    gmsh.model.geo.mesh.setTransfiniteSurface(22)
    gmsh.model.mesh.setRecombine(2, 22)
    gmsh.model.mesh.generate(2)  # Unstructured Quad
    gmsh.model.mesh.optimize("QuadQuasiStructured")
    gmsh.option.setNumber("Mesh.SurfaceFaces", 1)  # show FE faces

    gmsh.write(filename)
    gmsh.fltk.run()
    gmsh.finalize()
