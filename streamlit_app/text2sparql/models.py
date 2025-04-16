from google.genai import types
from openai import OpenAI
from google import genai

# Group models by their provider as they have different APIs
google_models = ["gemma-3-27b-it"]
openai_models = ["gpt-3.5-turbo"]

# Common interface to use all models in the same way
class LLM_MODEL:
    def __init__(self, model_name):
        if model_name in google_models:
            self.client = genai.Client()
            self.model = model_name
        elif model_name in openai_models:
            self.client = OpenAI()
            self.model = model_name
        else:
            raise ValueError(f"Unsupported model name: {model_name}")

    def generate(self, prompt):
        if self.model in google_models:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    safety_settings=[
                        types.SafetySetting(
                            category='HARM_CATEGORY_SEXUALLY_EXPLICIT',
                            threshold='BLOCK_NONE',
                        ),
                        types.SafetySetting(
                            category='HARM_CATEGORY_HATE_SPEECH',
                            threshold='BLOCK_NONE',
                        ),
                        types.SafetySetting(
                            category='HARM_CATEGORY_HARASSMENT',
                            threshold='BLOCK_NONE',
                        ),
                        types.SafetySetting(
                            category='HARM_CATEGORY_DANGEROUS_CONTENT',
                            threshold='BLOCK_NONE',
                        ),
                    ],
                    temperature=1.0,
                )
            )
            return response.text
        elif self.model in openai_models:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return response.choices[0].message.content
        else:
            raise ValueError(f"Unsupported model name: {self.model}")