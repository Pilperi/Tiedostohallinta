'''
Biisien ja biisikirjastojen luokkamääritelmät,
biisien metadatan lukuun tarvittavat funktiot,
ja näiden tietojen luku ja kirjoitus tietokantatiedostosta.

Pohjaa lähinnä moduuleihin 'mutagen' (metadatan luku)
ja 'json' (tiedon jäsentely).
'''

import os
import time
import json
import mutagen as mtg
import tiedostohallinta.vakiot_kansiovakiot as kvak
import tiedostohallinta.funktiot_kansiofunktiot as kfun
from mutagen.easyid3 import EasyID3
from mutagen.flac import FLAC


class Biisi():
	'''
	Biisitietojen perusluokka.
	Biiseistä ei tarvitse ihan kauheaa
	määrää tietoa, kenttiä voi "helposti"
	lisäillä sitten jälkikäteen jos tarvitsee.
	'''
	TYYPPI = "biisi"
	def __init__(self, kohteesta=None):
		'''
		Alustetaan biisi nulleilla,
		ja jos (kun) 'kohteesta'-parametri on määritelty,
		täytetään tiedot sen mukaan.
		'''
		# Tiedostopolusta pelkkä loppuosa,
		# turha toistaa samoja pätkiä moneen kertaan
		# (pidetään kirjaa muualla)
		self.tyyppi = Biisi.TYYPPI
		self.tiedostonimi	= None
		self.albuminimi		= None
		self.albumiesittaja = None
		self.esittaja		= None
		self.biisinimi		= None
		self.vuosi			= None
		self.raita			= None
		self.raitoja		= None
		self.lisayspaiva	= 0
		self.hash           = None

		# Lukukohteena tiedostopolku (str)
		if type(kohteesta) is str:
			self.lue_tiedostosta(kohteesta)

		# Lukukohteena dikti (luettu tiedostosta tmv)
		elif isinstance(kohteesta, dict):
			self.tiedostonimi   = kohteesta.get("tiedostonimi")
			self.albuminimi     = kohteesta.get("albuminimi")
			self.albumiesittaja = kohteesta.get("albumiesittaja")
			self.esittaja       = kohteesta.get("esittaja")
			self.biisinimi      = kohteesta.get("biisinimi")
			self.vuosi          = kohteesta.get("vuosi")
			self.raita          = kohteesta.get("raita")
			self.raitoja        = kohteesta.get("raitoja")
			self.lisayspaiva    = kohteesta.get("lisayspaiva")
			self.hash           = kohteesta.get("hash")

	@classmethod
	def diktista(cls, dikti):
		biisi = Biisi()
		if isinstance(dikti, dict):
			biisi.tiedostonimi   = dikti.get("tiedostonimi")
			biisi.albuminimi     = dikti.get("albuminimi")
			biisi.albumiesittaja = dikti.get("albumiesittaja")
			biisi.esittaja       = dikti.get("esittaja")
			biisi.biisinimi      = dikti.get("biisinimi")
			biisi.vuosi          = dikti.get("vuosi")
			biisi.raita          = dikti.get("raita")
			biisi.raitoja        = dikti.get("raitoja")
			biisi.lisayspaiva    = dikti.get("lisayspaiva")
			biisi.hash           = dikti.get("hash")
		return biisi

	def lue_tiedostosta(self, tiedostopolku):
		'''
		Lue biisin tiedot tiedostosta.
		Metadatan tyyppi arvataan päätteestä
		ja mietitään sit myöhemmin jos asiat ei toimikaan.
		Hitto kun kaikki mutagenin paluuarvot on yhden alkion listoja...
		'''
		paate = kfun.paate(tiedostopolku)[1].lower()
		if paate in kvak.MUSATIEDOSTOT:
			self.hash = kfun.hanki_hash(tiedostopolku)
			if paate == "mp3":
				try:
					tagit = EasyID3(tiedostopolku)
				except mtg.MutagenError as err:
					print(f"   tiedosto kusee\n  {err}")
					tagit = {}
				# print(tagit)
				self.tiedostonimi	= os.path.basename(tiedostopolku)
				if tagit.get("album"):
					self.albuminimi		= tagit.get("album")[0]
				if tagit.get("albumartist"):
					self.albumiesittaja = tagit.get("albumartist")[0]
				if tagit.get("artist"):
					self.esittaja		= tagit.get("artist")[0]
				if tagit.get("title"):
					self.biisinimi		= tagit.get("title")[0]
				if tagit.get("date"):
					self.vuosi			= tagit.get("date")[0]
				self.raita			= self.raitatiedot(tagit.get("tracknumber"))[0]
				self.raitoja		= self.raitatiedot(tagit.get("tracknumber"))[1]
				self.lisayspaiva	= self.paivays()[0]
			elif paate == "flac":
				try:
					tagit = FLAC(tiedostopolku)
				except mtg.MutagenError as err:
					print(f"   tiedosto kusee\n  {err}")
					tagit = {}
				self.tiedostonimi	= os.path.basename(tiedostopolku)
				if tagit.get("album"):
					self.albuminimi		= tagit.get("album")[0]
				if tagit.get("albumartist"):
					self.albumiesittaja = tagit.get("albumartist")[0]
				if tagit.get("artist"):
					self.esittaja		= tagit.get("artist")[0]
				if tagit.get("title"):
					self.biisinimi		= tagit.get("title")[0]
				if tagit.get("date"):
					self.vuosi			= tagit.get("date")[0]
				raitatiedot = self.raitatiedot(tagit.get("tracknumber"))
				if raitatiedot:
					self.raita			= raitatiedot[0]
				if raitatiedot and raitatiedot[1] is not None:
					self.raitoja = raitatiedot[1]
				elif tagit.get("tracktotal") and all([a.isnumeric for a in tagit.get("tracktotal")[0]]):
					try:
						self.raitoja		= int(tagit.get("tracktotal")[0])
					except ValueError:
						self.raitoja 		= 0
				self.lisayspaiva	= self.paivays()[0]
			elif paate == "wma":
				# Tää on kamala eikä pitäisi olla vuonna 2020
				try:
					tagit = mtg.File(tiedostopolku)
				except mtg.MutagenError as err:
					print(f"   tiedosto kusee\n  {err}")
					tagit = {}
				self.tiedostonimi	= os.path.basename(tiedostopolku)
				if tagit.get("Author"):
					self.albumiesittaja = tagit.get("Author")[0].value
					self.esittaja		= self.albumiesittaja
				if tagit.get("Title"):
					self.biisinimi		= tagit.get("Title")[0].value
				if tagit.get("WM/TrackNumber"):
					self.raita			= tagit.get("WM/TrackNumber")[0].value
					self.raitoja		= self.raita
				self.lisayspaiva	= self.paivays()[0]

	def raitatiedot(self, raitatagi):
		'''
		Lue raitanumero ja kokonaisraitamäärä
		metadatasta. Data hankalasti joko muotoa
		'n' (raidannumero) tai 'n/m' (raita/raitoja),
		niin täytyy vähän parsia.
		'''
		(raita, raitoja) = (None, None)
		# Pitäisi olla ei-tyhjä lista
		if raitatagi:
			splitattu = raitatagi[0].split("/")
			if all([a.isnumeric for a in splitattu[0]]):
				try:
					raita = int(splitattu[0])
				except ValueError:
					raita = 0
			if len(splitattu) > 1 and all([a.isnumeric for a in splitattu[1]]):
				try:
					raitoja = int(splitattu[1])
				except ValueError:
					raitoja = 0
		return((raita, raitoja))

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

	def diktiksi(self):
		'''
		Palauttaa
		---------
		dict
			Diktiversio biisistä.
			Olio rakennettavissa tämän pohjalta myöhemmin.
		'''
		diktiversio = {
					"tiedostonimi":     self.tiedostonimi,
					"esittaja":         self.esittaja,
					"biisinimi":        self.biisinimi,
					"albuminimi":       self.albuminimi,
					"raita":            self.raita,
					"raitoja":          self.raitoja,
					"vuosi":            self.vuosi,
					"albumiesittaja":   self.albumiesittaja,
					"lisayspaiva":      self.lisayspaiva,
					"hash":	            self.hash
					}
		return diktiversio

	def __str__(self):
		diktiversio = self.diktiksi()
		return(json.dumps(diktiversio))

	def __bool__(self):
		'''
		Jos tiedoston jokin perustiedoista
		(ihan tosi perustiedoista) ei ole
		määritelty, biisiä ei ole kunnolla määritelty.
		'''
		if None in [self.tiedostonimi, self.lisayspaiva]:
			return(False)
		return(True)
