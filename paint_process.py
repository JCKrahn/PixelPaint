"""
Paint Process
"""

import sys
import time
import pygame
import numpy
import cv2
import win32gui
import paint_window


def paint_process(title, size, background, paint_input_q, gui_input_q, image_maxsize):
    pygame.init()

    try:
        # scale (depends on size)
        if size[0] <= 64 or size[1] <= 64:
            scale = 4
        elif size[0] <= 256 or size[1] <= 256:
            scale = 2
        else:
            scale = 1

        # create window ----------------------------------------------------------------
        pygame.display.set_caption(title)
        pygame.display.set_icon(pygame.image.load("data/icons/no_icon.png"))

        #   move paint window directly under gui
        gui_id = win32gui.FindWindow(None, "PixelPaint")
        paint_win_id = win32gui.FindWindow(None, title)
        win32gui.MoveWindow(paint_win_id, win32gui.GetWindowRect(gui_id)[0] - 7, win32gui.GetWindowRect(gui_id)[1] + 46,
                size[0] + 20, size[1] + 20, True)  # (x, y seem to be treated differently on the executable version)

        #   setup window
        win = pygame.display.set_mode((size[0] * scale + 20, size[1] * scale + 20), pygame.RESIZABLE)
        win.set_alpha(None)
        win.fill((200, 200, 200))

        # new --------------------------------------------------------------------------
        if title == "untitled" or title == "unbenannt":
            image = paint_window.Image(win, size, background, scale)

        # open -------------------------------------------------------------------------
        else:
            pygame.display.set_icon(pygame.image.load(title))

            image_to_load = cv2.imread(title, cv2.IMREAD_UNCHANGED)

            if (image_to_load.shape[0] < 999 and image_to_load.shape[1] < 999) or image_maxsize == "false":

                if len(image_to_load.shape) == 3:  # more then one channel:

                    if image_to_load.shape[2] == 2:  # 2 channels:
                        gui_input_q.put("image_format_not_supported")
                        gui_input_q.put("paint_win_closed")
                        sys.exit()

                    elif image_to_load.shape[2] == 3:  # 3 channels:
                        pixel_colors = []
                        for y in range(0, size[1]):
                            row = []
                            for x in range(0, size[0]):
                                pixel_color = image_to_load[y, x]
                                pixel_color = (pixel_color[2], pixel_color[1], pixel_color[0], 255)
                                row.append(pixel_color)
                            pixel_colors.append(row)

                        image = paint_window.Image(win, size, background, scale, pixel_colors)

                    elif image_to_load.shape[2] == 4:  # 4 channels:
                        pixel_colors = []
                        for y in range(0, size[1]):
                            row = []
                            for x in range(0, size[0]):
                                pixel_color = image_to_load[y, x]
                                pixel_color = (pixel_color[2], pixel_color[1], pixel_color[0], pixel_color[3])
                                row.append(pixel_color)
                            pixel_colors.append(row)

                        image = paint_window.Image(win, size, background, scale, pixel_colors)

                    else:  # more than 4 channels
                        gui_input_q.put("image_format_not_supported")
                        gui_input_q.put("paint_win_closed")
                        sys.exit()

                else:  # 1 channel:
                    pixel_colors = []
                    for y in range(0, size[1]):
                        row = []
                        for x in range(0, size[0]):
                            pixel_color = (image_to_load[y, x], image_to_load[y, x], image_to_load[y, x], 255)
                            pixel_color = (pixel_color[2], pixel_color[1], pixel_color[0], pixel_color[3])
                            row.append(pixel_color)
                        pixel_colors.append(row)

                    image = paint_window.Image(win, size, background, scale, pixel_colors)

                if title[-4:] == ".png":
                    title = title[len(title) - title[::-1].find("/"):title.find(".png")]
                elif title[-4:] == ".jpg":
                    title = title[len(title) - title[::-1].find("/"):title.find(".jpg")]
                pygame.display.set_caption(title)

            else:
                gui_input_q.put("image_too_big")
                gui_input_q.put("paint_win_closed")
                sys.exit()

    except:
        gui_input_q.put("image_load_error")
        gui_input_q.put("paint_win_closed")
        sys.exit()

    pygame.display.update()

    # ------------------------------------------------------------------------------

    selected_color = None
    selected_tool = None
    draw_width = 1
    fill_alg_only_connected_pixels = "false"
    fill_alg_visual = "false"
    enable_fill_alg_tolerance = "false"
    fill_alg_tolerance = 10

    draw_cur = pygame.cursors.load_xbm("data/cursor/draw_cur.xbm", "data/cursor/draw_cur.mask")

    undo_list = []
    redo_list = []

    def undo():
        if len(undo_list) > 0:
            redo_list.append(image.get_pixel_colors())
            image.update_pixel_colors(undo_list.pop())
            image.draw_pixels()
            pygame.display.update()

    def redo():
        if len(redo_list) > 0:
            undo_list.append(image.get_pixel_colors())
            image.update_pixel_colors(redo_list.pop())
            image.draw_pixels()
            pygame.display.update()

    # main loop --------------------------------------------------------------------
    pygame.event.set_allowed([pygame.QUIT, pygame.VIDEORESIZE, pygame.KEYDOWN])

    run = True
    while run:

        # set mouse cursor
        if image.hover() and selected_tool is not None:
            pygame.mouse.set_cursor(*draw_cur)
        else:
            pygame.mouse.set_cursor(*pygame.cursors.arrow)

        # time delay; get events
        time.sleep(0.05)
        events = pygame.event.get()

        # input from gui
        while not paint_input_q.empty():
            paint_input = paint_input_q.get()

            if paint_input[0] == "color":
                selected_color = paint_input[1]

            elif paint_input[0] == "tool":
                selected_tool = paint_input[1]

            elif paint_input[0] == "draw_width":
                draw_width = paint_input[1]

            elif paint_input[0] == "request":

                if paint_input[1][0] == "save":  # save
                    try:
                        image_info = paint_input[1][1]

                        path = image_info[0]
                        filetype = image_info[1]
                        multiplier = image_info[3]/2  # size multiplier / 2 = side multiplier
                        if multiplier < 1: multiplier = 1  # at least 1
                        # compression or quality = image_info[2]]
                        grayscale = image_info[4]

                        if filetype == "png" and not grayscale:
                            img = numpy.zeros((image.real_h_in_pixels * multiplier, image.real_w_in_pixels * multiplier,
                                4), numpy.uint8)

                            y = 0
                            for row in image.pixels:
                                x = 0
                                for pixel in row:

                                    for i in range(0, multiplier):
                                        img[y, x+i] = pixel.rgba[2], pixel.rgba[1], pixel.rgba[0], pixel.rgba[3]
                                        for j in range(1, multiplier):
                                            img[y+j, x+i] = pixel.rgba[2], pixel.rgba[1], pixel.rgba[0], pixel.rgba[3]

                                    x += multiplier
                                y += multiplier

                            cv2.imwrite(path, img, [cv2.IMWRITE_PNG_COMPRESSION, image_info[2]])

                            if path[-4:] == ".png":
                                image_name = path[len(path) - path[::-1].find("/"):path.find(".png")]
                            elif path[-4:] == ".PNG":
                                image_name = path[len(path) - path[::-1].find("/"):path.find(".PNG")]

                        elif filetype == "jpg" and not grayscale:
                            img = numpy.zeros((image.real_h_in_pixels * multiplier, image.real_w_in_pixels * multiplier,
                                3), numpy.uint8)

                            y = 0
                            for row in image.pixels:
                                x = 0
                                for pixel in row:

                                    for i in range(0, multiplier):
                                        img[y, x + i] = pixel.rgba[2], pixel.rgba[1], pixel.rgba[0]
                                        for j in range(1, multiplier):
                                            img[y + j, x + i] = pixel.rgba[2], pixel.rgba[1], pixel.rgba[0]

                                    x += multiplier
                                y += multiplier

                            cv2.imwrite(path, img, [cv2.IMWRITE_JPEG_QUALITY, image_info[2]])

                            if path[-4:] == ".jpg":
                                image_name = path[len(path) - path[::-1].find("/"):path.find(".jpg")]
                            elif path[-4:] == ".JPG":
                                image_name = path[len(path) - path[::-1].find("/"):path.find(".JPG")]

                        elif grayscale:
                            img = numpy.zeros((image.real_h_in_pixels * multiplier, image.real_w_in_pixels * multiplier,
                                3), numpy.uint8)

                            y = 0
                            for row in image.pixels:
                                x = 0
                                for pixel in row:

                                    for i in range(0, multiplier):
                                        img[y, x + i] = pixel.rgba[2], pixel.rgba[1], pixel.rgba[0]
                                        for j in range(1, multiplier):
                                            img[y + j, x + i] = pixel.rgba[2], pixel.rgba[1], pixel.rgba[0]

                                    x += multiplier
                                y += multiplier

                            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

                            if filetype == "png":
                                cv2.imwrite(path, img, [cv2.IMWRITE_PNG_COMPRESSION, image_info[2]])

                                if path[-4:] == ".png":
                                    image_name = path[len(path) - path[::-1].find("/"):path.find(".png")]
                                elif path[-4:] == ".PNG":
                                    image_name = path[len(path) - path[::-1].find("/"):path.find(".PNG")]

                            elif filetype == "jpg":
                                cv2.imwrite(path, img, [cv2.IMWRITE_JPEG_QUALITY, image_info[2]])

                                if path[-4:] == ".jpg":
                                    image_name = path[len(path) - path[::-1].find("/"):path.find(".jpg")]
                                elif path[-4:] == ".JPG":
                                    image_name = path[len(path) - path[::-1].find("/"):path.find(".JPG")]

                        pygame.display.set_icon(pygame.image.load(path))
                        pygame.display.set_caption(image_name)

                    except:
                        gui_input_q.put("image_save_error")

                elif paint_input[1] == "close":
                    pygame.display.quit()
                    gui_input_q.put("paint_win_closed")
                    sys.exit()

                elif paint_input[1] == "undo":
                    undo()

                elif paint_input[1] == "redo":
                    redo()

            elif paint_input[0] == "fill_alg_only_connected_pixels":
                fill_alg_only_connected_pixels = paint_input[1]

            elif paint_input[0] == "fill_alg_visual":
                fill_alg_visual = paint_input[1]

            elif paint_input[0] == "fill_alg_tolerance":
                enable_fill_alg_tolerance = paint_input[1][0]
                fill_alg_tolerance = int(paint_input[1][1])

        # draw
        if selected_tool == "draw" and image.pressed():

            undo_list.append(image.get_pixel_colors())

            pygame.mouse.set_cursor(*draw_cur)

            if draw_width == "1*1":
                while image.pressed():
                    try:
                        image.draw_pixel(int((pygame.mouse.get_pos()[0] - image.xywh[0]) / image.scale),
                                         int((pygame.mouse.get_pos()[1] - image.xywh[1]) / image.scale),
                                         selected_color + (255,))
                        pygame.display.update()
                    except:
                        pass
                    pygame.event.clear()

            if draw_width == "3*3":
                while image.pressed():
                    center_pixel_x = int((pygame.mouse.get_pos()[0] - image.xywh[0]) / image.scale)
                    center_pixel_y = int((pygame.mouse.get_pos()[1] - image.xywh[1]) / image.scale)
                    try:
                        image.draw_pixel(center_pixel_x, center_pixel_y, selected_color + (255,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x + 1, center_pixel_y, selected_color + (255,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x + 1, center_pixel_y + 1, selected_color + (255,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x, center_pixel_y + 1, selected_color + (255,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x - 1, center_pixel_y + 1, selected_color + (255,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x - 1, center_pixel_y, selected_color + (255,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x - 1, center_pixel_y - 1, selected_color + (255,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x, center_pixel_y - 1, selected_color + (255,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x + 1, center_pixel_y - 1, selected_color + (255,))
                    except:
                        pass

                    pygame.display.update()
                    pygame.event.clear()

            if draw_width == "5*5":
                while image.pressed():
                    center_pixel_x = int((pygame.mouse.get_pos()[0] - image.xywh[0]) / image.scale)
                    center_pixel_y = int((pygame.mouse.get_pos()[1] - image.xywh[1]) / image.scale)
                    try:
                        image.draw_pixel(center_pixel_x, center_pixel_y, selected_color + (255,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x + 1, center_pixel_y, selected_color + (255,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x + 1, center_pixel_y + 1, selected_color + (255,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x, center_pixel_y + 1, selected_color + (255,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x - 1, center_pixel_y + 1, selected_color + (255,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x - 1, center_pixel_y, selected_color + (255,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x - 1, center_pixel_y - 1, selected_color + (255,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x, center_pixel_y - 1, selected_color + (255,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x + 1, center_pixel_y - 1, selected_color + (255,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x + 2, center_pixel_y, selected_color + (255,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x + 2, center_pixel_y + 1, selected_color + (255,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x + 2, center_pixel_y + 2, selected_color + (255,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x + 1, center_pixel_y + 2, selected_color + (255,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x, center_pixel_y + 2, selected_color + (255,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x - 1, center_pixel_y + 2, selected_color + (255,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x - 2, center_pixel_y + 2, selected_color + (255,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x - 2, center_pixel_y + 1, selected_color + (255,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x - 2, center_pixel_y, selected_color + (255,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x - 2, center_pixel_y - 1, selected_color + (255,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x - 2, center_pixel_y - 2, selected_color + (255,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x - 1, center_pixel_y - 2, selected_color + (255,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x, center_pixel_y - 2, selected_color + (255,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x + 1, center_pixel_y - 2, selected_color + (255,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x + 2, center_pixel_y - 2, selected_color + (255,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x + 2, center_pixel_y - 1, selected_color + (255,))
                    except:
                        pass

                    pygame.display.update()
                    pygame.event.clear()

            if draw_width == "7*7":
                while image.pressed():
                    center_pixel_x = int((pygame.mouse.get_pos()[0] - image.xywh[0]) / image.scale)
                    center_pixel_y = int((pygame.mouse.get_pos()[1] - image.xywh[1]) / image.scale)
                    try:
                        image.draw_pixel(center_pixel_x, center_pixel_y, selected_color + (255,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x + 1, center_pixel_y, selected_color + (255,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x + 1, center_pixel_y + 1, selected_color + (255,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x, center_pixel_y + 1, selected_color + (255,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x - 1, center_pixel_y + 1, selected_color + (255,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x - 1, center_pixel_y, selected_color + (255,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x - 1, center_pixel_y - 1, selected_color + (255,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x, center_pixel_y - 1, selected_color + (255,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x + 1, center_pixel_y - 1, selected_color + (255,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x + 2, center_pixel_y, selected_color + (255,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x + 2, center_pixel_y + 1, selected_color + (255,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x + 2, center_pixel_y + 2, selected_color + (255,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x + 1, center_pixel_y + 2, selected_color + (255,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x, center_pixel_y + 2, selected_color + (255,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x - 1, center_pixel_y + 2, selected_color + (255,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x - 2, center_pixel_y + 2, selected_color + (255,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x - 2, center_pixel_y + 1, selected_color + (255,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x - 2, center_pixel_y, selected_color + (255,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x - 2, center_pixel_y - 1, selected_color + (255,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x - 2, center_pixel_y - 2, selected_color + (255,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x - 1, center_pixel_y - 2, selected_color + (255,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x, center_pixel_y - 2, selected_color + (255,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x + 1, center_pixel_y - 2, selected_color + (255,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x + 2, center_pixel_y - 2, selected_color + (255,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x + 2, center_pixel_y - 1, selected_color + (255,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x + 3, center_pixel_y, selected_color + (255,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x + 3, center_pixel_y + 1, selected_color + (255,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x + 3, center_pixel_y + 2, selected_color + (255,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x + 3, center_pixel_y + 3, selected_color + (255,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x + 2, center_pixel_y + 3, selected_color + (255,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x + 1, center_pixel_y + 3, selected_color + (255,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x, center_pixel_y + 3, selected_color + (255,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x - 1, center_pixel_y + 3, selected_color + (255,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x - 2, center_pixel_y + 3, selected_color + (255,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x - 3, center_pixel_y + 3, selected_color + (255,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x - 3, center_pixel_y + 2, selected_color + (255,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x - 3, center_pixel_y + 1, selected_color + (255,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x - 3, center_pixel_y, selected_color + (255,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x - 3, center_pixel_y - 1, selected_color + (255,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x - 3, center_pixel_y - 2, selected_color + (255,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x - 3, center_pixel_y - 3, selected_color + (255,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x - 2, center_pixel_y - 3, selected_color + (255,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x - 1, center_pixel_y - 3, selected_color + (255,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x, center_pixel_y - 3, selected_color + (255,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x + 1, center_pixel_y - 3, selected_color + (255,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x + 2, center_pixel_y - 3, selected_color + (255,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x + 3, center_pixel_y - 3, selected_color + (255,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x + 3, center_pixel_y - 2, selected_color + (255,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x + 3, center_pixel_y - 1, selected_color + (255,))
                    except:
                        pass

                    pygame.display.update()
                    pygame.event.clear()

        # draw transparency
        if selected_tool == "draw_transparency" and image.pressed():

            undo_list.append(image.get_pixel_colors())

            pygame.mouse.set_cursor(*draw_cur)

            if draw_width == "1*1":
                while image.pressed():
                    try:
                        image.draw_pixel(int((pygame.mouse.get_pos()[0] - image.xywh[0]) / image.scale),
                                         int((pygame.mouse.get_pos()[1] - image.xywh[1]) / image.scale),
                                         selected_color + (0,))
                        pygame.display.update()
                    except:
                        pass
                    pygame.event.clear()

            if draw_width == "3*3":
                while image.pressed():
                    center_pixel_x = int((pygame.mouse.get_pos()[0] - image.xywh[0]) / image.scale)
                    center_pixel_y = int((pygame.mouse.get_pos()[1] - image.xywh[1]) / image.scale)
                    try:
                        image.draw_pixel(center_pixel_x, center_pixel_y, selected_color + (0,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x + 1, center_pixel_y, selected_color + (0,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x + 1, center_pixel_y + 1, selected_color + (0,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x, center_pixel_y + 1, selected_color + (0,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x - 1, center_pixel_y + 1, selected_color + (0,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x - 1, center_pixel_y, selected_color + (0,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x - 1, center_pixel_y - 1, selected_color + (0,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x, center_pixel_y - 1, selected_color + (0,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x + 1, center_pixel_y - 1, selected_color + (0,))
                    except:
                        pass

                    pygame.display.update()
                    pygame.event.clear()

            if draw_width == "5*5":
                while image.pressed():
                    center_pixel_x = int((pygame.mouse.get_pos()[0] - image.xywh[0]) / image.scale)
                    center_pixel_y = int((pygame.mouse.get_pos()[1] - image.xywh[1]) / image.scale)
                    try:
                        image.draw_pixel(center_pixel_x, center_pixel_y, selected_color + (0,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x + 1, center_pixel_y, selected_color + (0,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x + 1, center_pixel_y + 1, selected_color + (0,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x, center_pixel_y + 1, selected_color + (0,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x - 1, center_pixel_y + 1, selected_color + (0,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x - 1, center_pixel_y, selected_color + (0,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x - 1, center_pixel_y - 1, selected_color + (0,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x, center_pixel_y - 1, selected_color + (0,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x + 1, center_pixel_y - 1, selected_color + (0,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x + 2, center_pixel_y, selected_color + (0,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x + 2, center_pixel_y + 1, selected_color + (0,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x + 2, center_pixel_y + 2, selected_color + (0,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x + 1, center_pixel_y + 2, selected_color + (0,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x, center_pixel_y + 2, selected_color + (0,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x - 1, center_pixel_y + 2, selected_color + (0,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x - 2, center_pixel_y + 2, selected_color + (0,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x - 2, center_pixel_y + 1, selected_color + (0,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x - 2, center_pixel_y, selected_color + (0,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x - 2, center_pixel_y - 1, selected_color + (0,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x - 2, center_pixel_y - 2, selected_color + (0,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x - 1, center_pixel_y - 2, selected_color + (0,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x, center_pixel_y - 2, selected_color + (0,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x + 1, center_pixel_y - 2, selected_color + (0,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x + 2, center_pixel_y - 2, selected_color + (0,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x + 2, center_pixel_y - 1, selected_color + (0,))
                    except:
                        pass

                    pygame.display.update()
                    pygame.event.clear()

            if draw_width == "7*7":
                while image.pressed():
                    center_pixel_x = int((pygame.mouse.get_pos()[0] - image.xywh[0]) / image.scale)
                    center_pixel_y = int((pygame.mouse.get_pos()[1] - image.xywh[1]) / image.scale)
                    try:
                        image.draw_pixel(center_pixel_x, center_pixel_y, selected_color + (0,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x + 1, center_pixel_y, selected_color + (0,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x + 1, center_pixel_y + 1, selected_color + (0,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x, center_pixel_y + 1, selected_color + (0,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x - 1, center_pixel_y + 1, selected_color + (0,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x - 1, center_pixel_y, selected_color + (0,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x - 1, center_pixel_y - 1, selected_color + (0,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x, center_pixel_y - 1, selected_color + (0,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x + 1, center_pixel_y - 1, selected_color + (0,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x + 2, center_pixel_y, selected_color + (0,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x + 2, center_pixel_y + 1, selected_color + (0,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x + 2, center_pixel_y + 2, selected_color + (0,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x + 1, center_pixel_y + 2, selected_color + (0,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x, center_pixel_y + 2, selected_color + (0,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x - 1, center_pixel_y + 2, selected_color + (0,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x - 2, center_pixel_y + 2, selected_color + (0,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x - 2, center_pixel_y + 1, selected_color + (0,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x - 2, center_pixel_y, selected_color + (0,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x - 2, center_pixel_y - 1, selected_color + (0,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x - 2, center_pixel_y - 2, selected_color + (0,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x - 1, center_pixel_y - 2, selected_color + (0,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x, center_pixel_y - 2, selected_color + (0,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x + 1, center_pixel_y - 2, selected_color + (0,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x + 2, center_pixel_y - 2, selected_color + (0,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x + 2, center_pixel_y - 1, selected_color + (0,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x + 3, center_pixel_y, selected_color + (0,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x + 3, center_pixel_y + 1, selected_color + (0,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x + 3, center_pixel_y + 2, selected_color + (0,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x + 3, center_pixel_y + 3, selected_color + (0,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x + 2, center_pixel_y + 3, selected_color + (0,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x + 1, center_pixel_y + 3, selected_color + (0,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x, center_pixel_y + 3, selected_color + (0,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x - 1, center_pixel_y + 3, selected_color + (0,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x - 2, center_pixel_y + 3, selected_color + (0,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x - 3, center_pixel_y + 3, selected_color + (0,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x - 3, center_pixel_y + 2, selected_color + (0,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x - 3, center_pixel_y + 1, selected_color + (0,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x - 3, center_pixel_y, selected_color + (0,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x - 3, center_pixel_y - 1, selected_color + (0,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x - 3, center_pixel_y - 2, selected_color + (0,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x - 3, center_pixel_y - 3, selected_color + (0,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x - 2, center_pixel_y - 3, selected_color + (0,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x - 1, center_pixel_y - 3, selected_color + (0,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x, center_pixel_y - 3, selected_color + (0,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x + 1, center_pixel_y - 3, selected_color + (0,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x + 2, center_pixel_y - 3, selected_color + (0,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x + 3, center_pixel_y - 3, selected_color + (0,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x + 3, center_pixel_y - 2, selected_color + (0,))
                    except:
                        pass
                    try:
                        image.draw_pixel(center_pixel_x + 3, center_pixel_y - 1, selected_color + (0,))
                    except:
                        pass

                    pygame.display.update()
                    pygame.event.clear()

        # erase
        if selected_tool == "erase" and image.pressed():

            undo_list.append(image.get_pixel_colors())

            pygame.mouse.set_cursor(*draw_cur)

            if draw_width == "1*1":
                while image.pressed():
                    try:
                        image.erase_pixel(int((pygame.mouse.get_pos()[0] - image.xywh[0]) / image.scale),
                                          int((pygame.mouse.get_pos()[1] - image.xywh[1]) / image.scale))
                        pygame.display.update()
                    except:
                        pass
                    pygame.event.clear()

            if draw_width == "3*3":
                while image.pressed():
                    center_pixel_x = int((pygame.mouse.get_pos()[0] - image.xywh[0]) / image.scale)
                    center_pixel_y = int((pygame.mouse.get_pos()[1] - image.xywh[1]) / image.scale)
                    try:
                        image.erase_pixel(center_pixel_x, center_pixel_y)
                    except:
                        pass
                    try:
                        image.erase_pixel(center_pixel_x + 1, center_pixel_y)
                    except:
                        pass
                    try:
                        image.erase_pixel(center_pixel_x + 1, center_pixel_y + 1)
                    except:
                        pass
                    try:
                        image.erase_pixel(center_pixel_x, center_pixel_y + 1)
                    except:
                        pass
                    try:
                        image.erase_pixel(center_pixel_x - 1, center_pixel_y + 1)
                    except:
                        pass
                    try:
                        image.erase_pixel(center_pixel_x - 1, center_pixel_y)
                    except:
                        pass
                    try:
                        image.erase_pixel(center_pixel_x - 1, center_pixel_y - 1)
                    except:
                        pass
                    try:
                        image.erase_pixel(center_pixel_x, center_pixel_y - 1)
                    except:
                        pass
                    try:
                        image.erase_pixel(center_pixel_x + 1, center_pixel_y - 1)
                    except:
                        pass

                    pygame.display.update()
                    pygame.event.clear()

            if draw_width == "5*5":
                while image.pressed():
                    center_pixel_x = int((pygame.mouse.get_pos()[0] - image.xywh[0]) / image.scale)
                    center_pixel_y = int((pygame.mouse.get_pos()[1] - image.xywh[1]) / image.scale)
                    try:
                        image.erase_pixel(center_pixel_x, center_pixel_y)
                    except:
                        pass
                    try:
                        image.erase_pixel(center_pixel_x + 1, center_pixel_y)
                    except:
                        pass
                    try:
                        image.erase_pixel(center_pixel_x + 1, center_pixel_y + 1)
                    except:
                        pass
                    try:
                        image.erase_pixel(center_pixel_x, center_pixel_y + 1)
                    except:
                        pass
                    try:
                        image.erase_pixel(center_pixel_x - 1, center_pixel_y + 1)
                    except:
                        pass
                    try:
                        image.erase_pixel(center_pixel_x - 1, center_pixel_y)
                    except:
                        pass
                    try:
                        image.erase_pixel(center_pixel_x - 1, center_pixel_y - 1)
                    except:
                        pass
                    try:
                        image.erase_pixel(center_pixel_x, center_pixel_y - 1)
                    except:
                        pass
                    try:
                        image.erase_pixel(center_pixel_x + 1, center_pixel_y - 1)
                    except:
                        pass
                    try:
                        image.erase_pixel(center_pixel_x + 2, center_pixel_y)
                    except:
                        pass
                    try:
                        image.erase_pixel(center_pixel_x + 2, center_pixel_y + 1)
                    except:
                        pass
                    try:
                        image.erase_pixel(center_pixel_x + 2, center_pixel_y + 2)
                    except:
                        pass
                    try:
                        image.erase_pixel(center_pixel_x + 1, center_pixel_y + 2)
                    except:
                        pass
                    try:
                        image.erase_pixel(center_pixel_x, center_pixel_y + 2)
                    except:
                        pass
                    try:
                        image.erase_pixel(center_pixel_x - 1, center_pixel_y + 2)
                    except:
                        pass
                    try:
                        image.erase_pixel(center_pixel_x - 2, center_pixel_y + 2)
                    except:
                        pass
                    try:
                        image.erase_pixel(center_pixel_x - 2, center_pixel_y + 1)
                    except:
                        pass
                    try:
                        image.erase_pixel(center_pixel_x - 2, center_pixel_y)
                    except:
                        pass
                    try:
                        image.erase_pixel(center_pixel_x - 2, center_pixel_y - 1)
                    except:
                        pass
                    try:
                        image.erase_pixel(center_pixel_x - 2, center_pixel_y - 2)
                    except:
                        pass
                    try:
                        image.erase_pixel(center_pixel_x - 1, center_pixel_y - 2)
                    except:
                        pass
                    try:
                        image.erase_pixel(center_pixel_x, center_pixel_y - 2)
                    except:
                        pass
                    try:
                        image.erase_pixel(center_pixel_x + 1, center_pixel_y - 2)
                    except:
                        pass
                    try:
                        image.erase_pixel(center_pixel_x + 2, center_pixel_y - 2)
                    except:
                        pass
                    try:
                        image.erase_pixel(center_pixel_x + 2, center_pixel_y - 1)
                    except:
                        pass

                    pygame.display.update()
                    pygame.event.clear()

            if draw_width == "7*7":
                while image.pressed():
                    center_pixel_x = int((pygame.mouse.get_pos()[0] - image.xywh[0]) / image.scale)
                    center_pixel_y = int((pygame.mouse.get_pos()[1] - image.xywh[1]) / image.scale)
                    try:
                        image.erase_pixel(center_pixel_x, center_pixel_y)
                    except:
                        pass
                    try:
                        image.erase_pixel(center_pixel_x + 1, center_pixel_y)
                    except:
                        pass
                    try:
                        image.erase_pixel(center_pixel_x + 1, center_pixel_y + 1)
                    except:
                        pass
                    try:
                        image.erase_pixel(center_pixel_x, center_pixel_y + 1)
                    except:
                        pass
                    try:
                        image.erase_pixel(center_pixel_x - 1, center_pixel_y + 1)
                    except:
                        pass
                    try:
                        image.erase_pixel(center_pixel_x - 1, center_pixel_y)
                    except:
                        pass
                    try:
                        image.erase_pixel(center_pixel_x - 1, center_pixel_y - 1)
                    except:
                        pass
                    try:
                        image.erase_pixel(center_pixel_x, center_pixel_y - 1)
                    except:
                        pass
                    try:
                        image.erase_pixel(center_pixel_x + 1, center_pixel_y - 1)
                    except:
                        pass
                    try:
                        image.erase_pixel(center_pixel_x + 2, center_pixel_y)
                    except:
                        pass
                    try:
                        image.erase_pixel(center_pixel_x + 2, center_pixel_y + 1)
                    except:
                        pass
                    try:
                        image.erase_pixel(center_pixel_x + 2, center_pixel_y + 2)
                    except:
                        pass
                    try:
                        image.erase_pixel(center_pixel_x + 1, center_pixel_y + 2)
                    except:
                        pass
                    try:
                        image.erase_pixel(center_pixel_x, center_pixel_y + 2)
                    except:
                        pass
                    try:
                        image.erase_pixel(center_pixel_x - 1, center_pixel_y + 2)
                    except:
                        pass
                    try:
                        image.erase_pixel(center_pixel_x - 2, center_pixel_y + 2)
                    except:
                        pass
                    try:
                        image.erase_pixel(center_pixel_x - 2, center_pixel_y + 1)
                    except:
                        pass
                    try:
                        image.erase_pixel(center_pixel_x - 2, center_pixel_y)
                    except:
                        pass
                    try:
                        image.erase_pixel(center_pixel_x - 2, center_pixel_y - 1)
                    except:
                        pass
                    try:
                        image.erase_pixel(center_pixel_x - 2, center_pixel_y - 2)
                    except:
                        pass
                    try:
                        image.erase_pixel(center_pixel_x - 1, center_pixel_y - 2)
                    except:
                        pass
                    try:
                        image.erase_pixel(center_pixel_x, center_pixel_y - 2)
                    except:
                        pass
                    try:
                        image.erase_pixel(center_pixel_x + 1, center_pixel_y - 2)
                    except:
                        pass
                    try:
                        image.erase_pixel(center_pixel_x + 2, center_pixel_y - 2)
                    except:
                        pass
                    try:
                        image.erase_pixel(center_pixel_x + 2, center_pixel_y - 1)
                    except:
                        pass
                    try:
                        image.erase_pixel(center_pixel_x + 3, center_pixel_y)
                    except:
                        pass
                    try:
                        image.erase_pixel(center_pixel_x + 3, center_pixel_y + 1)
                    except:
                        pass
                    try:
                        image.erase_pixel(center_pixel_x + 3, center_pixel_y + 2)
                    except:
                        pass
                    try:
                        image.erase_pixel(center_pixel_x + 3, center_pixel_y + 3)
                    except:
                        pass
                    try:
                        image.erase_pixel(center_pixel_x + 2, center_pixel_y + 3)
                    except:
                        pass
                    try:
                        image.erase_pixel(center_pixel_x + 1, center_pixel_y + 3)
                    except:
                        pass
                    try:
                        image.erase_pixel(center_pixel_x, center_pixel_y + 3)
                    except:
                        pass
                    try:
                        image.erase_pixel(center_pixel_x - 1, center_pixel_y + 3)
                    except:
                        pass
                    try:
                        image.erase_pixel(center_pixel_x - 2, center_pixel_y + 3)
                    except:
                        pass
                    try:
                        image.erase_pixel(center_pixel_x - 3, center_pixel_y + 3)
                    except:
                        pass
                    try:
                        image.erase_pixel(center_pixel_x - 3, center_pixel_y + 2)
                    except:
                        pass
                    try:
                        image.erase_pixel(center_pixel_x - 3, center_pixel_y + 1)
                    except:
                        pass
                    try:
                        image.erase_pixel(center_pixel_x - 3, center_pixel_y)
                    except:
                        pass
                    try:
                        image.erase_pixel(center_pixel_x - 3, center_pixel_y - 1)
                    except:
                        pass
                    try:
                        image.erase_pixel(center_pixel_x - 3, center_pixel_y - 2)
                    except:
                        pass
                    try:
                        image.erase_pixel(center_pixel_x - 3, center_pixel_y - 3)
                    except:
                        pass
                    try:
                        image.erase_pixel(center_pixel_x - 2, center_pixel_y - 3)
                    except:
                        pass
                    try:
                        image.erase_pixel(center_pixel_x - 1, center_pixel_y - 3)
                    except:
                        pass
                    try:
                        image.erase_pixel(center_pixel_x, center_pixel_y - 3)
                    except:
                        pass
                    try:
                        image.erase_pixel(center_pixel_x + 1, center_pixel_y - 3)
                    except:
                        pass
                    try:
                        image.erase_pixel(center_pixel_x + 2, center_pixel_y - 3)
                    except:
                        pass
                    try:
                        image.erase_pixel(center_pixel_x + 3, center_pixel_y - 3)
                    except:
                        pass
                    try:
                        image.erase_pixel(center_pixel_x + 3, center_pixel_y - 2)
                    except:
                        pass
                    try:
                        image.erase_pixel(center_pixel_x + 3, center_pixel_y - 1)
                    except:
                        pass

                    pygame.display.update()
                    pygame.event.clear()

        # fill
        if selected_tool == "fill" and image.pressed():
            pygame.event.set_allowed(pygame.QUIT)
            pygame.mouse.set_cursor(*pygame.cursors.arrow)

            stop = False  # only for fill_alg_only_connected_pixels == "false"

            if fill_alg_only_connected_pixels == "false":  # fill all pixels with matching color

                if enable_fill_alg_tolerance == "true":  # tolerance enabled:
                    undo_list.append(image.get_pixel_colors())

                    mouse_pos = pygame.mouse.get_pos()

                    max_deviation = int(256 * fill_alg_tolerance / 100)

                    if image.pixel_exists(int((mouse_pos[0] - image.xywh[0]) / image.scale),
                                          int((mouse_pos[1] - image.xywh[1]) / image.scale)):  # starting pixel exists:

                        color_to_match = image.pixels[int((mouse_pos[1] - image.xywh[1]) / image.scale)][
                            int((mouse_pos[0] - image.xywh[0]) / image.scale)].rgba

                        if color_to_match != selected_color + (255,):

                            if fill_alg_visual == "true":  # visualize algorithm:
                                for y in range(image.real_h_in_pixels):
                                    events = pygame.event.get()

                                    for x in range(image.real_w_in_pixels):
                                        # color matches (with max_deviation)
                                        if -1 * max_deviation <= image.pixels[y][x].rgba[0] - \
                                                color_to_match[0] <= max_deviation \
                                                and -1 * max_deviation <= image.pixels[y][x].rgba[1] - \
                                                color_to_match[1] <= max_deviation \
                                                and -1 * max_deviation <= image.pixels[y][x].rgba[2] - \
                                                color_to_match[2] <= max_deviation \
                                                and -1 * max_deviation <= image.pixels[y][x].rgba[3] - \
                                                color_to_match[3] <= max_deviation:
                                            image.draw_pixel(x, y, selected_color + (255,))

                                            pygame.display.update()

                                    for e in events:
                                        if e.type == pygame.QUIT:
                                            stop = True
                                            pygame.event.clear()
                                            break
                                    if stop: break

                            else:  # don't visualize algorithm:
                                for y in range(image.real_h_in_pixels):
                                    events = pygame.event.get()

                                    for x in range(image.real_w_in_pixels):
                                        # color matches (with max_deviation)
                                        if -1 * max_deviation <= image.pixels[y][x].rgba[0] - \
                                                color_to_match[0] <= max_deviation \
                                                and -1 * max_deviation <= image.pixels[y][x].rgba[1] - \
                                                color_to_match[1] <= max_deviation \
                                                and -1 * max_deviation <= image.pixels[y][x].rgba[2] - \
                                                color_to_match[2] <= max_deviation \
                                                and -1 * max_deviation <= image.pixels[y][x].rgba[3] - \
                                                color_to_match[3] <= max_deviation:
                                            image.draw_pixel(x, y, selected_color + (255,))

                                    for e in events:
                                        if e.type == pygame.QUIT:
                                            stop = True
                                            pygame.event.clear()
                                            break
                                    if stop: break

                                pygame.display.update()

                else:  # tolerance disabled:

                    undo_list.append(image.get_pixel_colors())

                    mouse_pos = pygame.mouse.get_pos()

                    if image.pixel_exists(int((mouse_pos[0] - image.xywh[0]) / image.scale),
                                          int((mouse_pos[1] - image.xywh[1]) / image.scale)):  # starting pixel exists:

                        color_to_match = image.pixels[int((mouse_pos[1] - image.xywh[1]) / image.scale)][
                            int((mouse_pos[0] - image.xywh[0]) / image.scale)].rgba

                        if color_to_match != selected_color + (255,):

                            if fill_alg_visual == "true":  # visualize algorithm:
                                for y in range(image.real_h_in_pixels):
                                    events = pygame.event.get()

                                    for x in range(image.real_w_in_pixels):
                                        # color matches
                                        if image.pixels[y][x].rgba == color_to_match:
                                            image.draw_pixel(x, y, selected_color + (255,))

                                            pygame.display.update()

                                    for e in events:
                                        if e.type == pygame.QUIT:
                                            stop = True
                                            pygame.event.clear()
                                            break
                                    if stop: break

                            else:  # don't visualize algorithm:
                                for y in range(image.real_h_in_pixels):
                                    events = pygame.event.get()

                                    for x in range(image.real_w_in_pixels):
                                        # color matches
                                        if image.pixels[y][x].rgba == color_to_match:
                                            image.draw_pixel(x, y, selected_color + (255,))

                                    for e in events:
                                        if e.type == pygame.QUIT:
                                            stop = True
                                            pygame.event.clear()
                                            break
                                    if stop: break

                                pygame.display.update()

                pygame.event.set_allowed([pygame.QUIT, pygame.VIDEORESIZE, pygame.KEYDOWN])
                continue

            else:  # fill only connected pixels

                if enable_fill_alg_tolerance == "true":  # tolerance enabled:
                    undo_list.append(image.get_pixel_colors())

                    mouse_pos = pygame.mouse.get_pos()

                    pixels = [(int((mouse_pos[0] - image.xywh[0]) / image.scale), int((mouse_pos[1] - image.xywh[1])
                                                                                      / image.scale))]
                    drawn_pixels = []
                    max_deviation = int(256 * fill_alg_tolerance / 100)

                    if image.pixel_exists(*pixels[0]):  # starting pixel exists:
                        color_to_match = image.pixels[int((mouse_pos[1] - image.xywh[1]) / image.scale)][
                            int((mouse_pos[0] -
                                 image.xywh[0]) / image.scale)].rgba

                        if color_to_match != selected_color + (255,):

                            if fill_alg_visual == "true":  # visualize algorithm:
                                while len(pixels) > 0:
                                    events = pygame.event.get()
                                    current_pixel = pixels.pop()
                                    drawn_pixels.append(current_pixel)
                                    image.draw_pixel(current_pixel[0], current_pixel[1], selected_color + (255,))

                                    for pixel in image.get_neighbor_pixels(*current_pixel):
                                        # pixel not visited and color matches (with max_deviation)
                                        if pixel not in drawn_pixels and pixel not in pixels \
                                                and -1 * max_deviation <= image.pixels[pixel[1]][pixel[0]].rgba[0] - \
                                                color_to_match[0] <= max_deviation \
                                                and -1 * max_deviation <= image.pixels[pixel[1]][pixel[0]].rgba[1] - \
                                                color_to_match[1] <= max_deviation \
                                                and -1 * max_deviation <= image.pixels[pixel[1]][pixel[0]].rgba[2] - \
                                                color_to_match[2] <= max_deviation \
                                                and -1 * max_deviation <= image.pixels[pixel[1]][pixel[0]].rgba[3] - \
                                                color_to_match[3] <= max_deviation:
                                            pixels.append(pixel)

                                    pygame.display.update()

                                    for e in events:
                                        if e.type == pygame.QUIT:
                                            pixels = []
                                            pygame.event.clear()
                                            break

                            else:  # don't visualize algorithm:
                                while len(pixels) > 0:
                                    events = pygame.event.get()
                                    current_pixel = pixels.pop()
                                    drawn_pixels.append(current_pixel)
                                    image.draw_pixel(current_pixel[0], current_pixel[1], selected_color + (255,))

                                    for pixel in image.get_neighbor_pixels(*current_pixel):
                                        # pixel not visited and color matches (with max_deviation)
                                        if pixel not in drawn_pixels and pixel not in pixels \
                                                and -1 * max_deviation <= image.pixels[pixel[1]][pixel[0]].rgba[0] - \
                                                color_to_match[0] <= max_deviation \
                                                and -1 * max_deviation <= image.pixels[pixel[1]][pixel[0]].rgba[1] - \
                                                color_to_match[1] <= max_deviation \
                                                and -1 * max_deviation <= image.pixels[pixel[1]][pixel[0]].rgba[2] - \
                                                color_to_match[2] <= max_deviation \
                                                and -1 * max_deviation <= image.pixels[pixel[1]][pixel[0]].rgba[3] - \
                                                color_to_match[3] <= max_deviation:
                                            pixels.append(pixel)

                                    for e in events:
                                        if e.type == pygame.QUIT:
                                            pixels = []
                                            pygame.event.clear()
                                            break

                                pygame.display.update()

                else:  # tolerance disabled:

                    undo_list.append(image.get_pixel_colors())

                    mouse_pos = pygame.mouse.get_pos()

                    pixels = [(int((mouse_pos[0] - image.xywh[0]) / image.scale),
                               int((mouse_pos[1] - image.xywh[1]) / image.scale))]
                    drawn_pixels = []

                    if image.pixel_exists(*pixels[0]):  # starting pixel exists:
                        color_to_match = image.pixels[int((mouse_pos[1] - image.xywh[1]) / image.scale)][
                            int((mouse_pos[0] -
                                 image.xywh[0]) / image.scale)].rgba

                        if color_to_match != selected_color + (255,):

                            if fill_alg_visual == "true":  # visualize algorithm:
                                while len(pixels) > 0:
                                    events = pygame.event.get()
                                    current_pixel = pixels.pop()
                                    drawn_pixels.append(current_pixel)
                                    image.draw_pixel(current_pixel[0], current_pixel[1], selected_color + (255,))

                                    for pixel in image.get_neighbor_pixels(*current_pixel):
                                        if pixel not in drawn_pixels and pixel not in pixels \
                                                and image.pixels[pixel[1]][pixel[0]].rgba == color_to_match:
                                            pixels.append(pixel)

                                    pygame.display.update()

                                    for e in events:
                                        if e.type == pygame.QUIT:
                                            pixels = []
                                            pygame.event.clear()
                                            break

                            else:  # don't visualize algorithm:
                                while len(pixels) > 0:
                                    events = pygame.event.get()
                                    current_pixel = pixels.pop()
                                    drawn_pixels.append(current_pixel)
                                    image.draw_pixel(current_pixel[0], current_pixel[1], selected_color + (255,))

                                    for pixel in image.get_neighbor_pixels(*current_pixel):
                                        if pixel not in drawn_pixels and pixel not in pixels \
                                                and image.pixels[pixel[1]][pixel[0]].rgba == color_to_match:
                                            pixels.append(pixel)

                                    for e in events:
                                        if e.type == pygame.QUIT:
                                            pixels = []
                                            pygame.event.clear()
                                            break

                                pygame.display.update()

                pygame.event.set_allowed([pygame.QUIT, pygame.VIDEORESIZE, pygame.KEYDOWN])
                continue

        # fill with transparency
        if selected_tool == "fill_transparency" and image.pressed():
            pygame.event.set_allowed(pygame.QUIT)
            pygame.mouse.set_cursor(*pygame.cursors.arrow)

            stop = False  # only for fill_alg_only_connected_pixels == "false"

            if fill_alg_only_connected_pixels == "false":  # fill all pixels with matching color

                if enable_fill_alg_tolerance == "true":  # tolerance enabled:
                    undo_list.append(image.get_pixel_colors())

                    mouse_pos = pygame.mouse.get_pos()

                    max_deviation = int(256 * fill_alg_tolerance / 100)

                    if image.pixel_exists(int((mouse_pos[0] - image.xywh[0]) / image.scale),
                                          int((mouse_pos[1] - image.xywh[1]) / image.scale)):  # starting pixel exists:

                        color_to_match = image.pixels[int((mouse_pos[1] - image.xywh[1]) / image.scale)][
                            int((mouse_pos[0] - image.xywh[0]) / image.scale)].rgba

                        if color_to_match != (255, 255, 255, 0):

                            if fill_alg_visual == "true":  # visualize algorithm:
                                for y in range(image.real_h_in_pixels):
                                    events = pygame.event.get()

                                    for x in range(image.real_w_in_pixels):
                                        # color matches (with max_deviation)
                                        if -1 * max_deviation <= image.pixels[y][x].rgba[0] - \
                                                color_to_match[0] <= max_deviation \
                                                and -1 * max_deviation <= image.pixels[y][x].rgba[1] - \
                                                color_to_match[1] <= max_deviation \
                                                and -1 * max_deviation <= image.pixels[y][x].rgba[2] - \
                                                color_to_match[2] <= max_deviation \
                                                and -1 * max_deviation <= image.pixels[y][x].rgba[3] - \
                                                color_to_match[3] <= max_deviation:
                                            image.draw_pixel(x, y, (255, 255, 255, 0))

                                            pygame.display.update()

                                    for e in events:
                                        if e.type == pygame.QUIT:
                                            stop = True
                                            pygame.event.clear()
                                            break
                                    if stop: break

                            else:  # don't visualize algorithm:
                                for y in range(image.real_h_in_pixels):
                                    events = pygame.event.get()

                                    for x in range(image.real_w_in_pixels):
                                        # color matches (with max_deviation)
                                        if -1 * max_deviation <= image.pixels[y][x].rgba[0] - \
                                                color_to_match[0] <= max_deviation \
                                                and -1 * max_deviation <= image.pixels[y][x].rgba[1] - \
                                                color_to_match[1] <= max_deviation \
                                                and -1 * max_deviation <= image.pixels[y][x].rgba[2] - \
                                                color_to_match[2] <= max_deviation \
                                                and -1 * max_deviation <= image.pixels[y][x].rgba[3] - \
                                                color_to_match[3] <= max_deviation:
                                            image.draw_pixel(x, y, (255, 255, 255, 0))

                                    for e in events:
                                        if e.type == pygame.QUIT:
                                            stop = True
                                            pygame.event.clear()
                                            break
                                    if stop: break

                                pygame.display.update()

                else:  # tolerance disabled:

                    undo_list.append(image.get_pixel_colors())

                    mouse_pos = pygame.mouse.get_pos()

                    if image.pixel_exists(int((mouse_pos[0] - image.xywh[0]) / image.scale),
                                          int((mouse_pos[1] - image.xywh[1]) / image.scale)):  # starting pixel exists:

                        color_to_match = image.pixels[int((mouse_pos[1] - image.xywh[1]) / image.scale)][
                            int((mouse_pos[0] - image.xywh[0]) / image.scale)].rgba

                        if color_to_match != (255, 255, 255, 0):

                            if fill_alg_visual == "true":  # visualize algorithm:
                                for y in range(image.real_h_in_pixels):
                                    events = pygame.event.get()

                                    for x in range(image.real_w_in_pixels):
                                        # color matches
                                        if image.pixels[y][x].rgba == color_to_match:
                                            image.draw_pixel(x, y, (255, 255, 255, 0))

                                            pygame.display.update()

                                        for e in events:
                                            if e.type == pygame.QUIT:
                                                stop = True
                                                pygame.event.clear()
                                                break
                                        if stop: break

                            else:  # don't visualize algorithm:
                                for y in range(image.real_h_in_pixels):
                                    events = pygame.event.get()

                                    for x in range(image.real_w_in_pixels):
                                        # color matches
                                        if image.pixels[y][x].rgba == color_to_match:
                                            image.draw_pixel(x, y, (255, 255, 255, 0))

                                    for e in events:
                                        if e.type == pygame.QUIT:
                                            stop = True
                                            pygame.event.clear()
                                            break
                                    if stop: break

                                pygame.display.update()

                pygame.event.set_allowed([pygame.QUIT, pygame.VIDEORESIZE, pygame.KEYDOWN])
                continue

            else:  # fill only connected pixels

                if enable_fill_alg_tolerance == "true":  # tolerance enabled:
                    undo_list.append(image.get_pixel_colors())

                    mouse_pos = pygame.mouse.get_pos()

                    pixels = [(int((mouse_pos[0] - image.xywh[0]) / image.scale), int((mouse_pos[1] - image.xywh[1])
                                                                                      / image.scale))]
                    drawn_pixels = []
                    max_deviation = int(256 * fill_alg_tolerance / 100)

                    if image.pixel_exists(*pixels[0]):  # starting pixel exists:
                        color_to_match = image.pixels[int((mouse_pos[1] - image.xywh[1]) / image.scale)][
                            int((mouse_pos[0] -
                                 image.xywh[0]) / image.scale)].rgba

                        if color_to_match != (255, 255, 255, 0):

                            if fill_alg_visual == "true":  # visualize algorithm:
                                while len(pixels) > 0:
                                    events = pygame.event.get()
                                    current_pixel = pixels.pop()
                                    drawn_pixels.append(current_pixel)
                                    image.draw_pixel(current_pixel[0], current_pixel[1], (255, 255, 255, 0))

                                    for pixel in image.get_neighbor_pixels(*current_pixel):
                                        # pixel not visited and color matches (with max_deviation)
                                        if pixel not in drawn_pixels and pixel not in pixels \
                                                and -1 * max_deviation <= image.pixels[pixel[1]][pixel[0]].rgba[0] - \
                                                color_to_match[0] <= max_deviation \
                                                and -1 * max_deviation <= image.pixels[pixel[1]][pixel[0]].rgba[1] - \
                                                color_to_match[1] <= max_deviation \
                                                and -1 * max_deviation <= image.pixels[pixel[1]][pixel[0]].rgba[2] - \
                                                color_to_match[2] <= max_deviation \
                                                and -1 * max_deviation <= image.pixels[pixel[1]][pixel[0]].rgba[3] - \
                                                color_to_match[3] <= max_deviation:
                                            pixels.append(pixel)

                                    pygame.display.update()

                                    for e in events:
                                        if e.type == pygame.QUIT:
                                            pixels = []
                                            pygame.event.clear()
                                            break

                            else:  # don't visualize algorithm:
                                while len(pixels) > 0:
                                    events = pygame.event.get()
                                    current_pixel = pixels.pop()
                                    drawn_pixels.append(current_pixel)
                                    image.draw_pixel(current_pixel[0], current_pixel[1], (255, 255, 255, 0))

                                    for pixel in image.get_neighbor_pixels(*current_pixel):
                                        # pixel not visited and color matches (with max_deviation)
                                        if pixel not in drawn_pixels and pixel not in pixels \
                                                and -1 * max_deviation <= image.pixels[pixel[1]][pixel[0]].rgba[0] - \
                                                color_to_match[0] <= max_deviation \
                                                and -1 * max_deviation <= image.pixels[pixel[1]][pixel[0]].rgba[1] - \
                                                color_to_match[1] <= max_deviation \
                                                and -1 * max_deviation <= image.pixels[pixel[1]][pixel[0]].rgba[2] - \
                                                color_to_match[2] <= max_deviation \
                                                and -1 * max_deviation <= image.pixels[pixel[1]][pixel[0]].rgba[3] - \
                                                color_to_match[3] <= max_deviation:
                                            pixels.append(pixel)

                                    for e in events:
                                        if e.type == pygame.QUIT:
                                            pixels = []
                                            pygame.event.clear()
                                            break

                                pygame.display.update()

                else:  # tolerance disabled:

                    undo_list.append(image.get_pixel_colors())

                    mouse_pos = pygame.mouse.get_pos()

                    pixels = [(int((mouse_pos[0] - image.xywh[0]) / image.scale),
                               int((mouse_pos[1] - image.xywh[1]) / image.scale))]
                    drawn_pixels = []

                    if image.pixel_exists(*pixels[0]):  # starting pixel exists:
                        color_to_match = image.pixels[int((mouse_pos[1] - image.xywh[1]) / image.scale)][
                            int((mouse_pos[0] -
                                 image.xywh[0]) / image.scale)].rgba

                        if color_to_match != (255, 255, 255, 0):

                            if fill_alg_visual == "true":  # visualize algorithm:
                                while len(pixels) > 0:
                                    events = pygame.event.get()
                                    current_pixel = pixels.pop()
                                    drawn_pixels.append(current_pixel)
                                    image.draw_pixel(current_pixel[0], current_pixel[1], (255, 255, 255, 0))

                                    for pixel in image.get_neighbor_pixels(*current_pixel):
                                        if pixel not in drawn_pixels and pixel not in pixels \
                                                and image.pixels[pixel[1]][pixel[0]].rgba == color_to_match:
                                            pixels.append(pixel)

                                    for e in events:
                                        if e.type == pygame.QUIT:
                                            pixels = []
                                            pygame.event.clear()
                                            break

                                    pygame.display.update()

                            else:  # don't visualize algorithm:
                                while len(pixels) > 0:
                                    events = pygame.event.get()
                                    current_pixel = pixels.pop()
                                    drawn_pixels.append(current_pixel)
                                    image.draw_pixel(current_pixel[0], current_pixel[1], (255, 255, 255, 0))

                                    for pixel in image.get_neighbor_pixels(*current_pixel):
                                        if pixel not in drawn_pixels and pixel not in pixels \
                                                and image.pixels[pixel[1]][pixel[0]].rgba == color_to_match:
                                            pixels.append(pixel)

                                    for e in events:
                                        if e.type == pygame.QUIT:
                                            pixels = []
                                            pygame.event.clear()
                                            break

                                pygame.display.update()

                pygame.event.set_allowed([pygame.QUIT, pygame.VIDEORESIZE, pygame.KEYDOWN])
                continue

        # zoom
        if image.hover() and pygame.key.get_mods() & pygame.KMOD_CTRL:
            for e in events:
                if e.type == pygame.MOUSEBUTTONDOWN:
                    # zooming in
                    if e.button == 4 and image.scale < 16:
                        win.fill((200, 200, 200))
                        image.update_scale(image.scale + 1)
                        image.draw_pixels()
                        pygame.display.update()
                        break

                    # zooming out
                    elif e.button == 5 and image.scale > 1:
                        win.fill((200, 200, 200))
                        image.update_scale(image.scale - 1)
                        image.draw_pixels()
                        pygame.display.update()
                        break

        # drag image
        if (selected_tool is None and image.pressed()) or pygame.mouse.get_pressed()[2]:
            temp_surface = pygame.Surface((image.xywh[2], image.xywh[3]))
            image.blit_on_surface(temp_surface)

            # drag loop
            prev_mouse_pos = pygame.mouse.get_pos()
            while image.pressed() or pygame.mouse.get_pressed()[2]:
                mouse_pos = pygame.mouse.get_pos()
                image.xywh[0] = image.xywh[0] + (mouse_pos[0] - prev_mouse_pos[0])
                image.xywh[1] = image.xywh[1] + (mouse_pos[1] - prev_mouse_pos[1])
                win.fill((200, 200, 200))
                win.blit(temp_surface, (image.xywh[0], image.xywh[1]))
                pygame.display.update()

                prev_mouse_pos = mouse_pos
                pygame.event.clear()

            image.update_pos((image.xywh[0], image.xywh[1]))
            image.draw_pixels()

        # event handling
        for e in events:
            if e.type == pygame.VIDEORESIZE:  # resize window
                win = pygame.display.set_mode(e.size, pygame.RESIZABLE)
                win.fill((200, 200, 200))
                image.draw_pixels()
                pygame.display.update()
                break

            if e.type == pygame.QUIT:  # close window
                gui_input_q.put("paint_win_close_request")

            if e.type == pygame.KEYDOWN:
                if e.unicode == "s":  # save shortcut (s)
                    gui_input_q.put("save")

                if e.unicode == "z":  # undo shortcut (z)
                    undo()

                if e.unicode == "y":  # redo shortcut (y)
                    redo()

        pygame.event.clear()
