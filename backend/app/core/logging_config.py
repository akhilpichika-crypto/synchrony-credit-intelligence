import logging
import sys
from pathlib import Path


def setup_logging():
    # Project root: synchrony-credit-intelligence/
    project_root = Path(__file__).resolve().parents[3]

    # Create logs/ automatically if it does not exist
    log_dir = project_root / "logs"
    log_dir.mkdir(exist_ok=True)

    log_file = log_dir / "credit_intelligence.log"

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        handlers=[
            # Show logs in terminal
            logging.StreamHandler(sys.stdout),

            # Persist logs to file
            logging.FileHandler(
                log_file,
                encoding="utf-8",
            ),
        ],
        force=True,
    )

    logging.getLogger("credit_intelligence").setLevel(logging.INFO)