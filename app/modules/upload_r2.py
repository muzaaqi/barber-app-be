import uuid
from werkzeug.utils import secure_filename
from r2_config import s3, R2_BUCKET, R2_PUBLIC

def upload_image(name: str, file, folder: str):
    if not file or not file.filename:
        raise ValueError("No file provided")

    ext = file.filename.rsplit(".", 1)[-1].lower()
    safe_name = secure_filename(name)
    unique_name = f"{safe_name}.{ext}"

    key = f"{folder}/{unique_name}"

    s3.upload_fileobj(
        file,
        R2_BUCKET,
        key,
        ExtraArgs={"ContentType": file.content_type}
    )

    public_url = f"{R2_PUBLIC}/{key}"

    return {"filename": unique_name, "url": public_url, "key": key}


def delete_image(key: str):
    s3.delete_object(
        Bucket=R2_BUCKET,
        Key=key
    )