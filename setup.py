from setuptools import setup, find_packages

setup(
    name='joplinexport',
    version='0.2.5',
    packages=find_packages(),
    install_requires=[
        'altgraph==0.17.3',
        'certifi==2023.5.7',
        'charset-normalizer==3.1.0',
        'idna==3.4',
        'macholib==1.16.2',
        'pathvalidate==3.0.0',
        'pyinstaller==5.11.0',
        'pyinstaller-hooks-contrib==2023.3',
        'python-dotenv==1.0.0',
        'python-frontmatter==1.0.0',
        'PyYAML==5.1',
        'requests==2.31.0',
        'Unidecode==1.3.6'
    ],
    python_requires='>=3.6',
    author='Richard Sprague',
    author_email='sprague@personalscience.com',
    description='A package for handling Joplin notes and notebooks',
    url='https://github.com/richardsprague/joplinexport',  # If you have a repo for this package.
)
