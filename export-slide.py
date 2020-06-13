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
import hashlib
import cv2
import numpy as np
import re

step = 10 #time interval to extract frame from video. piu' alto e' il valore e piu' veloce sara' l'estrazione ma meno precisa(potrebbero perdersi delle slide). piu' basso e' il valore e piu' precisa sara' l'estrazione, ci vuole piu' tempo
loglevel = 'panic' #otherwise: warning -- loglevel ffmpeg
err_equal_accepted = 30000 #30000 possible duplicates. 50000 => possible remove similar slide not duplicated

regex = re.compile(
        r'^(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

if(re.match(regex, sys.argv[1]) is not None):
	os.system('wget ' + sys.argv[1])

dir_name = sys.argv[1].split("/")[-1].split(".")[0]

output_dir = './' + dir_name
os.system('mkdir ' + dir_name)
#last_digest_frame = ''
last_frame_read = None
filename = output_dir+'/img%04d.jpg'
os.system('ffmpeg -loglevel '+loglevel+' -i ' + sys.argv[1] + ' -vf fps=1/10 -q:v 2 '+filename)

#remove equal images
last_digest_frame = ''
found_and_removed = 0
for filename in os.listdir(output_dir):
	filename = output_dir+"/" + filename
	md5_hash = hashlib.md5()
	currentf = open(filename, "rb")
	content = currentf.read()
	md5_hash.update(content)
	digest = md5_hash.hexdigest()
	currentf.close()
	if(digest == last_digest_frame):
		found_and_removed += 1
		os.remove(filename)
	else:
		last_digest_frame = digest

print("duplicate found and removed: " + str(found_and_removed) + " [1]")
found_and_removed = 0
#remove not equal false positive --> set err_equal_accepted rate 
last_frame_read = None
for filename in os.listdir(output_dir):
	filename = output_dir+"/" + filename
	current_frame = cv2.imread(filename)
	if last_frame_read is not None:
		difference = cv2.subtract(current_frame, last_frame_read)
		b = difference[:,:,0]
		g = difference[:,:,1]
		r = difference[:,:,2]
		#b, g, r = cv2.split(difference)
		if cv2.countNonZero(b) <= err_equal_accepted and cv2.countNonZero(g) <= err_equal_accepted and cv2.countNonZero(r) <= err_equal_accepted:
			found_and_removed += 1
			os.remove(filename)

	last_frame_read = current_frame

print("duplicate found and removed: " + str(found_and_removed) + " [2]")