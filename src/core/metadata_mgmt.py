# TFG

'''
manages metadata extraction
'''

_metadata = {}

# Function to update metadata with a key-value pair:
def metadata_set(key, value):
    """
    Update metadata dictionary with a key-value pair.
    """
    _metadata[key] = value


# Function to update metadata with a dictionary:
def metadata_update(dictionary):
    """
    Update metadata dictionary with a dictionary.
    """
    _metadata.update(dictionary)

# Function to extract entries from the metadata:
def metadata_fetch(key=None):
    """
    Obtain a copy of the full metadata dictionary, or enter a key to obtain only the value of that entry.
    """
    if key is None:
        return _metadata.copy()
    return _metadata.get(key)

# Function to reset metadata:
def metadata_clear():
    """
    docstring
    """
    _metadata.clear()
