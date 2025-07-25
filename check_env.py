# check_env.py
import os
from dotenv import load_dotenv, dotenv_values
from pathlib import Path

dotenv_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=dotenv_path)

config = dotenv_values(".env")
for key, value in config.items():
    print(f"{key=}, {value=}")

print("API_KEY:", os.getenv("API_KEY"))
print("API_SECRET:", os.getenv("API_SECRET"))
print("ACCESS_TOKEN:", os.getenv("ACCESS_TOKEN"))
print("ACCESS_SECRET:", os.getenv("ACCESS_SECRET"))
print("OPENAI_API_KEY:", os.getenv("OPENAI_API_KEY"))
