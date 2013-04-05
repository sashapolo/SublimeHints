class ArrowPanel(object):
    def __init__(self, arrows, ):
        self.arrows = arrows


class Arrow(object):
    def __init__(self, start_line, end_line):
        self.start = start_line
        self.end = end_line

class RoutedArrow(object):
    def __init__(self, arrow):
        """
        start - (row, col) coordinates of arrow start point
        end - (row. col) coordinates of arrow end point
        vertical - number of column with vertical line of arrow
        """
        self.start = (arrow.start, 0)
        self.end = (arrow.end, 0)
        self.vertical = 0

class SimpleRouter(object):
    def __init__(self, arrows):
        self.arrows = map(RoutedArrow, arrows)
        
    class RoutingInfo(object):
        def __init__(self, arrow):
            self.arrow = arrow


    def route(self):
        self.arrows.sort(__sort_function__)
        width1 = self.__same_line__()
        width2 = self.__parallel_arrows__()
        self.width = max([width1, width2])

    def __sort_function__(x, y):
        if x.start[0] < y.start[0]:
            return -1
        elif x.start[0] == y.start[0]:
            if x.end[0] < y.end[0]:
                return -1
            elif x.end[0] == y.end[0]:
                return 0
            else:
                return 1
        else:
            return 1

    def __same_line__(self):
        curpos = -1
        groups_size = dict()
        routings = []
        for arrow in self.arrows:
            if arrow.start[0] == curpos:
                groups_size[curpos] += 1                   
            else:
                curpos = arrow.start[0]
                groups_size[curpos] = 1
            routing = RoutingInfo(arrow)
            routing.same_line_number = groups_size[curpos] 
            routings.append(routing)
        maxcount = max(groups_size, key = lambda x: groups_size[x])
        
        for routing in routings:
            size = groups_size[routing.arrow.start[0]]
            number = routing.same_line_number
            routing.arrow.start[1] = 2 * (size - number)

        self.arrow = map(lambda x: x.arrow, routings)
        return 3 + (maxcount - 1) * 2

    def __parallel_arrows__(self):
        curend = -1
        groups_size = dict()
        i = 0
        routings = []
        for arrow in self.arrows:
            if arrow.start[0] <= curend:
                groups_size[i] += 1
                curend = arrow.end[0]
            else:
                curend = arrow.end[0]
                groups_size[i] = 1
            routing = RoutingInfo(arrow)
            routing.group_number = i
            routing.parallel_number = groups_size[i]
            routings.append(routing)
            i += 1
        maxcount = max(groups_size, key = lambda x: groups_size[x])

        for routing in routings:
            size = groups_size[routing.group_number]
            number = routing.parallel_number
            vertical = 1 + size - number
            if vertical <= routing.arrow.start[1]:
                vertical = routing.arrow.start[1] + 1
            routing.arrow.vertical = vertical

        self.arrow = map(lambda x: x.arrow, routings)
        return 3 + (maxcount - 1)
