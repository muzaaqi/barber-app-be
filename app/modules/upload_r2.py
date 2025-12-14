from flask import request, jsonify
from r2_config import s3, R2_BUCKET, R2_ENDPOINT

def upload_image(name, dir:str):
    if 'image' not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    file = request.files['image']
    ext = file.filename.rsplit(".", 1)[-1]
    filename = f"{name}.{ext}"

    s3.upload_fileobj(
        file,
        R2_BUCKET,
        filename,
        ExtraArgs={"ContentType": file.content_type}
    )

    public_url = f"{R2_ENDPOINT}/{R2_BUCKET}/{dir}/{filename}"

    return jsonify({
        "filename": filename,
        "url": public_url
    })

def delete_image(pubolic_url):
    s3.delete_object(
        Bucket=R2_BUCKET,
        Key=pubolic_url.split("/")[-1]
    )