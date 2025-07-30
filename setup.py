from setuptools import setup, find_packages
from typing import List

def get_requirements(file_path: str) -> List[str]:
    '''
    Returns a list of requirements from a requirements.txt file
    '''
    requirement_list = []
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            for line in lines:
                requirement = line.strip()
                if requirement and requirement != '-e .':
                    requirement_list.append(requirement)
    except FileNotFoundError:
        print(f"Error: The file {file_path} was not found.")

    return requirement_list

setup(
    name='NetworkSecurity',
    version='0.0.1',
    author='Saiaakash',
    author_email="saiaakash33333@gmail.com",
    packages=find_packages(),
    install_requires=get_requirements('requirements.txt')
)