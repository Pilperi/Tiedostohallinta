import os
import time
import shutil
import logging

from tiedostohallinta import vakiot_kansiovakiot as kvak
from tiedostohallinta import funktiot_kansiofunktiot as kfun
from tiedostohallinta.class_tiedosto import Tiedosto
from tiedostohallinta.class_biisi import Biisi
from tiedostohallinta.class_tiedostopuu import Tiedostopuu


def muodosta_latauslista(erotuspuu, maaranpaapuu):
    '''
    Muodosta minimaalinen määrä ladattavien polkujen lista.
    Läh. lataa kokonaisia puuttuvia kansioita aina kun mahdollista,
    niin ylhäältä puusta kuin järkevää ja vain yhden kerran.

    Sisään
    ------
    erotuspuu : Tiedostopuu
        Puuttuvat asiat jotka pitää ladata/lähettää
    maaranpaapuu : Tiedostopuu
        Referenssipuu, mitä määränpäässä on jo olemassa
        (älä lataa tiedostoa kansioon jota ei ole
        äläkä alikansiota kansioon jota ei ole)

    Ulos
    ----
    lista stringejä
        Erotuspuu muotoiltuna listaksi tiedosto- tai kansiopolkuja
        jotka voi sitten tunkea scp:hen tai mihin ikinä.
        Polut on kohdepolkuja.
    '''
    paluulista = []
    # Juuritason tiedostot menevät sellaisenaan
    for tiedosto in erotuspuu.tiedostot:
        paluulista.append(
            maaranpaapuu.hae_nykyinen_polku()
            +tiedosto.tiedostonimi
            )
    # Kansiot joko sellaisinaan (kun puuttuu kokonaan)
    # tai rekursiivisesti (sisältä puuttuu jotain)
    for kansio in erotuspuu.alikansiot:
        vastaava_maaranpaassa = maaranpaapuu.alikansio(kansio.kansio)
        # Määränpäässä ei ole koko kansiota laisinkaan
        if vastaava_maaranpaassa is None:
            paluulista.append(
                maaranpaapuu.hae_nykyinen_polku()
                +kansio.kansio
                +"/"
                )
        # Määränpäässä on kansio eli sieltä sisältä uupuu jotain
        else:
            kansiossa_uupuvat = muodosta_latauslista(
                erotuspuu=kansio,
                maaranpaapuu=vastaava_maaranpaassa
                )
            paluulista += kansiossa_uupuvat
    return paluulista


def lataa_tietokannat_palvelimelta(sijainnit):
    '''
    Lataa etäpalvelimelta sikäläiset tietokannat paikallisiksi tiedostoiksi
    jotta niitä voidaan vertaista täkäläisten kanssa.

    Sisään
    ------
    sijainnit : dict
        Lataussijainnit dictin muodossa:
        {
        "palvelin": str,
        "tietokannat_palvelimella": [str]
        "kohdetiedostot": [str]
        }
        missä `palvelin` on palvelimen nimi mistä ladataan,
        `tietokannat_palvelimella` lista tiedostopolkuja palvelimella ja
        `kohdetiedostot` näiden tiedostojen sijoituskohteet paikallisessa
        tiedostojärjestelmässä (ts. mihin ne ladataan), pareittain järkässä.

    Ulos
    ----
    [bool]
        True kaikille tiedostoille joiden lataus onnistui, False muille.
    '''
    paluuarvo = [False]*len(sijainnit["tietokannat_palvelimella"])
    palvelin = sijainnit["palvelin"]
    for t,tiedostopolku in enumerate(sijainnit["tietokannat_palvelimella"]):
        logging.info(
            "Lataa tietokanta {} palvelimelta {}\nkohteeseen {}".format(
                tiedostopolku,
                palvelin,
                sijainnit["kohdetiedostot"][t]
            ))
        koodi = kfun.lataa(
            vaintiedosto=True,
            lahdepalvelin=palvelin,
            lahdepolku=tiedostopolku,
            kohdepalvelin=None,
            kohdepolku=sijainnit["kohdetiedostot"][t]
            )
        logging.info(
            "    {}".format(
                int(koodi)*"ladattiin" + int(not koodi)*"ei onnistunut"
            ))
        paluuarvo[t] = koodi
    logging.info(
        "Ladattiin {sum(paluuarvo)}/{len(paluuarvo)} tietokantatiedostoa")
    return paluuarvo


def lataa_puuttuvat(lahdepuu, lahdepalvelin, kohdepuu, kohdepalvelin):
    '''
    Lataa puuttuvat tiedostot ja kansiot, joko paikalliselta koneelta
    etäkoneelle tai toisin päin.

    Sisään
    ------
    lahdepuu : Tiedostopuu
        Lähteen kansiorakenne Tiedostopuun muodossa.
        Asiat jotka tästä löytyy mutta puuttuu kohdepuusta
        ladataan kohdepuun suuntaan.
    lahdepalvelin : str tai None
        Palvelin jonka suunnalta asioita ladataan.
        Jos str, etäpalvelin (esim "pettankone").
        Jos None, paikallinen kone.
    kohdepuu : Tiedostopuu
        Puu josta katsotaan että mitä kaikkea sieltä puuttuu.
    kohdepalvelin : str tai None
        Palvelin jonka suuntaan ladataan.
        Jos str, etäkone, None paikalliselle koneelle.
    '''
    erotuspuu = lahdepuu - kohdepuu
    kohdetiedostot = muodosta_latauslista(erotuspuu, kohdepuu)
    lahdejuuri = lahdepuu.kansio
    kohdejuuri = kohdepuu.kansio
    for kohdepolku in kohdetiedostot:
        lahdepolku = kohdepolku.replace(kohdejuuri, lahdejuuri)
        vaintiedosto = kohdepolku[-1] not in ("\\", "/")
        logging.info(
            "lataa puuttuva {} {}:{}\nkohteeseen {}:{}".format(
                int(vaintiedosto)*"tiedosto" + int(not vaintiedosto)*"kansio",
                lahdepalvelin,
                lahdepolku,
                kohdepalvelin,
                kohdepolku
            ))
        koodi = kfun.lataa(
			vaintiedosto=vaintiedosto,
			lahdepalvelin=lahdepalvelin,
			lahdepolku=lahdepolku,
			kohdepalvelin=kohdepalvelin,
			kohdepolku=kohdepolku
			)
        logging.info(
            "    {}".format(
                int(koodi)*"ladattiin" + int(not koodi)*"ei onnistunut"
            ))


def poista_ylimaaraiset(lahdepuu, kohdepuu, kohdepalvelin):
    '''
    Poista tiedostot ja kansiot joita ei kuuluisi olla,
    joko paikallisella kovalevyllä tai etäpalvelimella.

    Sisään
    ------
    lahdepuu : Tiedostopuu
        Lähteen kansiorakenne Tiedostopuun muodossa.
        Asiat joita tästä ei löydy mutta kohdepuusta löytyy
        poistetaan kohdepuun kovalevyltä.
    kohdepuu : Tiedostopuu
        Puu josta katsotaan että mitä kaikkea siellä on ylimääräisenä.
    kohdepalvelin : str tai None
        Palvelin mistä tavaraa poistetaan.
        Jos str, etäkone, None paikalliselle koneelle.
    '''
    erotuspuu = kohdepuu - lahdepuu
    kohdetiedostot = muodosta_latauslista(erotuspuu, lahdepuu)
    lahdejuuri = lahdepuu.kansio
    kohdejuuri = kohdepuu.kansio
    for kohdepolku in kohdetiedostot:
        kohdepolku = kohdepolku.replace(lahdejuuri, kohdejuuri)
        vaintiedosto = kohdepolku[-1] not in ("\\", "/")
        logging.info(
            "poista {} {}:{}".format(
                int(vaintiedosto)*"tiedosto" + int(not vaintiedosto)*"kansio",
                kohdepalvelin,
                kohdepolku
            ))
        koodi = kfun.etapoisto(
            vaintiedosto=vaintiedosto,
			palvelin=kohdepalvelin,
			tiedostopolku=kohdepolku
			)
        if koodi[0]:
            logging.info("    Poistettiin.")
        else:
            logging.info(f"    Ei onnistunut: {koodi[1]}")

def paivita_paikalliset(puu):
    '''
    Päivitä paikallinen puu, eli katso mitä
    puun määrittämissä kansioissa on ja mitä siellä ei ole.
    Poista puusta ne kansiot joita ei oikeasti ole kovalevyllä
    ja lisää ne mitkä on kovalevyllä mutta puuttuu puusta.
    '''
    puustr = puu.syvennystaso*" "+puu.kansio
    # Puuttuvat tiedostot veks
    alkuperaiset = [t.tiedostonimi for t in puu.tiedostot]
    puu.tiedostot = [
        tiedosto
        for tiedosto in puu.tiedostot
        if os.path.isfile(
            os.path.join(puu.hae_nykyinen_polku(), tiedosto.tiedostonimi)
            )
        ]
    poistetut = [
        nimi for nimi in alkuperaiset
        if not any(t.tiedostonimi == nimi for t in puu.tiedostot)
        ]
    if poistetut:
        logging.info("{}: Poistettiin puusta tiedostot {}".format(
            puustr,
            poistetut
            ))
    # Puuttuvat kansiot veks
    alkuperaiset = [k.kansio for k in puu.alikansiot]
    puu.alikansiot = [
        kansio
        for kansio in puu.alikansiot
        if os.path.isdir(
            kansio.hae_nykyinen_polku()
            )
        ]
    poistetut = [
        nimi for nimi in alkuperaiset
        if puu.alikansio(nimi) is None
        ]
    if poistetut:
        logging.info("{}: Poistettiin puusta kansiot {}".format(
            puu.syvennystaso*" "+puu.kansio,
            poistetut
            ))

    # Muuttuneet tiedostot
    for t,tiedosto in enumerate(puu.tiedostot):
        muokkausaika = int(time.strftime("%Y%m%d%H%M",
            time.gmtime(os.path.getmtime(
                os.path.join(puu.hae_nykyinen_polku(), tiedosto.tiedostonimi)
                ))
            ))
        if muokkausaika > tiedosto.lisayspaiva:
            logging.info(
                "{}/{} on muuttunut välissä, uusitaan ({} > {})".format(
                    puustr,
                    tiedosto.tiedostonimi,
                    muokkausaika,
                    tiedosto.lisayspaiva
                ))
            uusi_versio = puu.tiedostotyyppi(kohteesta=os.path.join(
                    puu.hae_nykyinen_polku(), tiedosto.tiedostonimi)
                    )
            puu.tiedostot[t] = uusi_versio
    # Kurkkaa alikansiotkin lävitte
    for k,alikansio in enumerate(puu.alikansiot):
        paivita_paikalliset(alikansio)

    # Määrittelemättömät tiedostot ja kansiot
    tiedostot, kansiot = kfun.kansion_sisalto(
        kansio=puu.hae_nykyinen_polku(),
        tiedostomuodot=puu.tiedostomuodot
        )
    for tiedosto in tiedostot:
        if not any(t.tiedostonimi == tiedosto for t in puu.tiedostot):
            logging.info("{}/{} määrittelemätön tiedosto, lisätään".format(
                puustr,
                tiedosto
                ))
            puu.tiedostot.append(puu.tiedostotyyppi(
                kohteesta=os.path.join(puu.hae_nykyinen_polku(), tiedosto)
                ))
    for kansio in kansiot:
        if puu.alikansio(kansio) is None:
            logging.info("{}/{} määrittelemätön kansio, lisätään".format(
                puustr,
                kansio
                ))
            alikansio = Tiedostopuu()
            alikansio.edellinentaso = puu
            alikansio.kansio = kansio
            alikansio.syvennystaso = puu.syvennystaso + 1
            alikansio.tiedostotyyppi = puu.tiedostotyyppi
            alikansio.kansoita()
            puu.alikansiot.append(alikansio)
