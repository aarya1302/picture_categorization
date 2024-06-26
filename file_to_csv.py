import os
import pandas as pd
from PIL import Image
from PIL.ExifTags import TAGS

# Function to extract image metadata
def get_image_metadata(image_path):
    try:
        image = Image.open(image_path)
        exif_data = image._getexif()
        metadata = {TAGS.get(tag): value for tag, value in exif_data.items()} if exif_data else {}
        return metadata
    except Exception as e:
        return {}

# Define the directory containing images
image_dir = '/Users/aaryabhorra/Desktop/test'

# List to store image metadata
data = []

# Walk through the directory and subdirectories
for root, dirs, files in os.walk(image_dir):
    for file in files:
        if file.lower().endswith(('png', 'jpg', 'jpeg', 'tiff', 'bmp')):
            file_path = os.path.join(root, file)
            
            labels = file_path.split("/")
            
            
            metadata = get_image_metadata(file_path)
            
            data.append({
                'Image ID/Name': file,
                'Location': 'Unknown',  # You can customize this based on folder structure or file naming
                'Year': labels[5],  # You can customize this
                'Date': metadata.get('DateTime', 'Unknown'),
                'Program': labels[6],  # Customize based on your needs
                'Approval': labels[7],  # Customize based on your needs
                'Tags': 'N/A',  # Customize based on your needs
                'File Path/URL': file_path
            })

# Convert to DataFrame
df = pd.DataFrame(data)

# Save to Excel
df.to_excel('image_metadata.xlsx', index=False)

# If you need to upload to Google Sheets, use the gspread library
# Example (ensure you have gspread and oauth2client installed and configured):
'''
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Use credentials to create a client to interact with the Google Drive API
scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('path_to_your_creds.json', scope)
client = gspread.authorize(creds)

# Find a workbook by name and open the first sheet
# Make sure you use the right name here.
spreadsheet = client.open("Your Spreadsheet Name").sheet1

# Clear existing content in the sheet
spreadsheet.clear()

# Upload DataFrame to Google Sheets
spreadsheet.update([df.columns.values.tolist()] + df.values.tolist())
'''
