import io
import datetime
import base64
from PIL import Image

# user-defined libraries
from utils.commons import *

def get_timestamp() -> str:
	return datetime.datetime.now().strftime("%Y%m%d%I%M%S%f")

def get_config(raw_image_path: str, theme: str, models) -> dict:
	return {
		"solids": {
			"get_raw_image_path": {
				"inputs": {
					"raw_image_path": {
						"value": raw_image_path,
					}
				}
			},
			"get_theme": {
				"inputs": {
					"theme": {
						"value": theme,
					}
				}
			},
			"get_models": {
				"inputs": {
					"models": {
						"value": models,
					}
				}
			},
		}
	}

def get_image_from_base64(image_b64: str):
	image_b64 = str(image_b64)

	if "data:image/" in image_b64: 
		image_b64 = image_b64.split(";base64,")[-1]
  
	image = base64.b64decode(image_b64)
	image = Image.open(io.BytesIO(image))
	image = image.convert('RGB')

	return image