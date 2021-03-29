import setuptools

setuptools.setup(
    name="tiedostohallinta",
    version="2021.03.29",
    url="https://github.com/Pilperi/Tiedostohallinta",
    author="Pilperi",
    description="Sekalainen kattaus tiedostonhallintatyökaluja",
    long_description=open('README.md').read(),
    packages=setuptools.find_packages(),
    install_requires=["mutagen", "hashlib"],
	python_requires=[">=3.8, <4"]
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
    ],
    include_package_data=True,
    package_data={'': ['./kansiovakiot.ini']}
)
