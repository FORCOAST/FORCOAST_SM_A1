#(C) Copyright FORCOAST H2020 project under Grant No. 870465. All rights reserved.

# Copyright notice
# --------------------------------------------------------------------
#  Copyright 2022 Deltares
#   Luis Rodriguez Galvez
#
#   luis.rodriguez@deltares.nl
#
#    This work is licenced under a Creative Commons Attribution 4.0 
#	 International License.
#
#
#        https://creativecommons.org/licenses/by/4.0/
# --------------------------------------------------------------------

import PIL
from PIL import Image, ImageDraw,ImageFont 
import os
import os.path, time
import sys, getopt
import csv
import glob



img_bulletin = Image.open('./output/forcoast_a1_bulletin_temp.png')
img_logo = Image.open('./FORCOAST_Logo_WhiteBack.png')
img_footer = Image.open('./FORCOAST_Footer_Blue.png')

img_bulletin_Width , img_bulletin_Height  = img_bulletin.size
img_logo_Width     , img_logo_Height      = img_logo.size
img_footer_Width   , img_footer_Height    = img_footer.size

margin = 25

# Resize the logo

img_logo_new_Height = 220

img_logo_height_percent = (img_logo_new_Height / float(img_logo.size[1]))
img_logo_new_Width = int((float(img_logo.size[0]) * float(img_logo_height_percent)))
img_logo_new = img_logo.resize((img_logo_new_Width, img_logo_new_Height), PIL.Image.NEAREST)

# Generate the new combined image

newImg = Image.new('RGBA', (img_bulletin_Width+3*margin, 4*margin + img_logo_new_Height + img_bulletin_Height + img_footer_Height), (255, 255, 255))

newImg.paste(img_logo_new , (margin                                     , margin))
newImg.paste(img_bulletin      , (margin                        , margin + img_logo_new_Height))
newImg.paste(img_footer   , (-20*margin                                     , 4*margin + img_bulletin_Height + img_logo_new_Height))

font_path_1 = "ariali.ttf"
font_1 = ImageFont.truetype(font_path_1, 36)

font_path_2 = "ariali.ttf"
font_2 = ImageFont.truetype(font_path_2, 20)

font_path_3 = "arialbd.ttf"
font_3 = ImageFont.truetype(font_path_3, 60)

# print("last modified: %s" % time.ctime(os.path.getmtime(file)))
filecreated = time.ctime(os.path.getctime('./output/forcoast_a1_bulletin_temp.png'))

draw = PIL.ImageDraw.Draw(newImg)
draw.text(((img_logo_new_Width + 510, img_logo_new_Height / 2.6)), ('MARINE CONDITIONS SERVICE'), font=font_3,fill=(23,111,176,255))
draw.text((img_bulletin_Width - 400, img_logo_new_Height - 200 ), ('Bulletin generated on: ' + filecreated), font=font_2,fill=(0,0,0,255))


newImg.save('./output/bulletin.png', quality = 95)
