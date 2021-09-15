import argparse
import logging
import time
import os
import cv2
import numpy as np

from tf_pose.estimator import TfPoseEstimator
from tf_pose.networks import get_graph_path, model_wh
import scripts.action_classification as act_class
import scripts.scene_classification as sce_class

logger = logging.getLogger('Pose_Action_and_Scene_Understanding')
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

fps_time = 0
address = os.getcwd()

pose_graph = act_class.graph

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='tf-human-action-classification')
	parser.add_argument('--image', type=str, required=True)
	parser.add_argument('--show-process', type=bool, default=False,
						help='for debug purpose, if enabled, speed for inference is dropped.')
	args = parser.parse_args()

	logger.debug('initialization %s : %s' % ('mobilenet_thin', get_graph_path('mobilenet_thin')))
	e = TfPoseEstimator(get_graph_path('mobilenet_thin'), target_size=(432, 368))
	image = cv2.imread(args.image)
	logger.info('cam image=%dx%d' % (image.shape[1], image.shape[0]))

	# count = 0
	
	logger.debug('+image processing+')
	logger.debug('+postprocessing+')
	start_time = time.time()
	humans = e.inference(image, upsample_size=4.0)
	img = TfPoseEstimator.draw_humans(image, humans, imgcopy=False)
	
	logger.debug('+classification+')
	# Getting only the skeletal structure (with white background) of the actual image
	image = np.zeros(image.shape,dtype=np.uint8)
	image.fill(255) 
	image = TfPoseEstimator.draw_humans(image, humans, imgcopy=False)
	
	# Classification
	action_class = act_class.classify(image, pose_graph)
	scene_class = sce_class.classify(args.image)
	end_time = time.time()
	logger.debug('+displaying+')
	cv2.putText(img,
				"Predicted Pose: %s" %(action_class),
				(10, 10),  cv2.FONT_HERSHEY_SIMPLEX, 0.5,
				(0, 0, 255), 2)
	cv2.putText(img,
				"Predicted Scene: %s" %(scene_class),
				(10, 30),  cv2.FONT_HERSHEY_SIMPLEX, 0.5,
				(0, 0, 255), 2)
	print('\n Overall Evaluation time (1-image): {:.3f}s\n'.format(end_time-start_time))
	cv2.imwrite('show1.png',img)
	cv2.imshow('tf-human-action-classification result', img)
	cv2.waitKey(0)
	logger.debug('+finished+')
	cv2.destroyAllWindows()

# =============================================================================
# For running the script simply run the following in the cmd prompt/terminal :
# python3 run_image.py --image=test.png
# =============================================================================
