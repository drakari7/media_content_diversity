import matplotlib.pyplot as plt
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import numpy as np

import tools as tl
from channel_class import NewsChannel

# Before plotting, make sure wordclouds are produced by running
# plot_wordclouds in wiki parser
links = tl.get_channel_links()
wordcloud_folder = tl.get_root_dir() + "graphs/wordclouds/"

x = []
y = []
img_array = []
y_labels = []
x_labels = []

for i, link in enumerate(links):
    channel = NewsChannel(link)
    img_folder = wordcloud_folder + channel.channel_name + '/'

    tmp_x = np.arange(1, channel.video_count + 1)
    tmp_y = [i+1] * len(tmp_x)
    img_names = list(map(lambda x:img_folder + str(x) + '.jpg', tmp_x))
    tmp_img_array = np.array(img_names)

    x.extend(tmp_x)
    y.extend(tmp_y)
    img_array.extend(tmp_img_array)
    y_labels.append(channel.channel_name)


### ----- Below this line is just plotting the graph
fig = plt.figure()
ax = fig.add_subplot(111)
line = plt.scatter(x, y, s=10)

image = plt.imread(img_array[0])
im = OffsetImage(image, zoom=0.5)
xybox = (100, 100)
ab = AnnotationBbox(im, (0,0), xybox=xybox, xycoords='data',
        boxcoords="offset points",  pad=0.0,  arrowprops=dict(arrowstyle="->"))
# add it to the axes and make it invisible
ax.add_artist(ab)
ab.set_visible(False)

def hover(event):
    # if the mouse is over the scatter points
    if line.contains(event)[0]:
        # find out the index within the array from the event
        ind, = line.contains(event)[1]["ind"]
        # get the figure size
        w,h = fig.get_size_inches()*fig.dpi
        ws = (event.x > w/2.)*-1 + (event.x <= w/2.) 
        hs = (event.y > h/2.)*-1 + (event.y <= h/2.)
        # if event occurs in the top or right quadrant of the figure,
        # change the annotation box position relative to mouse.
        ab.xybox = (xybox[0]*ws, xybox[1]*hs)
        # make annotation box visible
        ab.set_visible(True)
        # place it at the position of the hovered scatter point
        ab.xy =(x[ind], y[ind])
        # set the image corresponding to that point
        im.set_data(plt.imread(img_array[ind]))
    else:
        #if the mouse is not over a scatter point
        ab.set_visible(False)
    fig.canvas.draw_idle()

# add callback for mouse moves
fig.canvas.mpl_connect('motion_notify_event', hover)  

fig = plt.gcf()

### ----- Dont change anything above ^^. Copied from stackoverflow

### ------- Any personal changes like naming axis etc here

# plt.xticks(np.arange(1, len(x_labels)+1), x_labels, rotation=80)
plt.yticks(np.arange(1, 26), y_labels)
plt.axis([0, 30, 0, 26])
plt.tight_layout()
plt.show()
