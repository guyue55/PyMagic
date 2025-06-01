# PyMagic

A comprehensive utility library for Python development, providing tools for logging, debugging, and common operations.

## Installation

```bash
pip install pymagic
```

## Features

- **Logging System**: Advanced logging capabilities based on loguru with customizable formats
- **Utility Tools**: Common utility functions for string manipulation, file operations, and more
- **Decorators**: Useful decorators for exception handling, timing, and other common patterns
- **Base Classes**: Extensible base classes to simplify application development

## Usage

### Logging

```python
from pymagic import logger

# Basic logging
logger.info("This is an info message")
logger.error("This is an error message")

# Create a custom logger
from pymagic import LoggerUtils

custom_logger = LoggerUtils.new("logs/app.log", level="DEBUG")
custom_logger.debug("This is a debug message in custom logger")
```

### Utility Tools

```python
from pymagic import Tools

# Check if string contains Chinese characters
contains_chinese = Tools.is_contain_zh("你好 World")

# Get current timestamp
timestamp = Tools.get_timestamp()

# Format time
formatted_time = Tools.format_time(timestamp, "%Y-%m-%d")
```

### Using Base Class

```python
from pymagic import Base

class MyClass(Base):
    def process_data(self, data):
        # Automatically gets exception handling
        # and logging capabilities
        return data.transform()

# Use with context manager
with MyClass() as my_instance:
    result = my_instance.process_data(some_data)
```

## Documentation

For full documentation, visit [our documentation site](https://github.com/guyue55/pymagic).

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.