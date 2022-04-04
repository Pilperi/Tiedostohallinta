'''
Juttele Pettanflask-palvelimen kanssa.
Kysele mitä tietokantoja on tarjolla, lataa niitä ja tiedostoja ymv
'''
import logging
import requests
import shutil

from tiedostohallinta.class_http import Pyynto, Vastaus

LOGGER = logging.getLogger(__name__)


def suorita_pyynto(pyynto, osoite):
    '''
    Suorita pyyntö Pettanflask-palvelimelle.

    Sisään
    ------
    pyynto : Pyynto
        Pyyntöluokan olio, jossa argumentit parsittu kunnolliseen kuntoon.
    osoite : str
        Palvelimen osoite ilman lisämääreitä mutta loppukenon kanssa.
        esim. "http://127.0.0.1:5000/" tai "http://localhost:5000/"

    Ulos
    ----
    Vastaus
        Tulos Vastaus-luokan oliona.
        Attribuutteina siinä on vastaus, virhe, koodi.
        Sisältö vaihtelee pyynnön mukaan, mutta vastaus-kentän alla
        on mitä etsitään, jos on ollakseen (virheellä ja koodilla tietää
        onko vaiko eikö ole)
    '''
    try:
        vastaus = Vastaus(requests.post(
            osoite+"musatietokanta", json=pyynto.json())
            )
        return vastaus
    except requests.exceptions.ConnectionError as err:
        LOGGER.error(f"Ei saatu yhteyttä palvelimeen: {err}")
        return Vastaus(None, err)


def listaa_musatietokannat(osoite):
    '''
    Hae lista käytettävissä olevista musatietokannoista.

    Sisään
    ------
    osoite : str
        Palvelimen osoite ilman lisämääreitä mutta loppukenon kanssa.
        esim. "http://127.0.0.1:5000/" tai "http://localhost:5000/"

    Ulos
    ----
    Vastaus
        Tulos Vastaus-luokan oliona.
        Attribuutteina siinä on vastaus, virhe, koodi.
        Vastauksen alla pitäisi olla lista nimistringejä.
    '''
    LOGGER.debug("Listaa tietokannat.")
    pyynto = Pyynto("listaa_tietokannat", None)
    return suorita_pyynto(pyynto, osoite)


def lataa_tietokanta(nimi, osoite):
    '''
    Lataa tietokanta palvelimelta.

    Sisään
    ------
    nimi : str
        Tietokannan nimi, vaihtoehdot saa funktiolla `listaa_musatietokannat`
    osoite : str
        Palvelimen osoite ilman lisämääreitä mutta loppukenon kanssa.
        esim. "http://127.0.0.1:5000/" tai "http://localhost:5000/"

    Ulos
    ----
    Vastaus
        Tulos Vastaus-luokan oliona.
        Attribuutteina siinä on vastaus, virhe, koodi.
        Vastauksen alla pitäisi olla tietokanta diktinä.
    '''
    LOGGER.debug(f"Lataa tietokanta {nimi} osoitteesta {osoite}.")
    pyynto = Pyynto("anna_tietokanta", nimi)
    return suorita_pyynto(pyynto, osoite)


def etsi_tietokannasta(nimi, hakukriteerit, osoite):
    '''
    Lataa tietokanta palvelimelta.

    Sisään
    ------
    nimi : str
        Tietokannan nimi, vaihtoehdot saa funktiolla `listaa_musatietokannat`
    hakukriteerit : Hakukriteerit tai dict
        Millä ehdoilla haetaan.
        ks. tiedostohallinta.class_biisiselaus.Hakukriteerit detskuja varten.
    osoite : str
        Palvelimen osoite ilman lisämääreitä mutta loppukenon kanssa.
        esim. "http://127.0.0.1:5000/" tai "http://localhost:5000/"

    Ulos
    ----
    Vastaus
        Tulos Vastaus-luokan oliona.
        Attribuutteina siinä on vastaus, virhe, koodi.
    '''
    LOGGER.debug(f"Suorita haku tietokannasta {nimi}")
    pyynto = Pyynto("etsi_tietokannasta", nimi, hakukriteerit)
    return suorita_pyynto(pyynto, osoite)


def anna_latauslista(puu, osoite):
    '''
    Muodosta latauslista kaikille annetun puun tiedostoille.
    Niitä voi sitten tuuppailla latauskutsuun ja saada takaisin binääriä.

    Sisään
    ------
    puu : Tiedostopuu tai dict
        Tiedostopuu jota haluttaisiin latailla.
        Esim. valittu alikansio tai hakutulosdikti tai muu vastaava.
    osoite : str
        Palvelimen osoite ilman lisämääreitä mutta loppukenon kanssa.
        esim. "http://127.0.0.1:5000/" tai "http://localhost:5000/"

    Ulos
    ----
    Vastaus
        Tulos Vastaus-luokan oliona.
        Attribuutteina siinä on vastaus, virhe, koodi.
        Vastaus-kentän alla on lista stringejä.
    '''
    LOGGER.debug(f"Hanki latauspolut ")
    pyynto = Pyynto("anna_latauslista", puu)
    return suorita_pyynto(pyynto, osoite)


def lataa_biisi_kansioon(latauspolku, kohdepolku, osoite):
    '''
    Lataa palvelimelta tiedosto ja sijoita se osoitettuun kansioon.
    Kerro onnistuiko vaiko eikö onnistunut.

    Sisään
    ------
    latauspolku : str
        Polku josta ladataan, ts. yksi `anna_latauslista` paluuarvoista
        tai muu vastaava mitä voi vaan tuupata palvelimen suuntaan.
    kohdepolku : str
        Määränpäätiedostopolku, johon tarkoitus tuupata.
        Jos määränpäässä on saman niminen tiedosto, sen päälle kirjoitetaan,
        eli määritä loppusijoituspolku kunnolla ennen kuin kutsut.
    osoite : str
        Palvelimen osoite ilman lisämääreitä mutta loppukenon kanssa.
        esim. "http://127.0.0.1:5000/" tai "http://localhost:5000/"
    '''
    try:
        vastaus = requests.get(
            osoite+"musatietokanta/biisi",
            json={"polku": latauspolku}
            )
        if vastaus.status_code != 200:
            return False
        with open(kohdepolku, 'wb+') as filu:
            for chunk in vastaus.iter_content(chunk_size=1024):
                if chunk:
                    filu.write(chunk)
    except requests.exceptions.ConnectionError as err:
        LOGGER.error(f"Ei saatu yhteyttä palvelimeen: {err}")
        return False
    return True
