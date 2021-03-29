import os
import shutil
from . import vakiot_kansiovakiot as kvak
from . import funktiot_kansiofunktiot as kfun
from . import funktiot_logifunktiot as logfun
from .class_tiedosto import Tiedosto
from .class_biisit import Biisi
from .class_tiedostopuu import Tiedostopuu

def vertaa_puita(isantapuu=None, isantapalvelin=None, lapsipuu=None, lapsipalvelin=None, tulosta=False, logitiedosto=None):
	'''
	Vertaa lapsipuuta isäntäpuuhun.
	Jos lapsipuussa on kansioita tai tiedostoja jotka
	puuttuvat isäntäpuusta, poista ne (puusta ja kovalevyltä)
	Jos lapsipuusta puuttuu tiedostoja tai kansioita joita
	isäntäpuussa on, tai isäntäpuun versiot tiedostoista on uudempia,
	kopioi ne isäntäpuusta lokaaliin tiedostojärjestelmään.

	Käy koko puu rekursiivisesti läpi.
	Tiedostosiirrot käyvät SCP:llä, muodossa scp isantapalvelin:asia lapsipalvelin:asia
	Yleensä näistä toinen on lokaali tiedostojärjestelmä, jolloin sen palvelimeksi laitetaan None.
	'''
	if None in [isantapuu, lapsipuu]:
		return(None)

	# Tiedosto pitäisi olla ja puuttuu tai on vanhentunut ja sisältö muuttunut: kopioi
	for tiedosto in isantapuu.tiedostot:
		puuttuu       = True
		vanhentunut   = False
		muuttunut     = False
		for lapsitiedosto in [a for a in lapsipuu.tiedostot if a.tiedostonimi==tiedosto.tiedostonimi]:
			puuttuu     = False
			vanhentunut = lapsitiedosto.lisayspaiva < tiedosto.lisayspaiva
			muuttunut   = lapsitiedosto.hash != tiedosto.hash
		if puuttuu or (vanhentunut and muuttunut):
			# lahdetiedosto = os.path.join(isantapuu.hae_nykyinen_polku(), tiedosto.tiedostonimi)
			lahdetiedosto = isantapuu.hae_nykyinen_polku() + tiedosto.tiedostonimi
			# kohdetiedosto = os.path.join(lapsipuu.hae_nykyinen_polku(), tiedosto.tiedostonimi)
			kohdetiedosto = lapsipuu.hae_nykyinen_polku()
			# Siirrä
			logfun.kirjaa(logitiedosto, f"Lataa tiedosto\n   {lahdetiedosto}\n   kohteeseen\n   {kohdetiedosto}", 3)
			if kvak.VERBOOSI:
				print(f"Lataa tiedosto\n   {lahdetiedosto}\n   kohteeseen\n   {kohdetiedosto}")
			if kvak.TESTIMOODI:
				break
			else:
				siirrettiin = False
				for yritys in range(5):
					siirrettiin = kfun.lataa(True, isantapalvelin, lahdetiedosto, lapsipalvelin, kohdetiedosto)
					if siirrettiin:
						muutettiin = kfun.muuta_oikeudet(os.path.join(kohdetiedosto, tiedosto.tiedostonimi))
						lapsipuu.tiedostot.append(tiedosto)
						logfun.kirjaa(logitiedosto, "Siirrettiin.", 3)
						break
					else:
						logfun.kirjaa(logitiedosto, "Ei saatu siirrettyä :<", 3)
	# Tiedostoa ei pitäisi olla: poista
	poistetut_tiedostot = []
	for indeksi,tiedosto in enumerate(lapsipuu.tiedostot):
		if not any([a.tiedostonimi==tiedosto.tiedostonimi for a in isantapuu.tiedostot]):
			# lahdetiedosto = os.path.join(lapsipuu.hae_nykyinen_polku(), tiedosto.tiedostonimi)
			# lahdetiedosto = lapsipuu.hae_nykyinen_polku() + tiedosto.tiedostonimi
			lahdetiedosto = lapsipuu.hae_nykyinen_polku() + tiedosto.tiedostonimi
			# Tiedosto etäpalvelimella
			if type(lapsipalvelin) is str:
				logfun.kirjaa(logitiedosto, f"Poista tiedosto\n   {lahdetiedosto}\n   palvelimelta\n   {lapsipalvelin}", 3)
				if kvak.VERBOOSI:
					print(f"Poista tiedosto\n   {lahdetiedosto}\n   palvelimelta\n   {lapsipalvelin}")
				if not kvak.TESTIMOODI:
					poistettu = False
					for i in range(5):
						poistettu, virhe = kfun.etapoisto(True, lapsipalvelin, lahdetiedosto)
						if poistettu or "No such file or directory" in virhe:
							poistetut_tiedostot.append(indeksi)
							break
			# Lokaali tiedosto
			else:
				logfun.kirjaa(logitiedosto, f"Poista tiedosto\n   {lahdetiedosto}\n   lokaalilta kovalevyltä", 3)
				if kvak.VERBOOSI:
					print(f"Poista tiedosto\n   {lahdetiedosto}\n   lokaalilta kovalevyltä")
				if not kvak.TESTIMOODI:
					os.remove(lahdetiedosto)
	i = len(poistetut_tiedostot)-1
	while i >= 0:
		p = lapsipuu.tiedostot.pop(i)
		i -= 1

	# Sama alikansioille
	for alikansio in isantapuu.alikansiot:
		# Löytyy molemmista: sukella sisään
		molemmissa = False
		for indeksi,lapsi_alikansio in enumerate(lapsipuu.alikansiot):
			if alikansio.kansio == lapsi_alikansio.kansio:
				lapsi_alikansio = vertaa_puita(alikansio, isantapalvelin, lapsi_alikansio, lapsipalvelin, logitiedosto=logitiedosto)
				lapsipuu.alikansiot[indeksi] = lapsi_alikansio
				molemmissa = True
				break
		# Ei ole lapsipuussa: kopioi
		if not molemmissa:
			# lahdekansio = os.path.join(isantapuu.hae_nykyinen_polku(), alikansio.kansio)
			lahdekansio = isantapuu.hae_nykyinen_polku() + alikansio.kansio # / lopussa
			# kohdekansio = os.path.join(lapsipuu.hae_nykyinen_polku(), alikansio.kansio)
			# kohdekansio = lapsipuu.hae_nykyinen_polku() + alikansio.kansio
			kohdekansio = lapsipuu.hae_nykyinen_polku()
			# Siirrä
			logfun.kirjaa(logitiedosto, f"Kopioi kansio\n   {lahdekansio}\n   kohteeseen\n   {kohdekansio}", 3)
			if kvak.VERBOOSI:
				print(f"Kopioi kansio\n   {lahdekansio}\n   kohteeseen\n   {kohdekansio}")
			if not kvak.TESTIMOODI:
				siirrettiin = False
				for yritys in range(5):
					siirrettiin = kfun.lataa(False, isantapalvelin, lahdekansio, lapsipalvelin, kohdekansio)
					if siirrettiin:
						# Luo Tiedostopuu alikansiosta.
						# Voitaisiin vaan ottaa suoraan alikansiosta versio jonka isäntä on lapsipuun
						# kansio, mutta tällöin päiväykset menisivät ihan miten sattuu.
						# alikansiopuu = Tiedostopuu(kansio=alikansio.kansio, edellinenkansio=lapsipuu, syvennystaso=alikansio.syvennystaso, tiedostotyyppi=alikansio.tiedostotyyppi)
						# alikansiopuu.kansoita()
						muutettiin = kfun.muuta_oikeudet(os.path.join(kohdekansio, alikansio.kansio))
						lapsipuu.alikansiot.append(alikansio)
						logfun.kirjaa(logitiedosto, "kopioitu.", 3)
						break
					else:
						logfun.kirjaa(logitiedosto, "Ei saatu siirrettyä :<", 3)

	# Kansiota ei pitäisi olla: poista
	poistetut_kansiot = []
	for indeksi,alikansio in enumerate(lapsipuu.alikansiot):
		if not any([a.kansio==alikansio.kansio for a in isantapuu.alikansiot]):
			# lahdekansio = os.path.join(lapsipuu.hae_nykyinen_polku(), alikansio.kansio)
			lahdekansio = lapsipuu.hae_nykyinen_polku() + alikansio.kansio
			# Tiedosto etäpalvelimella
			if type(lapsipalvelin) is str:
				logfun.kirjaa(logitiedosto, f"Poista kansio\n   {lahdekansio}\n   palvelimelta\n   {lapsipalvelin}", 3)
				if kvak.VERBOOSI:
					print(f"Poista kansio\n   {lahdekansio}\n   palvelimelta\n   {lapsipalvelin}")
				if not kvak.TESTIMOODI:
					poistettu = False
					for i in range(5):
						poistettu, virhe = kfun.etapoisto(False, lapsipalvelin, lahdekansio)
						if poistettu or "No such file or directory" in virhe:
							poistetut_kansiot.append(indeksi)
							break
			# Lokaali tiedosto
			else:
				logfun.kirjaa(logitiedosto, f"Poista kansio\n   {lahdekansio}\n   lokaalilta kovalevyltä", 3)
				if kvak.VERBOOSI:
					print(f"Poista kansio\n   {lahdekansio}\n   lokaalilta kovalevyltä")
				if not kvak.TESTIMOODI:
					shutil.rmtree(lahdekansio)
	if not kvak.TESTIMOODI:
		i = len(poistetut_kansiot)-1
		while i >= 0:
			p = lapsipuu.alikansiot.pop(i)
			i -= 1

	# Palauta (ehkä) muokattu lapsipuu
	return(lapsipuu)

def kasaa_tietokanta(kansiotyyppi):
	'''
	Alusta annetun tyyppinen tietokanta.
	'''
	tiedostotyyppi = Tiedosto
	if kansiotyyppi == "Musiikki":
		tiedostotyyppi = Biisi
	for k,tietokansio in enumerate(kvak.KANSIOT[kvak.LOKAALI_KONE][kansiotyyppi]):
		puu = Tiedostopuu(tietokansio, None, 0, tiedostotyyppi, False)
		puu.kansoita()
		kohdetiedosto = kvak.LOKAALIT_TIETOKANNAT[kansiotyyppi][k]
		f = open(kohdetiedosto, "w+")
		f.write(str(puu))
		f.close()

def tarkista_onko_tietokannat(logitiedosto=None):
	'''
	Tarkista kustakin tietokantatyypistä, onko sen tiedot kirjattu
	vai eikö ole. Jos ei, aja 'kasaa_tietokanta()'
	'''
	for kansiotyyppi in kvak.LOKAALIT_TIETOKANNAT:
		if any([a and not os.path.exists(a) for a in kvak.LOKAALIT_TIETOKANNAT[kansiotyyppi]]):
			if kvak.VERBOOSI:
				print(f"Paikallista {kansiotyyppi}-tietokantaa ei oltu määritelty, määritetään...")
			logfun.kirjaa(logitiedosto, f"Paikallista {kansiotyyppi}-tietokantaa ei oltu määritelty, määritetään...", 3)
			kasaa_tietokanta(kansiotyyppi)
			if kvak.VERBOOSI:
				print("\tMääritetty")
			logfun.kirjaa(logitiedosto, "Määritetty", 5)

def paivita_puu(puu, logitiedosto=None):
	'''
	Päivitä paikallisen tietokantatiedoston puu ajan tasalle.
	Rekursiivinen alirutiini funktiolle 'paivita_paikalliset_tietokannat()'
	'''
	# Katsotaan mitä puun kansion alla oikeasti on (tiedostot ja kansiot)
	lok_tied, lok_kans = kfun.kansion_sisalto(puu.hae_nykyinen_polku())
	# Puussa tiedostoja jota ei oikeasti ole olemassa: poista
	poistettavat = []
	for p,puutiedosto in enumerate(puu.tiedostot):
		if puutiedosto.tiedostonimi not in lok_tied:
			logfun.kirjaa(logitiedosto, f"Tiedostoa {puutiedosto.tiedostonimi} ei enää ole, poista kirjastosta.", 3)
			poistettavat.append(p)
	if poistettavat:
		poistettavat.reverse()
		for p in poistettavat:
			puu.tiedostot.pop(p)
		poistettavat = []
	# Kansiossa tiedostoja joita ei ole puussa: lisää
	# Kansioss tiedostoja jotka muuttuneet: päivitä
	for paikallinen_tiedosto in lok_tied:
		puuttuu     = paikallinen_tiedosto not in [a.tiedostonimi for a in puu.tiedostot]
		lok_aika    = kfun.tiedoston_aikaleima(os.path.join(puu.hae_nykyinen_polku(), paikallinen_tiedosto))
		vanhentunut = any([a.lisayspaiva < lok_aika for a in puu.tiedostot if a.tiedostonimi == paikallinen_tiedosto])
		# Lisää
		if puuttuu:
			# Biisi
			if puu.tiedostotyyppi is Biisi and kfun.paate(paikallinen_tiedosto)[1] in kvak.MUSATIEDOSTOT:
				tiedosto = Biisi(os.path.join(puu.hae_nykyinen_polku(), paikallinen_tiedosto))
				logfun.kirjaa(logitiedosto, f"Tiedostoa {paikallinen_tiedosto} ei ole tietokannassa, lisätään.", 3)
				puu.tiedostot.append(tiedosto)
			# Yleinen tiedosto
			elif puu.tiedostotyyppi is not Biisi:
				tiedosto = Tiedosto(os.path.join(puu.hae_nykyinen_polku(), paikallinen_tiedosto))
				logfun.kirjaa(logitiedosto, f"Tiedostoa {paikallinen_tiedosto} ei ole tietokannassa, lisätään.", 3)
				puu.tiedostot.append(tiedosto)
		# Päivitä
		elif vanhentunut:
			for i,vanha in enumerate(puu.tiedostot):
				if vanha.tiedostonimi == paikallinen_tiedosto:
					# Biisi
					if puu.tiedostotyyppi is Biisi and kfun.paate(paikallinen_tiedosto)[1].lower() in kvak.MUSATIEDOSTOT:
						tiedosto = Biisi(os.path.join(puu.hae_nykyinen_polku(), paikallinen_tiedosto))
						if tiedosto.hash != vanha.hash:
							logfun.kirjaa(logitiedosto, f"Tiedosto {paikallinen_tiedosto} on muuttunut, päivitetään ({lok_aika} < {vanha.lisayspaiva}).", 3)
							puu.tiedostot[i] = tiedosto
					# Yleinen tiedosto yleisten tiedostojen puussa
					elif puu.tiedostotyyppi is not Biisi:
						tiedosto = Tiedosto(os.path.join(puu.hae_nykyinen_polku(), paikallinen_tiedosto))
						if tiedosto.hash != vanha.hash:
							logfun.kirjaa(logitiedosto, f"Tiedostoa {paikallinen_tiedosto} on muuttunut, päivitetään ({lok_aika} < {vanha.lisayspaiva}).", 3)
							puu.tiedostot[i] = tiedosto
					else:
						logfun.kirjaa(logitiedosto, f"Tiedostoa {paikallinen_tiedosto} ei tarvitse seurata.", 3)
						puu.tiedostot.pop(i)
					break
	# Kansiot rekursiivisesti silloin kun aihetta
	for p,puukansio in enumerate([a.kansio for a in puu.alikansiot]):
		# Puussa kansioita joita ei oikeasti ole: poista
		if puukansio not in lok_kans:
			logfun.kirjaa(logitiedosto, f"Kansiota {puukansio} ei enää ole, poista kirjastosta.", 3)
			poistettavat.append(p)
		# On tietokannassa: sukella sisään ja katso ajantasaisuus
		else:
			# logfun.kirjaa(logitiedosto, f"Tarkistetaan alikansion {puukansio} ajantasaisuus.")
			puu.alikansiot[p] = paivita_puu(puu.alikansiot[p], logitiedosto=logitiedosto)
	if poistettavat:
		poistettavat.reverse()
		for p in poistettavat:
			puu.alikansiot.pop(p)
	# Tietokannasta puuttuvat kansiot: lisää
	for puuttuvakansio in [a for a in lok_kans if a not in [b.kansio for b in puu.alikansiot]]:
		logfun.kirjaa(logitiedosto, f"Kansiota {puuttuvakansio} ei ole tietokannassa, lisätään.", 3)
		uusipuu = Tiedostopuu(kansio=puuttuvakansio, edellinenkansio=puu, syvennystaso=puu.syvennystaso+1, tiedostotyyppi=puu.tiedostotyyppi)
		uusipuu.kansoita()
		puu.alikansiot.append(uusipuu)
	# Jos asiat on hassusti niin puussa saattaa olla samoja tiedostoja
	# moneen kertaan, mikä ei suinkaan ole tarkoitus.
	# Laskennan kannalta tämän pitäisi olla funktion alussa, mutta mielummin
	# varmistan että asiat on sitä mitä pitääkin olla kuin että ne tuotetaan fiksusti.
	puu = poista_kaksoiskappaleet(puu)
	return(puu)

def poista_kaksoiskappaleet(puu):
	'''
	Tarkista, ettei puussa ole tiedostoja kahteen kertaan.
	'''
	poistettavat = [] # indeksit poistettaville
	for t,tiedosto in enumerate(puu.tiedostot):
		for tt,toinentiedosto in enumerate(puu.tiedostot[t+1:]):
			if toinentiedosto.tiedostonimi == tiedosto.tiedostonimi:
				# print(f"{t}:    {puu.tiedostot[t]}")
				# print(f"{t}+{tt}: {puu.tiedostot[t+tt+1]}")
				if toinentiedosto.lisayspaiva >= tiedosto.lisayspaiva:
					poistettavat.append(t+tt+1)
				else:
					poistettavat.append(t)
	poistettavat.sort()
	poistettavat.reverse()
	for p in poistettavat:
		puu.tiedostot.pop(p)
	# Sama alikansiopuille
	for a,alikansio in enumerate(puu.alikansiot):
		puu.alikansiot[a] = poista_kaksoiskappaleet(alikansio)
	return(puu)


def muunna_paivaysformaatti(puu):
	'''
	Päivitä tiedostojen päiväysformaatti
	YYYYMMDD -> YYYYMMDDHHMM
	'''
	for tiedosto in puu.tiedostot:
		if tiedosto.lisayspaiva < 1E8:
			tiedosto.lisayspaiva *= 10000 # lisää neljä nollaa
	for kansio in puu.alikansiot:
		muunna_paivaysformaatti(kansio)


def paivita_paikalliset_tietokannat(logitiedosto=None):
	'''
	Katso, onko paikallinen tietokantatiedosto ajan tasalla.
	'''
	# Tietokantatyyppi kerrallaan
	for kansiotyyppi in kvak.LOKAALIT_TIETOKANNAT:
		logfun.kirjaa(logitiedosto, f"Päivitetään paikallinen tietokanta {kansiotyyppi}.")
		tiedostotyyppi = Tiedosto
		if kansiotyyppi == "Musiikki":
			tiedostotyyppi = Biisi
		# Tietokantatiedosto kerrallaan
		for tietokantatiedosto in kvak.LOKAALIT_TIETOKANNAT[kansiotyyppi]:
			# Varmuuskopioi
			shutil.copy(tietokantatiedosto, "{}.bk".format(tietokantatiedosto))
			logfun.kirjaa(logitiedosto, f"{kansiotyyppi}:{tietokantatiedosto} aloita")
			puu = Tiedostopuu(tiedostotyyppi=tiedostotyyppi)
			f = open(tietokantatiedosto, "r")
			puu.lue_tiedostosta(f)
			f.close()
			# muunna_paivaysformaatti(puu) # aja vain kerran
			puu = paivita_puu(puu, logitiedosto)
			f = open(tietokantatiedosto, "w+")
			f.write(str(puu))
			f.close()
			os.remove("{}.bk".format(tietokantatiedosto))
			logfun.kirjaa(logitiedosto, f"{kansiotyyppi}:{tietokantatiedosto} valmis")


def synkkaa(logitiedosto=None):
	'''
	Synkkaa paikalliset tiedostot ulkoisten tiedostojen kanssa.
	Se, mikä liikkuu mihinkin suuntaan on määritelty kansiovakioiden puolella.
	'''
	# Jos Pettankone, päivitetään vain paikalliset tietokannat
	if kvak.LOKAALI_KONE == "Pettan":
		if kvak.VERBOOSI:
			print("Pettankone, päivitetään vain paikalliset tietokannat.")
		logfun.kirjaa(logitiedosto, "Pettankone, päivitetään vain paikalliset tietokannat.")
		paivita_paikalliset_tietokannat(logitiedosto=logitiedosto)
		return(1)
	# Ei tehdä mitään jos asioita ei ole määritelty
	if None in [kvak.VOIMASUHTEET, kvak.LOKAALIT_TIETOKANNAT]:
		if kvak.VERBOOSI:
			print("Tietokonetta ei määritelty kansiovakioissa, ei tehdä mitään.")
		logfun.kirjaa(logitiedosto, "Tietokonetta ei määritelty kansiovakioissa, ei tehdä mitään.")
		return(0)

	# Varmistetaan että tietokannat on olemassa
	logfun.kirjaa(logitiedosto, "Tarkistetaan paikallisten tietokantojen olemassaolo.")
	tarkista_onko_tietokannat(logitiedosto=logitiedosto)
	# Varmistetaan että ovat ajan tasalla
	logfun.kirjaa(logitiedosto, "Tarkistetaan paikallisten tietokantojen ajantasaisuus.")
	paivita_paikalliset_tietokannat(logitiedosto=logitiedosto)

	# Kullekin tiedostokansiolle: kopioi Pettanin tietokantatiedosto ja vertaa sitä omaan
	for kansiotyyppi in kvak.LOKAALIT_TIETOKANNAT:
		pettanin_tietokanta = kvak.TIETOKANNAT["Pettan"][kansiotyyppi] # lista tiedostopolkuja, valkkaa oikea
		lokaali_tietokanta  = kvak.LOKAALIT_TIETOKANNAT[kansiotyyppi][0]
		# Yritä siirtää max. viisi kertaa
		siirretty = False
		for yritys in range(5):
			siirretty = kfun.lataa(True, "pettankone", pettanin_tietokanta[kvak.VOIMASUHTEET[kansiotyyppi][1]], None, f"pettan_{kansiotyyppi}.tietokanta")
			if siirretty:
				break
		if siirretty:
			# Lue tietokantatiedostoista
			logfun.kirjaa(logitiedosto, f"Tietokanta \"{kansiotyyppi}\" kopioitu pettanilta")
			if kansiotyyppi == "Musiikki":
				puu_lokaali = Tiedostopuu(tiedostotyyppi=Biisi)
				puu_pettan  = Tiedostopuu(tiedostotyyppi=Biisi)
			else:
				puu_lokaali = Tiedostopuu(tiedostotyyppi=Tiedosto)
				puu_pettan  = Tiedostopuu(tiedostotyyppi=Tiedosto)
			f = open(lokaali_tietokanta, "r")
			puu_lokaali.lue_tiedostosta(f)
			logfun.kirjaa(logitiedosto, f"Paikallinen puu {lokaali_tietokanta} luettu.")
			f.close()
			f = open(f"pettan_{kansiotyyppi}.tietokanta", "r")
			puu_pettan.lue_tiedostosta(f)
			logfun.kirjaa(logitiedosto, f"Pettanin puu {kansiotyyppi} luettu.")
			f.close()

			# Vertaa tietokantatiedostoja
			# Paikallinen kone masteri
			if kvak.VOIMASUHTEET[kansiotyyppi][0]:
				logfun.kirjaa(logitiedosto, "Verrataan puita, paikallinen puu masteri.")
				puu_pettan = vertaa_puita(isantapuu=puu_lokaali, isantapalvelin=None, lapsipuu=puu_pettan, lapsipalvelin="pettankone", logitiedosto=logitiedosto)
				f = open(f"pettan_{kansiotyyppi}.tietokanta", "w+")
				f.write(str(puu_pettan))
				f.close()

			# Pettani masteri
			else:
				logfun.kirjaa(logitiedosto, "Verrataan puita, Pettani masteri.")
				puu_lokaali = vertaa_puita(isantapuu=puu_pettan, isantapalvelin="pettankone", lapsipuu=puu_lokaali, lapsipalvelin=None, logitiedosto=logitiedosto)
				f = open(lokaali_tietokanta, "w+")
				f.write(str(puu_lokaali))
				f.close()

			# Päivitä Pettanilla sijaitseva tietokantatiedosto
			logfun.kirjaa(logitiedosto, "Palauta Pettanille puu pettan_{}.tietokanta nimellä {}.".format(kansiotyyppi, pettanin_tietokanta[kvak.VOIMASUHTEET[kansiotyyppi][1]]))
			siirretty = False
			for yritys in range(5):
				siirretty = kfun.lataa(True, None, f"pettan_{kansiotyyppi}.tietokanta", "pettankone", pettanin_tietokanta[kvak.VOIMASUHTEET[kansiotyyppi][1]])
				if siirretty:
					break
			if siirretty:
				logfun.kirjaa(logitiedosto, "Palautettu.")
			else:
				logfun.kirjaa(logitiedosto, "Ei saatu palautettua :<")
			logfun.kirjaa(logitiedosto, f"Poista pettanilta napattu tiedosto pettan_{kansiotyyppi}.tietokanta")
			os.remove(f"pettan_{kansiotyyppi}.tietokanta")
		else:
			if kvak.VERBOOSI:
				print("Ei saatu kopioitua Pettanilta tiedostotietokantoja")
			logfun.kirjaa(logitiedosto, "Ei saatu kopioitua Pettanilta tiedostotietokantoja")
	return(1)
