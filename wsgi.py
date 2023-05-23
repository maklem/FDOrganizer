from server import APP
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env")

if __name__ == "__main__":
    APP.run()