from dagster import solid

import os

from urllib3.exceptions import HTTPError

# color transfer models
PALETTENET_API = os.environ["PALETTENET_API"] if "PALETTENET_API" in os.environ else "http://192.168.1.119:3006/colour_by_theme"
ITERATIVE_DISTRIBUTION_TRANSFER_API = os.environ["ITERATIVE_DISTRIBUTION_TRANSFER_API"] if "ITERATIVE_DISTRIBUTION_TRANSFER_API" in os.environ else "http://192.168.1.119:3011/iterative_distribution_transfer"

# segmentation
SEMANTIC_SEGMENTATION_API = os.environ["SEMANTIC_SEGMENTATION_API"] if "SEMANTIC_SEGMENTATION_API" in os.environ else "http://192.168.1.119:3005/SemanticSegmentation"

# miscellaneous
COLOR_PICKER_API = os.environ["COLOR_PICKER_API"] if "COLOR_PICKER_API" in os.environ else "http://192.168.1.119:3004/colour_picker"
SUPER_RESOLUTION_API = os.environ["SUPER_RESOLUTION_API"] if "SUPER_RESOLUTION_API" in os.environ else "http://192.168.1.119:3003/superres"

@solid
def request_palettenet(context, image_path: str, palette_path: str):
	with open(image_path, 'rb') as image_bytes, open(palette_path, 'rb') as palette_bytes:
		payload = {
			'imageX': image_bytes, 
			'imageY': palette_bytes,
		}
		response = requests.post(PALETTENET_API, files=payload)
		
		image_bytes.close()
		palette_bytes.close()

	if response.status_code == 200:
		return get_image_from_base64(response.content)
	else:
		print('[ERROR] HTTP Response:', response.status_code, response.reason)
		raise HTTPError

@solid
def request_iterative_distribution_transfer(context, image_path: str, reference_path: str):
	with open(image_path, 'rb') as image_bytes, open(reference_path, 'rb') as reference_bytes:
		payload = {
			'image': image_bytes, 
			'reference': reference_bytes,
		}
		response = requests.post(ITERATIVE_DISTRIBUTION_TRANSFER_API, files=payload)

		image_bytes.close()
		reference_bytes.close()

	if response.status_code == 200:
		return Image.open(io.BytesIO(response.content))
	else:
		print('[ERROR] HTTP Response:', response.status_code, response.reason)
		raise HTTPError

@solid
def request_semantic_segmentation(context, image_path: str):
	with open(image_path, 'rb') as image_bytes:
		payload = {
			'file': image_bytes
		}
		response = requests.post(SEGMENTATION_API, files=payload)

		image_bytes.close()

	if response.status_code == 200:
		result = response.json()
		return get_image_from_base64(result['result'])
	else:
		print('[ERROR] HTTP Response:', response.status_code, response.reason)
		raise HTTPError


@solid
def request_color_picker(context, image_path: str):
	image_b64 = get_base64_from_image_path(image_path).decode('utf-8')

	payload = {
		'image': 'data:image/jpg;base64,' + image_b64,
		'select_type': 'base64',
	}
	response = requests.post(COLOR_PICKER_API, data=payload)

	if response.status_code == 200:
		result = response.json()
		
		result.pop("message")
		result.pop("select_type")

		return result
	else:
		print('[ERROR] HTTP Response:', response.status_code, response.reason)
		raise HTTPError

@solid
def request_super_resolution(context, image_path: str):
	with open(image_path, 'rb') as image_bytes:
		payload = {
			'original': image_bytes,
		}
		response = requests.post(SUPERRES_API, files=payload)
		
		image_bytes.close()

	if response.status_code == 200:
		result = response.json()
		return get_image_from_base64(result['result'])
	else:
		print('[ERROR] HTTP Response:', response.status_code, response.reason)
		raise HTTPError
