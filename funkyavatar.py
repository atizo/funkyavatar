#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# funkyavatar - avatar creation gone funky
# http://labs.atizo.com/software/#funkyavatar
#
# Copyright (c) 2010 Atizo AG. All rights reserved.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
#

from StringIO import StringIO
import cairo
import math
import pyparsing
import colorsys
import hashlib
import sys


SHAPES = [
    {
        'svg_path': 'M 110.87651,1.4697337 C 91.002422,109.73123 134.75067,88.526513 200.30993,86.719128 279.03698,84.563143 316.53623,131.27114 327.39951,175.62954 339.95157,226.88378 301.7724,285.46005 212.86199,273.43099 123.95157,261.40194 3.1380145,167.78451 -0.52300238,113.91525 -3.2618575,73.614953 73.220343,52.200969 110.87651,1.4697337 z',
        'rotation_center': (200.0, 200.0),
        'translation': (0.0, -100.0),
    },
    {
        'svg_path': 'M 13.912833,268.78692 C 28.644067,339.98789 117.84607,325.24812 166.13559,186.12833 200.50847,87.101695 229.97094,53.547215 322.45036,1.1694915 275.80145,78.917676 270.89104,156.66586 303.62711,261.42131 c 29.0192,92.86141 -15.79457,111.28576 -88.3874,75.29298 -73.0216,-36.20537 -69.34513,-21.72051 -124.397095,25.37046 -57.539388,49.21869 -108.847458,17.18644 -76.929782,-93.29783 z',
        'rotation_center': (220.0, 250.0),
        'translation': (-220.0, -250.0),
    },
    {
        'svg_path': 'M 124.39709,-0.30024213 C 195.59807,36.527845 163.44038,180.61923 153.85956,214.93947 c -10.29388,36.87454 -4.092,71.20096 55.65134,94.11622 58.89685,22.59057 88.3874,12.27604 124.39709,37.64649 33.59834,23.67154 29.46247,78.56658 17.18644,91.66102 C 335.5448,391.71429 310.65321,371.44073 223.42373,363.07022 60.561742,347.52058 -47.467312,342.61017 18.823244,211.66586 79.32348,92.15923 126.10855,60.534344 124.39709,-0.30024213 z',
        'rotation_center': (90.0, 270.0),
        'translation': (-90.0, -70.0),
    },
]


class FunkyAvatar(object):
    def __init__(self, size):
        self.width = size
        self.height = size
        self.surface = None

    def generate(self, hash_value):
        if len(hash_value) != 32:
            raise Exception('hash value has not length 32')
        conf = self.__get_conf(hash_value)

        self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, self.width, self.height)

        cr = cairo.Context(self.surface)

        # white background
        cr.save()
        cr.rectangle(0.0, 0.0, float(self.width), float(self.height))
        cr.set_source_rgb(1.0, 1.0, 1.0);
        cr.fill()
        cr.restore()

        # scale to surface size (shapes have been created for 200x200)
        cr.scale(float(self.width)/200.0, float(self.height)/200.0)

        # create shape objects
        shapes = []
        for i in range(0, len(SHAPES)):
            tx1, ty1 = SHAPES[i]['translation']
            tx2, ty2 = conf['shape_translations'][i]
            s = Shape(SHAPES[i]['svg_path'], (tx1+tx2, ty1+ty2), SHAPES[i]['rotation_center'],
                conf['shape_angles'][i], conf['gradient_directions'][i],
                conf['colored_shape_index'] == i and conf['color'] or None)
            shapes.append(s)

        # put to colored shape on top
        s = shapes.pop(conf['colored_shape_index'])
        shapes.append(s)

        # draw shapes
        for s in shapes:
            cr.save()
            s.draw(cr)
            cr.restore()

    def save_png(self, filename):
        if self.surface:
            self.surface.write_to_png(filename)
            return True
        else:
            return False

    def get_png_data(self):
        if self.surface:
            s = StringIO()
            self.surface.write_to_png(s)
            return s.getvalue()
        else:
            return None

    def __get_conf(self, hash_value):
        hash_value = hash_value.lower()
        conf = {}

        color = int(hash_value[0:6], 16)
        r = (color >> 16) & 255
        g = (color >> 8) & 255
        b = color & 255
        conf['color'] = (r, g, b)

        conf['colored_shape_index'] = int(float(int(hash_value[6], 16))/16 * len(SHAPES))

        angles = int(hash_value[7:13], 16)
        conf['shape_angles'] = {
            0: float(angles >> 16 & 255)/255 * 2.0*math.pi,
            1: float(angles >> 8 & 255)/255 * 2.0*math.pi,
            2: float(angles & 255)/255 * 2.0*math.pi,
        }

        # variable shape translation between (-50, -50) and (50, 50)
        translations = int(hash_value[14:26], 16)
        tx1 = float(translations >> 40 & 255)/255 * 100 - 50
        ty1 = float(translations >> 32 & 255)/255 * 100 - 50
        tx2 = float(translations >> 24 & 255)/255 * 100 - 50
        ty2 = float(translations >> 16 & 255)/255 * 100 - 50
        tx3 = float(translations >> 8 & 255)/255 * 100 - 50
        ty3 = float(translations & 255)/255 * 100 - 50
        conf['shape_translations'] = {
            0: (tx1, ty1),
            1: (tx2, ty2),
            2: (tx3, ty3),
        }

        directions = int(hash_value[27:28], 16)
        conf['gradient_directions'] = {
            0: (directions >> 4 & 3) + 1,
            1: (directions >> 2 & 3) + 1,
            2: (directions & 3) + 1,
        }

        return conf


class Shape(object):
    def __init__(self, svg_path, translation, rotation_center, rotation_angle, gradient_direction, color=None):
        self.svg_path = svg_path
        self.translation = translation
        self.rotation_center = rotation_center
        self.rotation_angle = rotation_angle
        self.gradient_direction = gradient_direction
        self.color = color

    def draw(self, cr):
        tx, ty = self.translation
        cr.translate(tx, ty)
        self.__rotate(cr)
        self.__render_svg_path(cr)
        self.__set_gradient_pattern(cr, tx, ty)
        cr.fill()

    def __rotate(self, cr):
        cx, cy = self.rotation_center
        cr.translate(cx, cy)
        cr.rotate(self.rotation_angle)
        cr.translate(-cx, -cy)

    def __render_svg_path(self, cr):
        # define svg path grammar
        dot = pyparsing.Literal(".")
        comma = pyparsing.Literal(",").suppress()
        floater = pyparsing.Combine(pyparsing.Optional("-") + pyparsing.Word(pyparsing.nums) + dot + pyparsing.Word(pyparsing.nums))
        floater.setParseAction(lambda toks:float(toks[0]))
        couple = floater + comma + floater
        M_command = "M" + pyparsing.Group(couple)
        m_command = "m" + pyparsing.Group(couple)
        C_command = "C" + pyparsing.OneOrMore(pyparsing.Group(couple + couple + couple))
        c_command = "c" + pyparsing.OneOrMore(pyparsing.Group(couple + couple + couple))
        L_command = "L" + pyparsing.OneOrMore(pyparsing.Group(couple))
        l_command = "l" + pyparsing.OneOrMore(pyparsing.Group(couple))
        Z_command = pyparsing.Literal("Z") ^ pyparsing.Literal("z")
        svgcommand = M_command | m_command | C_command | c_command | L_command | l_command | Z_command
        phrase = pyparsing.OneOrMore(pyparsing.Group(svgcommand))

        tokens = phrase.parseString(self.svg_path)
        for token in tokens:
            command = token[0]
            if len(token) > 1:
                values = token[1:]

            if command == 'M':
                v = values[0]
                cr.move_to(v[0], v[1])
            elif command == 'C':
                for v in values:
                    cr.curve_to(v[0], v[1], v[2], v[3], v[4], v[5])
            elif command == 'c':
                for v in values:
                    cr.rel_curve_to(v[0], v[1], v[2], v[3], v[4], v[5])
            elif command == 'L':
                for v in values:
                    cr.line_to(v[0], v[1])
            elif command == 'l':
                for v in values:
                    cr.rel_line_to(v[0], v[1])
            elif command == 'z' or command == 'Z':
                cr.close_path()

    def __set_gradient_pattern(self, cr, tx, ty):
        # use gray if no color is given
        r1, g1, b1 = 0.2, 0.2, 0.2
        r2, g2, b2 = 0.8, 0.8, 0.8

        if self.color:
            r, g, b = self.color
            r, g, b = float(r)/255, float(g)/255, float(b)/255

            h, s, v = colorsys.rgb_to_hsv(r, g, b)
            r1, g1, b1 = colorsys.hsv_to_rgb(h, s, min(v+0.2, 1.0))

            h, s, v = colorsys.rgb_to_hsv(r, g, b)
            r2, g2, b2 = colorsys.hsv_to_rgb(h, s, max(v-0.2, 0))

        if self.gradient_direction == 1:
            pat = cairo.LinearGradient(0.0, 0.0, 0.0, 200.0-ty)
        elif self.gradient_direction == 2:
            pat = cairo.LinearGradient(0.0, 200.0-ty, 0.0, 0.0)
        elif self.gradient_direction == 3:
            pat = cairo.LinearGradient(0.0, 0.0, 200.0-tx, 0.0)
        else:
            pat = cairo.LinearGradient(200.0-tx, 0.0, 0.0, 0.0)

        pat.add_color_stop_rgba(0, r2, g2, b2, 0.8)
        pat.add_color_stop_rgba(1, r1, g1, b1, 0.8)
        cr.set_source(pat)


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print 'Usage: %s size email' % sys.argv[0]
        sys.exit(1)

    size = int(sys.argv[1])
    email = sys.argv[2].lower()

    a = FunkyAvatar(size)

    hash_value = hashlib.md5(email).hexdigest()
    a.generate(hash_value)

    a.save_png('avatar-%d-%s.png' % (size, email))

    # alternatively you can use:
    # data =  a.get_png_data()
