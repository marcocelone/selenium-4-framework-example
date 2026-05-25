from dotenv import load_dotenv
import os

load_dotenv()

cms_user: str = os.getenv("WHIZ_USER", "")
cms_pass: str = os.getenv("WHIZ_PASS", "")
base_url: str = os.getenv("BASE_URL", "https://whiz.test.sbra-automation.com/")