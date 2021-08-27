'''
Lue oleellisimmat kansiosijainnit ymv ini-tiedostosta ja aseta
ne globaaleiksi vakioiksi
'''
import os
import sys
import json
import configparser
import pkg_resources

VERBOOSI = any([arg in sys.argv for arg in ("-v", "--verbose", "--verboosi")]) # ei turhaa printtailua

BUFFERI         = 65536 # tiedostoja RAM:iin 64kb paloissa
MERKKIBUFFERI   = 4000	# jsoneita RAM:iin 4000 merkin paloissa

TESTIMOODI = "--testimoodi" in sys.argv # varovainen testiympäristö, ts. ei kirjoittelua vaan pelkkää printtiä

LOKAALIT_MUSIIKIT    = []
LOKAALIT_INTERNET    = []
LOKAALIT_SCREENSHOTS = []
LOKAALIT_TIETOKANNAT = {
                       "Musiikki":    [],
                       "INTERNET":    [],
                       "Screenshots": []
                       }
MUSATIEDOSTOT        = ["mp3", "flac", "wma", "ogg"]
KIELLETYT            = []
ETAPALVELIN          = "pettankone"
VOIMASUHTEET         = {
                       "Musiikki":    (False, 0),
                       "INTERNET":    (False, 0),
                       "Screenshots": (False, 0)
                       }


# Tunnista käytettävä kone kotikansion perusteella.
KOTIKANSIO = os.path.expanduser("~")
LOGITIEDOSTO = os.path.join(KOTIKANSIO, "tiedostohallinta_logi") # todo
LOKAALI_KONE = os.path.basename(KOTIKANSIO)
if VERBOOSI:
	print(f"Lokaali kone: {LOKAALI_KONE}")

# Luetaan asetukset INI-tiedostosta, jos sellainen löytyy.
config = configparser.ConfigParser(default_section="pilperi")
if VERBOOSI:
	print("Luetaan asetukset .ini-tiedostosta")
if os.path.exists(os.path.join(KOTIKANSIO, "kansiovakiot.ini")):
	config.read(os.path.join(KOTIKANSIO, "kansiovakiot.ini"))
else:
	config.read(pkg_resources.resource_stream(__name__, 'kansiovakiot.ini'))
# Luetaan määrittelyt configista
# Otetaan lokaalia konetta vastaava asetuskokoonpano
if LOKAALI_KONE in config:
	ASETUSKOKOONPANO = LOKAALI_KONE
	if VERBOOSI:
		print(f"Käytetään arvoja {ASETUSKOKOONPANO}")
# Mitään ei ole määritelty: laitetaan pääkone
else:
	ASETUSKOKOONPANO = "pilperi"
	if VERBOOSI:
		print(f"Tyhjä asetustiedosto, käytetään arvoja {ASETUSKOKOONPANO}")
	config[ASETUSKOKOONPANO] = {}


def tarkasta_config():
	'''
	Tarkastetaan että käytössä oleva asetuskokoonpano
	on järkevästi määritelty. Jos jokin asia on hölmösti,
	laitetaan oletusarvo (pääkone)
	'''
	global ASETUSKOKOONPANO
	global config
	if VERBOOSI:
		print(f"Asetuskokoonpano {ASETUSKOKOONPANO}")
	# Tarkistetaan että kokoonpano ylipäätään on configissa
	if ASETUSKOKOONPANO not in config.keys():
		config[ASETUSKOKOONPANO] = {}
	# Tarkistetaan että tarvittavat asiat löytyy initiedostosta. Jos ei, laitetaan oletukset mukaan.
	# Musakansio uupuu
	if "logitiedosto" not in config[ASETUSKOKOONPANO]:
		if VERBOOSI:
			print("Logitiedoston sijaintia ei määritelty")
		config.set(ASETUSKOKOONPANO, "logitiedosto", "/home/pilperi/synkkalogi")
	# Musakansio uupuu
	if "kansiot musiikki" not in config[ASETUSKOKOONPANO]:
		if VERBOOSI:
			print("Musakansioiden sijainteja ei määritelty")
		config.set(ASETUSKOKOONPANO, "kansiot musiikki", "[\"/home/pilperi/Musiikki/\"]")
	# INTERNET-kansio uupuu
	if "kansiot internet" not in config[ASETUSKOKOONPANO]:
		if VERBOOSI:
			print("Kuvakansioiden sijainteja ei määritelty")
		config.set(ASETUSKOKOONPANO, "kansiot internet", "[\"/mnt/Norot/Data/INTERNET/\"]")
	# Screenshottikansio uupuu
	if "kansiot screenshots" not in config[ASETUSKOKOONPANO]:
		if VERBOOSI:
			print("Kuvakansioiden sijainteja ei määritelty")
		config.set(ASETUSKOKOONPANO, "kansiot screenshots", "[\"/mnt/Suzuya/Suzuyajako/Screenshots/Jaotellut/\"]")
	# Musatietokannat uupuu
	if "tietokannat musiikki" not in config[ASETUSKOKOONPANO]:
		if VERBOOSI:
			print("Musatietokannan sijaintia ei määritelty")
		config.set(ASETUSKOKOONPANO, "tietokannat musiikki", "[\"/home/pilperi/Tietokannat/Musiikit/musiikit.tietokanta\"]")
	# INTERNET-tietokannat uupuu
	if "tietokannat internet" not in config[ASETUSKOKOONPANO]:
		if VERBOOSI:
			print("Kuvatietokannan sijaintia ei määritelty")
		config.set(ASETUSKOKOONPANO, "tietokannat internet", "[\"/home/pilperi/Tietokannat/Synkka/INTERNET.tietokanta\"]")
	# INTERNET-tietokannat uupuu
	if "tietokannat screenshots" not in config[ASETUSKOKOONPANO]:
		if VERBOOSI:
			print("Screenshottitietokannan sijaintia ei määritelty")
		config.set(ASETUSKOKOONPANO, "tietokannat screenshots", "[\"/home/pilperi/Tietokannat/Synkka/Screenshots.tietokanta\"]")
	# Sallitut tiedostomuodot uupuu
	if "sallitut tiedostomuodot" not in config[ASETUSKOKOONPANO]:
		if VERBOOSI:
			print("Sallittuja musatiedostomuotoja ei määritelty, asetetaan oletusarvot")
		config.set(ASETUSKOKOONPANO, "sallitut tiedostomuodot", "[\"mp3\", \"flac\", \"wma\", \"ogg\"]")
	# Kielletyt tiedostomuodot uupuu (tätä ei oikeestaan tarttis)
	if "kielletyt tiedostomuodot" not in config[ASETUSKOKOONPANO]:
		if VERBOOSI:
			print("Kiellettyjä tiedostomuotoja ei määritelty, asetetaan oletusarvot muodon vuoksi")
		config.set(ASETUSKOKOONPANO, "kielletyt tiedostomuodot", "[]")
	# Etäpalvelin uupuu
	if "etapalvelin" not in config[ASETUSKOKOONPANO]:
		if VERBOOSI:
			print("Etäpalvelinta ei määritelty, laitetaan \'pettankone\'")
		config.set(ASETUSKOKOONPANO, "etapalvelin", "pettankone")
	# Etätietokannat (musiikki) uupuu
	if "etakone tietokannat musiikki" not in config[ASETUSKOKOONPANO]:
		if VERBOOSI:
			print("Etäkoneen musiikkitietokantasijainteja ei määritelty, laitetaan pettanin")
		config.set(ASETUSKOKOONPANO, "etakone tietokannat musiikki", json.dumps(["/home/taira/tietokannat/Musakirjasto/jounimusat.tietokanta",\
	                                 "/home/taira/tietokannat/Musakirjasto/nipamusat.tietokanta",\
	                                 "/home/taira/tietokannat/Musakirjasto/tursamusat.tietokanta"], indent=4))
	# Etätietokannat (INTERNET) uupuu
	if "etakone tietokannat internet" not in config[ASETUSKOKOONPANO]:
		if VERBOOSI:
			print("Etäkoneen kuvatietokantasijainteja ei määritelty, laitetaan pettanin")
		config.set(ASETUSKOKOONPANO, "etakone tietokannat internet", "[\"/home/taira/tietokannat/Synkka/INTERNET.tietokanta\"]")
	# Etätietokannat (screenshots) uupuu
	if "etakone tietokannat screenshots" not in config[ASETUSKOKOONPANO]:
		if VERBOOSI:
			print("Etäkoneen screenshottitietokantasijainteja ei määritelty, laitetaan pettanin")
		config.set(ASETUSKOKOONPANO, "etakone tietokannat screenshots", "[\"/home/taira/tietokannat/Synkka/Screenshots.tietokanta\"]")
	# Masteristatus (musiikki) uupuu
	if "masteri musiikki" not in config[ASETUSKOKOONPANO]:
		if VERBOOSI:
			print("Masteristatusta (musiikki) ei määritelty")
		config.set(ASETUSKOKOONPANO, "masteri musiikki", json.dumps([True, 0]))
	# Masteristatus (INTERNET) uupuu
	if "masteri internet" not in config[ASETUSKOKOONPANO]:
		if VERBOOSI:
			print("Masteristatusta (INTERNET) ei määritelty")
		config.set(ASETUSKOKOONPANO, "masteri internet", json.dumps([True, 0]))
	# Masteristatus (INTERNET) uupuu
	if "masteri screenshots" not in config[ASETUSKOKOONPANO]:
		if VERBOOSI:
			print("Masteristatusta (screenshots) ei määritelty")
		config.set(ASETUSKOKOONPANO, "masteri screenshots", json.dumps([False, 0]))


def aseta_vakiot():
	'''
	Asettaa globaalit vakiot asetuskokoonpanon mukaisiksi.
	'''
	# Asetusmäärittelyt
	global ASETUSKOKOONPANO
	global config
	global VERBOOSI

	# Itse asetukset
	global LOKAALIT_MUSIIKIT
	global MUSATIEDOSTOT
	global KIELLETYT
	global ETAPALVELIN
	global LOKAALIT_TIETOKANNAT
	global ETAPALVELIN_TIETOKANNAT
	global VOIMASUHTEET

	# Asetetaan vakioihin, jos asetuskokoonpano määritelty
	if ASETUSKOKOONPANO in config:
		if VERBOOSI:
			print("Asetetaan vakiot")
		# Kansiorakenteet
		LOKAALIT_MUSIIKIT                   = json.loads(config.get(ASETUSKOKOONPANO,"kansiot musiikki"))
		LOKAALIT_INTERNET                   = json.loads(config.get(ASETUSKOKOONPANO,"kansiot internet"))
		LOKAALIT_SCREENSHOTS                = json.loads(config.get(ASETUSKOKOONPANO,"kansiot screenshots"))
		LOKAALIT_TIETOKANNAT                = {
                                               "Musiikki":    json.loads(config.get(ASETUSKOKOONPANO,"tietokannat musiikki")),
                                               "INTERNET":    json.loads(config.get(ASETUSKOKOONPANO,"tietokannat internet")),
                                               "Screenshots": json.loads(config.get(ASETUSKOKOONPANO,"tietokannat screenshots"))
                                               }
		ETAPALVELIN_TIETOKANNAT             = {
                                               "Musiikki":    json.loads(config.get(ASETUSKOKOONPANO,"etakone tietokannat musiikki")),
                                               "INTERNET":    json.loads(config.get(ASETUSKOKOONPANO,"etakone tietokannat internet")),
                                               "Screenshots": json.loads(config.get(ASETUSKOKOONPANO,"etakone tietokannat screenshots"))
                                               }
		KIELLETYT                           = json.loads(config.get(ASETUSKOKOONPANO,"kielletyt tiedostomuodot"))
		MUSATIEDOSTOT                       = json.loads(config.get(ASETUSKOKOONPANO,"sallitut tiedostomuodot"))
		ETAPALVELIN                         = config.get(ASETUSKOKOONPANO,"etapalvelin")
		VOIMASUHTEET                        = {"Musiikki": config.get(ASETUSKOKOONPANO,"masteri musiikki"),
                                               "INTERNET": config.get(ASETUSKOKOONPANO,"masteri internet"),
                                               "Screenshots": config.get(ASETUSKOKOONPANO,"masteri screenshots")}

	# Tällaisia asetuksia ei ole, mistä moiset keksit?
	elif VERBOOSI:
		print(f"Asetuskokoonpanoa {ASETUSKOKOONPANO} ei ole määritelty.")


def tallenna_asetukset():
	'''
	Tallentaa asetukset tiedostoon.
	'''
	global config
	with open('./asetukset.ini', 'w+') as configfile:
		if VERBOOSI:
			print("Tallennetaan asetukset tiedostoon")
			for key in config.keys():
				print(key)
				for asetus in config[key]:
					print(f"  {asetus} = {config[key][asetus]}")
		config.write(configfile)
		if VERBOOSI:
			print("Tallennettu.")

# Tarkasta asetukset
tarkasta_config()
aseta_vakiot()
# tallenna_asetukset()
