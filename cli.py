import argparse
import os
import sys

import data
import base


def main():
    """
    This function is the entry point for the program. It parses the command line arguments using the `parse_args` function and assigns the result to the `args` variable. It then assigns the `args.func` value to `args`.

    Parameters:
        None

    Returns:
        None
    """
    args = parse_args()
    args.func = (args)
    
def parse_args():
    """
    Parse the command-line arguments and return the parsed arguments.

    Parameters:
        None
    
    Returns:
        The parsed command-line arguments.

    """
    parser = argparse.ArgumentParser()
    
    commands = parser.add_subparsers(dest='command')
    commands.required = True
    
    # init parser
    init_parser = commands.add_parser('init')
    init_parser.set_defaults(func=init)
    
    # hash_object parser
    hash_object_parser = commands.add_parser('hash_object')
    hash_object_parser.set_defaults(func=hash_object)
    hash_object_parser.add_argument('file')
    
    # cat_file parser
    cat_file_parser = commands.add_parser('cat_file')
    cat_file_parser.set_defaults(func=cat_file)
    cat_file_parser.add_argument('object')
    
    
    write_tree_parser = commands.add_parser('write_tree')
    write_tree_parser.set_defaults(func=write_tree)
    
    return parser.parse_args()

def init(args):
    data.init()
    print (f'Initialized empty ugit repository in {os.getcwd()}/{data.GIT_DIR}')
    
def hash_object(args):
    with open(args.file, 'rb') as f:
        print(data.hash_object(f.read()))
        
def cat_file(args):
    sys.stdout.flush()
    sys.stdout.buffer.write(data.get_object(args.object, expected=None))

def write_tree():
    print(base.write_tree())