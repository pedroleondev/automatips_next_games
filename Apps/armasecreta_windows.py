import re
import pandas as pd
from PrettyColorPrinter import add_printer

add_printer()  # Initialize PrettyColorPrinter

# Define a function to parse the HTML content
def parse_html_content(html_content):
    # Regular expression pattern to match the required elements
    pattern = re.compile(r'<div><p>ELEMENTSEPSTART(\d+)</p></div>(.*?)<div><p>ELEMENTSEPEND\1</p></div>', re.DOTALL)
    matches = pattern.findall(html_content)

    all_frames = []
    for match in matches:
        element_id, content = match
        # Here you can add further parsing logic based on your requirements
        # For simplicity, let's just use the element ID and a simplified content
        simplified_content = re.sub('<[^<]+?>', '', content)[:30]  # Extract text and limit to 30 characters
        all_frames.append(pd.DataFrame({'Element ID': [element_id], 'Content': [simplified_content]}))

    if all_frames:
        df_final = pd.concat(all_frames).reset_index(drop=True)
        return df_final
    else:
        return pd.DataFrame()

# Load the HTML content from the file
file_path = 'saved_page_20240214T181156.983Z.html'
with open(file_path, 'r', encoding='utf-8') as file:
    html_content = file.read()

# Parse the HTML content
df_final = parse_html_content(html_content)
print(df_final)
