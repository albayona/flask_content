import os

S3_BUCKET = "isis2503"
S3_KEY = "AKIAJKVXXAMBCGTQQ3UQ"
S3_SECRET = "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"
S3_LOCATION = 'http://{}.s3.amazonaws.com/'.format(S3_BUCKET)

SECRET_KEY = os.urandom(32)
