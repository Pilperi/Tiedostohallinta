import os
import json
import logging
from tiedostohallinta import funktiot_kansiofunktiot as kfun
from tiedostohallinta.class_biisi import Biisi
from tiedostohallinta.class_tiedosto import Tiedosto


class Tiedostopuu():
    '''
    Tiedostopuun luokka, hyvinni yleinen sellainen.
    Käytännössä sisältää tiedot kansioista
    ja siitä, mitä tiedostoja on minkäkin kansion alla,
    jottei tarvitse roikottaa täysiä tiedostopolkuja
    koko aikaa messissä.
    Pääpointti lähinnä siinä, että asiat saadaan
    kirjoitettua tiedostoon fiksusti ja luettua sieltä ulos.
    '''
    MAHDOLLISET_TYYPIT = (Biisi, Tiedosto) # Mitä kaikkea puut voi syödä
    SALLITUT_PAATTEET = {
        Biisi.TYYPPI: [ # vain äänitiedostot
            "mp3",
            "flac",
            "wma",
            "ogg"
            ],
        Tiedosto.TYYPPI: [], # kaikki kelpaa
        }
    TYYPPI = "tiedostopuu"
    def __init__(self):
        self._tyyppi = Tiedostopuu.TYYPPI
        self._tiedostotyyppi = Tiedosto # Millaista dataa pyöritellään
        self._edellinentaso = None     # edellinen kansio (Tiedostopuu tai None)
        self._kansio        = ""       # str, pelkkä kansionimi
        self._tiedostot      = []      # Lista tiedostoja
        self._alikansiot     = []      # Lista Tiedostopuita
        self.syvennystaso = 0 # (printtailu nätiksi)

    # Setterit ja getterit (pidetään datatyypit kontrollissa)
    # Tyyppi on kiinteä, voi lukea muttei muuttaa
    @property
    def tyyppi(self):
        return self._tyyppi
    @tyyppi.setter
    def tyyppi(self, val):
        return
    # Sallitut tiedostotyypit on biisit ja geneeriset tiedostot
    @property
    def tiedostotyyppi(self):
        return self._tiedostotyyppi
    @tiedostotyyppi.setter
    def tiedostotyyppi(self, uusiarvo):
        # Suoraan luokkapointteri
        if any(
            uusiarvo is tyyppi
            for tyyppi in Tiedostopuu.MAHDOLLISET_TYYPIT
            ):
            self._tiedostotyyppi = uusiarvo
        # Tyyppistringin perusteella
        elif isinstance(uusiarvo, str):
            for tyyppi in Tiedostopuu.MAHDOLLISET_TYYPIT:
                if uusiarvo == tyyppi.TYYPPI:
                    self._tiedostotyyppi = tyyppi
                    break
    # Sallitut tiedostomuodot (pelkkä getteri)
    @property
    def tiedostomuodot(self):
        tiedostomuodot = Tiedostopuu.SALLITUT_PAATTEET.get(
            self.tiedostotyyppi.TYYPPI
            )
        if not isinstance(tiedostomuodot, list):
            tiedostomuodot = []
        return tiedostomuodot
    # Edellinen taso voi olla joko toinen tiedostopuu tai None (puun juuri)
    @property
    def edellinentaso(self):
        return self._edellinentaso
    @edellinentaso.setter
    def edellinentaso(self, uusiarvo):
        if isinstance(uusiarvo, (Tiedostopuu, type(None))):
            self._edellinentaso = uusiarvo
    # Kansio on aina str
    @property
    def kansio(self):
        return self._kansio
    @kansio.setter
    def kansio(self, uusiarvo):
        if isinstance(uusiarvo, str) and uusiarvo:
            # Poista lopusta kauttamerkit
            while uusiarvo[-1] in ("/", "\\") and len(uusiarvo) > 1:
                uusiarvo = uusiarvo[:-1]
            self._kansio = uusiarvo
    # Tiedostolista on lista puun tiedostotyypin edustajia
    @property
    def tiedostot(self):
        return self._tiedostot
    @tiedostot.setter
    def tiedostot(self, uusiarvo):
        # Valmiita olioita
        if (
            isinstance(uusiarvo, list)
            and all(isinstance(a, self.tiedostotyyppi) for a in uusiarvo)
            ):
            self._tiedostot = uusiarvo
        # Dictejä joista pitäisi kasata olioita
        elif (
            isinstance(uusiarvo, list)
            and all(isinstance(a, dict) for a in uusiarvo)
            ):
            lista = [self.tiedostotyyppi.diktista(dikti) for dikti in uusiarvo]
            self._tiedostot = lista
    # Alikansiolista on lista Tiedostopuita
    @property
    def alikansiot(self):
        return self._alikansiot
    @alikansiot.setter
    def alikansiot(self, uusiarvo):
        # Valmiita olioita
        if (
            isinstance(uusiarvo, list)
            and all(isinstance(a, Tiedostopuu) for a in uusiarvo)
            ):
            self._alikansiot = uusiarvo
        # Dictejä joista pitäisi kasata olioita
        elif (
            isinstance(uusiarvo, list)
            and all(isinstance(a, dict) for a in uusiarvo)
            ):
            lista = [Tiedostopuu.diktista(dikti) for dikti in uusiarvo]
            self._alikansiot = lista

    def diktiksi(self):
        '''
        Palauttaa
        ---------
        dict
            Diktiversio oliosta. Vain perusdatatyyppejä.
            Edellisen tason tiedot jätetään pois, kirjoitetaan ylhäältä
            alas uudelleenkasatessa.
        '''
        diktiversio = {
            "tiedostotyyppi": self.tiedostotyyppi.TYYPPI,
            "kansio": self.kansio,
            "tiedostot": [tiedosto.diktiksi() for tiedosto in self.tiedostot],
            "alikansiot": [kansio.diktiksi() for kansio in self.alikansiot]
            }
        return diktiversio

    @classmethod
    def diktista(cls, dikti):
        '''
        Määritä tiedostopuu sisäänmenodiktin pohjalta.
        '''
        puu = Tiedostopuu()
        if not isinstance(dikti, dict):
            return puu
        tiedostotyyppi = dikti.get("tiedostotyyppi")
        for tyyppi in Tiedostopuu.MAHDOLLISET_TYYPIT:
            if tyyppi.TYYPPI == tiedostotyyppi:
                puu.tiedostotyyppi = tyyppi
                break
        puu.kansio = dikti.get("kansio")
        puu.tiedostot = dikti.get("tiedostot")
        puu.alikansiot = dikti.get("alikansiot")
        puu.tiedostot = sorted(puu.tiedostot, key=lambda t: t.tiedostonimi)
        puu.alikansiot = sorted(puu.alikansiot, key=lambda k: k.kansio)
        puu.tayta_hierarkiat()
        return puu

    def tayta_hierarkiat(self, edellinentaso=None):
        '''
        Täytä puuhun hierarkiat, ts. tieto siitä mikä on minkäkin
        alikansion edellinen kansio.

        Sisään
        ------
        edellinentaso : None tai Tiedostopuu
            Nykyisen puun edellinen taso, joka asetetaan selffiin.
        '''
        # Oma edellinen taso on annettu
        self.edellinentaso = edellinentaso
        # Anna oma olemus alikansioille edelliseksi tasoksi.
        for alikansio in self.alikansiot:
            alikansio.tayta_hierarkiat(self)

    def kansoita(self):
        '''
        Lado kansion tiedostot tiedostolistaan ja
        alikansiot alikansiolistaan.
        '''
        sallitut_paatteet = Tiedostopuu.SALLITUT_PAATTEET.get(
            self.tiedostotyyppi.TYYPPI
            )
        if not isinstance(sallitut_paatteet, (list,tuple)):
            sallitut_paatteet = []
        tiedostot, alikansiot = kfun.kansion_sisalto(
            self.hae_nykyinen_polku(),
            sallitut_paatteet
            )
        # Tiedostot tiedostolistaan
        # (tässä vaihtelee, minkä tyyppinen tiedosto kyseessä)
        for tiedosto in tiedostot:
            logging.debug("{}{}".format((self.syvennystaso+1)*" ", tiedosto))
            polku = os.path.join(self.hae_nykyinen_polku(), tiedosto)
            tiedosto_olio = self.tiedostotyyppi(kohteesta=polku)
            self.tiedostot.append(tiedosto_olio)
        # Alikansiot yhtä tasoa syvemmällä, ole näiden 'edellinenkansio'
        for kansio in alikansiot:
            logging.debug("{}{}".format((self.syvennystaso+1)*" ", kansio))
            puu = Tiedostopuu()
            puu.tiedostotyyppi = self.tiedostotyyppi
            puu.edellinentaso = self
            puu.kansio = kansio
            puu.syvennystaso = self.syvennystaso+1
            puu.kansoita()
            self.alikansiot.append(puu)
        self.tiedostot = sorted(self.tiedostot, key=lambda t: t.tiedostonimi)
        self.alikansiot = sorted(self.alikansiot, key=lambda k: k.kansio)

    def hae_nykyinen_polku(self):
        '''
        Hae nykyisen tason koko polku edeltävistä tasoista latomalla.
        '''
        polku = [self.kansio]
        ylempitaso = self.edellinentaso
        while ylempitaso is not None:
            polku.append(ylempitaso.kansio)
            ylempitaso = ylempitaso.edellinentaso
        polku.reverse()
        polkustringi = ""
        for osa in polku:
            polkustringi += osa+"/"
        return polkustringi

    def sisallon_maara(self):
        '''
        Laske paljonko puussa ja alipuissa on tavaraa,
        sekä eroteltuna että ynnättynä.
        '''
        itsessa = len(self.tiedostot)
        alipuissa = 0
        for alipuu in self.alikansiot:
            alipuissa += alipuu.sisallon_maara()[0]
        return itsessa+alipuissa, itsessa, alipuissa

    def alikansio(self, nimi):
        '''
        Hae alikansio nimen perusteella.
        Jos ei löydy, palauttaa None.
        '''
        for kansio in self.alikansiot:
            if kansio.kansio == nimi:
                return(kansio)
        return None

    def sisaltaa_kansion(self, kansio):
        '''
        Katso onko kansiota (Tiedostopuu)
        vastaava kansio myös tässä puurakenteessa.
        '''
        # Käy puu järjestyksessä läpi juureen asti
        kansio_askeleet = [kansio.kansio]
        edellinentaso = kansio.edellinentaso
        while edellinentaso is not None:
            kansio_askeleet.append(edellinentaso)
            edellinentaso = edellinentaso.edellinentaso
        # Käy toisesta suunnasta läpi ja katso löytyykö
        # joka askel myös omasta puusta
        kansio_askeleet.reverse()
        oma_askel = self
        for askel in kansio_askeleet:
            alikansio = oma_askel.alikansio(askel.kansio) # hae nimellä
            if alikansio is None:
                return False
            oma_askel = alikansio
        return True

    def copy(self):
        '''
        Tee oliosta kopio diktimuunnoksen kautta.
        '''
        return Tiedostopuu.diktista(self.diktiksi())

    def __sub__(self, toinen):
        '''
        Kasaa kahden puun erotuspuu, ts.
        kerro mitä yhdessä puussa on sellaista mikä
        toisesta puusta puuttuu kokonaan.
        '''
        # Väärä datatyyppi -> kaikki puuttuu
        if not isinstance(toinen, Tiedostopuu):
            return self
        # Muutoin kansio kerrallaan läpi, poimi kokonaan puuttuvat
        paluuarvo = self.copy()
        # Tiedostot
        tiedostot = []
        for tiedosto in paluuarvo.tiedostot:
            if not any(
                tt.tiedostonimi == tiedosto.tiedostonimi
                for tt in toinen.tiedostot
                ):
                tiedostot.append(tiedosto)
        paluuarvo.tiedostot = tiedostot
        # Kansiot tarkemmin, puuttuvat sellaisenaan ja löytyvät rekursiivisesti
        # (katso ettei sisällä ole eroja)
        eroavat_kansiot = []
        for kansio in paluuarvo.alikansiot:
            kansio_toisessa = toinen.alikansio(kansio.kansio)
            if isinstance(kansio_toisessa, Tiedostopuu):
                erotus = kansio - kansio_toisessa # sisällön ero
                if erotus.tiedostot or erotus.alikansiot:
                    eroavat_kansiot.append(erotus)
            else:
                eroavat_kansiot.append(kansio)
        paluuarvo.alikansiot = eroavat_kansiot
        return paluuarvo

    def lue_tiedostosta(self, tiedosto):
        '''
        Lue puurakenne tietokantatiedostosta.
        Huom. 'tiedosto' on tiedostokahva (vai mikälie), ei tiedostopolku str
        (toim. huom. apua)

        !! legacykamaa                                                  !!
        !! roikkuu mukana vain taaksepäinyhteensopivuuden takaamiseksi  !!
        '''
        rivi = tiedosto.readline()
        # Jos pääkansio, lue tietokannan pääkansion nimi
        # ekalta riviltä ja siirry seuraavalle
        if self.syvennystaso == 0 and rivi and rivi[1] == "\"":
            kansionimi = ""
            i = 2
            while rivi[i] != "\"":
                kansionimi += rivi[i]
                i += 1
            self.kansio = kansionimi
            rivi = tiedosto.readline()
        while rivi:
            # Laske syvennystaso: rivin alussa luvut ilmaisemassa
            syvennys = ""
            i = 0
            while rivi[i].isnumeric():
                syvennys += rivi[i]
                i += 1
            syvennys = int(syvennys)
            if syvennys == self.syvennystaso+1:
                # Tapaus tiedosto nykyisellä syvennystasolla: lisää tiedostolistaan
                if type(self.tiedostotyyppi) is not None and rivi[i] == "{":
                    diktitiedosto = json.loads(rivi[i:-1])
                    self.tiedostot.append(self.tiedostotyyppi(diktitiedosto))
                    rivi = tiedosto.readline()
                # Tapaus kansio: lisää Tiedostopuu alikansioihin
                elif rivi[i] == "\"":
                    # Lue kansion nimi, joka on "" välissä
                    i += 1
                    kansionimi = ""
                    while rivi[i] != "\"":
                        kansionimi += rivi[i]
                        i += 1
                    alipuu = Tiedostopuu()
                    alipuu.kansio = kansionimi
                    alipuu.edellinentaso = self
                    alipuu.syvennystaso = self.syvennystaso+1
                    alipuu.tiedostotyyppi = self.tiedostotyyppi
                    rivi = alipuu.lue_tiedostosta(tiedosto)
                    self.alikansiot.append(alipuu)
            else:
                # Palauta viimeisin rivi, koska sitä tarvitaan vielä ylemmällä tasolla
                return(rivi)

    def __str__(self):
        '''
        Rekursiivinen str-operaatio, käydään kaikki alikansiotkin läpi.
        Palauttaa sen vanhan ihme hässäkän
        (taaksepäinyhteensopivuus toistaiseksi)
        '''
        st = "{:d}\"{:s}\"\n".format(self.syvennystaso, str(self.kansio))
        for tiedosto in self.tiedostot:
            st += "{:d}{:s}\n".format((self.syvennystaso+1), str(tiedosto))
        for kansio in self.alikansiot:
            st += str(kansio)
        return st
