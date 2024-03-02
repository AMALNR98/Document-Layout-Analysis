import cv2
import pytesseract
import time
import numpy as np
from tabulate import tabulate

def detect_characters(image_path):
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    config = "--oem 1 --psm 6"  # Page Segmentation Mode: Assume a single uniform block of text
    text = pytesseract.image_to_string(binary, config=config)

    return text
###################################################################################################

def detect_titles_and_subtitles(image_path, min_font_size, max_font_size):
    image = cv2.imread(image_path)
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    ocr_text = pytesseract.image_to_string(gray_image)
    lines = ocr_text.split('\n')
    titles = []
    subtitles = []
    for line in lines:
        font_size = len(line.strip())
        if min_font_size <= font_size <= max_font_size:
            titles.append(line)
        elif font_size < min_font_size:
            subtitles.append(line)

    return titles, subtitles

####################################################################################################
def replace_words(input_string, lst_1, lst_2):
    words = input_string.split()
    for i, word in enumerate(words):
        if word in lst_1:
            index = lst_1.index(word)
            words[i] = lst_2[index]
    output_string = ' '.join(words)
    return output_string
####################################################################################################
def remove_tables_from_image(image_path):
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    binary = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 11, 10)
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        if w > 100 and h > 50:
            cv2.rectangle(image, (x, y), (x + w, y + h), (255, 255, 255), -1)
    return image
#############################################################################
def replace_strings_with_dict(input_string, lst_1, lst_2):
    replacement_dict = dict(zip(lst_1, lst_2))
    replaced_string = input_string
    for key, value in replacement_dict.items():
        replaced_string = replaced_string.replace(key, value)
    return replaced_string

#############################################################################

# Function to detect table from document image 
def detect_table(image_path):
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    binary = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 11, 4)
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    bounding_boxes = [cv2.boundingRect(contour) for contour in contours]
    potential_tables = []
    for x, y, w, h in bounding_boxes:
        aspect_ratio = w / h
        area = w * h
        if aspect_ratio > 3 and area > 10000:
            potential_tables.append((x, y, w, h))

    return potential_tables


# Function to extract text from the detected table region 
def extract_table_content(image, table_region):
    x, y, w, h = table_region
    table_image = image[y:y+h, x:x+w]
    table_text = pytesseract.image_to_string(table_image)
    return table_text


# Function to parse the extracted text into a tabular format
def parse_tabular_data(table_text):
    lines = [line.strip() for line in table_text.split('\n') if line.strip()]
    table_data = [line.split() for line in lines]

    return table_data


# Function to print the extracted tabular data using tabulate
def print_tabular_data(table_data):
    print(tabulate(table_data, headers="firstrow"))


###############################################################################
def table_to_markdown(table_data):
    headers = table_data[0]
    data = table_data[1:]
    markdown_table = tabulate(data, headers=headers, tablefmt="pipe")
    return markdown_table
###############################################################################
def string_to_md_file(input_string, output_file_path):
    with open(output_file_path, 'w') as file:
        file.write(input_string)


# Main function
if __name__ == "__main__":

    image_path = 'Data/sample.png'
    output_image = remove_tables_from_image(image_path)

 

    cv2.imwrite('outputimage.jpg', output_image)
    input_image_path = 'outputimage.jpg'
    detected_text = detect_characters(input_image_path)
    # print(detected_text)

    min_font_size = 20  
    max_font_size = 25  
    titles, subtitles = detect_titles_and_subtitles(image_path, min_font_size, max_font_size)
    # Converting titles and subtitles to markdown formant
    titles_md = ['# ' + item + ' <br>' for item in titles]
    subtitles_md = ['## ' + item + ' <br>'for item in subtitles]
    replaced_string = replace_strings_with_dict(detected_text, titles, titles_md)
    # Detect potential table regions in the document image
    potential_tables = detect_table(image_path)    
    # Extract text from the detected table region using Tesseract OCR
    table_text = extract_table_content(cv2.imread(image_path), potential_tables[0])
        
    # Parse the extracted text into tabular format
    table_data = parse_tabular_data(table_text)
       
    # Print the extracted tabular data using tabulate
    print_tabular_data(table_data)

    markdown_table = table_to_markdown(table_data)

    final_output = replaced_string + markdown_table
    print(final_output)

    output_file_path = 'output_file.md'
    string_to_md_file(final_output, output_file_path)