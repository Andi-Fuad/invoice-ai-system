from PIL import Image
import io
import hashlib
import imagehash

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

def calculate_file_hash(file_bytes: bytes) -> str:
    """
    Calculate SHA-256 hash of file content for exact duplicate detection
    """
    return hashlib.sha256(file_bytes).hexdigest()

def calculate_perceptual_hash(file_bytes: bytes) -> str:
    """
    Calculate perceptual hash for detecting similar images
    (e.g., same invoice but different quality, rotation, or format)
    """
    img = Image.open(io.BytesIO(file_bytes))
    # Use average hash for robustness
    phash = imagehash.average_hash(img)
    return str(phash)

