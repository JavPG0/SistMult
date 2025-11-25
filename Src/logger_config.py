import logging
import json 
from datetime import datetime
from pathlib import Path

#Create logs directory if it doesn't exist
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

# Formater to transform logs to JSON (most easy to manipulate)
class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "line_no": record.lineno,
        }

        #Add extra information.
        if hasattr(record,'extra_info'):
            log_data['data'] = record.extra_data

        #If it is a error, include the traceback
        if record.exc_info:
            log_data['excception'] = self.formatException(record.exc_info)

        #Convert to JSON string
        return json.dumps(log_data)
    
def setup_logger(name, log_file, level=logging.INFO):
    """Function to setup a logger with JSON formatting."""
    logger = logging.getLogger(name)
    logger.setLevel(level)

    #Clear previous handlers
    logger.handlers.clear()

    #Create first handler (console)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(JsonFormatter())
    logger.addHandler(console_handler)

    #Create second handler (file)
    if log_file:
        file_path = log_dir / log_file
        file_handler = logging.FileHandler(file_path, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG) #More details tha the other.
        file_handler.setFormatter(JsonFormatter())
        logger.addHandler(file_handler)

    return logger
    
    