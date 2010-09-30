#!/usr/bin/python
#(c)www.stani.be (read __doc__ for more information)                            

__version__ = """v0.1 (2010-09-30)"""
__author__  = "Erik Gilling"
__license__ = "GPL"
__url__     = "http://www.konkers.net/boxmaker"
__doc__     = \
"""boxmaker
Creates vector art of finger jointed boxes suitible for 
laser cutting

Copyright %s
Version %s
License %s
Homepage %s

""" % \
(__author__,__version__,__license__,__url__)

import os

#needed for shared hosting with reportlab installed with virtualpython
activate_this = os.path.expanduser('~/local/bin/activate_this.py')
if os.path.exists(activate_this):
    execfile(activate_this, dict(__file__=activate_this))

import cgi

import cgitb
cgitb.enable()

import sys
import sdxf


form = cgi.FieldStorage()

from box import *;

height = float(form['height'].value)
width = float(form['width'].value)
depth = float(form['depth'].value)
spacing = float(form['spacing'].value)
thickness = float(form['thickness'].value)
if form['format'].value == 'pdf':
    output = 'pdf'
elif form['format'].value == 'single_pdf':
    output = 'single_pdf'
elif form['format'].value == 'dxf':
    output = 'dxf'
elif form['format'].value == 'single_dxf':
    output = 'single_dxf'
else:
    raise NameError('unkown format')

box = Box(height, width, depth, spacing, thickness)


front_block = sdxf.Block("front");
front_block.append(sdxf.LwPolyLine(points = box.front_points, flag = 1, color = 8))

bottom_block = sdxf.Block("bottom");
bottom_block.append(sdxf.LwPolyLine(points = box.bottom_points, flag = 1, color = 8))

top_block = sdxf.Block("top");
top_block.append(sdxf.LwPolyLine(points = box.top_points, flag = 1, color = 8))

back_block = sdxf.Block("back");
back_block.append(sdxf.LwPolyLine(points = box.back_points, flag = 1, color = 8))

right_block = sdxf.Block("right");
right_block.append(sdxf.LwPolyLine(points = box.right_points, flag = 1, color = 8))

left_block = sdxf.Block("left");
left_block.append(sdxf.LwPolyLine(points = box.left_points, flag = 1, color = 8))

if output == 'single_dxf':
    d = sdxf.Drawing()
    d.blocks.append(front_block)
    d.blocks.append(bottom_block)
    d.blocks.append(top_block)
    d.blocks.append(back_block)
    d.blocks.append(right_block)
    d.blocks.append(left_block)

    offset = 0
    d.append(sdxf.Insert('front', point = (offset, 0.5, 0)))
    d.append(sdxf.Text('front', point = (offset, 0), height = 0.25))
    offset += width + 1

    d.append(sdxf.Insert('back', point = (offset, 0.5, 0)))
    d.append(sdxf.Text('back', point = (offset, 0), height = 0.25))
    offset += width + 1

    d.append(sdxf.Insert('top', point = (offset, 0.5, 0)))
    d.append(sdxf.Text('top', point = (offset, 0), height = 0.25))
    offset += width + 1

    d.append(sdxf.Insert('bottom', point = (offset, 0.5, 0)))
    d.append(sdxf.Text('bottom', point = (offset, 0), height = 0.25))
    offset += width + 1

    d.append(sdxf.Insert('right', point = (offset, 0.5, 0)))
    d.append(sdxf.Text('right', point = (offset, 0), height = 0.25))
    offset += depth + 1

    d.append(sdxf.Insert('left', point = (offset, 0.5, 0)))
    d.append(sdxf.Text('left', point = (offset, 0), height = 0.25))
    offset += depth + 1

    print 'Content-Type: application/dxf'
    print 'Content-disposition: attachement; filename=box.dxf'
    print ''
    print str(d)

elif output == 'dxf':
    import zipfile
    import StringIO
    zipstr = StringIO.StringIO()

    z = zipfile.ZipFile(zipstr, 'w')

    d = sdxf.Drawing()
    d.blocks.append(front_block)
    d.append(sdxf.Insert('front', point = (0, 0, 0)))
    zi = zipfile.ZipInfo('front.dxf')
    zi.external_attr = 0644 << 16L
    z.writestr(zi, str(d))

    d = sdxf.Drawing()
    d.blocks.append(back_block)
    d.append(sdxf.Insert('back', point = (0, 0, 0)))
    zi = zipfile.ZipInfo('back.dxf')
    zi.external_attr = 0644 << 16L
    z.writestr(zi, str(d))

    d = sdxf.Drawing()
    d.blocks.append(top_block)
    d.append(sdxf.Insert('top', point = (0, 0, 0)))
    zi = zipfile.ZipInfo('top.dxf')
    zi.external_attr = 0644 << 16L
    z.writestr(zi, str(d))

    d = sdxf.Drawing()
    d.blocks.append(bottom_block)
    d.append(sdxf.Insert('bottom', point = (0, 0, 0)))
    zi = zipfile.ZipInfo('bottom.dxf')
    zi.external_attr = 0644 << 16L
    z.writestr(zi, str(d))

    d = sdxf.Drawing()
    d.blocks.append(left_block)
    d.append(sdxf.Insert('left', point = (0, 0, 0)))
    zi = zipfile.ZipInfo('left.dxf')
    zi.external_attr = 0644 << 16L
    z.writestr(zi, str(d))

    d = sdxf.Drawing()
    d.blocks.append(right_block)
    d.append(sdxf.Insert('right', point = (0, 0, 0)))
    zi = zipfile.ZipInfo('right.dxf')
    zi.external_attr = 0644 << 16L
    z.writestr(zi, str(d))

    z.close()

    print 'Content-Type: application/zip'
    print 'Content-disposition: attachement; filename=box-dxf.zip'
    print ''
    print zipstr.getvalue()
    zipstr.close()

elif output == 'pdf':
    from reportlab.pdfgen import canvas
    from reportlab.lib.units import inch

    c = canvas.Canvas(sys.stdout)

    def draw_page(c, name, points):
        max_x = 0
        max_y = 0

        for point in points:
            if point[0] > max_x:
                max_x = point[0]
            if point[1] > max_y:
                max_y = point[1]

        c.setPageSize(((max_x + 2) * inch, (max_y + 2) * inch))

        c.setFontSize(0.25 * inch)
        c.drawCentredString((max_x + 2) * inch / 2, (max_y + 2 - 0.66) * inch, name)

        c.translate(inch, inch)

        p = c.beginPath()
        p.moveTo(points[0][0] * inch, points[0][1] * inch)
        for point in points[1:]:
            p.lineTo(point[0] * inch, point[1] * inch)
        c.drawPath(p, fill = 0)
        c.showPage()

    draw_page(c, 'front', box.front_points)
    draw_page(c, 'back', box.back_points)
    draw_page(c, 'top', box.top_points)
    draw_page(c, 'bottom', box.bottom_points)
    draw_page(c, 'right', box.left_points)
    draw_page(c, 'left', box.right_points)

    print 'Content-Type: application/pdf'
    print 'Content-disposition: filename=box.pdf'
    print ''

    c.save()

elif output == 'single_pdf':
    from reportlab.pdfgen import canvas
    from reportlab.lib.units import inch

    c = canvas.Canvas(sys.stdout)

    def draw_side(c, name, points):
        max_x = 0
        max_y = 0

        for point in points:
            if point[0] > max_x:
                max_x = point[0]
            if point[1] > max_y:
                max_y = point[1]

        c.setFontSize(0.25 * inch)
        c.drawCentredString((max_x + 2) * inch / 2, 0.5 * inch, name)

        c.translate(inch, inch)

        p = c.beginPath()
        p.moveTo(points[0][0] * inch, points[0][1] * inch)
        for point in points[1:]:
            p.lineTo(point[0] * inch, point[1] * inch)
        c.drawPath(p, fill = 0)
        c.translate(max_x * inch, -inch)

    c.setPageSize(((width * 4 + depth * 2 + 7) * inch,
                  (max(height, depth) + 2) * inch))

    draw_side(c, 'front', box.front_points)
    draw_side(c, 'back', box.back_points)
    draw_side(c, 'top', box.top_points)
    draw_side(c, 'bottom', box.bottom_points)
    draw_side(c, 'right', box.left_points)
    draw_side(c, 'left', box.right_points)

    print 'Content-Type: application/pdf'
    print 'Content-disposition: filename=box.pdf'
    print ''

    c.save()
