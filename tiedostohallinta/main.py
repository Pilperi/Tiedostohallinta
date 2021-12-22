'''
Synkkatoiminnallisuudet scriptin muodossa.

1) Päivitä paikalliset puut
2) Lataa verrokkipuut palvelimelta
3) Vertaa paikallisia puita verrokkipuihin ja tee tarvittavat korjausliikkeet
'''

import os
import json
import logging

from tiedostohallinta import vakiot_kansiovakiot as kvak
from tiedostohallinta import funktiot_puuvertailu as pfun
from tiedostohallinta.class_tiedostopuu import Tiedostopuu

def main():
    asetukset = kvak.ASETUKSET
    # Päivitä paikalliset tietokannat.
    # Lisää tiedostopuut diktiin sitä mukaa kuin ne on luettu/määritelty
    paikalliset_tietokannat = asetukset["paikalliset_tietokannat"]
    for _,tietokanta in paikalliset_tietokannat.items():
        tietokannan_sijainti = tietokanta["tietokannan_sijainti"]
        tietokannan_kohde = tietokanta["tietokannan_kohde"]
        # Tietokantaa ei ole tiedoston muodossa siellä missä pitäisi
        if not os.path.exists(tietokannan_sijainti):
            logging.info(f"Tietokantaa\n    {tietokannan_sijainti}\n"
                +f"    ({tietokannan_kohde})\n"
                +"    ei ole määritelty, luodaan uusi.")
            puu = Tiedostopuu()
            puu.kansio = tietokannan_kohde
            puu.tiedostotyyppi = tietokanta["tiedostotyyppi"]
            puu.kansoita()
            logging.debug("Tietokanta muodostettu.")
            d = puu.diktiksi()
            f = open(
                tietokannan_sijainti,
                "w+",
                encoding="utf8")
            json.dump(d, f)
            f.close()
            logging.debug("Tietokanta tallennettu.")
            tietokanta["tiedostopuu"] = puu
        # Lue tiedostosta ja päivitä sieltä mistä tarvitsee
        else:
            logging.info(f"Päivitetään tietokanta\n    {tietokannan_sijainti}\n")
            f = open(
                tietokannan_sijainti,
                "r",
                encoding="utf8")
            puu = Tiedostopuu.diktista(json.load(f))
            f.close()
            pfun.paivita_paikalliset(puu)
            logging.debug("Päivitetty.")
            d = puu.diktiksi()
            f = open(
                tietokannan_sijainti,
                "w+",
                encoding="utf8")
            json.dump(d, f)
            f.close()
            logging.debug("Tallennettu.")
            tietokanta["tiedostopuu"] = puu


    sijainnit = asetukset["sijainnit"]
    ladatut_tietokannat = pfun.lataa_tietokannat_palvelimelta(sijainnit)

    voimasuhteet = asetukset["voimasuhteet"]
    for tietokanta_indeksi,ladattu in enumerate(ladatut_tietokannat):
        tyyppi = sijainnit["tyypit"][tietokanta_indeksi]
        logging.info(f"Synkataan {tyyppi}")
        if not ladattu:
            logging.info("Tietokantatiedostoa\n    {}:{}\n".format(
                sijainnit["palvelin"],
                sijainnit["tietokannat_palvelimella"][tietokanta_indeksi])
                +"    ei saatu ladattua, skipataan vertailu"
                )
            continue
        # Lue etäpalvelimen puu ja vertaa sitä paikalliseen
        logging.debug(
            "Luetaan etäkoneen tietokanta tiedostosta\n"
            +"    {}".format(sijainnit["kohdetiedostot"][tietokanta_indeksi])
            )
        f = open(
            sijainnit["kohdetiedostot"][tietokanta_indeksi],
            "r",
            encoding="utf8"
            )
        puu_eta = Tiedostopuu.diktista(json.load(f))
        f.close()
        logging.debug("Luettu.")
        puu_paikallinen = paikalliset_tietokannat[tyyppi]["tiedostopuu"]
        # Tarkista mihin suuntaan datan pitäisi liikkua
        if voimasuhteet[tyyppi]:
            logging.debug("Paikallinen puu masteri")
            # Paikallinen puu määrittä mitä etäpalvelimella saa olla
            lahdepuu = puu_paikallinen
            lahdepalvelin = None
            kohdepuu = puu_eta
            kohdepalvelin = sijainnit["palvelin"]
        else:
            # Etäpalvelimen puu määrittää mitä paikallisesti saa olla
            logging.debug("Etäkoneen puu masteri")
            lahdepuu = puu_eta
            lahdepalvelin = sijainnit["palvelin"]
            kohdepuu = puu_paikallinen
            kohdepalvelin = None
        logging.info(f"Poista ylimääräiset palvelimelta {kohdepalvelin}")
        pfun.poista_ylimaaraiset(
            lahdepuu=lahdepuu,
            kohdepuu=kohdepuu,
            kohdepalvelin=kohdepalvelin
            )
        logging.debug("Poistettu")
        logging.info(
            "Lataa puuttuvat"
            +f"palvelimelta {lahdepalvelin}"
            +f"palvelimelle {kohdepalvelin}")
        pfun.lataa_puuttuvat(
            lahdepuu=lahdepuu,
            lahdepalvelin=lahdepalvelin,
            kohdepuu=kohdepuu,
            kohdepalvelin=kohdepalvelin
            )
        logging.debug("Ladattu")
    logging.info("Valmis.")

if __name__ == "__main__":
    main()
