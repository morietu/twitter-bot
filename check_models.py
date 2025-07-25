from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

if __name__ == "__main__":
    models = client.models.list()
    for m in models.data:
        print(m.id)
