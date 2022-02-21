''' 
	This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
    Author: Alessandro Capezzera <Demacri>
'''
import os
import sys
import cv2
import re
from skimage.metrics import structural_similarity as ssim
from PIL import Image, ImageChops

def removePointer(images):
    if len(images) <= 1:
        return None
    if(len(images) == 2):
        os.remove(images[1])
        return None
    fn1 = images.pop(0)
    img1 = Image.open(fn1)
    pixR = img1.load()
    fn2 = images.pop(0)
    img2 = Image.open(fn2)
    pix2 = img2.load()
    diff = ImageChops.difference(img1,img2)
    pixdiff = diff.load()
    diffPixelsList = []
    for col in range(0,img1.size[0]):
        for row in range(0,img1.size[1]):
            if pixdiff[col,row] != (0,0,0):
                diffPixelsList.append([col,row])

    while(len(images) > 0):
        fn3 = images.pop(0)
        img3 = Image.open(fn3)
        pix3 = img3.load()
        diff = ImageChops.difference(img1,img3)
        pixdiff = diff.load()
        newDiffPixelsList = []
        for p in diffPixelsList:
            # if(pixR[p[0],p[1]] == pix3[p[0],p[1]]): #pixel X,Y at img 1 is equal to pixel X2,Y2 at img 3, so in the img 2 there's a pointer
                #it's already ok
            if pix2[p[0],p[1]] == pix3[p[0],p[1]]:
                pixR[p[0],p[1]] = pix2[p[0],p[1]]
                continue
            newDiffPixelsList.append(p)
        diffPixelsList = newDiffPixelsList
        img3.close()
        os.remove(fn3)
    img2.close()
    os.remove(fn2)
    img1.save(fn1)


step = 10 #time interval to extract frame from video. piu' alto e' il valore e piu' veloce sara' l'estrazione ma meno precisa(potrebbero perdersi delle slide). piu' basso e' il valore e piu' precisa sara' l'estrazione, ci vuole piu' tempo
loglevel = 'panic' #otherwise: warning -- loglevel ffmpeg
err_equal_accepted = 100000 #30000 possible duplicates. 50000 => possible remove similar slide not duplicated

regex = re.compile(
        r'^(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

if(re.match(regex, sys.argv[1]) is not None):
	os.system('wget ' + sys.argv[1]+'')

dir_name = sys.argv[1].split("/")[-1].split(".")[0]

output_dir = './' + dir_name
os.system('mkdir ' + dir_name)
last_frame_read = None
filename = output_dir+'/img%04d.jpg'
os.system('ffmpeg -loglevel '+loglevel+' -i ' + sys.argv[1] + ' -vf fps=1/4 -q:v 2 '+filename)

found_and_removed = 0
last_frame_read = None
slide_group_images = []
for filename in os.listdir(output_dir):
    filename = output_dir+"/" + filename
    current_frame = cv2.imread(filename)
    current_frame = cv2.cvtColor(current_frame, cv2.COLOR_BGR2GRAY)
    if(last_frame_read is not None):
        similarity = ssim(current_frame, last_frame_read)
        if(similarity > 0.90):
            print(filename," is similar to previous")
            slide_group_images.append(filename)
        else:
            removePointer(slide_group_images)
            slide_group_images = [filename]
    
    last_frame_read = current_frame



print("duplicate found and removed: " + str(found_and_removed))

#idea: check if similarity with previous is > 90 and similarity with previous previous > 90 -> interpolation


