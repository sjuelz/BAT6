import boto3
import os
import sys
import uuid
from urllib.parse import unquote_plus
from PIL import Image
import PIL.Image
import cv2

s3_client = boto3.client('s3')

def bilateralFilterfy(image_path, sketched_path):
    file_name= os.path.basename(image_path)
    img = cv2.imread(image_path)
    smooth = 5
    kernel =3
    edge_preserve = 50
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) 
    gray = cv2.medianBlur(gray, kernel) 
    edges = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 9, 9)
    color = cv2.bilateralFilter(img, smooth, edge_preserve, smooth) 
    cartoon = cv2.bitwise_and(color, color, mask=edges) 
    cv2.imwrite(sketched_path, cartoon)

#def pencilSketch(image_path, sketched_path):
#    file_name= os.path.basename(image_path)
#    img = cv2.imread(image_path)
#    gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) 
#    inverted_gray_image = 255 - gray_image
#    blurred_img = cv2.GaussianBlur(inverted_gray_image, (21,21),0) 
#    inverted_blurred_img = 255 - blurred_img
#    pencil_sketch_IMG = cv2.divide(gray_image, inverted_blurred_img, scale = 256.0)
#   #cv2.imwrite(sketched_path+f"/pencil_sketch_{file_name}", pencil_sketch_IMG)
#    cv2.imwrite(sketched_path, pencil_sketch_IMG)

def lambda_handler(event, context):
  for record in event['Records']:
      bucket = record['s3']['bucket']['name']
      key = unquote_plus(record['s3']['object']['key'])
      tmpkey = key.replace('/', '')
      download_path = '/tmp/{}{}'.format(uuid.uuid4(), tmpkey)
      upload_path = '/tmp/cartoons-{}'.format(tmpkey)
      s3_client.download_file(bucket, key, download_path)
      bilateralFilterfy(download_path, upload_path)
      s3_client.upload_file(upload_path, '{}-destination1'.format(bucket), key)
