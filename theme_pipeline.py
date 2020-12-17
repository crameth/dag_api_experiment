# dagster
from dagster import solid, composite_solid, pipeline

# other packages
import os
import logging

# user-defined libraries
from utils.backend import *
from utils.commons import *
from utils.image import *
from utils.models import * 
from utils.utils import *

@solid
def get_raw_image_path(context, raw_image_path: str):
	context.log.info(f"raw_image_path is: {raw_image_path}")
	return raw_image_path

@solid
def get_theme(context, theme: str):
	context.log.info(f"theme is: {theme}")
	return theme

@solid 
def get_models(context, models):
	context.log.info(f"models is: {models}")
	return models

@solid
def preprocess_raw_image(context, raw_image_path):

	return raw_image_path

@solid
def execute_color_transfer_model_wrapper(context, raw_image_path: str, palette_path: str, model: str):
	# expected output: image array
	
	if model == PALETTENET:
		return request_palettenet(raw_image_path, palette_path)
	elif model == ITERATIVE_DISTRIBUTION_TRANSFER:
		return request_iterative_distribution_transfer(raw_image_path, palette_path)
	else:
		raise HTTPError

@solid
def construct_output_object(context, segmentation_result_paths: list, color_picker_result: dict):
	output = {}
	
	for index, segmentation_result_path, color_picker_result in enumerate(zip(segmentation_result_paths, color_picker_results)):
		output_class = "result_" + str(index + 1)

		output[output_class] = {}
		output[output_class]["image_path"] = segmentation_result_paths[index]
		output[output_class]["colors"] = color_picker_result[index]

	return output

@composite_solid
def generate_palettes(theme: str) -> list:
	# get palettes from theme name
	palettes = get_theme_palettes(theme)
	palette_colors = {
		"palette_1": [p['colour_name'] for p in palettes['palette_1_colours']],
		"palette_2": [p['colour_name'] for p in palettes['palette_2_colours']],
		"palette_3": [p['colour_name'] for p in palettes['palette_3_colours']],
	}
	logging.info(f"Retrieved color names of {theme}: {palette_colors}")

	# generate palette images using palettes
	palette_paths = []
	for index, colors in enumerate(palette_colors):
		index = index + 1

		palette_path = os.path.join(TEMP_DIR, f"palette_{index}_{timestamp}.jpg")
		palette = generate_palette_image(colors[f"palette_{index}"])
		palette.save(palette_path)

		palette_paths.append(palette_path)

		logging.info(f'Retrieved palette image for: {colors}')

	# # result 3
	# palette_b_path = os.path.join(TEMP_DIR, 'palette_b.jpg')
	# palette_b = saturate_image(palette_path, 192)
	# cv2.imwrite(palette_b_path, palette_b)

	return palette_paths

@solid
def color_transfer(context, raw_image_path: str, palette_paths: list, models: list) -> list:
	timestamp = get_timestamp_from_filepath(raw_image_path)
	dimensions = get_image_dimensions(raw_image_path)

	result_paths = []
	for index, palette_path, model in enumerate(zip(palette_paths, models)):
		index = index + 1

		result_path = os.path.join(TEMP_DIR, f"colorized_{index}_{timestamp}.jpg")
		result = execute_color_transfer_model_wrapper(image_path, palette_path, model)
		result = result.resize(dimensions)
		result.save(result_path)

		result_paths.append(result_path)

	return result_paths

@solid
def segmentation(context, raw_image_path: str, new_image_paths: list) -> list:
	timestamp = get_timestamp_from_filepath(raw_image_path)

	# call segmentation API once
	mask_path = os.path.join(TEMP_DIR, f"mask_{timestamp}.png")
	mask = segmentation_request(raw_image_path)
	mask.save(mask_path)

	# overlay results of segmentation API over results
	for index, new_image_path in enumerate(new_image_paths):
		result_path = os.path.join(TEMP_DIR, f"segmented_{index}_{timestamp}.jpg")
		result = apply_mask(raw_image_path, new_image_path, mask_path)
		result.save(result_path)

	return result_paths

@solid
def color_picker(context, raw_image_path: str):
	timestamp = get_timestamp_from_filepath(raw_image_path)

	# run color picker API
	results = []
	for index, raw_image_path in enumerate(raw_image_path):
		result = request_color_picker(raw_image_path)

		results.append(result)

	return results

@solid
def super_resolution(context, image_paths: list):
	result_paths = []

	for index, image_path in enumerate(image_paths):
		result_path = os.path.join(TEMP_DIR, 'superres_result_' + index + '.jpg')

		result = superres_request(image_path, result_path)

		result_paths.append(result_path)

	return result_paths

@pipeline
def colorization_by_theme() -> dict:
	"""
	raw_image_path: string, local path of image
	theme: string, theme name
	""" 

	# get timestamp from filepath
	raw_image_path = get_raw_image_path()
	theme = get_theme()
	models = get_models()

	timestamp = get_timestamp_from_filepath(raw_image_path)

	# process raw image
	raw_image = get_image(raw_image_path)
	raw_image = proportionate_resize_image(image=raw_image)
	raw_image = reduce_image_to_multiples(image=raw_image)
	raw_image_path = save_image(raw_image, raw_image_path)

	# raw_image_path = preprocess_raw_image(raw_image_path)
	logging.info(f"Processed raw image: {raw_image_path}")

	# generate palettes
	palette_paths = generate_palettes(theme)
	logging.info(f"Generate palettes completed: {palette_paths}")

	# color transfer
	color_transfer_result_paths = color_transfer(raw_image_path, palette_paths, models)
	logging.info(f"Color transfer completed: {color_transfer_result_paths}")

	# segmentation
	segmentation_result_paths = segmentation(raw_image_path, color_transfer_result_paths)
	logging.info(f"Segmentation completed: {segmentation_result_paths}")

	# color picker
	color_picker_results = color_picker(segmentation_result_paths)
	logging.info(f"Color picker completed: {color_picker_results}")

	# super resolution
	# super_resolution_result_paths = super_resolution(segmentation_result_paths)
	# logging.info(f"Super resolution completed: {super_resolution_result_paths}")

	# return results in json structure as base64 strings
	results = construct_output_object(segmentation_result_paths, color_picker_results)

	return results

