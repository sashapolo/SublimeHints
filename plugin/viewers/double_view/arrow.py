import string as string_module

class ArrowPanel(object):
    def __init__(self, arrows, height):
        self.arrows = arrows
        self.height = height
        self.router = SimpleRouter(self.arrows)
        self.routed = self.router.route()
        self.width = self.router.width
        self.drawer = SimpleDrawer(self.routed, self.width, self.height)
        self.content = self.drawer.draw()

    def get_content(self):
        return self.content


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
        self.start = [arrow.start, 0]
        self.end = [arrow.end, 0]
        self.vertical = 0


class SimpleRouter(object):
    def __init__(self, arrows):
        self.arrows = map(RoutedArrow, arrows)

    class RoutingInfo(object):
        def __init__(self, arrow):
            self.arrow = arrow


    def route(self):
        self.arrows.sort(SimpleRouter.__sort_function__)
        width1 = self.__same_line__()
        width2 = self.__parallel_arrows__()
        self.width = max([width1, width2])
        for arrow in self.arrows:
            arrow.end[1] = self.width - 1
        return self.arrows

    @staticmethod
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
            routing = SimpleRouter.RoutingInfo(arrow)
            routing.same_line_number = groups_size[curpos] 
            routings.append(routing)
        maxcount = max(groups_size.values())
        
        #print groups_size
        #print maxcount
        
        for routing in routings:
            size = groups_size[routing.arrow.start[0]]
            number = routing.same_line_number
            routing.arrow.start[1] = 2 * (size - number)

        self.arrow = map(lambda x: x.arrow, routings)
        return 3 + (maxcount - 1) * 2

    def __parallel_arrows__(self):
        curend = -1
        groups_size = dict()
        i = -1
        routings = []
        for arrow in self.arrows:
            if arrow.start[0] <= curend:
                groups_size[i] += 1
                curend = arrow.end[0]
            else:
                curend = arrow.end[0]
                i += 1
                groups_size[i] = 1
            routing = SimpleRouter.RoutingInfo(arrow)
            routing.group_number = i
            routing.parallel_number = groups_size[i]
            routings.append(routing)            
        maxcount = max(groups_size.values())

        for routing in routings:
            size = groups_size[routing.group_number]
            number = routing.parallel_number
            vertical = 1 + size - number
            if vertical <= routing.arrow.start[1]:
                vertical = routing.arrow.start[1] + 1
            routing.arrow.vertical = vertical

        self.arrow = map(lambda x: x.arrow, routings)
        return 3 + (maxcount - 1)


class Symbols(object):
    hor = u"\u2500"
    ver = u"\u2502"
    arrow = u"<"
    left_angle = u"\u2510"
    right_angle = u"\u2514"  


class SimpleDrawer(object):
    def __init__(self, routed, width, height):
        self.routed = routed
        self.width = width
        self.content = []
        for i in range(height):
            self.content.append(" " * width)

    def draw(self):
        for arrow in self.routed:
            self.__draw_arrow__(arrow)
        return string_module.join(self.content, "\n")

    def __draw_arrow__(self, arrow):
        #print arrow.start, arrow.end, arrow.vertical
        hshift = arrow.start[1]
        vshift = arrow.start[0]
        hsize = arrow.end[1] - arrow.start[1] + 1
        vsize = arrow.end[0] - arrow.start[0] + 1
        
        if vsize == 1:
            arrow_string = Symbols.arrow + Symbols.hor * (hsize - 1)
            string = self.content[vshift]
            string = string[:hshift] + arrow_string + string[hshift + hsize:]
            self.content[vshift] = string
        else:
            first_hsize = arrow.vertical - hshift + 1
            first_string = Symbols.arrow + (Symbols.hor * (first_hsize - 2)) + Symbols.left_angle
            last_hsize = hsize - first_hsize + 1
            last_string = Symbols.right_angle + (Symbols.hor * (last_hsize - 1))
            string = self.content[vshift]
            string = string[:hshift] + first_string + string[hshift + first_hsize:]
            self.content[vshift] = string
            string = self.content[vshift + vsize - 1]
            string = string[:hshift + first_hsize - 1] + last_string + string[hshift + hsize:]
            self.content[vshift + vsize - 1] = string
            for i in range(vshift + 1, vshift + vsize - 1):
                self.content[i] = self.content[i][:arrow.vertical] + Symbols.ver + self.content[i][arrow.vertical + 1:]