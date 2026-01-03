from PIL import Image
import io

def convert_to_supported_format(file_bytes: bytes, mime_type: str) -> tuple[bytes, str]:
    """
    Convert uploaded file to a format supported by Gemini Vision
    Gemini supports: PNG, JPEG, WEBP, HEIC, HEIF
    """
    if mime_type in ['image/png', 'image/jpeg', 'image/jpg', 'image/webp']:
        return file_bytes, mime_type
    
    # Convert other formats to PNG
    img = Image.open(io.BytesIO(file_bytes))
    output = io.BytesIO()
    img.save(output, format='PNG')
    return output.getvalue(), 'image/png'

