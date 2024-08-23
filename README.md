# Text Extraction from Electoral Roll PDF

## Introduction
This project focuses on extracting specific information from a scanned electoral roll PDF. The goal was to develop a solution capable of accurately identifying and extracting data such as voter names, relations, house numbers, ages, and genders from a complex and structured document.

## Process Overview

### 1. PDF to Image Conversion
- The initial step involved converting the PDF pages to images using the `pdf2image` library.
- This was essential for Optical Character Recognition (OCR) using Tesseract, which requires image input.
- Each page was converted into a high-resolution image to preserve detail.

### 2. Image Preprocessing
To enhance OCR accuracy, several preprocessing techniques were used:
- **Grayscale Conversion**: Simplified image data and improved contrast.
- **Denoising**: Used OpenCV's `fastNlMeansDenoising` function to remove noise.
- **Thresholding**: Applied Otsu's thresholding to better separate text from the background.

### 3. Text Extraction Workflow
The text extraction process included:
- **Rectangular Box Detection**: Contour detection identified rectangular boxes containing voter information.
- **Region Identification**: Specific regions were identified within the boxes (e.g., serial numbers, EPIC numbers).
- **OCR Text Extraction**: Tesseract was used to extract text from the identified regions.

### 4. Data Cleaning and Formatting
Custom functions were developed to clean and format the raw OCR output:
- **extract_and_format_name()**: Cleaned and formatted voter names.
- **extract_name_and_relation()**: Separated relative names and relation types.
- **extract_house_number()**: Isolated house numbers.
- **extract_age()** and **extract_gender()**: Identified age and gender.

These functions used regular expressions and string manipulation to refine OCR results.

### 5. Data Organization and Export
- Extracted data was organized into a DataFrame using pandas for easy manipulation and analysis.
- The cleaned dataset was exported to an Excel file for further use.

## Challenges Faced and Solutions

### 1. Watermark Removal
- **Issue**: 'DELETED' watermarks interfered with data extraction.
- **Attempted Solutions**:
  - Binary mask creation to isolate watermarks.
  - Morphological operations and inpainting.
- **Future Improvements**:
  - Experiment with different thresholding techniques.
  - Explore machine learning-based watermark removal.

### 2. OCR Accuracy
- **Challenges**: Non-standard characters and low-quality scans affected OCR accuracy.
- **Solutions**:
  - Extensive image preprocessing.
  - Custom post-processing functions.
  - Context-specific extraction for names and numbers.

### 3. Handling Document Structure Variations
- **Challenges**: Variations in page layout or formatting.
- **Solutions**:
  - Flexible parsing to handle variations.
  - Error handling for missing or unexpected data.
  - Regular expressions for pattern matching to accommodate text structure variations.
