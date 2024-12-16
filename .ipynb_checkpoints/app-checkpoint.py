#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import os
import random
import streamlit as st
import openai
import time

# Pobieranie klucza API z secrets
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]

# Ustawienie klucza dla OpenAI
openai.api_key = OPENAI_API_KEY

# Funkcja losująca obrazek
def get_random_image():
    """
    Losuje losowy obrazek z folderu, w którym znajduje się aplikacja.
    """
    current_folder = os.getcwd()
    images = [img for img in os.listdir(current_folder) if img.endswith(('png', 'jpg', 'jpeg'))]
    if not images:
        st.error("Brak obrazów w folderze aplikacji. Dodaj pliki PNG, JPG lub JPEG.")
        return None
    return random.choice(images)

# Funkcja wysyłająca zapytanie do GPT API OpenAI (zgodnie z nowym interfejsem)
def analyze_textual_difference_with_gpt(image_name, user_description, expected_description, retries=5, wait_time=20):
    """
    Analizuje różnice między opisem użytkownika a oczekiwanym opisem za pomocą modelu GPT OpenAI.
    """
    prompt = (
        f"Opis użytkownika: {user_description}\n"
        f"Poprawny opis powinien wyglądać tak: {expected_description}.\n"
        f"Twoje zadanie to:\n"
        f"1. Porównać opis użytkownika z poprawnym wzorcem.\n"
        f"2. Wypisać elementy, które są brakujące w opisie użytkownika.\n"
        f"3. Wskazać elementy, które są błędne lub niezgodne z poprawnym wzorcem, wraz z krótkim wyjaśnieniem.\n"
        f"4. Podać, czy w opisie użytkownika znajdują się elementy zbędne lub nieistotne.\n"
        f"Format odpowiedzi: konkretna lista różnic, wyraźnie oznaczając brakujące, błędne i zbędne elementy.\n"
    )
    
    for attempt in range(retries):
        try:
            response = openai.ChatCompletion.create(  # Zwróć uwagę na nowy sposób wywołania
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Jesteś asystentem oceniającym opisy obrazów."},
                    {"role": "user", "content": prompt}
                ]
            )
            return response['choices'][0]['message']['content']
        except Exception as e:
            if attempt < retries - 1:
                st.warning(f"Próba {attempt + 1}/{retries} nieudana. Czekam {wait_time} sekund przed kolejną próbą...")
                time.sleep(wait_time)
            else:
                return f"Błąd podczas komunikacji z API OpenAI: {str(e)}"

    return "Nie udało się uzyskać odpowiedzi od API po maksymalnej liczbie prób."

# Główna aplikacja Streamlit
st.markdown(
    "<h1 style='font-size: 2.5rem;'>Asystent AI do Analizy Pantomogramów</h1>", 
    unsafe_allow_html=True
)
st.write("Opisz pantomogram widoczny poniżej, a system oceni Twój opis.")

# Losowanie obrazka
image_name = get_random_image()
if image_name:
    image_path = os.path.join(os.getcwd(), image_name)
    st.image(image_path, caption=f"Losowy obrazek: {image_name}")

    # Formularz do opisu
    user_description = st.text_area("Wpisz opis obrazka:", "")

    # Przycisk do wysłania opisu
    if st.button("Prześlij"):
        if user_description.strip():
            # Predefiniowany prawidłowy opis
            expected_description = (
                "Pantomogram przedstawia obraz szczęki i żuchwy w projekcji panoramicznej. "
                "W obrębie górnej szczęki widoczne są wszystkie zęby, w tym zęby mądrości, które nie wykazują oznak erupcji. "
                "Zęby przednie i trzonowe w obu ćwiartkach górnych wykazują obecność wypełnień kompozytowych. "
                "W dolnej szczęce zęby mądrości znajdują się w pozycji prawie pionowej, bez oznak resorpcji korzeni. "
                "W rejonie zębów trzonowych dolnych widoczna jest niewielka zmiana patologiczna w postaci zagęszczenia kości, "
                "sugerująca obecność stanu zapalnego lub torbieli okołowierzchołkowej. Brak widocznych zmian w obrębie stawów skroniowo-żuchwowych. "
                "Kości szczęk i żuchwy wykazują prawidłową gęstość i strukturę, bez widocznych złamań czy rozchwiania zębów. "
                "Przestrzenie międzyzębowe w obrębie obu szczęk są zachowane, bez widocznych objawów próchnicy o dużym stopniu zaawansowania."
            )

            # Analiza opisu przez OpenAI API
            try:
                feedback = analyze_textual_difference_with_gpt(image_name, user_description, expected_description)
                st.subheader("Wynik analizy:")
                st.write(feedback)
            except Exception as e:
                st.error(f"Wystąpił błąd podczas analizy: {e}")
        else:
            st.error("Proszę wpisać opis obrazka przed wysłaniem.")

