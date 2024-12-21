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
                    {"role": "user", "content": prompt}
                ]
            )
            return response['choices'][0]['message']['content']
        except Exception as e:
            if attempt < retries - 1:
                st.warning(f"Attempt {attempt + 1}/{retries} failed. Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                return f"Error communicating with OpenAI API: {str(e)}"
    return "Failed to get a response from the API after maximum attempts."

# Main Streamlit application
st.markdown("<h1 style='font-size: 2.5rem;'>AI Assistant for Pantomogram Analysis</h1>", unsafe_allow_html=True)
st.write("Describe the pantomogram shown below, and the system will evaluate your description.")

# Ensure the image is only randomized once
if "image_name" not in st.session_state:
    st.session_state.image_name = get_random_image()

image_name = st.session_state.image_name

if image_name:
    image_path = os.path.join(current_folder, image_name)
    st.image(image_path, caption=f"Random Image: {image_name}")

    if "test_(" in image_name and ")" in image_name:
        try:
            image_number = int(image_name.split("test_(")[1].split(")")[0])
            reference_data = get_row_by_image_number(image_number)

            if reference_data:
                reference_description = format_for_prompt(reference_data)

                # Display reference description
                st.subheader("Reference Description:")
                st.write(reference_description)

                user_description = st.text_area("Enter your description of the image:", "")

                if st.button("Submit"):
                    if user_description.strip():
                        feedback = analyze_textual_difference_with_gpt(image_name, user_description, reference_description)
                        st.subheader("Analysis Result:")
                        st.write(feedback)
                    else:
                        st.error("Please enter a description of the image before submitting.")
            else:
                st.error("Failed to retrieve reference data for this image.")
        except ValueError:
            st.error("Invalid image number format in the file name.")
    else:
        st.error("Cannot extract the image number from the file name.")
else:
    st.error("No image selected.")
le name.")
