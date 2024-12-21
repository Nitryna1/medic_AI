import csv
import os
import random
import streamlit as st
import openai
import time

# OpenAI API key
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]

# Set OpenAI API key
openai.api_key = OPENAI_API_KEY

# Path to the Dataset.csv file
current_folder = os.getcwd()
datafile_path = os.path.join(current_folder, 'Dataset.csv')

# Mapping of statuses to English descriptions
status_descriptions = {
    "M": "Lack of natural tooth in this area",
    "R": "Presence of a filling in at least one root canal",
    "E": "Periapical radiolucency suggesting inflammation",
    "I": "Presence of a dental implant",
    "A": "Superstructure attached to the implant",
    "P": "Prosthetic crown replacing a missing tooth in a bridge",
    "C": "Prosthetic crown on a tooth",
    "S": "Healthy tooth with no diagnoses from the above list"
}

# Function to fetch a row based on image number
def get_row_by_image_number(image_number):
    if not os.path.exists(datafile_path):
        st.error(f"The file {datafile_path} does not exist. Ensure the file is in the correct folder.")
        return None

    try:
        with open(datafile_path, 'r', newline='', encoding='utf-8') as csvfile:
            csvreader = csv.reader(csvfile, delimiter=',')
            headers = next(csvreader)
            for row in csvreader:
                if row[0] == str(image_number):
                    return dict(zip(headers[1:], row[1:]))
        st.error(f"No row found for image number {image_number}.")
        return None
    except Exception as e:
        st.error(f"Error reading the dataset: {str(e)}")
        return None

# Function to format data into a prompt-friendly format
def format_for_prompt(data):
    if not data:
        return "No data to format."
    return "\n".join(
        f"Tooth {tooth}: {status_descriptions.get(status, 'Unknown status')}"
        for tooth, status in data.items()
    )

# Function to randomly select an image
def get_random_image():
    images = [img for img in os.listdir(current_folder) if img.lower().endswith(('png', 'jpg', 'jpeg'))]
    if not images:
        st.error("No images found in the application folder. Add PNG, JPG, or JPEG files.")
        return None
    return random.choice(images)

# Function to send a query to the GPT API
def analyze_textual_difference_with_gpt(image_name, user_description, reference_description, retries=5, wait_time=20):
    prompt = (
        f"The user provided the following description of the panoramic X-ray:\n{user_description}\n\n"
        f"Reference data for the image description:\n{reference_description}\n\n"
        f"Your task is to analyze and provide feedback as follows:\n"
        f"1. **Highlight discrepancies**: Clearly indicate any differences between the user's description and the reference data.\n"
        f"2. **Avoid incorrect confirmations**: Do not confirm an element as correct unless it fully matches the reference data.\n"
        f"3. **List missing elements**: Identify elements that are present in the reference data but absent in the user's description (excluding healthy teeth).\n"
        f"4. **Confirm correct elements**: Indicate elements that match exactly between the user's description and the reference data.\n"
        f"**Important**: Be strict and precise when comparing descriptions.\n"
        f"Format your response as a list with concise bullet points."
    )

    for attempt in range(retries):
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an assistant evaluating image descriptions."},
                    {"role": "user", "content": promp
le name.")
