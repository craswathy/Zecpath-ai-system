import logging

logging.basicConfig(
    filename="ai_activity.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger("zecpath_ai")