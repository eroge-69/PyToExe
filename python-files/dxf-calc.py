#!/usr/bin/env python3
'''
Usage: %s <task-directory>

task-directory      Contains DXF-files. Name of the directory consists of order
                    number and customer name. For expample: 123-customer.

The result of order processing will be in the directory in the file result.xlsx.
'''

import math
import os
import sys

import ezdxf
from PIL import Image, ImageDraw, ImageOps
from xlsxwriter import Workbook

EQUALITY_RADIUS = 0.1
LINE_WIDTH = 1


class Entity:
    def __init__(self):
        self.start = (0, 0)
        self.end = (0, 0)
        self.box = (0, 0, 0, 0)
        self.line_length = 0
        self.closed = True

    def draw(self, im, shift_x, shift_y):
        pass

    def __str__(self):
        return "%s<(%.4f, %.4f), (%.4f, %.4f), %.4f>" % (
            self.__class__.__name__,
            self.start[0], self.start[1],
            self.end[0], self.end[1],
            self.line_length
        )


class Arc(Entity):
    def __init__(self, arc):
        self.center = arc.dxf.center[:2]
        self.radius = arc.dxf.radius
        self.start_angle = arc.dxf.start_angle % 360
        self.end_angle = arc.dxf.end_angle % 360
        if self.start_angle > self.end_angle:
            self.start_angle = self.start_angle - 360

        self.start = (
            round(self.center[0] + self.radius * math.cos(math.radians(self.start_angle)), 4),
            round(self.center[1] + self.radius * math.sin(math.radians(self.start_angle)), 4)
        )
        self.end = (
            round(self.center[0] + self.radius * math.cos(math.radians(self.end_angle)), 4),
            round(self.center[1] + self.radius * math.sin(math.radians(self.end_angle)), 4)
        )

        box_x = [self.start[0], self.end[0]]
        box_y = [self.start[1], self.end[1]]
        if self.start_angle < 0 and self.end_angle > 0:  # Дуга проходит 0 градусов
            box_x.append(self.center[0] + self.radius)
        if self.start_angle <= 90 and 90 <= self.end_angle:  # Дуга проходит через 90 градусов
            box_y.append(self.center[1] + self.radius)
        if self.start_angle <= 180 and 180 <= self.end_angle:  # Дуга проходит через 180 градусов
            box_x.append(self.center[0] - self.radius)
        if self.start_angle <= 270 and 270 <= self.end_angle:  # Дуга проходит через 270 градусов
            box_y.append(self.center[1] - self.radius)
        box_x.sort()
        box_y.sort()
        self.box = [
            box_x[0],
            box_y[0],
            box_x[-1],
            box_y[-1],
        ]

        arc_angle = self.end_angle - self.start_angle
        self.line_length = math.radians(arc_angle) * self.radius
        self.closed = False

    def draw(self, draw, shift_x, shift_y, coeff):
        box = [
            round((self.center[0] - self.radius + shift_x) * coeff),
            round((self.center[1] - self.radius + shift_y) * coeff),
            round((self.center[0] + self.radius + shift_x) * coeff),
            round((self.center[1] + self.radius + shift_y) * coeff),
        ]
        draw.arc(box, self.start_angle, self.end_angle, 0, LINE_WIDTH)

    def __str__(self):
        return "%s<(%.4f, %.4f), (%.4f, %.4f), %.4f / %i (%i, %i)>" % (
            self.__class__.__name__,
            self.start[0], self.start[1],
            self.end[0], self.end[1],
            self.line_length,
            self.end_angle - self.start_angle,
            self.start_angle, self.end_angle,
        )


class Circle(Entity):
    def __init__(self, circle):
        self.center = circle.dxf.center[:2]
        self.radius = circle.dxf.radius

        self.start = (
            self.center[0] + self.radius,
            self.center[1]
        )
        self.end = self.start

        self.box = [
            self.center[0] - self.radius,
            self.center[1] - self.radius,
            self.center[0] + self.radius,
            self.center[1] + self.radius,
        ]

        self.line_length = 2 * math.pi * self.radius
        self.closed = True

    def draw(self, draw, shift_x, shift_y, coeff):
        box = self.box.copy()
        box[0] = round((box[0] + shift_x) * coeff)
        box[1] = round((box[1] + shift_y) * coeff)
        box[2] = round((box[2] + shift_x) * coeff)
        box[3] = round((box[3] + shift_y) * coeff)
        draw.ellipse(box, None, 0, LINE_WIDTH)


class Line(Entity):
    def __init__(self, line):
        self.start = line.dxf.start[:2]
        self.end = line.dxf.end[:2]
        self.box = [
            min(self.start[0], self.end[0]),
            min(self.start[1], self.end[1]),
            max(self.start[0], self.end[0]),
            max(self.start[1], self.end[1]),
        ]
        self.line_length = math.sqrt(
            (self.start[0] - self.end[0]) ** 2 +
            (self.start[1] - self.end[1]) ** 2
        )
        self.closed = False

    def draw(self, draw, shift_x, shift_y, coeff):
        box = self.box.copy()
        box[0] = round((self.start[0] + shift_x) * coeff)
        box[1] = round((self.start[1] + shift_y) * coeff)
        box[2] = round((self.end[0] + shift_x) * coeff)
        box[3] = round((self.end[1] + shift_y) * coeff)
        draw.line(box, 0, LINE_WIDTH)


class Spline(Entity):
    def __init__(self, spline):
        self.control_points = cp = spline.get_control_points()
        self.start = cp[0][:2]
        self.end = cp[-1][:2]
        self.closed = bool(spline.dxf.flags & 1)

        self.line_length = 0
        for i in range(1, len(cp)):
            self.line_length += math.sqrt(
                (cp[i-1][0] - cp[i][0]) ** 2 +
                (cp[i-1][1] - cp[i][1]) ** 2
            )

        if self.closed:
            self.line_length = math.sqrt(
                (self.start[0] - self.end[0]) ** 2 +
                (self.start[1] - self.end[1]) ** 2
            )

        box_x = [p[0] for p in cp]
        box_y = [p[1] for p in cp]
        box_x.sort()
        box_y.sort()
        self.box = [
            box_x[0],
            box_y[0],
            box_x[-1],
            box_y[-1],
        ]

    def draw(self, draw, shift_x, shift_y, coeff):
        for i in range(1, len(self.control_points)):
            line = (
                round((self.control_points[i-1][0] + shift_x) * coeff),
                round((self.control_points[i-1][1] + shift_y) * coeff),
                round((self.control_points[i][0] + shift_x) * coeff),
                round((self.control_points[i][1] + shift_y) * coeff)
            )
            draw.line(line, 0, LINE_WIDTH, 'curve')

        if self.closed:
            line = (
                round((self.end[0] + shift_x) * coeff),
                round((self.end[1] + shift_y) * coeff),
                round((self.start[0] + shift_x) * coeff),
                round((self.start[1] + shift_y) * coeff)
            )
            draw.line(line, 0, LINE_WIDTH, 'curve')

    def __str__(self):
        return "%s<(%.4f, %.4f), (%.4f, %.4f), %.4f>" % (
            self.__class__.__name__,
            self.start[0], self.start[1],
            self.start[0] if self.closed else self.end[0],
            self.start[1] if self.closed else self.end[1],
            self.line_length
        )


def points_equal(p1, p2):
    return math.sqrt(
        (p1[0] - p2[0]) ** 2 +
        (p1[1] - p2[1]) ** 2
    ) <= EQUALITY_RADIUS


def find_next(entities, point):
    for i in range(len(entities)):
        e = entities[i]

        if points_equal(e.start, point):
            entities.pop(i)
            return e.end, e

        if points_equal(e.end, point):
            entities.pop(i)
            return e.start, e

    return point, False


def process_dxf(dxf_file_name):
    print('===', dxf_file_name, '===')
    dwg = ezdxf.readfile(dxf_file_name)
    modelspace = dwg.modelspace()

    contours = [Line(l) for l in modelspace.query('LINE')]
    contours += [Arc(a) for a in modelspace.query('ARC')]
    closed_contours = [[Circle(c)] for c in modelspace.query('CIRCLE')]

    for s in modelspace.query('SPLINE'):
        spline = Spline(s)
        if spline.closed:
            closed_contours.append(spline)
        else:
            contours.append(spline)

    open_contours = []

    while len(contours):
        entity = contours.pop(0)
        next_point = entity.end
        contour = []
        while entity:
            contour.append(entity)
            next_point, entity = find_next(contours, next_point)

        if points_equal(next_point, contour[0].start):
            closed_contours.append(contour)
        else:
            open_contours.append(contour)

    cut_length = sum([sum([c.line_length for c in contour]) for contour in contours])
    cut_length += sum([sum([c.line_length for c in contour]) for contour in closed_contours])

    print(
        'Open contours: %s\n'
        'Closed contours: %s\n'
        'Length: %s' % (
            len(open_contours),
            len(closed_contours),
            round(cut_length, 2)
        )
    )

    box_x = []
    box_y = []
    for contours in (open_contours, closed_contours):
        for contour in contours:
            for entity in contour:
                box_x.append(entity.box[0])
                box_y.append(entity.box[1])
                box_x.append(entity.box[2])
                box_y.append(entity.box[3])

    box_x.sort()
    box_y.sort()
    box = (
        box_x[0],
        box_y[0],
        box_x[-1],
        box_y[-1],
    )

    if (box[2] - box[0] + 20) >= (box[3] - box[1] + 20):
        coeff = min(180 / (box[2] - box[0] + 20), 90 / (box[3] - box[1] + 20))
    else:
        coeff = min(180 / (box[3] - box[1] + 20), 90 / (box[2] - box[0] + 20))

    size = (round((box[2] - box[0] + 20) * coeff), round((box[3] - box[1] + 20) * coeff))

    im = Image.new('1', size, 1)
    draw = ImageDraw.Draw(im)
    for contours in (open_contours, closed_contours):
        for contour in contours:
            for entity in contour:
                entity.draw(draw, 10 - box[0], 10 - box[1], coeff)

    im = ImageOps.flip(im)
    if size[0] < size[1]:
        im = im.rotate(270, expand=True)

    img_name = os.path.splitext(dxf_file_name)[0] + '.png'
    im.save(img_name, 'PNG')
    print('-' * 20)

    return img_name, cut_length, len(open_contours) + len(closed_contours), box, im.size


def main():
    if len(sys.argv) != 2:
        print(__doc__ % sys.argv[0])
        exit(2)

    if not os.path.isdir(sys.argv[1]):
        print("'%s' is not a directory" % sys.argv[1])
        exit(os.EX_DATAERR)

    wb = Workbook(os.path.join(sys.argv[1], 'result.xlsx'))
    ws = wb.add_worksheet()
    bold = wb.add_format({'bold': True, 'valign': 'top'})
    hstyle = wb.add_format({'bold': True, 'align': 'center', 'valign': 'top'})
    gstyle = wb.add_format({'align': 'right', 'valign': 'top'})
    top = wb.add_format({'valign': 'top'})
    order_n, customer = os.path.basename(sys.argv[1]).split('(', 1)
    ws.write(0, 1, '№ заказа: %s' % order_n.strip(), bold)
    ws.write(0, 3, 'Заказчик: %s' % customer[:-1].strip(), bold)

    header = (
        "№",
        "Название",
        "Эскиз",
        "Толщина\n(мм)",
        "Ширина\n(мм)",
        "Высота\n(мм)",
        "Металл",
        "Кол-во",
        "Длина реза\n(мм)",
        "Кол-во\nврезок",
        "Гибка",
        "Кол-во\nгибов",
        "Цена\nгиба",
        "Итого"
    )
    col_width = [len(h.split('\n', 1)[0]) for h in header]
    row_height = []
    for i in range(len(header)):
        ws.write_string(2, i, header[i], hstyle)

    ws.set_row(2, 24)

    with os.scandir(sys.argv[1]) as directory:
        n = 3
        g = set(['г', 'g'])
        for entry in directory:
            if not entry.is_file() or not entry.name.lower().endswith('.dxf'):
                continue

            img_name, cut_length, cut_count, box, im_size = process_dxf(entry.path)
            fname = os.path.split(entry.path)[1]
            fname_parts = os.path.splitext(fname)[0].split('_')

            ws.write(n, 0, n - 2, top)

            ws.write(n, 1, fname_parts[2], top)  # Название
            col_width[1] = max(col_width[1], len(fname_parts[2]))

            ws.insert_image(n, 2, img_name, {'x_offset': 2, 'y_offset': 2, 'x_scale': 1.1, 'y_scale': 1.1})  # Изображение
            row_height.append(max(im_size[1], 20))

            ws.write(n, 3, round(float(fname_parts[0].replace(',', '.')), 2), top)  # Толщина
            col_width[3] = max(col_width[3], len(fname_parts[0]))

            ws.write(n, 4, round(box[2] - box[0], 2), top)  # Ширина
            col_width[4] = max(col_width[4], len(str(round(box[2] - box[0], 2))))

            ws.write(n, 5, round(box[3] - box[1], 2), top)  # Высота
            col_width[5] = max(col_width[5], len(str(round(box[3] - box[1], 2))))

            ws.write(n, 6, fname_parts[1], gstyle)  # Металл
            col_width[6] = max(col_width[6], len(fname_parts[1]))

            ws.write(n, 7, int(fname_parts[3]), top)  # Количество
            col_width[7] = max(col_width[7], len(fname_parts[3]))

            ws.write(n, 8, round(cut_length, 2), top)  # Длина реза
            col_width[8] = max(col_width[8], len(str(round(cut_length, 2))))

            ws.write(n, 9, cut_count, top)  # Количество резов
            col_width[9] = max(col_width[9], len(str(cut_count)))

            # Гибка (да/нет)
            ws.write(n, 10, 'да' if fname_parts[-1].lower() in g else 'нет', gstyle)

            n += 1

        col_width[0] = max(len(str(n)), 2)
        col_width[2] = 26
        for i in range(len(col_width)):
            ws.set_column(i, i, col_width[i] + 2)

        for i in range(len(row_height)):
            ws.set_row(i + 3, row_height[i] * 0.8 + 5.5)

    wb.close()

    return 0

if __name__ == '__main__':
    main()
