'''
Lue oleellisimmat kansiosijainnit ymv ini-tiedostosta ja aseta
ne globaaleiksi vakioiksi
'''
import os
import time
import json
import logging
import argparse
import configparser
import pkg_resources

loglevel = "INFO"
parser = argparse.ArgumentParser(description='Synkkaa tiedostot ja kansiot.')
parser.add_argument(
    "--log",
    type=str,
    nargs=1,
    default="INFO",
    choices=["INFO", "DEBUG", "WARNING", "ERROR", "CRITICAL"],
    help='Säädä loggauksen tasoa. Oletuksena INFO (vain isot askeleet)')
args, _ = parser.parse_known_args()
if isinstance(args.log, str):
    loglevel = args.log
elif isinstance(args.log, list) and args.log:
    loglevel = args.log[0]
loglevel= getattr(logging, loglevel.upper())

ASETUKSET = {}

IP = "http://127.0.0.1/"
nyt = time.strftime("%Y%m%d%H%M",time.localtime(time.time()))

# Tunnista käytettävä kone kotikansion perusteella.
KOTIKANSIO = os.path.expanduser("~")
TYOKANSIO = os.path.join(KOTIKANSIO, ".tiedostohallinta")
if not os.path.isdir(TYOKANSIO):
    os.mkdir(TYOKANSIO)
LOGITIEDOSTO = os.path.join(TYOKANSIO, f"tiedostohallinta_logi_{nyt}")
logging.basicConfig(
    format='[%(asctime)s][%(levelname)s] %(message)s',
    datefmt='%m-%d-%Y %H:%M:%S',
    filename=LOGITIEDOSTO,
    filemode='w+',
    level=loglevel)
logging.info(f"Aloitettu, käytetään logitasoa {loglevel}")

LOKAALI_KONE = os.path.basename(KOTIKANSIO)
ASETUSTIEDOSTO = os.path.join(TYOKANSIO, "kansiovakiot.ini")
logging.debug("Kansiomääritelmät:\n"
    +f"    LOKAALI_KONE = {LOKAALI_KONE}\n"
    +f"    KOTIKANSIO = {KOTIKANSIO}\n"
    +f"    TYOKANSIO = {TYOKANSIO}\n"
    +f"    LOGITIEDOSTO = {LOGITIEDOSTO}\n"
    +f"    ASETUSTIEDOSTO = {ASETUSTIEDOSTO}"
    )

# Luetaan asetukset INI-tiedostosta, jos sellainen löytyy.
config = configparser.ConfigParser(default_section="pilperi")

logging.debug(f"Luetaan asetukset asetustiedostosta")
if os.path.isfile(ASETUSTIEDOSTO):
    logging.debug("Asetustiedosto löytyi!")
    config.read(ASETUSTIEDOSTO)
    logging.debug("Luettu.")
else:
    logging.debug("Asetustiedostoa ei löydy, katsotaan resource_stream...")
    config.read(pkg_resources.resource_stream(__name__, 'kansiovakiot.ini'))
    logging.debug("Luettu.")
# Luetaan määrittelyt configista
# Otetaan lokaalia konetta vastaava asetuskokoonpano
if LOKAALI_KONE in config:
    ASETUSKOKOONPANO = LOKAALI_KONE
    logging.info(f"Käytetään asetuskokoonpanoa {ASETUSKOKOONPANO}")
# Mitään ei ole määritelty: laitetaan pääkone
else:
    ASETUSKOKOONPANO = "pilperi"
    logging.info(f"Tyhjä asetustiedosto, käytetään arvoja {ASETUSKOKOONPANO}")
    config[ASETUSKOKOONPANO] = {}


def tarkasta_config():
    '''
    Tarkastetaan että käytössä oleva asetuskokoonpano
    on järkevästi määritelty. Jos jokin asia on hölmösti,
    laitetaan oletusarvo (pääkone)
    '''
    global ASETUSKOKOONPANO
    global ASETUKSET
    global LOGITIEDOSTO
    global KOTIKANSIO
    global TYOKANSIO
    global config
    logging.debug(f"tarkasta_config, asetuskokoonpano = {ASETUSKOKOONPANO}")
    # Tarkistetaan että kokoonpano ylipäätään on configissa
    if ASETUSKOKOONPANO not in config.keys():
        logging.debug("Asetuskokoonpanoa ei asetuksissa, alustetaan")
        config[ASETUSKOKOONPANO] = {}
    # Tarkistetaan että tarvittavat asiat löytyy initiedostosta.
    #Jos ei, laitetaan oletukset mukaan.
    # Paikalliseten tietokantojen sijainti uupuu
    if "paikalliset_tietokannat" not in config[ASETUSKOKOONPANO]:
        logging.debug("Paikallisten tietokantojen sijainteja ei määritelty")
        paikalliset_tietokannat = {
            "musiikki":{
                "tietokannan_sijainti": os.path.join(TYOKANSIO,"musiikit.json"),
                "tietokannan_kohde": os.path.join(KOTIKANSIO, "Musiikki"),
                "tiedostotyyppi": "biisi"
                },
            "internet":{
                "tietokannan_sijainti": os.path.join(TYOKANSIO,"internet.json"),
                "tietokannan_kohde": os.path.join(KOTIKANSIO, "INTERNET"),
                "tiedostotyyppi": "tiedosto"
                },
            "kuvakaappaukset":{
                "tietokannan_sijainti": os.path.join(TYOKANSIO,"kuvakaappaukset.json"),
                "tietokannan_kohde": os.path.join(KOTIKANSIO, "Screenshots"),
                "tiedostotyyppi": "tiedosto"
                }
            }
        config.set(ASETUSKOKOONPANO,
            "paikalliset_tietokannat",
            str(paikalliset_tietokannat))
    ASETUKSET["paikalliset_tietokannat"] = json.loads(
        config.get(ASETUSKOKOONPANO, "paikalliset_tietokannat"))
    # Etäkoneen sijaintimääritelmät uupuu
    if "sijainnit" not in config[ASETUSKOKOONPANO]:
        logging.debug("Etäkoneen tietokantojen händläystä ei määritelty")
        sijainnit = {
            "palvelin": "pettankone",
            "tietokannat_palvelimella": [
                "/home/taira/tietokannat/Musakirjasto/jounimusat.json",
                "/home/taira/tietokannat/Synkka/internet.json",
                "/home/taira/tietokannat/Synkka/kuvakaappaukset.json"
                ],
            "kohdetiedostot": [
                "/home/pilperi/Tietokannat/Synkka/pettan-jounimusat.json",
                "/home/pilperi/Tietokannat/Synkka/pettan-internet.json",
                "/home/pilperi/Tietokannat/Synkka/pettan-kuvakaappaukset.json"
                ],
            "tyypit": [
                "musiikki",
                "internet",
                "kuvakaappaukset"
                ]
            }
        config.set(ASETUSKOKOONPANO,
            "sijainnit",
            str(sijainnit))
    ASETUKSET["sijainnit"] = json.loads(
        config.get(ASETUSKOKOONPANO, "sijainnit"))
    # Voimasuhteita ei määritelty
    if "voimasuhteet" not in config[ASETUSKOKOONPANO]:
        logging.debug("Valta-asetelmaa ei määritelty")
        voimasuhteet = {
            "musiikki": False,
            "internet": False,
            "kuvakaappaukset": False
            }
        config.set(ASETUSKOKOONPANO,
            "voimasuhteet",
            json.dumps(voimasuhteet))
    ASETUKSET["voimasuhteet"] = json.loads(
        config.get(ASETUSKOKOONPANO, "voimasuhteet"))


def tallenna_asetukset():
    '''
    Tallentaa asetukset tiedostoon.
    '''
    global config
    global ASETUSTIEDOSTO
    logging.debug(f"Tallennetaan asetukset tiedostoon {ASETUSTIEDOSTO}")
    with open(ASETUSTIEDOSTO, 'w+') as configfile:
        for key in config.keys():
            logging.debug(f"    {key}")
            for asetus in config[key]:
                logging.debug(f"        {asetus} = {config[key][asetus]}")
        config.write(configfile)
        logging.debug("Tallennettu.")

# Tarkasta asetukset
tarkasta_config()
tallenna_asetukset()
