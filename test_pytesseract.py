try:
    import Image
except ImportError:
    from PIL import Image
import pytesseract

ocr_output = pytesseract.image_to_string(Image.open('testimages/hq_public_places.PNG'))
print(type(ocr_output))
print(ocr_output)