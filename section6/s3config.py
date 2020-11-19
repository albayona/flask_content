import os

S3_BUCKET = "isis2503"
S3_KEY = ""
S3_SECRET = ""
S3_LOCATION = 'http://{}.s3.amazonaws.com/'.format(S3_BUCKET)

SECRET_KEY = os.urandom(32)
