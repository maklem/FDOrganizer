from dotenv import load_dotenv
from server import APP

if __name__ == "__main__":
    if load_dotenv(dotenv_path=".env"):
        APP.config.from_prefixed_env(prefix="FDO")
    APP.run()