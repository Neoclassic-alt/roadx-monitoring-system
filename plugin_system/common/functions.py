from shapely.geometry import Point, Polygon

def intersect_detecting(points, polygons):
    for polygon in polygons:
        # поиск пересечений точки с многоугольником
        polygon = Polygon(polygon)
        for point in points:
            point = Point(point)
            if polygon.contains(point):
                return True
    return False