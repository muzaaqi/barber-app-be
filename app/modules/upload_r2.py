from flask import request, jsonify
from app.r2_config import s3, R2_BUCKET, R2_ENDPOINT

def upload_image(name):
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

    public_url = f"{R2_ENDPOINT}/{R2_BUCKET}/{filename}"

    return jsonify({
        "filename": filename,
        "url": public_url
    })
