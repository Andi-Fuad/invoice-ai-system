import google.generativeai as genai
from app.config import settings
import json
from PIL import Image
import io

class GeminiService:
    def __init__(self):
        genai.configure(api_key=settings.gemini_api_key)
        self.model = genai.GenerativeModel(settings.gemini_flash_3)
    
    def extract_invoice_data(self, image_bytes: bytes, mime_type: str) -> dict:
        """
        Extract structured data from invoice image using Gemini Vision
        
        Args:
            image_bytes: Raw bytes of the image
            mime_type: MIME type of the image (e.g., 'image/jpeg')
        
        Returns:
            dict: Structured invoice data
        """
        # Prepare the image for Gemini
        image = Image.open(io.BytesIO(image_bytes))
        
        # Create the prompt for extraction
        prompt = """
        Analyze this invoice image and extract the following information in JSON format:
        
        {
          "store_name": "Name of the vendor/store",
          "invoice_date": "Date in YYYY-MM-DD format",
          "total": numeric value of total amount after discounts,
          "details": [
            {
              "product_name": "Name of product/service",
              "quantity": numeric quantity,
              "unit": "unit of measurement (liter, pcs, box)",
              "amount": numeric amount for this item before discount,
              "discount": numeric discount for the product
            }
          ]
        }
        
        Important:
        - Return ONLY valid JSON, no markdown code blocks or additional text
        - Ensure all numeric values are numbers, not strings
        - If the quantity written in string, extract only the numerical value from the string.
        - If the unit of measurement is missing, use the most likely unit for the product, such as grams for fruit products, or use 'pcs' as the default.
        - If you can't find a field, use null for that field or 0 if the field required numerical value
        - Extract ALL line items from the invoice into the details array
        """
        
        try:
            # Generate content with image
            response = self.model.generate_content([prompt, image])
            
            # Parse the response
            text = response.text.strip()
            
            # Remove markdown code blocks if present
            if text.startswith("```json"):
                text = text[7:]
            if text.startswith("```"):
                text = text[3:]
            if text.endswith("```"):
                text = text[:-3]
            
            result = json.loads(text.strip())
            
            # Validate required fields
            if not all(key in result for key in ['store_name', 'invoice_date', 'total', 'details']):
                raise ValueError("Missing required fields in extracted data")
            
            return result
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON from Gemini response: {str(e)}")
        except Exception as e:
            raise ValueError(f"Error processing image with Gemini: {str(e)}")
