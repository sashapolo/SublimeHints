class ArrowPanel(object):
    def __init__(self, arrows, ):
        self.arrows = arrows


class Arrow(object):
    def __init__(self, start_line, end_line):
        self.start = start_line
        self.end = end_line


class SimpleRouter(object):
    def __init__(self, arrows):
        self.arrows = arrows

    def route(self):
        self.arrows.sort(__sort_function__)
        width1 = self.__single_line_width__()
        width2 = self.__parallel_arrows_width__()
        self.width = max([width1, width2])

    def __sort_function__(x, y):
        if x.start < y.start:
            return -1
        elif x.start == y.start:
            if x.end < y.end:
                return -1
            elif x.end == y.end:
                return 0
            else:
                return 1
        else:
            return 1

    def __single_line_width__(self):
        maxcount = 0
        curcount = 0
        curpos = 0
        for arrow in self.arrows:
            if arrow.start == curpos:
                curcount += 1
            else:
                curpos = arrow.start
                curcount = 1
            if curcount > maxcount:
                    maxcount = curcount
        return 3 + (maxcount - 1) * 2

    def __parallel_arrows_width__(self):
        maxcount = 0
        curcount = 0
        curend = 0
        for arrow in self.arrows:
            if arrow.start <= curend:
                curcount += 1
                curend = arrow.end
            else:
                curend = arrow.end
                curcount = 1
            if curcount > maxcount:
                    maxcount = curcount
        return 3 + (maxcount - 1)
