# fastapi
from fastapi import FastAPI, UploadFile, File, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# dagster
from dagster import execute_pipeline

# python libraries
import os

# user-defined libraries
from theme_pipeline import colorization_by_theme
from utils.api import *
from utils.commons import *
from utils.s3_bucket import *

class Query(BaseModel):
	image: str
	theme: str

app = FastAPI()
app.add_middleware(
	CORSMiddleware,
	allow_origins=["*"],
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)

@app.post('/theme_pipeline')
def colorization_by_theme_s3(query: Query):
	s3_bucket = S3_Bucket()

	raw_image_s3 = query.image
	theme = query.theme

	raw_image_path = s3_bucket.download_image(raw_image_s3, TEMP_DIR)

	models = [PALETTENET, ITERATIVE_DISTRIBUTION_TRANSFER, PALETTENET]

	config = get_config(raw_image_path, theme, models)
	results = execute_pipeline(colorization_by_theme, run_config=config)

	r1_s3 = s3_bucket.upload_image(results['result_1']['image_path'], "result_images")
	r2_s3 = s3_bucket.upload_image(results['result_2']['image_path'], "result_images")
	r3_s3 = s3_bucket.upload_image(results['result_3']['image_path'], "result_images")

	response = {
		"result_1": r1_s3,
		"result_1_colors": results['result_1']['colors'],
		"result_2": r2_s3,
		"result_2_colors": results['result_2']['colors'],
		"result_3": r3_s3,
		"result_3_colors": results['result_3']['colors'],
	}
	result = execute_pipeline(colorization_by_theme, run_config=config)

	return response

@app.post('/theme_pipeline_local')
def colorization_by_theme_local(query: Query):
	raw_image_b64 = query.image
	theme = query.theme
	timestamp = get_timestamp()

	raw_image_path = os.path.join(TEMP_DIR, "raw_" + timestamp + ".jpg")
	raw_image = get_image_from_base64(raw_image_b64)
	raw_image.save(raw_image_path)
	raw_image.close()

	models = [PALETTENET, ITERATIVE_DISTRIBUTION_TRANSFER, PALETTENET]

	config = get_config(raw_image_path, theme, models)
	results = execute_pipeline(colorization_by_theme, run_config=config)

	response = {
		"result_1": get_base64_from_image_path(results['result_1']['image_path']),
		"result_1_colors": results['result_1']['colors'],
		"result_2": get_base64_from_image_path(results['result_2']['image_path']),
		"result_2_colors": results['result_2']['colors'],
		"result_3": get_base64_from_image_path(results['result_3']['image_path']),
		"result_3_colors": results['result_3']['colors'],
	}

	return response
