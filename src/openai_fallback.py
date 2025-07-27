
import base64
from io import BytesIO
from PIL import Image
import openai

from src.config import Config

def run_openai_vision(image_path):
    if not Config.OPENAI_API_KEY:
        raise ValueError('Missing OpenAI API key')

    openai.api_key = Config.OPENAI_API_KEY

    with Image.open(image_path) as img:
        buffer = BytesIO()
        img.save(buffer, format='JPEG')
        img_b64 = base64.b64encode(buffer.getvalue()).decode()

    response = openai.chat.completions.create(
        model='gpt-4o-vision-preview',
        messages=[
            {
                'role': 'user',
                'content': [
                    {'type': 'text', 'text': 'Extract all label information from this herbarium specimen image.'},
                    {'type': 'image_url', 'image_url': {'url': f'data:image/jpeg;base64,{img_b64}'}}
                ]
            }
        ],
        max_tokens=1024
    )

    text_output = response.choices[0].message.content
    return {'text': text_output.strip(), 'confidence': 1.0, 'source': 'openai_vision'}
