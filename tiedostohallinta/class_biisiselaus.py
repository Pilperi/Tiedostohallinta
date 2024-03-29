'''
Biisien hakemiseen ja selaamiseen tarvittavat luokat
keskitetysti samassa paikassa.
'''
import os
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

    def diktiksi(self):
        dikti = {
            "ehtona_ja": self.ehtona_ja,
            "artistissa": self.artistinimessa,
            "biisissa": self.biisinimessa,
            "albumissa": self.albuminimessa,
            "tiedostossa": self.tiedostonimessa,
            "raitanumero": self.raitanumero,
            "vapaahaku": self.vapaahaku,
            }
        return dikti

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
