# Zerynth - libs - sitronix-st7735/st7735.py
#
# Zerynth library for ST7735 display
#
# @Author: Stefano Torneo
#
# @Date: 2020-09-17
# @Last Modified by: 
# @Last Modified time:

"""
.. module:: ST7735

**************
ST7735 Module
**************

This module exposes all functionalities of Sitronix ST7735 Display driver (`datasheet <https://www.displayfuture.com/Display/datasheet/controller/ST7735.pdf>`_).
    """

import spi

# Constants for interacting with display registers.
ST7735_TFTWIDTH = 80
ST7735_TFTHEIGHT = 160

ST7735_COLS = 132
ST7735_ROWS = 162

ST7735_NOP = 0x00
ST7735_SWRESET = 0x01
ST7735_RDDID = 0x04
ST7735_RDDST = 0x09

ST7735_SLPIN = 0x10
ST7735_SLPOUT = 0x11
ST7735_PTLON = 0x12
ST7735_NORON = 0x13

ST7735_INVOFF = 0x20
ST7735_INVON = 0x21
ST7735_DISPOFF = 0x28
ST7735_DISPON = 0x29

ST7735_CASET = 0x2A
ST7735_RASET = 0x2B
ST7735_RAMWR = 0x2C
ST7735_RAMRD = 0x2E

ST7735_PTLAR = 0x30
ST7735_COLMOD = 0x3A

# Rotation cmd
ST7735_MADCTL = 0x36
# Rotation data
ST7735_MAD_MY  = 0x80
ST7735_MAD_MX  = 0x40
ST7735_MAD_MV  = 0x20
ST7735_MAD_ML  = 0x10
ST7735_MAD_BGR = 0x08
ST7735_MAD_MH  = 0x04
ST7735_MAD_RGB = 0x00

ST7735_FRMCTR1 = 0xB1
ST7735_FRMCTR2 = 0xB2
ST7735_FRMCTR3 = 0xB3
ST7735_INVCTR = 0xB4
ST7735_DISSET5 = 0xB6

ST7735_PWCTR1 = 0xC0
ST7735_PWCTR2 = 0xC1
ST7735_PWCTR3 = 0xC2
ST7735_PWCTR4 = 0xC3
ST7735_PWCTR5 = 0xC4
ST7735_VMCTR1 = 0xC5

ST7735_RDID1 = 0xDA
ST7735_RDID2 = 0xDB
ST7735_RDID3 = 0xDC
ST7735_RDID4 = 0xDD

ST7735_GMCTRP1 = 0xE0
ST7735_GMCTRN1 = 0xE1

ST7735_PWCTR6 = 0xFC

# Colours
ST7735_BLACK = 0x0000  # 0b 00000 000000 00000
ST7735_BLUE = 0x001F  # 0b 00000 000000 11111
ST7735_GREEN = 0x07E0  # 0b 00000 111111 00000
ST7735_RED = 0xF800  # 0b 11111 000000 00000
ST7735_CYAN = 0x07FF  # 0b 00000 111111 11111
ST7735_MAGENTA = 0xF81F  # 0b 11111 000000 11111
ST7735_YELLOW = 0xFFE0  # 0b 11111 111111 00000
ST7735_WHITE = 0xFFFF  # 0b 11111 111111 11111

OLED_TEXT_ALIGN_NONE    = 0
OLED_TEXT_ALIGN_LEFT    = 0x1
OLED_TEXT_ALIGN_RIGHT   = 0x2
OLED_TEXT_ALIGN_CENTER  = 0x3
OLED_TEXT_VALIGN_TOP    = 0x10
OLED_TEXT_VALIGN_BOTTOM = 0x20
OLED_TEXT_VALIGN_CENTER = 0x30

OLED_TEXT_ALIGN = [
    OLED_TEXT_ALIGN_NONE,
    OLED_TEXT_ALIGN_LEFT,
    OLED_TEXT_ALIGN_RIGHT,
    OLED_TEXT_ALIGN_CENTER,
    OLED_TEXT_VALIGN_TOP,
    OLED_TEXT_VALIGN_BOTTOM,
    OLED_TEXT_VALIGN_CENTER
]

class ST7735(spi.Spi):
    """
    
===============
 ST7735 class
===============

.. class:: ST7735(drv, cs, dc, bl=None, rst=None, clock=27000000)

    Creates an intance of a new ST7735.

    :param drv: SPI Bus used '( SPI0, ... )'
    :param cs: Chip Select
    :param dc: Data Control Pin
    :param bl: Backlight Pin
    :param rst: Reset Pin
    :param clock: Clock speed, default 100kHz

    Example: ::

        from sitronix.st7735 import st7735

        ...

        display = st7735.ST7735(SPI0, D5, D23, bl=D27, rst=D26)
        display.clear()
        display.fill_screen([255,0,0])
        display.fill_rect(10, 20, 20, 100, [255,255,0])
        display.draw_pixel(50, 50, [255,255,255])
        display.draw_line(30, 20, 100, [0,0,255])
        display.draw_text("Hello Zerynth")

    """ 
    # list of configuration to set the rotation
    rotation_settings = [
        [ST7735_MAD_MX | ST7735_MAD_MY | ST7735_MAD_MH | ST7735_MAD_BGR, 26, 1, ""],
        [ST7735_MAD_MV | ST7735_MAD_MY | ST7735_MAD_BGR, 1, 26, "swap"],
        [ST7735_MAD_BGR, 26, 1, ""],
        [ST7735_MAD_MX | ST7735_MAD_MV | ST7735_MAD_BGR, 1, 26, "swap"]
    ]

    def __init__(self, drv, cs, dc, bl=None, rst=None, clock=27000000):

        spi.Spi.__init__(self, cs, drv, clock)
        self.dc = dc
        self.backlight = bl
        self.rst = rst
        self.font_init = False
        self.dynamic_area = {
            "x": 0,
            "y": 0,
            "width": 0,
            "height": 0,
            "buffer": None
        }
        self.buf = bytearray(1)
        self.s_buf = None
        self.c_buf = None

        pinMode(self.dc, OUTPUT)

        if self.rst is not None:
            pinMode(self.rst, OUTPUT)
        
        # Set backlight as output (if provided).
        if self.backlight is not None:
            pinMode(self.backlight, OUTPUT)
            self.set_backlight(0)
            sleep(1)
            self.set_backlight(1)
    
        self.width = ST7735_TFTWIDTH
        self.height = ST7735_TFTHEIGHT

        # reset display and call _init()
        self.reset()

    ##
    ## @brief      Init the display.
    ##
    ## @param      self
    ## @return     nothing
    ##
    def _init(self):
        
        self._command(ST7735_SWRESET) # Software reset
        sleep(150)

        self._command(ST7735_SLPOUT) # Out of sleep mode
        sleep(500)

        self._command(ST7735_FRMCTR1) # Frame rate ctrl
        self._data(0x01) # Rate = fosc/(1x2+40) * (LINE+2C+2D)
        self._data(0x2C)
        self._data(0x2D)
        
        self._command(ST7735_FRMCTR2) # Frame rate ctrl
        self._data(0x01)
        self._data(0x2C)
        self._data(0x2D)

        self._command(ST7735_FRMCTR3) # Frame rate ctrl
        self._data(0x01)
        self._data(0x2C)
        self._data(0x2D)
        self._data(0x01)
        self._data(0x2C)
        self._data(0x2D)

        self._command(ST7735_INVCTR) # Display inversion ctrl
        self._data(0x07) # No inversion

        self._command(ST7735_PWCTR1) # Power control
        self._data(0xA2)
        self._data(0x02) # GVDD = 4.7V
        self._data(0x84) # 1.0uA

        self._command(ST7735_PWCTR2) # Power control
        self._data(0xC5) # VGH25 = 2.4C VGSEL = -10 VGH = 3 * AVDD

        self._command(ST7735_PWCTR3) # Power control
        self._data(0x0A)
        self._data(0x00)

        self._command(ST7735_PWCTR4) # Power control
        self._data(0x8A)
        self._data(0x2A)

        self._command(ST7735_PWCTR5) # Power control
        self._data(0x8A)
        self._data(0xEE)

        self._command(ST7735_VMCTR1)
        self._data(0x0E)

        self.set_invert(1)

        self.set_rotation()

        self._command(ST7735_COLMOD) # Set color mode
        self._data(0x05)

        self._command(ST7735_CASET) # Column addr set
        self._data(0x00) # XSTART = 0
        self._data(0x00)
        self._data(0x00)               
        self._data(0x7F) # XEND = 127

        self._command(ST7735_RASET) # Row addr set
        self._data(0x00) # YSTART = 0
        self._data(0x00)
        self._data(0x00)
        self._data(0x9F) # YEND = 159

        self._command(ST7735_GMCTRP1) # Set Gamma
        self._data(0x2C)
        self._data(0x1C)
        self._data(0x07)
        self._data(0x12)
        self._data(0x37)
        self._data(0x32)
        self._data(0x29)
        self._data(0x2D)
        self._data(0x29)
        self._data(0x25)
        self._data(0x2B)
        self._data(0x39)
        self._data(0x00)
        self._data(0x01)
        self._data(0x03)
        self._data(0x10) 

        self._command(ST7735_NORON) # Normal display on
        sleep(10)

        self._command(ST7735_DISPON) # Display on
        sleep(100)

    ##
    ## @brief      Send a command to display.
    ##
    ## @param      self
    ## @param      cmd   is the command to send
    ## @return     nothing
    ##
    def _command(self, cmd):
        self.select()
        digitalWrite(self.dc, 0)
        self.buf[0] = cmd
        self.write(self.buf)
        self.unselect()
    
    ##
    ## @brief      Send a data to display.
    ##
    ## @param      self
    ## @param      data   is data to send
    ## @return     nothing
    ##
    def _data(self, data):
        self.select()
        digitalWrite(self.dc, 1)
        self.buf[0] = data
        self.write(self.buf)
        self.unselect()
    
    ##
    ## @brief      Send a data as bitearray to display.
    ##
    ## @param      self
    ## @param      data   is data to send
    ## @return     nothing
    ##
    def _send_data(self, data):
        self.select()
        digitalWrite(self.dc, 1)
        self.write(data)
        self.unselect()

    def on(self):
        """

    .. method:: on()

        Turns on the display.

        """
        self._command(ST7735_DISPON)
        
    def off(self):
        """

    .. method:: off()

        Turns off the display.

        """
        self._command(ST7735_DISPOFF)

    def reset(self):
        """
    .. method:: reset()

        Reset the display.
        
        """
        if self.rst is not None:
            digitalWrite(self.rst, 0)
            sleep(100)
            digitalWrite(self.rst, 1)
            sleep(100)
        self._init()

    def set_rotation(self, rotation=1):
        """
    .. method:: set_rotation(rotation = 1)

        :param rotation: is the rotation value to set (default = 1). Values accepted: 0, 1, 2 or 3.

        Set the direction of frame memory.
        
        """
        if (rotation not in [0, 1, 2, 3]):
            raise ValueError

        self._command(ST7735_MADCTL)
        self.rotation = rotation
        values = self.rotation_settings[self.rotation]
        self._data(values[0])
        self.colstart = values[1]
        self.rowstart = values[2]
        if (values[3] == "swap"):
            self.width  = ST7735_TFTHEIGHT
            self.height = ST7735_TFTWIDTH
        else:
            self.width = ST7735_TFTWIDTH
            self.height = ST7735_TFTHEIGHT

    def set_backlight(self, state):
        """
    .. method:: set_backlight(state)

        :param state: is the state of backlight. Values accepted: 0 or 1.

        Set the backlight.
        
        """
        if self.backlight is not None:
            digitalWrite(self.backlight, state)
    
    def set_invert(self, value):
        """
    .. method:: invert(value)

        :param value: is the value of display inversion mode. Values accepted: 0 or 1.

        Set the display inversion mode.
        
        """
        if value:
            self._command(ST7735_INVON)   # Invert display
        else:
            self._command(ST7735_INVOFF)  # Don't invert display
    
    ##
    ## @brief      Convert red, green, blue components to a 16-bit 565 RGB value. Components should be values 0 to 255. 
    ##
    ## @param      self
    ## @return     red, green, blue values in a 16-bit 565 RGB value.
    ##
    def _color565(self, color):
        r = color[0]
        g = color[1]
        b = color[2]
        return ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)

    ##
    ## @brief      Set the color. 
    ##
    ## @param      self
    ## @param      color   is a rgb color
    ## @return     a list composed by the two byte of the color
    ##
    def _set_color(self, color):
        color = self._color565(color)
        d1 = color >> 8
        d2 = color & 0x00FF
        return d1, d2

    ##
    ## @brief      Create and send a bytearray buffer.
    ##
    ## @param      self
    ## @param      lenght  is the lenght of buffer
    ## @param      d1      is the first byte of color
    ## @param      d2      is the second byte of color
    ## @return     nothing
    ##
    def _create_send_buffer(self, lenght, d1, d2):
        self.s_buf = bytearray(lenght*2)
        for i in range(lenght):
            self.s_buf[2*i] = d1
            self.s_buf[(2*i)+1] = d2
        self._send_data(self.s_buf)
        self.s_buf = None
    
    ##
    ## @brief      Set the pixel address window for proceeding drawing commands.
    ##
    ## @param      self
    ## @param      x0  is the minimum x pixel bound
    ## @param      y0  is the minimum y pixel bound
    ## @param      x1  is the maximum x pixel bound
    ## @param      y1  is the maximum y pixel bound
    ## @return     nothing
    ##
    def _prepare(self, x0=0, y0=0, x1=0, y1=0):

        x0 += self.colstart
        x1 += self.colstart
        y0 += self.rowstart
        y1 += self.rowstart

        self._command(ST7735_CASET) # Coloumn addr set
        self._data(x0 >> 8)
        self._data(x0) # XSTART
        self._data(x1 >> 8)
        self._data(x1) # XEND
        self._command(ST7735_RASET) # Row addr set
        self._data(y0 >> 8)
        self._data(y0) # YSTART
        self._data(y1 >> 8)
        self._data(y1) # YEND
        self._command(ST7735_RAMWR)  

    def clear(self):
        """
    .. method:: clear()

        Clears the display.

        """
        self.fill_screen([0,0,0])

    def fill_screen(self, color):
        """
    .. method:: fill_screen(color)

        :param color: is a list composed by RGB color.

        Fills the entire display with RGB color provided as argument.

        """
        if (type(color) != PLIST):
            raise ValueError
        
        self.fill_rect(0, 0, self.width, self.height, color)

    def fill_rect(self, x, y, w, h, color):
        """
    .. method:: fill_rect(x, y, w, h, color)

        :param x: x-coordinate for left high corner of the rectangular area.
        :param y: y-coordinate for left high corner of the rectangular area.
        :param w: width of the rectangular area.
        :param h: height of the rectangular area.
        :param color: is a list composed by RGB color for the rectangular area.

        Draws a rectangular area in the screen colored with the RGB color provided as argument.

        """
        if (x > self.width or y > self.height):
            raise ValueError

        if (w < 1) or (h < 1) or (x < 0) or (y < 0):
            raise ValueError

        if type(color) != PLIST:
            raise ValueError
        
        # check if coordinates are in the border of the display
        if (x == self.width):
            x = self.width - 1
        if (y == self.height):
            y = self.height - 1

        # check if rect goes out of the display
        if (x + w) > self.width:
            w = self.width - x
        if (y + h) > self.height:
            h = self.height - y

        self._prepare(x, y, x + w - 1, y + h - 1)
        d1, d2 = self._set_color(color)
        lenght = w*h
        self._create_send_buffer(lenght, d1, d2)
    
    def draw_pixel(self, x, y, color):
        """
    .. method:: draw_pixel(x, y, color)

        :param x: pixel x-coordinate.
        :param y: pixel y-coordinate.
        :param color: is a list composed by RGB color.

        Draws a single pixel in the screen colored with the RGB color provided as argument.

        """
        if (x > self.width or y > self.height):
            raise ValueError

        if (x < 0 or y < 0):
            raise ValueError
        
        if type(color) != PLIST:
            raise ValueError
        
        # check if coordinates are in the border of the display
        if (x == self.width):
            x = self.width - 1
        if (y == self.height):
            y = self.height - 1

        self._prepare(x, y, 1, 1)
        d1, d2 = self._set_color(color)
        self._send_data(bytearray([d1,d2]))
    
    def draw_line(self, x, y, lenght, color):
        """
    .. method:: draw_line(x, y, lenght, color)

        :param x: pixel x-coordinate.
        :param y: pixel y-coordinate.
        :param lenght: is the lenght of line.
        :param color: is a list composed by RGB color.

        Draws a line in the screen colored with the RGB color provided as argument.

        """
        if (x > self.width or y > self.height):
            raise ValueError

        if (x < 0 or y < 0 or lenght < 1):
            raise ValueError
            
        if type(color) != PLIST:
            raise ValueError
    
        # check if coordinates are in the border of the display
        if (x == self.width):
            x = self.width - 1
        if (y == self.height):
            y = self.height - 1
        
        # check if line goes out of the display
        if (x + lenght) > self.width:
            w = self.width - x

        d1, d2 = self._set_color(color)
        self._prepare(x, y, x+lenght-1, y)
        self._create_send_buffer(lenght, d1, d2)
    
    def draw_img(self, image, x=0, y=0, w=80, h=80):
        """
    .. method:: draw_img(image, x=0, y=0, w=80, h=80)

        :param image: image to draw in the display converted to hex array format and passed as bytearray.
        :param x: x-coordinate for left high corner of the image (default value is 0).
        :param y: y-coordinate for left high corner of the image (default value is 0).
        :param w: width of the image (default value is 80).
        :param h: height of the image (default value is 80).

        Draws the image passed in bytearray format as argument.

        .. note :: To obtain a converted image in hex array format, you can go and use this `online tool <http://www.digole.com/tools/PicturetoC_Hex_converter.php>`_.
                   
                   After uploading your image, you can resize it setting the width and height fields; you can also choose the code format (HEX:0x recommended) and the color format
                   (65K color recommended).
                   
                   Clicking on the "Get C string" button, the tool converts your image with your settings to a hex string that you can copy and paste inside a bytearray in your project and privide to this function.
        """
        if type(image) != PBYTEARRAY:
            raise ValueError
        
        if (x > self.width or y > self.height):
            raise ValueError

        if (x < 0 or y < 0 or w < 1 or h < 1):
            raise ValueError
        self._prepare(x, y, x+w-1, y+h-1)
        self._send_data(image)
    
    ##
    ## @brief      Set the font of text.
    ##
    ## @param      self
    ## @param      font is the font text
    ## @param      font_color is the font color
    ## @return     nothing
    ##
    def _set_font(self, font=None, font_color=None):
        try:
            if font != None:
                self.font = font
                self.first_char = font[2] | font[3] << 8
                self.last_char = font[4] | font[5] << 8
                self.font_height = font[6]
            if font_color == None:
                font_color = [255, 255, 255]
            self.font_color = self._set_color(font_color)
        except Exception as e:
            print("font not recognized:", e)

    ##
    ## @brief      Set the align and background color of text.
    ##
    ## @param      self
    ## @param      align is the align of text
    ## @param      background is the background color
    ## @return     nothing
    ##
    def _set_text_prop(self, align=None, background=None):
        if align not in OLED_TEXT_ALIGN:
            align = OLED_TEXT_ALIGN_CENTER
        self.align = align
        if (background == None):
            background = [0, 0, 0]
        self.background = self._set_color(background)

    ##
    ## @brief      Get the text width.
    ##
    ## @param      self
    ## @param      text is the text to write on display
    ## @return     nothing
    ##
    def _get_text_width(self, text):
        t_width = 0
        for c in text:
            index = 8 + ((ord(c) - self.first_char) << 2)
            t_width += self.font[index]
            # insert 1 px for space
            t_width += 1
        # remove last space
        t_width -= 1
        return t_width

    ##
    ## @brief      Add text for dynamic area.
    ##
    ## @param      self
    ## @param      text is the text to put in dynamic area
    ## @return     nothing
    ##
    def _add_text(self, text):
        t_width = self._get_text_width(text)

        if self.dynamic_area["width"]<t_width or self.dynamic_area["height"]<self.font_height:
            # resize dynamic area
            self.dynamic_area["width"] = t_width
            self.dynamic_area["height"]=self.font_height
        y = (self.dynamic_area["height"] - self.font_height) >> 1

        if self.align == OLED_TEXT_ALIGN_LEFT:
            x = 0
        elif self.align == OLED_TEXT_ALIGN_RIGHT:
            x = self.dynamic_area["width"] - t_width
        elif self.align == OLED_TEXT_ALIGN_CENTER:
            x = ((self.dynamic_area["width"] - t_width)//2)
        elif self.align == OLED_TEXT_ALIGN_NONE:
            x = 0
       
        # write the characters into designated space, one by one
        self._create_text_background()
        for c in text:
            c_width = self._write_c_to_buf(c)
            idx = ((y*self.dynamic_area["width"]*2) + x*2)#+OLED_COLUMN_OFFSET
            self._add_char_to_dynamic_area(idx, c_width)
            x += c_width + 1
            self.c_buf = None

    ##
    ## @brief      Create the text background.
    ##
    ## @param      self
    ## @return     nothing
    ##
    def _create_text_background(self):
        count = 0
        area = self.dynamic_area["width"]*self.dynamic_area["height"]
        self.dynamic_area["buffer"] = bytearray(area*2)
        while count < area:
            self.dynamic_area["buffer"][2*count] = self.background[0]
            self.dynamic_area["buffer"][(2*count) + 1] = self.background[1]
            count +=1

    ##
    ## @brief      Add char to dynamic area.
    ##
    ## @param      self
    ## @param      idx 
    ## @param      c_width
    ## @param      c_height
    ## @return     nothing
    ##
    def _add_char_to_dynamic_area(self, idx, c_width, c_height):
        x_count = 0
        for b in self.c_buf:
            self.dynamic_area["buffer"][idx] = b
            x_count += 1
            if x_count == c_width*2:
                x_count = 0
                idx += (self.dynamic_area["width"]-c_width)*2
            idx += 1

    ##
    ## @brief      Add elements to buffer for dynamic area.
    ##
    ## @param      self
    ## @param      c
    ## @return     nothing
    ##
    def _write_c_to_buf(self, c):
        idx = 8 + ((ord(c) - self.first_char) << 2)
        c_width = self.font[idx]
        offset = self.font[idx+1] | (self.font[idx+2] << 8) | (self.font[idx+3] << 16)
        area = self.font_height*c_width
        self.c_buf = bytearray(area*2)
        cnt = 0
        x_count = 0
        while cnt < area:
            if x_count == 0:
                mask = 1
                byte = self.font[offset]
            if (byte & mask) != 0:
                self.c_buf[cnt*2] = self.font_color[0]
                self.c_buf[(cnt*2) + 1] = self.font_color[1]
            else:
                self.c_buf[cnt*2] = self.background[0]
                self.c_buf[(cnt*2) + 1] = self.background[1]
            mask = mask << 1
            cnt += 1
            x_count += 1
            if x_count == c_width:
                x_count = 0
                offset += 1
        return c_width
        

    def draw_text(self, text, x=0, y=0, w=None, h=None, font_text=None, font_color=None, align=3, background=None):
        """
    .. method:: draw_text(text, x=0, y=0, w=None, h=None, font_text=None, font_color=None, align=3, background=None)

        **Parameters:**

        **text:** string to be written in the display.

        **x:** x-coordinate for left high corner of the text box (default value is 0).

        **y:** y-coordinate for left high corner of the text box (default value is 0).

        **w:** width of the text box (default value is None).

        **h:** height of the text box (default value is None).

        **font_text:** is text font (default value is None). You can pass a font like showing in "write on display" example.

        **font_color:** is a list of RGB color for the font color (default value is None).
        
        **align:** alignment of the text inside the text box (default value is 3).
        
        ======== =====================
         align       Alignment
        ======== =====================
         0         None
         1         Left
         2         Right
         3         Center
        ======== =====================

        **background:** is a list composed by RGB color (default value is None).

        Prints a string inside a text box in the screen.
        """
        if (x > self.width or y > self.height):
            raise ValueError
        
        if (x < 0 or y < 0):
            raise ValueError

        if (w != None and w < 1) or (h != None and h < 1):
            raise ValueError

        if (font_color != None and type(font_color) != PLIST) or (background != None and type(background) != PLIST):
            raise ValueError
        
        if (font_text == None):
            from sitronix.st7735 import fonts
            font_text = fonts.guiFont_Tahoma_7_Regular
        self._set_font(font=font_text, font_color=font_color)
        self._set_text_prop(align=align, background=background)
       
        if w is None:
            w = self._get_text_width(text)
        if h is None:
            h = self.font_height

        # create dynamic area    
        self.dynamic_area["x"] = x
        self.dynamic_area["y"] = y
        self.dynamic_area["width"] = w
        self.dynamic_area["height"] = h
        self._add_text(text)
        self._prepare(self.dynamic_area["x"], self.dynamic_area["y"], self.dynamic_area["x"]+self.dynamic_area["width"]-1, self.dynamic_area["y"]+self.dynamic_area["height"]-1)
        self._send_data(self.dynamic_area["buffer"])
        self.dynamic_area["buffer"] = None
