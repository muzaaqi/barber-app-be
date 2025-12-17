import boto3
from botocore.client import Config
import os

R2_ACCESS_KEY = os.getenv("CLOUDFLARE_R2_KEY_ID")
R2_SECRET_KEY = os.getenv("CLOUDFLARE_R2_SECRET")
R2_BUCKET = os.getenv("CLOUDFLARE_R2_BUCKET")
R2_ENDPOINT = os.getenv("CLOUDFLARE_R2_ENDPOINT")
R2_PUBLIC = os.getenv("CLOUDFLARE_R2_PUBLIC")

s3 = boto3.client(
    service_name="s3",
    endpoint_url=R2_ENDPOINT,
    aws_access_key_id=R2_ACCESS_KEY,
    aws_secret_access_key=R2_SECRET_KEY,
    config=Config(signature_version="s3v4"),
)