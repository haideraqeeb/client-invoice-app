import base64

def image_to_base64(uploaded_file):
    """Convert uploaded image to base64 string"""
    try:
        bytes_data = uploaded_file.getvalue()
        base64_encoded = base64.b64encode(bytes_data).decode()
        return f"data:image/png;base64,{base64_encoded}"
    except Exception as e:
        return None