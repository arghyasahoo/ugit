import os

import data


def write_tree(directory='.'):
    """
    Generates a tree object from the given directory.

    Args:
        directory (str): The directory to generate the tree from. Default is the current directory.

    Returns:
        str: The hash of the generated tree object.
    """
    entries = []
    with os.scandir(directory) as it:
        for entry in it:
            fullpath = f'{directory}/{entry.name}'
            
            if is_ignored(fullpath):
                continue
            
            if entry.is_file(follow_symlinks=False):
                type_ = 'blob'
                with open(fullpath, 'rb') as f:
                    oid = data.hash_object(f.read())
            elif entry.is_dir(follow_symlinks=False):
                type_ = 'tree'
                oid = write_tree(fullpath)
                
            entries.append((entry.name, oid, type_))
        
    tree = ''.join(f'{type_} {oid} {name}\n'
                    for name, oid, type_ in sorted(entries))
    
    return data.hash_object(tree.encode(), 'tree')

def _iter_tree_entries(oid):
    """
    Iterates over the entries in a tree object and yields their type, oid, and name.

    Parameters:
        - oid (str): The object ID of the tree to iterate over.
    Yields: 
        - A generator that yields tuples of the form (type, oid, name).
    """
    if not oid:
        return
    tree = data.get_object(oid, 'tree')
    for entry in tree.decode().splitlines():
        type_, oid, name = entry.split(' ', 2)
        yield type_, oid, name
        
def get_tree(oid, base_path=''):
    """
    Retrieves the contents of a tree object recursively and returns a dictionary
    representing the tree structure.

    Parameters:
    - oid (str): The object ID of the tree to retrieve.
    - base_path (str): The base path to prepend to the paths of the tree entries.

    Returns:
    - result (dict): A dictionary representing the tree structure, where the keys
      are the paths of the tree entries and the values are the object IDs of the
      corresponding blob entries.
    """
    result = {}
    for type_, oid, name in _iter_tree_entries(oid):
        assert '/' not in name
        assert name not in ('..', '.')
        path = base_path + name
        
        if type_ == 'blob':
            result[path] = oid
        elif type_ == 'tree':
            result.update(get_tree, (oid, f'{path}/'))
        else:
            assert False, f'Unknown tree entry {type_}'
    
    return result

def _empty_current_directory():
    """
    Deletes all files and directories in the current directory recursively,
    excluding the ones that are ignored. This function does not return anything.
    
    Parameters:
        None
    
    Returns:
        None
    """
    for root, dirname, filenames in os.walk('.', topdown=False):
        for filename in filenames:
            path = os.path.relpath(f'{root}/{filename}')
            if is_ignored(path) or not os.path.isfile(path):
                continue
            os.remove(path)
            
        for dirname in dirnames:
            path = os.path.relpath(f'{root}/{dirname}')
            if is_ignored(path):
                continue
            try:
                os.rmdir(path)
            except (FileNotFoundError, OSError):
                pass

def read_tree(tree_oid):
    """
    Reads a tree from the given tree_oid and saves its contents to the current directory.

    Parameters:
        tree_oid (str): The object ID of the tree to be read.
    
    Returns:
        None
    """
    _empty_current_directory()
    for path, oid in get_tree(tree_oid, base_path='./').items():
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'wb') as f:
            f.write(data.get_object(oid))

def is_ignored(path):
    return '.ugit' in path.split('/')
