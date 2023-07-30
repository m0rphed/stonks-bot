import creds

# ensure needed environment variables are loaded
creds.load_env_file("./secret/.env")

TELEGRAM_API_ID = creds.get_from_env("TELEGRAM_API_ID")
TELEGRAM_API_HASH = creds.get_from_env("TELEGRAM_API_HASH")
TELEGRAM_BOT_TOKEN = creds.get_from_env("TELEGRAM_BOT_TOKEN")

BOT_SESSION_NAME = "stonks-bot"
DEFAULT_DATA_PROVIDER = "alpha_vantage"
ALPHA_VANTAGE_KEY = creds.get_from_env("ALPHA_VANTAGE_TOKEN")

SUPABASE_URL = creds.get_from_env("SUPABASE_URL")
SUPABASE_KEY = creds.get_from_env("SUPABASE_SEC_KEY")
