def upload_to(instance, filename, folder):
    if instance.id is None:
        id = (
            instance.__class__.objects.last().id + 1
            if instance.__class__.objects.exists()
            else 1
        )
    else:
        id = instance.id
    ext = filename.rsplit(".", 1)[1]
    new_filename = f"{filename.rsplit('.', 1)[0]}-{id}.{ext}"
    return f"uploads/{folder}/{new_filename}"
