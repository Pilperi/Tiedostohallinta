import os
import time
import json
from . import funktiot_kansiofunktiot as kfun

class Tiedosto:
	'''
	Luokka yleisille tiedostoille.
	Tiedot: tiedostonimi, muokkauspäivä, hash.
	'''
	def __init__(self, kohteesta=None):
		self.tiedostonimi = None
		self.lisayspaiva  = None
		self.hash         = None

		# print(kohteesta)

		# Lukukohteena tiedostopolku (str)
		if type(kohteesta) is str:
			self.lue_tiedostosta(kohteesta)

		# Lukukohteena dikti (luettu tiedostosta tmv)
		elif type(kohteesta) is dict:
			self.lue_diktista(kohteesta)

	def lue_tiedostosta(self, tiedostopolku):
		'''
		Lue biisin tiedot tiedostosta.
		Metadatan tyyppi arvataan päätteestä
		ja mietitään sit myöhemmin jos asiat ei toimikaan.
		Hitto kun kaikki mutagenin paluuarvot on yhden alkion listoja...
		'''
		self.tiedostonimi = os.path.basename(tiedostopolku)
		self.lisayspaiva  = self.paivays()[0]
		self.hash         = kfun.hanki_hash(tiedostopolku)

	def paivays(self, lue=None):
		'''
		Muodosta tai lue päiväys, formaatissa
		(inttimuoto yyyymmdd, (yyyy, mm, dd))-tuple
		'''
		kokoversio	= 0
		vuosi		= 0
		kuukausi	= 0
		paiva		= 0
		tunnit      = 0
		minuutit    = 0
		# Pilko annettu päiväys
		if type(lue) in [int, str]:
			stringiversio = str(lue)
			if len(stringiversio) == 12 and all([a.isnumeric for a in stringiversio]):
				kokoversio  = int(stringiversio)
				vuosi       = int(stringiversio[:4])
				kuukausi    = int(stringiversio[4:6])
				paiva       = int(stringiversio[6:8])
				tunnit      = int(stringiversio[8:10])
				minuutit    = int(stringiversio[10:12])
			# Vanha versio ilman tunteja ja minuutteja
			elif len(stringiversio) == 8 and all([a.isnumeric for a in stringiversio]):
				kokoversio  = int(stringiversio)*10000
				vuosi       = int(stringiversio[:4])
				kuukausi    = int(stringiversio[4:6])
				paiva       = int(stringiversio[6:8])
				tunnit      = 0
				minuutit    = 0
		# Nykyhetken päiväys
		else:
			paivays  = time.localtime()
			vuosi    = paivays.tm_year
			kuukausi = paivays.tm_mon
			paiva    = paivays.tm_mday
			tunnit   = paivays.tm_hour
			minuutit = paivays.tm_min
			kokoversio = int("{:04d}{:02d}{:02d}{:02d}{:02d}".format(vuosi,kuukausi,paiva,tunnit,minuutit))
		return((kokoversio, (vuosi, kuukausi, paiva, tunnit, minuutit)))

	def lue_diktista(self, dikti):
		'''
		Koetetaan lukea diktistä metadatat.
		'''
		self.tiedostonimi = dikti.get("tiedostonimi")
		self.lisayspaiva  = dikti.get("lisayspaiva")
		self.hash         = dikti.get("hash")

	def __str__(self):
		diktiversio = {
					"tiedostonimi":		self.tiedostonimi,
					"lisayspaiva":		self.lisayspaiva,
					"hash":		        self.hash
					}
		return(json.dumps(diktiversio))

	def __bool__(self):
		if None in [self.tiedostonimi, self.lisayspaiva]:
			return(False)
		return(True)
