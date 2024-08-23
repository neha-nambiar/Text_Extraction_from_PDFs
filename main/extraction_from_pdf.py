import pytesseract
from PIL import Image, ImageEnhance
import cv2
import numpy as np
import pdf2image
import pandas as pd

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
poppler_path = r'D:\Release-24.07.0-0\poppler-24.07.0\Library\bin'

def preprocess_image(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
    thresh = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    return thresh

def remove_watermark(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Create a binary mask of the watermark
    _, thresh = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY_INV)
    
    # Create a kernel for morphological operations
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
    
    # Perform dilation to connect watermark components
    dilated = cv2.dilate(thresh, kernel, iterations=2)
    
    # Find contours of the watermark
    contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Create a mask to store the watermark area
    mask = np.zeros(gray.shape, np.uint8)
    
    # Draw the contours on the mask
    for contour in contours:
        if cv2.contourArea(contour) > 100:  # Adjust this threshold as needed
            cv2.drawContours(mask, [contour], 0, (255,255,255), -1)
    
    # Inpaint the watermark area
    result = cv2.inpaint(img, mask, 3, cv2.INPAINT_TELEA)
    
    return result

def find_boxes(img):
    contours, _ = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)
    return [cv2.boundingRect(contour) for contour in contours[:30]]  # Get the 30 largest contours

def find_inner_boxes(roi):
    h, w = roi.shape
    top_left = roi[0:h//3, 0:w//3]
    contours_tl, _ = cv2.findContours(top_left, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if contours_tl:
        box_tl = cv2.boundingRect(max(contours_tl, key=cv2.contourArea))
        return [box_tl]
    return []

def extract_number(img, x, y, w, h):
    roi = img[y:y+h, x:x+w]
    
    # Increase contrast
    pil_img = Image.fromarray(roi)
    enhancer = ImageEnhance.Contrast(pil_img)
    pil_img = enhancer.enhance(2.0)
    roi = np.array(pil_img)
    
    # Find the rightmost non-white column
    gray_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray_roi, 200, 255, cv2.THRESH_BINARY_INV)
    col_sums = np.sum(binary, axis=0)
    rightmost_col = np.max(np.where(col_sums > 0))
    
    # Extract a small region around the rightmost number
    number_width = 30  # Adjust this value if needed
    number_roi = roi[0:h, max(0, rightmost_col-number_width):rightmost_col+5]
    
    number = pytesseract.image_to_string(number_roi, config='--psm 10 --oem 3 -c tessedit_char_whitelist=0123456789').strip()
    return number

def extract_text(img, x, y, w, h):
    roi = img[y:y+h, x:x+w]
    text = pytesseract.image_to_string(roi, config='--psm 6').strip()
    return text

all_data = []
images = pdf2image.convert_from_path('electoral_roll_data.pdf', poppler_path=poppler_path)

for i, image in enumerate(images):
    print(f"Processing page {i+1}")
    img = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    preprocessed = preprocess_image(img)

    boxes = find_boxes(preprocessed)
    print(f"Number of larger boxes found: {len(boxes)}")

    vis_img = img.copy()

    for j, (x, y, w, h) in enumerate(boxes):
        print(f"Processing larger box {j+1}")
        cv2.rectangle(vis_img, (x, y), (x+w, y+h), (0, 255, 0), 2)

        box_img = img[y:y+h, x:x+w]
        box_img_clean = remove_watermark(box_img)

        roi = preprocessed[y:y+h, x:x+w]
        inner_boxes = find_inner_boxes(roi)

        if inner_boxes:
            ix, iy, iw, ih = inner_boxes[0]
            number = extract_number(box_img_clean, ix, iy, iw, ih)
            
            cv2.rectangle(vis_img, (x+ix, y+iy), (x+ix+iw, y+iy+ih), (255, 0, 0), 2)

            top_right_text = extract_text(box_img_clean, iw+10, 0, w-iw-10, ih)

            text_x = 5
            text_y = iy + ih + 5
            text_w = int(w * 2/3)
            text_h = h - text_y - 5
            text = extract_text(box_img_clean, text_x, text_y, text_w, text_h)

            lines = text.split('\n')
            lines = [line.strip() for line in lines if line.strip()]
            while len(lines) < 4:
                lines.append('')
            lines = lines[:4]

            # Store the extracted data in a dictionary
            data = {
                'page': i+1,
                'box': j+1,
                'number': number,
                'top_right_text': top_right_text,
                'line1': lines[0],
                'line2': lines[1],
                'line3': lines[2],
                'line4': lines[3]
            }
            all_data.append(data)

        else:
            print(f"No inner box found in larger box {j+1}")

    cv2.imwrite(f'page_{i+1}_boxes.png', vis_img)

print("Processing complete")

# Convert the list of dictionaries to a pandas DataFrame
df = pd.DataFrame(all_data)

# Save the DataFrame to a CSV file
df.to_csv('extracted_data.csv', index=False)

print("Data saved to CSV file")
