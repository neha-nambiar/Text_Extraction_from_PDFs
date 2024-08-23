def preprocess_image(img):
    """
    Preprocess the input image for OCR by converting it to grayscale, denoising it, 
    and applying thresholding to create a binary image.

    Parameters:
    img (numpy.ndarray): The input image in BGR format.

    Returns:
    numpy.ndarray: The preprocessed binary image after thresholding.
    """
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
    thresh = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    return thresh


def remove_watermark(img):
    """
    Remove the watermark from the input image using morphological operations 
    and inpainting techniques.

    Parameters:
    img (numpy.ndarray): The input image in BGR format.

    Returns:
    numpy.ndarray: The image with the watermark removed.
    """
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
    """
    Find the largest rectangular boxes (contours) in the preprocessed image, 
    which represent regions containing important information.

    Parameters:
    img (numpy.ndarray): The input preprocessed binary image.

    Returns:
    list: A list of bounding rectangles for the 30 largest contours in the image.
    Each rectangle is represented as (x, y, width, height).
    """
    contours, _ = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)
    return [cv2.boundingRect(contour) for contour in contours[:30]]  # Get the 30 largest contours


def find_inner_boxes(roi):
    """
    Find inner boxes within a region of interest (ROI) of an image, specifically in 
    the top-left corner, which typically contains a smaller box of interest.

    Parameters:
    roi (numpy.ndarray): The region of interest (ROI) of the image.

    Returns:
    list: A list of bounding rectangles for the inner boxes found in the top-left region.
    Each rectangle is represented as (x, y, width, height).
    """
    h, w = roi.shape
    top_left = roi[0:h//3, 0:w//3]
    contours_tl, _ = cv2.findContours(top_left, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if contours_tl:
        box_tl = cv2.boundingRect(max(contours_tl, key=cv2.contourArea))
        return [box_tl]
    return []


def extract_number(img, x, y, w, h):
    """
    Extract a number from a specific region in the image, enhancing contrast and 
    using OCR to recognize the digits.

    Parameters:
    img (numpy.ndarray): The input image in BGR format.
    x (int): The x-coordinate of the top-left corner of the region.
    y (int): The y-coordinate of the top-left corner of the region.
    w (int): The width of the region.
    h (int): The height of the region.

    Returns:
    str: The extracted number as a string.
    """
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
    """
    Extract text from a specific region in the image using OCR.

    Parameters:
    img (numpy.ndarray): The input image in BGR format.
    x (int): The x-coordinate of the top-left corner of the region.
    y (int): The y-coordinate of the top-left corner of the region.
    w (int): The width of the region.
    h (int): The height of the region.

    Returns:
    str: The extracted text as a string.
    """
    roi = img[y:y+h, x:x+w]
    text = pytesseract.image_to_string(roi, config='--psm 6').strip()
    return text
