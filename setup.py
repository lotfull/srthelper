from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read()
setup(
    name='srthelper',
    version='0.0.5',
    author='Kamil Lotfullin',
    author_email='kamil@lotfullin.com',
    license='MIT License',
    description='SRT Helper',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/Lotfull/srt-path-configurator',
    py_modules=['srthelper', 'app'],
    packages=find_packages(),
    install_requires=[requirements],
    python_requires='>=3.8',
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "Operating System :: OS Independent",
    ],
    entry_points='''
        [console_scripts]
        srthelper=srthelper:cli
    '''
)
