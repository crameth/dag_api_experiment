
'''
boto3==1.16.13
'''
'''
View s3 buket using cli
pip install awscli
aws configure

aws s3 ls s3://duluxpreviewservice-com/project/gallery/
'''
''' 
aws s3 bucket
Username: akzonobelcdn 
Pass: y7SV2rcfCnrDth9D
Permission: S3 Full Access
Access key: AKIASWZED675NQVBZXUQ
Secret access key: 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
Bucket Name:duluxpreviewservice-com
s3://duluxpreviewservice-com

s3 bucket dir
duluxpreviewservice-com/
    -project/
        -gallery/
        -requests/
            -raw_images/
            -ref_images/
            -result_images/
'''

import boto3
import os
import datetime
from pathlib import Path
import urllib.request

class S3_Bucket:
    bucket = "duluxpreviewservice-com"
    gallery_dir = os.path.join("project","gallery")
    raw_image_dir = os.path.join("project","requests","raw_images")
    ref_image_dir = os.path.join("project","requests","ref_images")
    result_image_dir = os.path.join("project","requests","result_images")


    def __init__(self):
        self.conn = boto3.client(
            's3',
            aws_access_key_id = 'AKIASWZED675NQVBZXUQ',
            aws_secret_access_key = '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'
        )

    def getTimeStamp(self):
        out = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
        return out

    def upload_image(self, image_path, s3_dir):
        try:
            if s3_dir == "gallery":
                to_dir = self.gallery_dir
                prefix_name = "gallery_"
            elif s3_dir == "raw_images":
                to_dir = self.raw_image_dir
                prefix_name = "raw_"
            elif s3_dir == "ref_images":
                to_dir = self.ref_image_dir
                prefix_name = "ref_"
            elif s3_dir == "result_images":
                to_dir = self.result_image_dir
                prefix_name = "result_"
            else:
                print("Invalid s3_dir", s3_dir)
                return False

            with open(image_path, "rb") as f:
                filename = prefix_name + self.getTimeStamp() + Path(image_path).suffix
                s3_path =  os.path.join(to_dir, filename)
                self.conn.upload_fileobj(f, self.bucket, s3_path)
            return s3_path
        except Exception as e:
            print(e)
            return False

    def get_image(self, s3_path):
        try:
            url = self.conn.generate_presigned_url('get_object',
                                                    Params={
                                                        'Bucket': self.bucket,
                                                        'Key': s3_path
                                                    },
                                                    ExpiresIn=604800)
            return url
        except Exception as e:
            print(e)
            return False

    def download_image(self, s3_path, io_path):
        '''
        function to download image from s3 bucket
        '''
        try:
            if not os.path.exists(io_path):
                print(io_path, "not exist")
                return False
            url = self.get_image(s3_path)

            filename = os.path.join(io_path, self.getTimeStamp() + Path(s3_path).suffix)
            
            urllib.request.urlretrieve(url, filename)

            return filename
        except Exception as e:
            print(e)
            return False


