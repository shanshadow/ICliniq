import pytesseract
from pdf2image import convert_from_path
from PIL import Image
import cv2
import os

# I specify the path to the Tesseract executable
pytesseract.pytesseract.tesseract_cmd = r'C://Program Files//Tesseract-OCR//tesseract.exe'  # need to be available in host system

# Function to extract text from an image

def extract_text_from_image(image_path):
    try:
        # Open the image using PIL
        image = Image.open(image_path)
        
        # Use pytesseract to perform OCR on the image
        text = pytesseract.image_to_string(image, lang='eng')
        
        return text
    except Exception as e:
        print(f"Error processing image {image_path}: {e}")
        return ""

# Function to extract text from a large PDF
def extract_text_from_large_pdf(pdf_path, chunk_size=10):
    try:
        # Convert PDF to images
        images = convert_from_path(pdf_path)
        
        all_text = ""
        page_count = len(images)
        
        # Process images in chunks for better performance in large PDFs
        for i in range(0, page_count, chunk_size):
            chunk_images = images[i:i + chunk_size]
            for j, image in enumerate(chunk_images):
                # Save the image temporarily
                image_path = f"page_{i + j}.jpg"
                image.save(image_path, 'JPEG')
                
                # Extract text from the image (page)
                text = extract_text_from_image(image_path)
                all_text += f"Page {i + j + 1}:\n{text}\n"
                
                # Remove the temporary image file
                os.remove(image_path)
        
        return all_text
    except Exception as e:
        print(f"Error processing PDF {pdf_path}: {e}")
        return ""

# Main function to handle both image and PDF input
def extract_text(file_path):
    try:
        # Check if the file is a PDF
        if file_path.lower().endswith('.pdf'):
            print(f"Processing PDF: {file_path}")
            return extract_text_from_large_pdf(file_path)
        else:
            print(f"Processing Image: {file_path}")
            return extract_text_from_image(file_path)
    except Exception as e:
        print(f"Error processing file {file_path}: {e}")
        return ""

# Example usage
if __name__ == "__main__":
    # Replace with the path to your image or PDF file
    import tkinter as tk
    from tkinter import filedialog
    

# Initialize Tkinter root (this keeps the root window from showing)
    root = tk.Tk()
    root.withdraw()

    # Open file dialog and get the file path
    file_path = filedialog.askopenfilename(
        title="Select the file to open",
        filetypes=[("All Files", "*.*")]
    )
        # Extract text
    extracted_text = extract_text(file_path)
    
    # Print the extracted text
    print("Extracted Text:")
    print(extracted_text)
