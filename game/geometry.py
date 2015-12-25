class Point(object):
    def __init__(self, x, y):
        self._x = x
        self._y = y
    
    @property
    def x(self):
        return self._x
    
    @property
    def y(self):
        return self._y
    
    def __getitem__(self, index):
        if index == 0:
            return self._x
        if index == 1:
            return self._y
        return super(Point, self).__getitem__(index)
    
    def __iter__(self):
        yield self._x
        yield self._y
    
    def manhattan_distance_to_point(self, point):
        dist_x = abs(self.x - point.x)
        dist_y = abs(self.y - point.y)
        return max(dist_x, dist_y)


class Rect(object):
    def __init__(self, x, y, width, height):
        self._x1 = x
        self._x2 = x + width
        self._y1 = y
        self._y2 = y + height
    
    def __hash__(self):
        return hash((self._x1, self._x2, self._y1, self._y2))
    
    def __eq__(self, other):
        return ((self._x1, self._x2, self._y1, self._y2) ==
                (other._x1, other._x2, other._y1, other._y2))
    
    @property
    def x(self):
        return self._x1
    
    @property
    def y(self):
        return self._y1
    
    @property
    def width(self):
        return self._x2 - self._x1
    
    @property
    def height(self):
        return self._y2 - self._y1
    
    @property
    def center(self):
        return Point((self._x1 + self._x2) / 2.0,
                     (self._y1 + self._y2) / 2.0)
    
    def __repr__(self):
        return "Rect(%f, %f, %f, %f)" % (self.x, self.y, self.width, self.height)
    
    def contains_point(self, point):
        px, py = point
        min_x, max_x = sorted([self._x1, self._x2])
        min_y, max_y = sorted([self._y1, self._y2])
        if min_x < px <= max_x and min_y < py < max_y:
            return True
        return False
    
    @property
    def points(self):
        return (Point(self._x1, self._y1), Point(self._x1, self._y2),
                Point(self._x2, self._y1), Point(self._x2, self._y2))
    
    def manhattan_distance_to_point(self, point):
        if self.contains_point(point):
            return 0.0
        px, py = point
        
        dists = (p.manhattan_distance_to_point(point) for p in self.points)
        return min(dists)
    
    def manhattan_distance_to_rect(self, other_rect):
        dists = [self.manhattan_distance_to_point(point)
                 for point in other_rect.points]
        return min(dists)
    
    def union(self, other_rect):
        points = self.points + other_rect.points
        x = min([point.x for point in points])
        y = min([point.y for point in points])
        w = max([point.x for point in points]) - x
        h = max([point.y for point in points]) - y
        return Rect(x, y, w, h)
            

def get_rects_containing_rects(rects, threshold):
    rects = list(rects)
    while True:
        found_merge = False
        for i_one, rect_one in enumerate(rects):
            for i_two, rect_two in enumerate(rects):
                if i_one == i_two:
                    continue
                if rect_one.manhattan_distance_to_rect(rect_two) > threshold:
                    continue
                new_rect = rect_one.union(rect_two)
                found_merge = True
                break
            if found_merge:
                break
        if found_merge:
            del rects[max(i_one, i_two)]
            del rects[min(i_one, i_two)]
            rects.append(new_rect)
        else:
            return rects
                
    
def get_rects_containing_points(points, threshold):
    rects = [Rect(point[0], point[1], 1, 1) for point in points]
    return get_rects_containing_rects(rects, threshold)


if __name__ == '__main__':
    origin = Point(0, 0)
    assert origin.manhattan_distance_to_point(Point(0, 0)) == 0
    assert origin.manhattan_distance_to_point(Point(1, 0)) == 1
    assert origin.manhattan_distance_to_point(Point(2, 1)) == 2
    
    rect = Rect(-1, -1, 2, 2)
    assert rect.contains_point(origin)
    assert not rect.contains_point((5, 0))
    
    assert rect.manhattan_distance_to_point(origin) == 0.0
    assert rect.manhattan_distance_to_point(Point(-1, -1)) == 0.0
    
    points = (0, 0), (0, 1), (-1, -1), (10, 10), (10, 11), (9, 11)
    points = [Point(*point) for point in points]
    rects = get_rects_containing_points(points, threshold=2)
    print set(rects)
    assert set(rects) == set([Rect(-1, -1, 1, 2), Rect(9, 10, 1, 1)])
    rects = get_rects_containing_points(points, threshold=0)
    assert set(rects) == set([Rect(point.x, point.y, 0, 0) for point in points])
