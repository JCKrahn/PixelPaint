import pygame


class PixelSurface(pygame.Surface):
    def __init__(self, size):
        super(PixelSurface, self).__init__(size)


class Pixel:
    def __init__(self, xywh, rgba, background=(255, 255, 255, 0), transparency_color=None):
        self.xywh = xywh
        self.rgba = rgba
        self.background = background
        self.transparency_color = transparency_color


class Image:
    def __init__(self, win, wh, background=(255, 255, 255, 0), scale=1, input_pixel_colors=None):
        self.parent = win
        self.xywh = [10, 10, wh[0] * scale, wh[1] * scale]
        self.real_w_in_pixels = wh[0]
        self.real_h_in_pixels = wh[1]
        self.scale = scale
        self.pixel_surface = PixelSurface((scale, scale))

        # create pixels

        if wh[0] % 2 == 0:  # if even width
            if not input_pixel_colors:
                if background == (255, 255, 255, 0):
                    self.pixels = []
                    y = 0
                    n = -1  # transparency color alternately white, grey
                    for row in range(wh[1]):
                        row = []
                        x = 0
                        n = n * -1
                        for pixel in range(wh[0]):
                            if n == 1:
                                row.append(
                                    Pixel([x + self.xywh[0], y + self.xywh[1], self.scale, self.scale],
                                          (255, 255, 255, 0), background, (220, 220, 220)))
                            elif n == -1:
                                row.append(
                                    Pixel([x + self.xywh[0], y + self.xywh[1], self.scale, self.scale],
                                          (255, 255, 255, 0), background, (160, 160, 160)))
                            x += scale
                            n = n * -1
                        self.pixels.append(row)
                        y += scale
                else:
                    self.pixels = []
                    y = 0
                    n = -1
                    for row in range(wh[1]):
                        row = []
                        x = 0
                        n = n * -1
                        for pixel in range(wh[0]):
                            if n == 1:
                                row.append(Pixel([x + self.xywh[0], y + self.xywh[1], self.scale, self.scale],
                                    background, background, (220, 220, 220)))
                            else:
                                row.append(Pixel([x + self.xywh[0], y + self.xywh[1], self.scale, self.scale],
                                    background, background, (160, 160, 160)))
                            x += scale
                            n = n * -1
                        self.pixels.append(row)
                        y += scale

            else:  # create pixels from list of pixel colors
                self.pixels = []
                y = 0
                n = -1  # transparency color alternately white, grey
                for row_n in input_pixel_colors:
                    row = []
                    x = 0
                    n = n * -1
                    for pixel in row_n:
                        if n == 1:
                            row.append(Pixel([x + self.xywh[0], y + self.xywh[1], self.scale, self.scale], pixel,
                                (255, 255, 255, 0), (220, 220, 220)))
                            x += scale
                        elif n == -1:
                            row.append(Pixel([x + self.xywh[0], y + self.xywh[1], self.scale, self.scale], pixel,
                                (255, 255, 255, 0), (160, 160, 160)))
                            x += scale
                        n = n * -1
                    self.pixels.append(row)
                    y += scale

        else:  # if uneven width
            if not input_pixel_colors:
                if background == (255, 255, 255, 0):
                    self.pixels = []
                    y = 0
                    n = -1  # transparency color alternately white, grey
                    for row in range(wh[1]):
                        row = []
                        x = 0
                        for pixel in range(wh[0]):
                            if n == 1:
                                row.append(
                                    Pixel([x + self.xywh[0], y + self.xywh[1], self.scale, self.scale],
                                          (255, 255, 255, 0), background, (220, 220, 220)))
                            elif n == -1:
                                row.append(
                                    Pixel([x + self.xywh[0], y + self.xywh[1], self.scale, self.scale],
                                          (255, 255, 255, 0), background, (160, 160, 160)))
                            x += scale
                            n = n * -1
                        self.pixels.append(row)
                        y += scale
                else:
                    self.pixels = []
                    y = 0
                    n = -1
                    for row in range(wh[1]):
                        row = []
                        x = 0
                        for pixel in range(wh[0]):
                            if n == 1:
                                row.append(
                                    Pixel([x + self.xywh[0], y + self.xywh[1], self.scale, self.scale],
                                          background, background, (220, 220, 220)))
                            else:
                                row.append(
                                    Pixel([x + self.xywh[0], y + self.xywh[1], self.scale, self.scale],
                                          background, background, (160, 160, 160)))
                            x += scale
                            n = n * -1
                        self.pixels.append(row)
                        y += scale

            else:  # create pixels from list of pixel colors
                self.pixels = []
                y = 0
                n = -1  # transparency color alternately white, grey
                for row_n in input_pixel_colors:
                    row = []
                    x = 0
                    for pixel in row_n:
                        if n == 1:
                            row.append(Pixel([x + self.xywh[0], y + self.xywh[1], self.scale, self.scale], pixel,
                                (255, 255, 255, 0), (220, 220, 220)))
                            x += scale
                        elif n == -1:
                            row.append(Pixel([x + self.xywh[0], y + self.xywh[1], self.scale, self.scale], pixel,
                                (255, 255, 255, 0), (160, 160, 160)))
                            x += scale
                        n = n * -1
                    self.pixels.append(row)
                    y += scale

        self.draw_pixels()

    def draw_pixels(self):
        for row in self.pixels:
            for pixel in row:
                if pixel.rgba[3] == 0:
                    self.pixel_surface.fill(pixel.transparency_color)
                else:
                    self.pixel_surface.fill(pixel.rgba)
                self.parent.blit(self.pixel_surface, pixel.xywh)

    def draw_pixel(self, x, y, color=None):  # (+ change color)
        if x >= 0 and y >= 0:
            if color is not None:
                self.pixels[y][x].rgba = color
            if self.pixels[y][x].rgba[3] == 0:
                self.pixel_surface.fill(self.pixels[y][x].transparency_color)
            else:
                self.pixel_surface.fill(self.pixels[y][x].rgba)
            self.parent.blit(self.pixel_surface, self.pixels[y][x].xywh)

    def erase_pixel(self, x, y):
        if x >= 0 and y >= 0:
            self.pixels[y][x].rgba = self.pixels[y][x].background
            if self.pixels[y][x].rgba[3] == 0:
                self.pixel_surface.fill(self.pixels[y][x].transparency_color)
            else:
                self.pixel_surface.fill(self.pixels[y][x].rgba)
            self.parent.blit(self.pixel_surface, self.pixels[y][x].xywh)

    def hover(self):
        if self.xywh[0] <= pygame.mouse.get_pos()[0] <= self.xywh[0] + self.xywh[2] \
                and self.xywh[1] + self.xywh[3] >= pygame.mouse.get_pos()[1] >= self.xywh[1]:
            return True
        return False

    def pressed(self):
        if self.xywh[0] <= pygame.mouse.get_pos()[0] <= self.xywh[0] + self.xywh[2] \
                and self.xywh[1] + self.xywh[3] >= pygame.mouse.get_pos()[1] >= self.xywh[1] \
                and pygame.mouse.get_pressed()[0]:
            return True
        return False

    def update_pos(self, xy):
        self.xywh = [xy[0], xy[1], self.xywh[2], self.xywh[3]]

        y = 0
        for row in self.pixels:
            x = 0
            for pixel in row:
                pixel.xywh = (x + self.xywh[0], y + self.xywh[1], pixel.xywh[2], pixel.xywh[3])
                x += self.scale
            y += self.scale

    def update_scale(self, new_scale):
        self.xywh = [self.xywh[0], self.xywh[1], self.xywh[2] / self.scale * new_scale,
                     self.xywh[3] / self.scale * new_scale]
        self.scale = new_scale
        self.pixel_surface = PixelSurface((self.scale, self.scale))
        self.pixel_surface.convert()

        y = 0
        for row in self.pixels:
            x = 0
            for pixel in row:
                pixel.xywh = [x + self.xywh[0], y + self.xywh[1], self.scale, self.scale]
                x += self.scale
            y += self.scale

    def update_pixel_colors(self, pixels):
        y = 0
        for row in pixels:
            x = 0
            for pixel in row:
                self.pixels[y][x].rgba = pixel
                x += 1
            y += 1

    def blit_on_surface(self, surface):
        for row in self.pixels:
            for pixel in row:
                if pixel.rgba[3] == 0 and pixel.transparency_color is not None:
                    self.pixel_surface.fill(pixel.transparency_color)
                else:
                    self.pixel_surface.fill(pixel.rgba)
                surface.blit(self.pixel_surface, (pixel.xywh[0] - self.xywh[0], pixel.xywh[1] - self.xywh[1]))

    def pixel_exists(self, x, y):
        if self.real_w_in_pixels > x >= 0 and self.real_h_in_pixels > y >= 0:
            return True
        return False

    def get_neighbor_pixels(self, x, y):  # (not diagonally)
        pixels = []
        if self.real_w_in_pixels > x+1 >= 0 and self.real_h_in_pixels > y >= 0:
            pixels.append((x+1, y))
        if self.real_w_in_pixels > x >= 0 and self.real_h_in_pixels > y+1 >= 0:
            pixels.append((x, y+1))
        if self.real_w_in_pixels > x-1 >= 0 and self.real_h_in_pixels > y >= 0:
            pixels.append((x-1, y))
        if self.real_w_in_pixels > x >= 0 and self.real_h_in_pixels > y-1 >= 0:
            pixels.append((x, y-1))
        return pixels

    def get_pixel_colors(self):
        pixels = []
        for row_n in self.pixels:
            row = []
            for pixel in row_n:
                row.append(pixel.rgba)
            pixels.append(row)
        return pixels
