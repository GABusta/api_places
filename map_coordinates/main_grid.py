from map_grid_generation import mesh_generation_file
from map_grid_reader import Mesh


if __name__ == "__main__":
    model_name = "buenos_aires"
    size_element = 0.15

    mesh_generation_file(
        model_name=model_name,
        size_element=size_element,
        )