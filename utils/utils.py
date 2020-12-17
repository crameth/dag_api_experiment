from dagster import solid

import os

@solid
def get_timestamp_from_filepath(context, filepath: str) -> str:
	filename = os.path.basename(filepath)

	name, extension = os.path.splitext(filename)
	
	return name.split('_')[-1]