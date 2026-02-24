import logging
import sys
from datetime import datetime
import os
import json
import traceback


class LoggerManager:
    def __init__(self, log_dir="logs", log_level=logging.INFO, log_format="%(message)s"):
        """
        Initializes the LoggerManager.
        """
        self.log_dir = log_dir
        self.log_level = log_level
        self.log_format = log_format
        self.logger = logging.getLogger()
        self._configure_logger()

    def _configure_logger(self):
        """
        Configures the logger with a file handler and a stream handler.
        """
        # Get current time for directory and file naming
        current_time = datetime.now()
        year_month_day = current_time.strftime("%Y_%m_%d")
        time_name = current_time.strftime("%H_%M_%S")

        # Construct directory and file path
        log_directory = os.path.join(self.log_dir, year_month_day)
        os.makedirs(log_directory, exist_ok=True)
        log_file = os.path.join(log_directory, f"{time_name}.log")

        # Set logger configurations
        self.logger.setLevel(self.log_level)
        formatter = logging.Formatter(self.log_format)

        # File handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

        # Stream handler (console)
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(formatter)
        self.logger.addHandler(stream_handler)

        # Redirect stdout and stderr
        sys.stdout = StreamToLogger(self.logger, logging.INFO)
        sys.stderr = StreamToLogger(self.logger, logging.ERROR)

    def get_logger(self, name=None):
        """
        Returns a logger instance, optionally with a custom name.
        
        :param name: Name of the logger.
        :return: Logger instance.
        """
        if name:
            return logging.getLogger(name)
        return self.logger

    def close(self):
        """
        Closes all handlers to release file resources.
        """
        for handler in self.logger.handlers:
            handler.close()
            self.logger.removeHandler(handler)


class StreamToLogger:
    def __init__(self, logger, log_level):
        """
        Redirects standard output to the logger.
        
        :param logger: Logger instance to write to.
        :param log_level: Logging level for messages.
        """
        self.logger = logger
        self.log_level = log_level

    def write(self, message):
        """
        Writes a message to the logger.
        
        :param message: Message to log.
        """
        if message.strip():
            # Check if the message is a valid JSON string
            formatted_message = self._format_message(message)
            self.logger.log(self.log_level, formatted_message)

    def flush(self):
        """
        No-op for flush to comply with file-like object requirements.
        """
        pass

    @staticmethod
    def _format_message(message):
        """
        Formats a message, handling JSON pretty-printing if applicable.
        
        :param message: Original message string.
        :return: Formatted message.
        """
        try:
            # Attempt to load the message as JSON
            json_object = json.loads(message)
            # If successful, return pretty-printed JSON
            return json.dumps(json_object, indent=4, ensure_ascii=False)
        except json.JSONDecodeError:
            # If not JSON, return the original message
            return message


# Usage example
if __name__ == "__main__":
    log_manager = LoggerManager()
    logger = log_manager.get_logger()

    # Test logging with a JSON string
    print('{"key1": "value1", "key2": {"subkey": "subvalue"}}')
    print("This is a plain text message.")
    try:
        raise ValueError("This is an error that will be logged.")
    except Exception as e:
        logger.error("An exception occurred:", exc_info=True)

    # Clean up
    log_manager.close()
