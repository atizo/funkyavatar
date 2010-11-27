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
        if len(hash_value) != 32:
            raise Exception('hash value has not length 32')
        conf = self.__get_conf(hash_value)

        if self.surface:
            self.surface.destroy()
        self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, self.width, self.height)

        cr = cairo.Context(self.surface)
        # cr.scale(self.width/200, self.height/200)
        cr.translate(300, 300)

        # white background
        cr.save()
        cr.rectangle(0, 0, 200, 200)
        cr.set_source_rgb(1, 1, 1);
        cr.fill()
        cr.restore()

        # shape 1
        cr.save()
        x = 200
        y = 200
        cr.translate(x, y)
        cr.rotate(conf['shape1_angle'])
        cr.translate(-x, -y)

        self.__draw_shape1(cr)
        self.__set_gradient_pattern(cr, conf['color'])
        cr.fill()
        cr.restore()

        # shape 2
        # cr.save()
        # cr.translate(0.3, 0.1)
        # cr.rotate(0*math.pi)
        # cr.scale(1, 1)
        # self.__draw_shape2(cr)
        # self.__set_gradient_pattern(cr, hash_value)
        # cr.fill()
        # cr.restore()

        # shape 3
        # cr.save()
        # cr.translate(0.7, 0.1)
        # cr.rotate(0*math.pi)
        # cr.scale(1, 1)
        # self.__draw_shape3(cr)
        # self.__set_gradient_pattern(cr, hash_value)
        # cr.fill()
        # cr.restore()

        cr.save()
        cr.rectangle(-10, -10, 220, 220)
        cr.set_source_rgb(0, 0, 0);
        cr.set_line_width(20)
        cr.stroke()
        cr.restore()

    def __get_conf(self, hash_value):
        hash_value = hash_value.lower()
        conf = {}

        color = int(hash_value[0:6], 16)
        r = (color >> 16) & 255
        g = (color >> 8) & 255
        b = color & 255
        conf['color'] = (r, g, b)

        conf['colored_shape'] = int(float(int(hash_value[6], 16))/16 * 3)

        angles = int(hash_value[7:19], 16)
        conf['shape1_angle'] = float(angles >> 24 & 4095)/4095 * 2.0*math.pi
        conf['shape2_angle'] = float(angles >> 12 & 4095)/4095 * 2.0*math.pi
        conf['shape3_angle'] = float(angles & 4095)/4095 * 2.0*math.pi

        print conf
        return conf

    def __set_gradient_pattern(self, cr, color):
        r, g, b = color
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
        cr.set_source(pat)

    def __draw_shape1(self, cr):
        cr.move_to(260.00001,95.5)
        cr.rel_curve_to(56.55496,10.48079, 82.61749,54.65247, 77.85714,112.14286)
        cr.rel_curve_to(-4.64286,56.07142, -103.65592,87.85722, -186.42857,48.21432)
        cr.curve_to(53.02906, 208.72994, 3.36238, 147.56320, 7.47469, 110.89573)
        cr.curve_to(12.215894, 68.62078, 50.560167, 80.61123, 118.21429, 0.5)
        cr.rel_curve_to(-7.08555,41.02475, -6.81073,73.60264, 11.26333,84.55833)
        cr.rel_curve_to(31.16131,18.88859, 69.25437,-0.91254, 130.52239,10.44167)
        cr.close_path()

    def __draw_shape2(self, cr):
        cr.move_to(0, 0)
        cr.arc(0.2, 0.1, 0.1, -math.pi/2, 0) # Arcr(cx, cy, radius, start_angle, stop_angle)
        cr.line_to(0.5, 0.1) # Line to (x,y)
        cr.curve_to(0.5, 0.2, 0.5, 0.4, 0.2, 0.8) # Curve(x1, y1, x2, y2, x3, y3)
        cr.close_path()

    def __draw_shape3(self, cr):
        cr.move_to(0, 0)
        cr.arc(0.2, 0.1, 0.1, -math.pi/2, 0) # Arc(cx, cy, radius, start_angle, stop_angle)
        cr.line_to(0.5, 0.1) # Line to (x,y)
        cr.curve_to(0.5, 0.2, 0.5, 0.4, 0.2, 0.8) # Curve(x1, y1, x2, y2, x3, y3)
        cr.close_path()

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

    a = FunkyAvatar(1000, 1000)
    a.generate(hash_value)
    a.save_to_file('avatar-%s.png' % email)
