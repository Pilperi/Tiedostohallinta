import os
import shutil
import subprocess
import hashlib
import logging
from datetime import datetime

KIELLETYT = []
BUFFERI         = 65536 # tiedostoja RAM:iin 64kb paloissa
MERKKIBUFFERI   = 4000    # jsoneita RAM:iin 4000 merkin paloissa

def lataa(vaintiedosto, lahdepalvelin, lahdepolku, kohdepalvelin, kohdepolku):
    '''
    Lataa SCP:llä biisi tai kansio kansiopolusta
    (/lokaali/polku tai servu:/polku/servulla)
    määränpäähän (/lokaali/polku tai servu:/polku/servulla)
    '''
    # Polku palvelimella
    if lahdepalvelin:
        kansiopolku = "{}:{}".format(
            lahdepalvelin,
            siisti_tiedostonimi(lahdepolku)
            )
    # Paikallinen polku
    else:
        # kansiopolku = "\"{}\"".format(lahdepolku)
        kansiopolku = "{}".format(lahdepolku)
    # Polku palvelimella
    if kohdepalvelin:
        kohde = "{}:{}".format(kohdepalvelin, siisti_tiedostonimi(kohdepolku))
    # Paikallinen polku
    else:
        # kohde = "\"{}\"".format(kohdepolku)
        kohde = "{}".format(kohdepolku)

    if vaintiedosto:
        koodi = subprocess.run(
            ["scp", "-T", kansiopolku, kohde],
            capture_output=True,
            encoding="utf-8")
    else:
        koodi = subprocess.run(
            ["scp","-r", "-T", kansiopolku, kohde],
            capture_output=True,
            encoding="utf-8")
    if koodi.returncode != 1:
        return True
    return False

def siisti_tiedostonimi(nimi):
    '''
    Siisti tiedostonimen hankalat merkit scp-yhteensopiviksi,
    koska ähhh.

    Ottaa:
    nimi : str
        Stringi jonka ikävät merkit muokataan vähemmän ikäviksi.

    Palauttaa:
    nimi : str
        Siivottu stringi.
    '''
    nimi = nimi.replace("\"", "\\\"")\
              .replace(" ", "\\ ")\
              .replace("\'", "\\\'")\
              .replace("!", "\\!")\
              .replace("(", "\\(")\
              .replace(")", "\\)")\
              .replace("&", "\\&")\
              .replace(";", "\\;")
    return(nimi)

def hanki_hash(tiedosto, binmode=True):
    '''
    Laskee annetun tiedoston md5-summan heksana,
    lukemalla sitä sopivan kokoinen palanen kerrallaan.
    Parametri 'binmode' määrittää, luetaanko tiedostoa
    binäärimuodossa (metadatoineen kaikkineen) vai
    tiedoston varsinaista sisältöä utf8-merkkeinä.
    Oletuksena 64kb binääripaloina,
    binmode=False -> 4000 merkkiä kerrallaan.
    '''
    md5 = hashlib.md5()
    if os.path.exists(tiedosto):
        if binmode:
            with open(tiedosto, 'rb') as filu:
                while True:
                    data = filu.read(BUFFERI)
                    if not data:
                        break
                    md5.update(data)
        else:
            with open(tiedosto, 'r') as filu:
                while True:
                    data = filu.read(MERKKIBUFFERI)
                    if not data:
                        break
                    md5.update(data.encode("utf-8"))
    return(md5.hexdigest())

def tiedoston_aikaleima(tiedosto):
    '''
    Anna tiedoston muokkausajan aikaleima
    kokonaislukumuodossa.
    '''
    aika = 0
    if os.path.isfile(tiedosto):
        aika = int(datetime.fromtimestamp(os.path.getmtime("Warranty.pdf")).strftime("%Y%m%H%M"))
    return(aika)

#------------Funktiot kansiorakenteiden läpikäymiseen--------------------------
def paate(tiedosto):
    '''
    Pilkkoo tiedoston filu.pääte osiin 'filu' ja 'pääte'
    '''
    paate = tiedosto.split(".")[-1]
    if len(paate) < len(tiedosto):
        alkuosa = tiedosto[:-1*len(paate)-1]
        return(alkuosa, paate)
    return(tiedosto, "")


def joinittuonko(*lista):
    '''
    Liittää argumenttistringit toisiinsa ja tarkistaa onko lopputulos olemassaoleva kansio.
    Aika tosi usein tarvitsee rakennetta os.path.exists(os.path.join(a,b,c)) eikä
    sitä jaksaisi jok'ikinen kerta naputella uusiksi...
    '''
    joinittu = ""
    for a in lista:
        joinittu = os.path.join(joinittu, a)
    return(os.path.exists(joinittu))


def kansion_sisalto(kansio, tiedostomuodot=[]):
    '''
    Käy kansion läpi ja palauttaa listat
    sen sisältämistä tiedostoista
    sekä alikansioista
    '''
    tiedostot = []
    kansiot = []
    if os.path.exists(kansio):
        asiat = os.listdir(kansio)
        tiedostot = [
            a for a in asiat
            if os.path.isfile(os.path.join(kansio,a))
            and (not(tiedostomuodot) or paate(a)[1].lower() in tiedostomuodot)
            ]
        kansiot = [a for a in asiat if os.path.isdir(os.path.join(kansio,a))]
    return(tiedostot,kansiot)


def hanki_kansion_tiedostolista(kansio, tiedostomuodot=[],
                                kielletyt=KIELLETYT):
    '''
    Palauttaa annetun kansion tiedostolistan,
    ts. listan kaikista tiedostoista kansiossa ja sen alikansioista
    täysinä tiedostopolkuina
    '''
    tiedostolista = []
    if os.path.exists(kansio):
        for tiedosto in os.listdir(kansio):
            # Oikeassa tiedostomuodossa oleva tiedosto:
            if (os.path.isfile(os.path.join(kansio, tiedosto))
                and (not(tiedostomuodot)
                    or paate(tiedosto)[1].lower() in tiedostomuodot)
                ):
                # Käy läpi kielletyt sanat
                ban = False
                for sana in kielletyt:
                    if sana in tiedosto.lower():
                        ban = True
                        break
                if not ban:
                    tiedostolista.append(os.path.join(kansio, tiedosto))
            # Kansio:
            elif os.path.isdir(os.path.join(kansio, tiedosto)):
                tiedostolista += hanki_kansion_tiedostolista(
                    os.path.join(kansio, tiedosto)
                    )
    return tiedostolista


def kay_kansio_lapi(source_path, dest_path, level):
    '''
    Käy läpi kansiot 'source_path' ja 'dest_path', ja katsoo mitkä
    source_pathista löytyvät tiedostot ja kansiot puuttuvat dest_pathista.
    Eli ei, tämä ei osaa katsoa, onko tiedostoja tai kansiota uudelleennimetty
    tai siirrelty kansion sisällä toisiin alikansioihin.
    Käy rekursiivisesti läpi myös yhteiset alikansiot.
    '''

    kopioituja = 0
    kopioarvo = 0
    if os.path.exists(source_path) and os.path.exists(dest_path):
        try:
            source_objects = os.listdir(source_path) # Noutokansion tiedostot ja alikansiot, nettikatkeamisvaralla
        except OSError:
            return(-1)
        dest_objects = os.listdir(dest_path) # Kohdekansion tiedostot ja alikansiot

        prlen = max(5, 69 - 15*level)
        i = 0
        j = prlen
        while j < len(str(os.path.basename(source_path))):
            #print("{:s}{:s}".format("\t"*level, str(os.path.basename(source_path))[i:j]))
            i = j
            j += prlen

        # Käydään läpi noutokansion tiedostot ja alikansiot
        for object in source_objects:
            # Kansio joka on molemmissa: käy läpi ja katso löytyykö kaikki tiedostot (ja rekursiivisesti alikansiot
            if os.path.isdir(os.path.join(source_path, object)) and object in dest_objects:
                kopioarvo = kay_kansio_lapi(os.path.join(source_path, object), os.path.join(dest_path, object), level+1)
                if kopioarvo >= 0:
                    kopioituja += kopioarvo
                elif not kopioituja:
                    kopioituja = -1
                    break

            # Kansio tai tiedosto joka ei ole kohdekansiossa: kopsaa kohdekansioon
            elif object not in dest_objects:
                # Puuttuva kansio
                if os.path.isdir(os.path.join(source_path, object)):
                    shutil.copytree(os.path.join(source_path, object), os.path.join(dest_path, object))
                    kopioituja += 1
                # Puuttuva tiedosto
                elif os.path.isfile(os.path.join(source_path, object)):
                    shutil.copy2(os.path.join(source_path, object), os.path.join(dest_path, object))
                    kopioituja += 1
    return kopioituja


def luo_tiedostolista(kansio):
    tiedostopolkulista = []
    for tiedosto in os.listdir(kansio):
        if os.path.isfile(os.path.join(kansio, tiedosto)):
            tiedostopolkulista.append(os.path.join(kansio,tiedosto))
        else:
            tiedostopolkulista += luo_tiedostolista(
                os.path.join(kansio, tiedosto)
                )
    return(tiedostopolkulista)

def etapoisto(vaintiedosto, palvelin, tiedostopolku):
    '''
    Poista etäpalvelimella oleva tiedosto SSH yli
    '''
    #tiedostopolku = siisti_tiedostonimi(tiedostopolku)
    logging.debug("etapoisto: {}".format([
        "ssh",
        palvelin,
        "rm{:s} \"{:s}\"".format(
            " -r"*int(not(vaintiedosto)),
            tiedostopolku)
        ]))
    koodi = subprocess.run([
        "ssh",
        palvelin,
        "rm{:s} \"{:s}\"".format(
            " -r"*int(not(vaintiedosto)),
            tiedostopolku)
        ],
        capture_output=True,
        encoding="utf-8")
    # print(koodi)
    if koodi.returncode != 1:
        return(True, "")
    return(False, str(koodi.stderr))
