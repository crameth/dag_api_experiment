from dagster import solid

import io
import base64
import cv2
from PIL import Image

sky = [6, 230, 230]
grass = [4, 250, 7]
tree = [4, 200, 3]
plant = [204, 255, 4]
sidewalk = [235, 255, 7]
road = [140, 140, 140]
earthground = [120,120,70]
water = [61, 230, 250]
sea = [9, 7, 230]

MASK_LIST = [
  sky, 
  grass, 
  tree, 
  plant, 
  sidewalk, 
  road, 
  earthground, 
  water, 
  sea, 
]

@solid
def get_image(context, image_path: str):
	image = Image.open(image_path)
	image = image.convert('RGB')

	return image

@solid
def save_image(context, image, image_path: str):
	image.save(image_path)

	return image_path

@solid
def proportionate_resize_image(context, image, max_width=352, max_height=352):
	width, height = image.size

	ratio = min(max_width / width, max_height / height)

	new_width = width * ratio
	new_height = height * ratio

	# print("Image scaled down from", width, height, "to", new_width, new_height)

	return image.resize((new_width, new_height))

@solid
def reduce_image_to_multiples(context, image, multiple=16):
	width, height = image.size

	while width % multiple != 0:
		width = width - 1
	while height % multiple != 0:
		height = height - 1

	return image.resize((width, height))

@solid
def get_image_from_base64(context, image_b64: str):
	image_b64 = str(image_b64)

	if "data:image/" in image_b64: 
		image_b64 = image_b64.split(";base64,")[-1]
  
	image = base64.b64decode(image_b64)
	image = Image.open(io.BytesIO(image))
	image = image.convert('RGB')

	return image

@solid
def get_base64_from_image_path(context, image_path: str) -> str:
	# assume image is path to image
	image = Image.open(image_path)

	buf = io.BytesIO()
	image.save(buf, format="JPEG")
	image.close()

	return base64.b64encode(buf.getvalue())

@solid
def saturate_image(context, image_path: str, intensity=0):
	image = cv2.imread(image_path)
	image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
	image[..., 1] = intensity
	image = cv2.cvtColor(image, cv2.COLOR_HSV2BGR)

	return image

@solid
def get_image_dimensions(context, image_path: str):
	image = Image.open(image_path)
	
	return image.size

@solid
def apply_mask(context, original, new, mask):
	# Byan: this is the same function as makeTransparent2 re-written to be easier to understand and more efficient

	# assume original, new and mask to be paths
	original = Image.open(original)
	original = original.convert("RGB")
	original_data = original.load()

	new = Image.open(new)
	new = new.convert("RGB")
	new_data = new.load()

	mask = Image.open(mask)
	mask = mask.convert("RGB")
	mask_data = mask.load()

	w, h = mask.size
	for y in range(h):
		for x in range(w):
			for i in MASK_LIST:
				if mask_data[x, y] == (i[0], i[1], i[2]):
					new_data[x, y] = original_data[x, y]

	return new
