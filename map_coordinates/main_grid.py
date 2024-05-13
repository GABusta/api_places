from files_map_logic.map_grid_generation import mesh_generation_file
from files_map_logic.map_grid_reader import Mesh


if __name__ == "__main__":
    # -- MODIFY THIS --
    model_name = "buenos_aires"
    size_element = 0.15
    # -----------------

    mesh_generation_file(
        model_name=model_name,
        size_element=size_element,
        )
    
    mesh = Mesh()
    mesh.read_gmsh_file(f'map_coordinates/msh_files/{model_name}.msh')
    mesh.calculate_and_save_centroids(model_name)