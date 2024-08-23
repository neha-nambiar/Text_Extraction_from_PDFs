import pandas as pd
import re


def extract_and_format_name(text):
    """
    Extract and format a name from the given text.

    This function removes any non-alphabetic characters (except spaces) from the input text,
    trims extra spaces, and capitalizes the first letter of each word. The function assumes
    that the name starts after the first word in the input string.

    Parameters:
    text (str): The input text containing the name.

    Returns:
    str: The formatted name, with the first letter of each word capitalized. Returns an empty
    string if the name could not be extracted.
    """
    
    # Remove any non-alphabetic characters (except space) and extra spaces
    cleaned = re.sub(r'[^a-zA-Z\s]', '', text)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    
    # Split the string and take all words after the first one (assumed to be "Name")
    parts = cleaned.split(' ')
    if len(parts) > 1:
        name = ' '.join(parts[1:])
        
        # Capitalize the first letter of each word
        name = ' '.join(word.capitalize() for word in name.split())
        
        return name
    else:
        return ''
    
    
    
def extract_name_and_relation(text):
    """
    Extract a name and determine the relationship type from the given text.

    This function removes non-alphabetic characters (except spaces) and extra spaces from the
    input text, extracts the name after the keywords "name" or "others," and determines the
    relationship type based on keywords such as "father," "husband," or "others." The name is
    formatted with the first letter of each word capitalized.

    Parameters:
    text (str): The input text containing the name and relationship information.

    Returns:
    tuple: A tuple containing:
        - name (str): The formatted name with the first letter of each word capitalized.
        - relation (str): A short code representing the relationship type:
            "FTHR" for father, "HSBN" for husband, "OTHR" for others, or an empty string if no
            relationship type is detected.
    """
    
    # Remove any non-alphabetic characters (except space) and extra spaces
    cleaned = re.sub(r'[^a-zA-Z\s]', ' ', text)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip().lower()
    
    # Extract name
    name_match = re.search(r'(?:name|others)\s*(.*)', cleaned)
    name = name_match.group(1).strip() if name_match else ''
    
    # Format name
    name = ' '.join(word.capitalize() for word in name.split())
    
    # Determine relation type
    if "father" in cleaned:
        relation = "FTHR"
    elif "husband" in cleaned:
        relation = "HSBN"
    elif "others" in cleaned:
        relation = "OTHR"
    else:
        relation = ""
    
    return name, relation



def extract_house_number(text):
    """
    Extract the house number from the given text.

    This function removes non-alphanumeric characters (except spaces and hyphens) and extra spaces
    from the input text, and attempts to extract the house number following the phrase "house number."
    If the extracted entry is empty or consists only of a hyphen, it is returned as is.

    Parameters:
    text (str): The input text containing the house number information.

    Returns:
    str: The extracted house number, with leading and trailing spaces or hyphens removed. Returns
    an empty string if no house number is detected.
    """
    
    # Remove any non-alphanumeric characters (except space and hyphen) and extra spaces
    cleaned = re.sub(r'[^a-zA-Z0-9\s-]', ' ', str(text))
    cleaned = re.sub(r'\s+', ' ', cleaned).strip().lower()
    
    # Try to find the entry after "house number" and any characters
    match = re.search(r'house\s*number.*?[:\s](.*)', cleaned)
    
    if match:
        entry = match.group(1).strip()
        # If entry is empty or just a hyphen, return it as is
        if entry in ['', '-']:
            return entry
        # Otherwise, remove any leading/trailing spaces or hyphens
        return entry.strip(' -')
    else:
        return ''
    
    
    
def clean_number(value):
    """
    Clean and convert a number from the given value.

    This function converts the input value to a string, removes everything after the first decimal point,
    and removes any non-digit characters. The cleaned value is then converted to an integer. If the cleaned
    value does not contain any digits, the function returns `pd.NA`.

    Parameters:
    value: The input value containing the number (can be any data type).

    Returns:
    int or pd.NA: The cleaned and converted integer value, or `pd.NA` if the value does not contain
    any digits.
    """
    
    if pd.isna(value):  # Check if the value is NaN
        return pd.NA
    
    # Convert the value to a string
    value_str = str(value)
    
    # Stop at the decimal point (remove everything after the first decimal)
    before_decimal = value_str.split('.')[0]
    
    # Remove any non-digit characters
    cleaned = re.sub(r'\D', '', before_decimal)
    
    # If we have digits, convert to integer
    if cleaned:
        return int(cleaned)
    else:
        return pd.NA
    
    
    
def extract_age(text):
    """
    Extract age from the given text.

    This function searches the input text for a pattern that matches "Age" followed by a separator (e.g., 
    ":", "!", "l", "+") and a numeric value, and returns the extracted age as an integer.

    Parameters:
    text (str): The input text containing the age information.

    Returns:
    int or None: The extracted age as an integer, or `None` if no age is found.
    """
    
    match = re.search(r'Ag[ee]\s*[:!l+]\s*(\d+)', text, re.IGNORECASE)
    return int(match.group(1)) if match else None



def extract_gender(text):
    """
    Extract gender from the given text.

    This function searches the input text for a pattern that matches "Gender" followed by a separator (e.g., 
    ":", "!", "l", "+") and a gender-related word (e.g., "Male", "Female"). It returns 'M' for male and 'F' 
    for female. If the direct match fails, a more lenient approach is used to search for "ma" or "fe" 
    patterns to determine the gender.

    Parameters:
    text (str): The input text containing the gender information.

    Returns:
    str or None: The gender as 'M' (male) or 'F' (female), or `None` if no gender is detected.
    """
    
    match = re.search(r'Gen[de]r\s*[:!l+]\s*(\w+)', text, re.IGNORECASE)
    if match:
            gender = match.group(1).lower()
            if re.search(r'ma', gender):
                    return 'M'
            elif re.search(r'fe', gender):
                    return 'F'

    # If the above doesn't work, try a more lenient approach
    if re.search(r'\bma', text.lower()):
            return 'M'
    elif re.search(r'\bfe', text.lower()):
            return 'F'

    return None
