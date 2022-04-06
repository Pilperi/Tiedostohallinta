import os
import shutil
import setuptools

setuptools.setup(
    name="tiedostohallinta",
    version="2022.04.06",
    url="https://github.com/Pilperi/Tiedostohallinta",
    author="Pilperi",
    description="Sekalainen kattaus tiedostonhallintatyökaluja",
    long_description=open('README.md').read(),
    packages=setuptools.find_packages(),
    install_requires=["mutagen", "requests"],
	python_requires=">=3.8, <4",
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
    ],
    include_package_data=True,
    package_data={'tiedostohallinta': ['data/kansiovakiot.ini']}
)

# Luo kotikansioon työkansio asetustiedostoille, logeille ja milleikinä
KOTIKANSIO = os.path.expanduser("~")
TYOKANSIO = os.path.join(KOTIKANSIO, ".tiedostohallinta")
if not os.path.isdir(TYOKANSIO):
    os.mkdir(TYOKANSIO)
    print(f"Tehtiin kansio {TYOKANSIO}")
if not os.path.isfile(os.path.join(TYOKANSIO, "kansiovakiot.ini")):
    shutil.copyfile(
        os.path.join(
            os.path.dirname(__file__),
            "tiedostohallinta",
            "data",
            "kansiovakiot.ini"),
        os.path.join(TYOKANSIO, "kansiovakiot.ini"),
        )
    print("Kopioitiin asetustiedosto paikkaan {}".format(
        os.path.join(TYOKANSIO, "kansiovakiot.ini")
        ))
