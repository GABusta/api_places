from typing import List


class Points:
    """
    Attributes: \n
        `points_number:` int \n
        `point:` List[int] \n
        `point_coord:` List[List[float]] \n
    Methods: \n
        `__init__():`
    """
    def __init__(self):
        self.points_number: int = 0
        self.point: List[int] = []
        self.point_coord: List[List[float]] = []


class Curves:
    """
    Attributes: \n
        `curves_number:` int 
        `curve_tag:` List[int] \n
        `curve_coord:` \n
        `physical_tags_number:` List[int] \n
        `physical_tags:` List[int] \n
        `bounding_curves_number:` List[int] \n
        `bounding_curves:` List[int] \n
    Methods: \n
        `__init__():`
    """
    def __init__(self):
        self.curves_number: int = 0
        self.curve_tag: List[int] = []
        self.curve_coord: List[List[float]] = []
        self.physical_tags_number: List[int] = []
        self.physical_tags: List[int] = []
        self.bounding_curves_number: List[int] = []
        self.bounding_curves: List[int] = []


class Surfaces:
    """
    Attributes: \n
        `surfaces_number:` int \n
        `surfaces_tag:` List[int] \n
        `surfaces_coord:` List[List[float]] \n
        `physical_tags_number:` List[int] \n
        `physical_tags:` List[int] \n
        `bounding_curves_number:` List[int] \n
        `curves_tags:` List[int] \n
    Methods: \n
        `__init__():`
    """
    def __init__(self):
        self.surfaces_number: int = 0
        self.surfaces_tag: List[int] = []
        self.surfaces_coord: List[List[float]] = []
        self.physical_tags_number: List[int] = []
        self.physical_tags: List[int] = []
        self.bounding_curves_number: List[int] = []
        self.curves_tags: List[int] = []


class PhysicalEntitiesBase:
    """
    Attributes: \n
        `contours_number:` int \n
        `contour_idxs:` List[int] \n
        `contour_tag:` List[int] \n
        `surface_numbers:` int \n
        `surface_idxs:` List[int] \n
        `surface_tag:` List[int] \n
    Methods: \n
        `__init__():`
    """
    def __init__(self):
        self.contours_number: int = 0
        self.contour_idxs: List[int] = []
        self.contour_tag: List[int] = []
        self.surface_numbers: int = 0
        self.surface_idxs: List[int] = []
        self.surface_tag: List[int] = []


class GeometryBase:
    """
    Attributes: \n
        `points =` Points() \n
        `curves =` Curves() \n
        `surfaces =` Surfaces() \n
    Methods: \n
        `__init__():`
    """
    def __init__(self):
        self.points = Points()
        self.curves = Curves()
        self.surfaces = Surfaces()


class MeshingBase:
    """
    Attributes: \n
        `nodes_number:` int \n
        `nodes_entities_tag:` List[int] \n
        `nodes_coord:` List[List[float]] \n
        `elements_number:` int \n
        `elements_connection:` List[int] \n
    Methods: \n
        `__init__():`
    """
    def __init__(self):
        self.nodes_number: int = 0
        self.nodes_entities_tag: List[int] = []
        self.nodes_coord: List[List[float]] = []
        self.elements_number: int= 0
        self.elements_connection: List[int] = []
