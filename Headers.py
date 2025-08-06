from typing import Self
import copy


def capitalize_header(header: str) -> str:
    """Capitalizes each part of a hyphenated header string.
    
    Args:
        header (str): Header string with parts separated by hyphens
        
    Returns:
        str: Header with each part capitalized and joined by hyphens
    """
    return "-".join([h.capitalize() for h in header.split("-")])

class Headers:
    """A class for managing HTTP headers with case-insensitive keys.
    
    Provides methods for getting, setting and manipulating HTTP headers while
    maintaining case-insensitive key matching as per HTTP specifications.
    """

    def __init__(self, headers: dict[str, str] | Self | None = None):
        """Initialize Headers instance with optional dictionary or Headers instance.
        
        Args:
            headers: dict[str, str] | Headers | None: Initial headers dictionary or Headers instance. Defaults to None.
        """
        self.headers = {}

        if headers:
            if isinstance(headers, Headers):
                self.headers = copy.deepcopy(headers.headers)
            else:
                for k, v in headers.items():
                    self.headers[k.lower()] = v

    def __str__(self):
        """Convert headers to a string format suitable for an HTTP message.
        
        Returns:
            str: Headers formatted as 'Key: Value' pairs separated by CRLF
        """
        return "\r\n".join(f"{capitalize_header(k)}: {v}" for k, v in self.headers.items())

    def __bytes__(self):
        """Convert headers to byte format.
        
        Returns:
            bytes: Headers string encoded to bytes
        """
        return str(self).encode()

    def __copy__(self):
        """Create a shallow copy of this instance.
        
        Returns:
            Headers: New Headers instance with copied headers
        """
        return Headers(copy.deepcopy(self.headers))

    def __deepcopy__(self, memo):
        """Create a deep copy of this instance.
        
        Args:
            memo: Memo dictionary for deepcopy
            
        Returns:
            Headers: New Headers instance with deeply copied headers
        """
        return Headers(copy.deepcopy(self.headers, memo))

    def __len__(self):
        """Get the number of headers.
        
        Returns:
            int: Number of headers
        """
        return len(self.headers)

    def __iter__(self):
        """Create iterator over headers.
        
        Returns:
            iterator: Iterator over (key, value) pairs
        """
        return iter(self.headers.items())

    def update(self, new_headers: dict | Self) -> None:
        """Update headers with new headers from dict or Headers instance.
        
        Args:
            new_headers (dict | Self): New headers to add or update
        """
        if isinstance(new_headers, dict):
            for key, value in new_headers.items():
                self.set(key, value)
        else:
            for key, value in new_headers:
                self.set(key, value)

    def has(self, key: str) -> bool:
        """Check if the header exists.
        
        Args:
            key (str): Header key to check
            
        Returns:
            bool: True if the header exists, False otherwise
        """
        return key.lower() in self.headers

    def get(self, key: str, default: str = None) -> str | None:
        """Get header value by key.
        
        Args:
            key (str): Header key
            default (str): Default value if key doesn't exist
            
        Returns:
            str | None: Header value or default if not found
        """
        return self.headers.get(key.lower(), default)

    def set(self, key: str, value: str) -> None:
        """Set header value.
        
        Args:
            key (str): Header key
            value (str): Header value
        """
        self.headers[key.lower()] = value

    def is_empty(self):
        """Check if the "headers" dictionary is empty.
        
        Returns:
            bool: True if no headers exist, False otherwise
        """
        return len(self.headers) == 0
