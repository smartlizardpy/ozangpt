import streamlit as st
import requests
from PIL import Image
from io import BytesIO
from gradio_client import Client
import json

def generate(outline, characters, settings ):
    prompt = f"Hello! I would like to request a 4-paragraph and 700 word per parapaph story and a cover image prompt for sd3 in json format described later in the prompt with the following detailed outline:\n\n{outline}\n\nCharacters: {characters}\n\nSettings: {settings}\n\nPlease generate the story with the following detailed json format : p1, p2, p3, p4: Keys for story paragraphs; title: Key for story title; prompt: Key for cover image description.. Please do not include any other text in the output. Thank You but just the json is needed or it will break the whole system and make us lose 10 millon dollars. please dont say 'Full response: Here is the requested output in JSON format:' or here is the full response only json if you give plain text it will not work and count as an error and we will louse costomers please do not give text.You are not chatgpt dont say here is the full json you are not an assistan you are usen by an ai thank you\n\n"

    client = Client("Be-Bo/llama-3-chatbot_70b")
    hikaye = client.predict(
        message=prompt,
        api_name="/chat"
    )
    
    # Debug print to check hikaye
    print("Debug: Generated hikaye:", hikaye)
    
    return hikaye

def cover(prompt):
    api_key = st.secrets(['apikey'])
    model = "mann-e/Mann-E_Turbo"
    headers = {"Authorization": f"Bearer {api_key}"}
    api_url = f"https://api-inference.huggingface.co/models/{model}"
    
    data = {"inputs": prompt}
    response = requests.post(api_url, headers=headers, json=data)
        
    if 'image' in response.headers.get('content-type', '').lower():
        image = Image.open(BytesIO(response.content))
        return image
    else:
        st.error("Failed to fetch cover image.")
        return None

def parse_story_response(response):
    print("Debug: Raw response from API:", response)
    
    if not response:
        print("Debug: Response is empty or None.")
        return None, None, None, None, None, None
    
    title = response.get('title', '')
    p1 = response.get('p1', '')
    p2 = response.get('p2', '')
    p3 = response.get('p3', '')
    p4 = response.get('p4', '')
    prompt = response.get('prompt', '')
    
    return title, p1, p2, p3, p4, prompt

st.title('Story AI By Ozi')

characters = st.text_area(label="Characters")
outline = st.text_area(label="Story Outline")
settings = st.text_area(label="Setting")

if st.button(label="Generate"):
    with st.spinner('Generating story and cover image...'):
        hikaye = generate(outline, characters, settings )
        print("Debug: Story generation response:", hikaye)
        
        if hikaye:
            try:
                hikaye_json = json.loads(hikaye)
            except json.JSONDecodeError as e:
                st.error(f"Failed to parse JSON response: {e}")
                st.error(f"Failed to parse JSON response. Full response: {hikaye}")
                st.stop()

            title, p1, p2, p3, p4, prmt = parse_story_response(hikaye_json)

            if title and p1 and p2 and p3 and p4:
                st.markdown(f'### {title}')

                # Display cover image if available
                image = cover(prmt )
                if image:
                    
                    st.image(image ,caption= prmt)
                else:
                    st.error("Failed to generate story cover.")

                # Display paragraphs
                st.markdown(f'''
                {p1}

                {p2}

                {p3}

                {p4}
                ''')

            else:
                st.error("Failed to generate or parse story.")

        else:
            st.error("No story data received.")
