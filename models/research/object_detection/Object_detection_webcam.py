
# Import packages
import time
import os
import cv2
import numpy as np
import tensorflow as tf
import sys
import pandas as pd

# This is needed since the notebook is stored in the object_detection folder.
sys.path.append("..")

# Import utilites
from utils import label_map_util
from utils import visualization_utils as vis_util

# Name of the directory containing the object detection module we're using
MODEL_NAME = 'inference_graph'

# Grab path to current working directory
CWD_PATH = os.getcwd()

# Path to frozen detection graph .pb file, which contains the model that is used
# for object detection.
PATH_TO_CKPT = os.path.join(CWD_PATH,MODEL_NAME,'frozen_inference_graph.pb')

# Path to label map file
PATH_TO_LABELS = os.path.join(CWD_PATH,'training','labelmap.pbtxt')

# Number of classes the object detector can identify
NUM_CLASSES = 10

## Load the label map.
# Label maps map indices to category names, so that when our convolution
# network predicts `5`, we know that this corresponds to `king`.
# Here we use internal utility functions, but anything that returns a
# dictionary mapping integers to appropriate string labels would be fine
label_map = label_map_util.load_labelmap(PATH_TO_LABELS)
categories = label_map_util.convert_label_map_to_categories(label_map, max_num_classes=NUM_CLASSES, use_display_name=True)
category_index = label_map_util.create_category_index(categories)

# Load the Tensorflow model into memory.
detection_graph = tf.Graph()

with detection_graph.as_default():
    od_graph_def = tf.GraphDef()
    with tf.gfile.GFile(PATH_TO_CKPT, 'rb') as fid:
        serialized_graph = fid.read()
        od_graph_def.ParseFromString(serialized_graph)
        tf.import_graph_def(od_graph_def, name='')

    sess = tf.Session(graph=detection_graph)


# Define input and output tensors (i.e. data) for the object detection classifier

# Input tensor is the image
image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')

# Output tensors are the detection boxes, scores, and classes
# Each box represents a part of the image where a particular object was detected
detection_boxes = detection_graph.get_tensor_by_name('detection_boxes:0')

# Each score represents level of confidence for each of the objects.
# The score is shown on the result image, together with the class label.
detection_scores = detection_graph.get_tensor_by_name('detection_scores:0')
detection_classes = detection_graph.get_tensor_by_name('detection_classes:0')

# Number of objects detected
num_detections = detection_graph.get_tensor_by_name('num_detections:0')

# Initialize webcam feed
#video = cv2.VideoCapture("http://199.199.51.201")
#video = cv2.VideoCapture("http://[2409:4041:61d:63ed:38f4:4bff:fe39:5eb8]:8080/video")
video = cv2.VideoCapture(0)
ret = video.set(3,1280)
ret = video.set(4,720)
k=[]
w=[]
while(True):

    # Acquire frame and expand frame dimensions to have shape: [1, None, None, 3]
    # i.e. a single-column array, where each item in the column has the pixel RGB value
    ret, frame = video.read()
    stime = time.time()
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame_expanded = np.expand_dims(frame_rgb, axis=0)

    # Perform the actual detection by running the model with the image as input
    (boxes, scores, classes, num) = sess.run(
        [detection_boxes, detection_scores, detection_classes, num_detections],
        feed_dict={image_tensor: frame_expanded})



    # Draw the results of the detection (aka 'visulaize the results')
    vis_util.visualize_boxes_and_labels_on_image_array(
        frame,
        np.squeeze(boxes),
        np.squeeze(classes).astype(np.int32),
        np.squeeze(scores),
        category_index,
        use_normalized_coordinates=True,
        line_thickness=4,
        min_score_thresh=0.60)

    #print('FPS {:.1f}'.format(1 / (time.time() - stime)))

    print ([category_index.get(value) for i,value in enumerate(classes[0]) if scores[0,i] > 0.4])
    #d=print([category_index.get(value) for i,value in enumerate(classes[0]) if scores[0,i] > 0.6])
    k.append([category_index.get(value) for i,value in enumerate(classes[0]) if scores[0,i] > 0.4])


    csv_df=pd.DataFrame([category_index.get(value) for i,value in enumerate(classes[0]) if scores[0,i] > 0.6])
    csv_df = pd.DataFrame(k)
    csv_df.to_csv('csv_test.csv')

    #for i in range(len(np.squeeze(boxes))):
        #d=print({"xmin": [np.squeeze(boxes)[i]], "ymax": [np.squeeze(boxes)[i]]})
    #    w.append({"xmin": [np.squeeze(boxes)[i]], "ymax": [np.squeeze(boxes)[i]]})
    #    box_df = pd.DataFrame(w)
    #    box_df.to_csv('box_test.csv')
    #box_df = pd.DataFrame({"xmin": [np.squeeze(boxes)[0]], "ymax": [np.squeeze(boxes)[1]]})
    #box_df.to_csv('box_test.csv')
    # All the results have been drawn on the frame, so it's time to display it.
    cv2.imshow('Object detector', frame)
    time.sleep(15)
    # Press 'q' to quit
    if cv2.waitKey(1) == ord('q'):
        break

# Clean up
video.release()
cv2.destroyAllWindows()

