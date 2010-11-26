#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Atizo - The Open Innovation Platform
# http://www.atizo.com/
#
# Copyright (c) 2008-2010 Atizo AG. All rights reserved.
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

import cairo
import math
import re
import colorsys
import hashlib
import sys

class FunkyAvatar(object):
    def __init__(self, width=200, height=200):
        self.width = width
        self.height = height
        self.surface = None

    def generate(self, hash_value):
        if self.surface:
            self.surface.destroy()
        self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, self.width, self.height)

        c = cairo.Context(self.surface)
        c.scale(self.width, self.height) # Normalizing the canvas

        c.rectangle(0, 0, 1, 1)
        c.set_source_rgb(1, 1, 1);
        c.fill()

        c.save()
        c.translate(0.1, 0.1)
        c.rotate(0*math.pi)
        c.scale(1, 1)
        self.__draw_shape1(c)
        self.__set_gradient_pattern(c, hash_value, 1)
        c.fill()
        c.restore()

        c.save()
        c.translate(0.3, 0.1)
        c.rotate(0*math.pi)
        c.scale(1, 1)
        self.__draw_shape2(c)
        self.__set_gradient_pattern(c, hash_value, 2)
        c.fill()
        c.restore()

        c.save()
        c.translate(0.7, 0.1)
        c.rotate(0*math.pi)
        c.scale(1, 1)
        self.__draw_shape3(c)
        self.__set_gradient_pattern(c, hash_value, 3)
        c.fill()
        c.restore()

    def __get_color(self, hash_value, index):
        if len(hash_value) != 32:
            raise Exception('hash value not of length 32')
        if index < 0 or index > 3:
            raise Exception('index must be between 0 and 3')

        colors = re.findall('([\da-f]{6})', hash_value, re.IGNORECASE)

        color = int(colors[index], 16)
        r = (color >> 16) & 255
        g = (color >> 8) & 255
        b = color & 255

        return r, g, b

    def __set_gradient_pattern(self, c, hash_value, index):
        r, g, b = self.__get_color(hash_value, index)
        r, g, b = float(r)/255, float(g)/255, float(b)/255

        # TODO: why isn't v=1.0 white?
        h, s, v = colorsys.rgb_to_hsv(r, g, b)
        r1, g1, b1 = colorsys.hsv_to_rgb(h, s, v+0.4)

        h, s, v = colorsys.rgb_to_hsv(r, g, b)
        r2, g2, b2 = colorsys.hsv_to_rgb(h, s, v-0.4)

        # TODO: gradient has to be aligned
        pat = cairo.LinearGradient(0.0, 0.0, 0.0, 1.0)
        pat.add_color_stop_rgba(0, r2, g2, b2, 0.8)
        pat.add_color_stop_rgba(1, r1, g1, b1, 0.8)
        c.set_source(pat)

    def __draw_shape1(self, c):
        c.move_to(0, 0)
        c.arc(0.2, 0.1, 0.1, -math.pi/2, 0) # Arc(cx, cy, radius, start_angle, stop_angle)
        c.line_to(0.5, 0.1) # Line to (x,y)
        c.curve_to(0.5, 0.2, 0.5, 0.4, 0.2, 0.8) # Curve(x1, y1, x2, y2, x3, y3)
        c.close_path()

    def __draw_shape2(self, c):
        c.move_to(0, 0)
        c.arc(0.2, 0.1, 0.1, -math.pi/2, 0) # Arc(cx, cy, radius, start_angle, stop_angle)
        c.line_to(0.5, 0.1) # Line to (x,y)
        c.curve_to(0.5, 0.2, 0.5, 0.4, 0.2, 0.8) # Curve(x1, y1, x2, y2, x3, y3)
        c.close_path()

    def __draw_shape3(self, c):
        c.move_to(0, 0)
        c.arc(0.2, 0.1, 0.1, -math.pi/2, 0) # Arc(cx, cy, radius, start_angle, stop_angle)
        c.line_to(0.5, 0.1) # Line to (x,y)
        c.curve_to(0.5, 0.2, 0.5, 0.4, 0.2, 0.8) # Curve(x1, y1, x2, y2, x3, y3)
        c.close_path()

    def save_to_file(self, filename):
        if self.surface:
            self.surface.write_to_png(filename)
            return True
        else:
            return False


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print 'Usage: %s email' % sys.argv[0]
        sys.exit(1)

    email = sys.argv[1].lower()
    hash_value = hashlib.md5(email).hexdigest()

    a = FunkyAvatar()
    a.generate(hash_value)
    a.save_to_file('avatar.png')
