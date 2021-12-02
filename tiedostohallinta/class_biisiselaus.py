'''
Biisien hakemiseen ja selaamiseen tarvittavat luokat
keskitetysti samassa paikassa.
'''

from tiedostohallinta.class_biisi import Biisi
from tiedostohallinta.class_tiedostopuu import Tiedostopuu

class Hakukriteerit:
	'''
	Hakukriteerien luokka.
	Helpompi että kriteerinäätitelmät on täällä
	piilossa kuin että roikkuvat jossain
	erillisessä funktiossa tmv. (?)
	'''
	def __init__(self, dikti={}):
		self.ehtona_ja       = dikti.get("ehtona_ja")   # onko str-haut ja- vai tai-rakenteisia
		self.artistinimessa  = dikti.get("artistissa")  # lista stringejä
		self.biisinimessa    = dikti.get("biisissa")    # lista stringejä
		self.albuminimessa   = dikti.get("albumissa")   # lista stringejä
		self.tiedostonimessa = dikti.get("tiedostossa") # lista stringejä
		self.raitanumero     = dikti.get("raitanumero") # tuple inttejä
		self.vapaahaku       = dikti.get("vapaahaku")   # vapaakenttähaku

		self.hakukriteereita = len(dikti.keys())-1
		self.tulospuu        = None                     # Tiedostopuu hakutuloksille
		self.hakutuloksia    = 0                        # Montako tulosta löytyi

	def tarkista_biisi(self, biisi, puu):
		'''
		Tarkista biisistä, täyttääkö se annetut hakuehdot.
		Jos jokin annetuista hakuehdoista ei täsmää, palauta False.
		Jos mikään ei palauta Falsea, ehdot täyttyvät.
		'''
		# Vapaakenttähaku menee eri reittiä
		if type(self.vapaahaku) is list and all(type(a) is str for a in self.vapaahaku):
			self.vapaahaku = [a.lower() for a in self.vapaahaku]
			if any([a in str(biisi.esittaja).lower() for a in self.vapaahaku]):
				# print(f"{biisi.esittaja} täsmää johonkin {self.vapaahaku}")
				return(True)
			if any([a in str(biisi.biisinimi).lower() for a in self.vapaahaku]):
				# print(f"{biisi.biisinimi} täsmää johonkin {self.vapaahaku}")
				return(True)
			if any([a in str(biisi.albuminimi).lower() for a in self.vapaahaku]):
				# print(f"{biisi.albuminimi} täsmää johonkin {self.vapaahaku}")
				return(True)
			if any([a in str(biisi.tiedostonimi).lower() for a in self.vapaahaku]):
				# print(f"{biisi.tiedostonimi} täsmää johonkin {self.vapaahaku}")
				return(True)
			# purkkaa: korvaa tiedostonimitermi hetkellisesti vapaahakutermeillä
			vanha_tiedostonimi = self.tiedostonimessa
			for termi in self.vapaahaku:
				self.tiedostonimessa = [termi]
				if self.tarkista_kansio(puu):
					self.tiedostonimessa = vanha_tiedostonimi
					return(True)
			self.tiedostonimessa = vanha_tiedostonimi
			return(False)

		tayttyneet_kriteerit = 0
		# Artistin nimellä haku
		if self.artistinimessa is not None and type(biisi.esittaja) is str:
			if self.ehtona_ja:
				if not(all([a in biisi.esittaja.lower() for a in self.artistinimessa])):
					# print("{}: artistin nimi ei täsmää".format(biisi.esittaja))
					return(False)
			else:
				if not(any([a in biisi.esittaja.lower() for a in self.artistinimessa])):
					# print("{}: artistin nimi ei täsmää".format(biisi.esittaja))
					return(False)
			tayttyneet_kriteerit += 1
		# Biisin nimellä haku
		if self.biisinimessa is not None and type(biisi.biisinimi) is str:
			if self.ehtona_ja:
				if not(all([a in biisi.biisinimi.lower() for a in self.biisinimessa])):
					# print("{}: biisin nimi ei täsmää".format(biisi.biisinimi))
					return(False)
			else:
				if not(any([a in biisi.biisinimi.lower() for a in self.biisinimessa])):
					# print("{}: biisin nimi ei täsmää".format(biisi.biisinimi))
					return(False)
			tayttyneet_kriteerit += 1
		# Albumin nimellä haku
		if self.albuminimessa is not None and type(biisi.albuminimi) is str:
			if self.ehtona_ja:
				if not(all([a in biisi.albuminimi.lower() for a in self.albuminimessa])):
					# print("{}: albumin nimi ei täsmää".format(biisi.albuminimi))
					return(False)
			else:
				if not(any([a in biisi.albuminimi.lower() for a in self.albuminimessa])):
					# print("{}: albumin nimi ei täsmää".format(biisi.albuminimi))
					return(False)
			tayttyneet_kriteerit += 1
		# Tiedoston nimellä haku (biisin tiedostonimi tai kansionimi)
		if self.tiedostonimessa is not None and type(biisi.tiedostonimi) is str:
			if not self.tarkista_kansio(puu):
				if self.ehtona_ja:
					if not all([a in biisi.tiedostonimi.lower() for a in self.tiedostonimessa]):
						# print("{}: tiedostonimi ei täsmää".format(biisi.tiedostonimi))
						return(False)
				else:
					if not any([a in biisi.tiedostonimi.lower() for a in self.tiedostonimessa]):
						# print("{}: tiedostonimi ei täsmää".format(biisi.tiedostonimi))
						return(False)
			tayttyneet_kriteerit += 1
		# Raitanumeron perusteella haku
		if self.raitanumero is not None and type(biisi.raita) is int:
			if biisi.raita not in range(self.raitanumero[0], self.raitanumero[1]+1):
				# print("{}: raitanumero ei täsmää".format(biisi.raita))
				return(False)
			tayttyneet_kriteerit += 1
		# Kaikki annetut ehdot täyttyivät:
		if tayttyneet_kriteerit >= self.hakukriteereita:
			# print("MÄTSI {}".format(biisi.biisinimi))
			return(True)
		# print("Ei riittävästi täyttyneitä kriteereitä: {}/{}".format(tayttyneet_kriteerit, self.hakukriteereita))
		return(False)

	def tarkista_kansio(self, puu):
		'''
		Joskus on paikallaan hakea stringiä tiedostopolusta
		mukaanlukien kansion nimi. Simppeli funktio erillään
		biisitarkastuksesta, koska biisien tiedoissa ei ole tietoa
		kansiopolusta.
		'''
		if self.tiedostonimessa is not None:
			puupolku = puu.hae_nykyinen_polku().lower()
			if self.ehtona_ja and not all([a in puupolku for a in self.tiedostonimessa]):
				return(False)
			elif (not self.ehtona_ja) and (not any([a in puupolku for a in self.tiedostonimessa])):
				return(False)
			return True
		return(False)

	def etsi_tietokannasta(self, puu, uusipuu=None):
		'''
		Etsi annetusta tiedostopuusta kaikki biisit jotka täyttävät
		hakukriteerit, Tiedostopuun muodossa (karsittu versio annetusta puusta)
		'''
		tuloksia = False # Onko annetussa puussa käypiä hakutuloksia vai ei (rekursiota varten)
		if self.tulospuu is None:
			self.tulospuu = Tiedostopuu()
			self.tulospuu.kansio = puu.kansio
			self.tulospuu.kansio = "biisi"
		for biisi in puu.tiedostot:
			if self.tarkista_biisi(biisi, puu):
				self.hakutuloksia += 1
				# print("{} täyttää hakuehdot".format(biisi.biisinimi))
				tuloksia = True
				if uusipuu is None:
					# Juuripuu
					self.tulospuu.tiedostot.append(biisi)
				else:
					# Alikansio
					uusipuu.tiedostot.append(biisi)
		for alikansio in puu.alikansiot:
			# Katso rekursiivisesti, onko alikansiossa yhtään osumaa.
			# Jos on, lisää tulospuun alikansio-osastolle.
			# On myös mahdollista että koko alikansio on validi,
			# koska kansion nimessä on 'tiedostonimi'-hakustringin osuma.
			if uusipuu is None:
				alipuu = Tiedostopuu()
				alipuu.kansio = alikansio.kansio
				alipuu.edellinentaso = puu
				alipuu.syvennystaso = puu.syvennystaso+1
				alipuu.tiedostotyyppi = "biisi"
			else:
				alipuu = Tiedostopuu()
				alipuu.kansio = alikansio.kansio
				alipuu.edellinentaso = uusipuu
				alipuu.syvennystaso = uusipuu.syvennystaso+1
				alipuu.tiedostotyyppi = "biisi"
			kansiossa_oli, tuloskansio = self.etsi_tietokannasta(alikansio, uusipuu=alipuu)
			if kansiossa_oli and uusipuu is None:
				tuloksia = True
				self.tulospuu.alikansiot.append(tuloskansio)
			elif kansiossa_oli:
				tuloksia = True
				uusipuu.alikansiot.append(tuloskansio)
		if uusipuu is None:
			uusipuu = self.tulospuu
		return(tuloksia, uusipuu)

class Artistipuu():
	'''
	Vaihtoehtoversio tiedostopolkupuusta
	jossa kama on jaoteltu artistinnimen mukaan
	eikä kansiorakenteen.

	Ottaa sisään Tiedostopuun täydeltä biisejä,
	lukee näiden metadatasta että mikä esittäjä
	kyseessä ja lisää biisin kansioineen diktiin
	artistin nimen alle.

	Diktin rakenne on
	{Artisti : {
	           albuminnimi: [(Tiedostopuu, Biisi) kaikille albumin biiseille]}
               }
	'''
	def __init__(self, biisipuu=None):
		self.artistit = {}
		self.albumit  = {}
		if type(biisipuu) is Tiedostopuu:
			self.kansoita(biisipuu)
			self.lisaa_feattaajat()

	def kansoita(self, biisipuu):
		'''
		Täytä dikti annetun Tiedostopuun datalla.
		Käy biisit läpi, jäsentele albuminnimien mukaan
		ja lado sen jälkeen albumien biisit niiden artistien
		alle.
		'''
		# Kansion biisit läpi
		for biisi in [a for a in biisipuu.tiedostot if type(a) is Biisi]:
			artisti = biisi.esittaja
			albumi  = biisi.albuminimi
			# Kaikki huonosti määritellyt artistit mäppää Noneen
			if type(artisti) is str and not len(artisti):
				artisti = None
			# Kaikki huonosti määritellyt albuminnimet mäppää Noneen
			if type(albumi) is str and not len(albumi):
				albumi = None
			# Lisää artisti albumin esiintyviin esittäjiin (eka lista)
			# jollei se jo ole siellä, sekä
			# biisituple listaan albumin biisejä (toka lista)
			if albumi not in self.albumit:
				self.albumit[albumi] = [[artisti],[(biisipuu, biisi)]]
			else:
				if artisti not in self.albumit[albumi][0]:
					self.albumit[albumi][0].append(artisti)
				self.albumit[albumi][1].append((biisipuu, biisi))
		# Kansion alikansiot läpi (rekursio)
		for alikansio in biisipuu.alikansiot:
			self.kansoita(alikansio)

	def jarkkaa_biisinumeron_mukaan(self, lista_biiseja):
		'''
		Koeta järjestää listan biisit näiden raitanumeron mukaan.
		'''
		if type(lista_biiseja) not in (list, tuple) or any([type(a) is not tuple or len(a) != 2 for a in lista_biiseja]):
			return(lista_biiseja)
		fiksut = [] # helposti järkättävissä
		tyhmat = [] # määrittelemättömät ja "tr01" ymv
		for biisituple in lista_biiseja:
			if type(biisituple[1]) is not Biisi or biisituple[1].raita is None:
				tyhmat.append(biisituple)
			else:
				try:
					raitanumero = int(biisituple[1].raita)
					biisituple[1].raita = raitanumero
					fiksut.append(biisituple)
				except ValueError:
					tyhmat.append(biisituple)
		fiksut = sorted(fiksut, key = lambda t: t[1].raita)
		kansa = fiksut + tyhmat
		return(kansa)

	def lisaa_feattaajat(self):
		'''
		Täytä artistien albumit sellaisiksi
		että ne sisältävät myös feattaavat artistit.
		Skippaa None-sets.
		'''
		for albumi in self.albumit:
			for artisti in self.albumit[albumi][0]:
				# Lisää albumin _kaikki_ raidat artistin alle artistidiktissä
				if artisti not in self.artistit:
					self.artistit[artisti] = {albumi: self.albumit[albumi][1]}
				else:
					self.artistit[artisti][albumi] = self.albumit[albumi][1]
		# Laita lopuksi vielä albumien sisällöt raitanumerojärkkään
		for artisti in [art for art in self.artistit if art is not None]:
			for albumi in [alb for alb in self.artistit[artisti] if alb is not None]:
				self.artistit[artisti][albumi] = self.jarkkaa_biisinumeron_mukaan(self.artistit[artisti][albumi])

def kirjaa(asetukset=None):
	'''
	Kirjaa musiikkitiedot tietokantatiedostoihin.
	Ottaa vapaaehtoisena sisäänmenoparametrina diktin
	jossa määritelty mistä luetaan musiikkia ja mihin
	kansioon niistä lasketut tietokannat pitäisi talllentaa.
	Diktin formaattina
	{"LOKAALIT_MUSIIKIT": [kansio_1, kansio_2, ..., kansio_n],
	 "LOKAALIT_MUSIIKIT": [tulostiedosto_1, tulostiedosto_2, ..., tulostiedosto_n]}
	siten että arvot menevät pareittain indeksoidusti: kansion_1 musiikit kirjataan
	tiedostoon tulostiedosto_1 jne.

	(tilapäisratkaisu kunnes jaksan vääntää kunnon asetusolion kasaan)
	'''
	# Tarkista annettiinko asetuksia ja jos, onko ne validit
	validit_asetukset = False
	if type(asetukset) is dict:
		# Avain läsnä asetuksissa
		if type(asetukset.get("LOKAALIT_MUSIIKIT")) not in (list,tuple):
			pass
		# Avaimen takana lista stringejä
		elif not all([type(k) is str for k in asetukset.get("LOKAALIT_MUSIIKIT")]):
			pass
		# Kaikki stringit olemassaolevia kansioita
		elif not all([os.path.isdir(k) for k in asetukset.get("LOKAALIT_MUSIIKIT")]):
			pass
		# Sama toiselle avaimelle (tulostiedostojen ei vielä tarvitse olla olemassa)
		elif type(asetukset.get("LOKAALIT_TIETOKANNAT")) not in (list,tuple):
			pass
		elif all([type(k) is str for k in asetukset.get("LOKAALIT_TIETOKANNAT")]):
			validit_asetukset = True
	# Tarkista myös oletusasetusten järkevyys
	validit_oletusasetukset = False
	if type(kvak.LOKAALIT_MUSIIKIT) not in (list,tuple):
		pass
	elif not all([type(k) is str for k in kvak.LOKAALIT_MUSIIKIT]):
		pass
	elif not all([os.path.isdir(k) for k in kvak.LOKAALIT_MUSIIKIT]):
		pass
	elif type(kvak.LOKAALIT_TIETOKANNAT) not in (list,tuple):
		pass
	elif all([type(k) is str for k in kvak.LOKAALIT_TIETOKANNAT]):
		validit_oletusasetukset = True

	# Jos syötetyt asetukset on validit, käytetään niitä
	if validit_asetukset:
		mestat = {"LOKAALIT_MUSIIKIT":    asetukset.get("LOKAALIT_MUSIIKIT"),
                  "LOKAALIT_TIETOKANNAT": asetukset.get("LOKAALIT_TIETOKANNAT")}
	# Jos ei, niin käytä oletuksena paikallisissa asetuksissa määriteltyjä
	elif validit_oletusasetukset:
		mestat = {"LOKAALIT_MUSIIKIT":    kvak.LOKAALIT_MUSIIKIT,
                  "LOKAALIT_TIETOKANNAT": kvak.LOKAALIT_TIETOKANNAT}
	# Muutoin kaikki on menetetty
	else:
		print("Ei ole mitään oikeita kansioita joista lukea musiikkia tai mihin kirjoittaa tulokset")
		return

	t1 = time.time()
	for i,lokaali_musakansio in enumerate(mestat["LOKAALIT_MUSIIKIT"]):
		puu = Tiedostopuu()
		puu.kansio = lokaali_musakansio
		puu.tiedostotyyppi = "biisi"
		puu.kansoita()
		tietokantatiedosto = mestat["LOKAALIT_TIETOKANNAT"][i]
		f = open(tietokantatiedosto, "w+")
		f.write(str(puu))
		f.close()
	t2 = time.time()
	print("Aikaa kului {:.2f} s".format(t2-t1))

def lukutesti():
	'''
	Lue tietokannat tiedostoista Tiedostopuiksi
	ja kirjaa puut toisiin tietokantoihin, jotta voidaan
	testata onnistuuko toisiminen yks yhteen.
	'''
	for tiedosto in kvak.LOKAALIT_TIETOKANNAT:
		puu = Tiedostopuu()
		puu.tiedostotyyppi = "biisi"
		f = open(tiedosto, "r")
		puu.lue_tiedostosta(f)
		f.close()
		o = open(tiedosto.replace(".tietokanta", "_kopio.tietokanta"), "w+")
		o.write(str(puu))
		o.close()

if __name__ == "__main__":
	# pass
	kirjaa()
	# Testaa hakukriteereiden käyttöä:
	for tiedosto in kvak.LOKAALIT_TIETOKANNAT:
		puu = Tiedostopuu()
		puu.tiedostotyyppi=Biisi
		f = open(tiedosto, "r")
		puu.lue_tiedostosta(f)
		f.close()
		hakudikti = {
					"ehtona_ja":     False,
					"artistissa":    ["妖精", "亭刻"],
					# "biisissa":      ["ノゾム", "神"],
					# "albumissa":     ["神"],
					# "tiedostossa":   ["eroge"],
					# "raitanumero":   (1,3)
					}
		haku = Hakukriteerit(hakudikti)
		oli_tuloksia, tulokset = haku.etsi_tietokannasta(puu)
		print("Tuloksia: {:d}".format(haku.hakutuloksia))
		# Kirjaa tulokset tiedostoon
		#f = open(kvak.LOKAALIT_TIETOKANNAT[0].replace(".tietokanta", "_hakutulokset.tietokanta"), "w+")
		#f.write(str(tulokset))
		#f.close()
