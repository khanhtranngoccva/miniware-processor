import dotenv
from helpers.directory import get_application_path

ENV_PATH = get_application_path(".env")
dotenv.load_dotenv(ENV_PATH)