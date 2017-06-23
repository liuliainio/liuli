# -*- coding: utf-8 -*-
import os
import Image, ImageEnhance

PADDING = 0
POSITION = ('LEFTTOP', 'RIGHTTOP', 'CENTER', 'LEFTBOTTOM', 'RIGHTBOTTOM')


def reduce_opacity(im, opacity):
    """Returns an image with reduced opacity."""
    assert opacity >= 0 and opacity <= 1
    if im.mode != 'RGBA':
        im = im.convert('RGBA')
    else:
        im = im.copy()
    alpha = im.split()[3]
    alpha = ImageEnhance.Brightness(alpha).enhance(opacity)
    im.putalpha(alpha)
    return im


def parse_pos(img, mark, pos=POSITION[0]):
    """ parse the position of watermark according to img/mark/POSTION
    """
    if pos == POSITION[4]:   # right bottom
        position = (img.size[0] - mark.size[0] - PADDING, img.size[1] - mark.size[1] - PADDING)
    elif pos == POSITION[3]:    # left bottom
        position = (PADDING, img.size[1] - mark.size[1] - PADDING)
    elif pos == POSITION[2]:    # center
        position = ((img.size[0] - mark.size[0]) / 2, (img.size[1] - mark.size[1]) / 2)
    elif pos == POSITION[1]:    # right top
        position = (img.size[0] - mark.size[0] - PADDING, PADDING)
    else:     # left top (default)
        position = (PADDING, PADDING)
    return position


def watermark(imagefile, markfile, position=POSITION[0], opacity=1):
    """
    Adds a watermark to an image.
    @parmas:
        imagefile: original image file
        markfile: water mark image file
        position: 'LEFTTOP', 'RIGHTTOP', 'CENTER', 'LEFTBOTTOM', 'RIGHTBOTTOM'
        opacity: [0, 1], 0 means completely transparent, 1 means completely opaque
    """
    im = Image.open(imagefile)
    mark = Image.open(os.path.join(os.path.dirname(os.path.realpath(__file__)), markfile))
    if opacity < 1:
        mark = reduce_opacity(mark, opacity)
    if im.mode != 'RGBA':
        im = im.convert('RGBA')
    # adjust image size to (48, 48)
    if im.size[0] != 48 and im.size[1] != 48:
        im = im.resize((48, 48), Image.ANTIALIAS)
    # create a transparent layer the size of the image and draw the
    # watermark in that layer.
    layer = Image.new('RGBA', im.size, (0, 0, 0, 0))
    if position == 'title':
        for y in range(0, im.size[1], mark.size[1]):
            for x in range(0, im.size[0], mark.size[0]):
                layer.paste(mark, (x, y))
    elif position == 'scale':
        # scale, but preserve the aspect ratio
        ratio = min(
            float(im.size[0]) / mark.size[0], float(im.size[1]) / mark.size[1])
        w, h = int(mark.size[0] * ratio), int(mark.size[1] * ratio)
        mark = mark.resize((w, h), Image.ANTIALIAS)
        layer.paste(mark, ((im.size[0] - w) / 2, (im.size[1] - h) / 2))
    else:
        position = parse_pos(im, mark, position)
        layer.paste(mark, position)

    # composite the watermark with the layer
    return Image.composite(layer, im, layer)

#watermark(original_image_s_filename, mark_image_file_name).save(new_image_s_filename, quality=95)
