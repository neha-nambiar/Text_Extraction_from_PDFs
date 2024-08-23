import pytesseract
from PIL import Image, ImageEnhance
import cv2
import numpy as np
import pdf2image
import pandas as pd
from functions_extraction import *

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
poppler_path = r'D:\Release-24.07.0-0\poppler-24.07.0\Library\bin'

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
