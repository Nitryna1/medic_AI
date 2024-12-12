import os
import random
import streamlit as st
import openai

# Ustaw swój klucz API OpenAI
openai.api_key = "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"

# Ścieżka do folderu z obrazami (folder, w którym znajduje się app.py)
IMAGE_FOLDER = os.path.dirname(__file__)

# Funkcja losująca obrazek
def get_random_image():
    if not os.path.exists(IMAGE_FOLDER):
        st.error(f"Folder {IMAGE_FOLDER} nie istnieje. Sprawdź poprawność ścieżki.")
        return None
    # Wybierz pliki graficzne w folderze
    images = [img for img in os.listdir(IMAGE_FOLDER) if img.endswith(('png', 'jpg', 'jpeg'))]
    if not images:
        st.error(f"Folder {IMAGE_FOLDER} nie zawiera obrazów. Dodaj pliki PNG, JPG lub JPEG.")
        return None
    return random.choice(images)

# Funkcja do weryfikacji opisu
def analyze_description(image_name, user_description, expected_description):
    """
    Zakomentowane połączenie z OpenAI API. Funkcja zwraca teraz statyczny tekst.
    """
    # prompt = f"""
    # Obrazek: {image_name}
    # Opis użytkownika: {user_description}
    # Prawidłowy opis powinien zawierać: {expected_description}.
    # Porównaj oba opisy i wypisz, co pasuje, a czego brakuje w opisie użytkownika.
    # """
    # response = openai.ChatCompletion.create(
    #     model="gpt-3.5-turbo",
    #     messages=[
    #         {"role": "system", "content": "You are an assistant that evaluates image descriptions."},
    #         {"role": "user", "content": prompt}
    #     ]
    # )
    # return response["choices"][0]["message"]["content"]
    return "Tekst zwrotny analizy"

# Główna aplikacja Streamlit
#st.title("Asystent AI do Analizy Pantomogramów")
# Tytuł aplikacji z mniejszym rozmiarem
st.markdown(
    "<h1 style='font-size: 2.5rem;'>Asystent AI do Analizy Pantomogramów</h1>", 
    unsafe_allow_html=True
)
st.write("Opisz pantomogram widoczny poniżej, a system oceni Twój opis.")

# Losuj obrazek
image_name = get_random_image()
if image_name:
    image_path = os.path.join(IMAGE_FOLDER, image_name)
    st.image(image_path, caption=f"Losowy obrazek: {image_name}", use_container_width=True)

    # Formularz do opisu
    user_description = st.text_area("Wpisz opis obrazka:", "")

    # Przycisk do wysłania opisu
    if st.button("Prześlij"):
        if user_description.strip():
            # Predefiniowany prawidłowy opis
            expected_description = "Obraz przedstawia krajobraz z górami i rzeką w tle."

            # Analiza opisu przez GPT (lub statyczny tekst)
            try:
                feedback = analyze_description(image_name, user_description, expected_description)
                st.subheader("Wynik analizy:")
                st.write(feedback)
            except Exception as e:
                st.error(f"Wystąpił błąd podczas analizy: {e}")
        else:
            st.error("Proszę wpisać opis obrazka przed wysłaniem.")