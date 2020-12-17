from dagster import solid

import os

from urllib3.exceptions import HTTPError

# backend
GET_THEME_PALETTES_API = os.environ["GET_THEME_PALETTES_API"] if "GET_THEME_PALETTES_API" in os.environ else "http://192.168.1.119:3002/colour/theme/palette"
GET_PALETTE_IMAGE_API = os.environ["GET_PALETTE_IMAGE_API"] if "GET_PALETTE_IMAGE_API" in os.environ else "http://192.168.1.119:3002/colour/theme/palette/image"

@solid
def get_theme_palettes(context, theme: str):
	payload = {
		"theme_name": theme,
	}
	response = requests.post(GET_THEME_PALETTES_API, json=payload)

	if response.ok:
		return response.json()
	else:
		raise HTTPError

@solid
def generate_palette_image(context, palette: list, palette_width=6, palette_height=1):
	payload = {
		"colours": palette,
		"palette_width": palette_width,
		"palette_height": palette_height,
	}
	response = requests.post(GET_PALETTE_IMAGE_API, json=payload)

	if response.ok:
		return get_image_from_base64(response.content)
	else:
		raise HTTPError
