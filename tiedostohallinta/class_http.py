'''
Pyyntö- ja vastausluokat Pettanflaskin http-jutteluun.
'''

import logging
from requests import Response

from tiedostohallinta.class_tiedostopuu import Tiedostopuu
from tiedostohallinta.class_biisiselaus import Hakukriteerit

LOGGER = logging.getLogger(__name__)

class Pyynto:
    '''
    Pyynnöt luokkana, sisältää huolenpidon argumenttiparsinnoista sun muista.
    '''
    # Kunkin kutsutyypin odotetut argumenttityypit.
    # Datatyyppi per argumentti, jos useampi vaihtoehto niin tuplena
    ARGUMENTTITYYPIT = {
        "listaa_tietokannat": [],
        "anna_tietokanta": [
            (str,)
            ],
        "etsi_tietokannasta": [
            (str,),
            (Hakukriteerit, dict)
            ],
        "anna_latauslista": [
            (Tiedostopuu, dict)
            ],
        }
    def __init__(self, *args, **kwargs):
        '''
        Luokan luonti sisäänmenoargumenteilla.
        Hyväksyttävät skenaariot:

        - Pyynto(dikti)
          missä dikti = Pyynto.diktiksi()
          eli käytännössä oikotie Pyynto.diktista(dikti)

        - Pyynto(toimenpide, argumentti1, argumentti2, ...)
          toimenpide-stringi ja loput argumentit tulkataan
          argumentti-kentän arvoiksi.

        - Pyynto(toimenpide=str, argumentit=list)
          eksplisiittinen formulointi toimenpide-stringistä
          +argumenttilistasta.
        '''
        self._toimenpide = None
        self._argumentit = None
        # Diktisisääntulo
        if args and isinstance(args[0], dict):
            try:
                self.taydenna_diktista(args[0])
            except ValueError as err:
                errmsg = f"Ei saatu initoitua diktillä {args[0]}: {err}"
                raise ValueError(errmsg) from err
        # Argumentti kerrallaan sisääntulo
        elif args:
            try:
                self.taydenna_argumenttilistasta(*args)
            except ValueError as err:
                errmsg = f"Ei saatu initoitua argumenteilla {args}: {err}"
                raise ValueError(errmsg) from err
        # Eksplisiittinen muotoilu
        if kwargs:
            try:
                self.taydenna_diktista(kwargs)
            except ValueError as err:
                errmsg = f"Ei saatu initoitua kwargeilla {kwargs}: {err}"
                raise ValueError(errmsg) from err

    @property
    def toimenpide(self):
        '''
        Kerro toimenpiteen arvo.
        '''
        return self._toimenpide
    @toimenpide.setter
    def toimenpide(self, uusiarvo):
        '''
        Parsi toimenpide, ts. katso että se on joku tunnetuista.
        '''
        if uusiarvo in Pyynto.ARGUMENTTITYYPIT:
            self._toimenpide = uusiarvo
        else:
            errmsg = (
                f"Toimenpide {uusiarvo} ei ole tunnettu."
                +f" Mahdolliset arvot: {list(Pyynto.ARGUMENTTITYYPIT)}"
                )
            LOGGER.error(errmsg)
            raise ValueError(errmsg)
    @property
    def argumentit(self):
        '''
        Palauta argumenttilista
        '''
        return self._argumentit
    @ argumentit.setter
    def argumentit(self, uusiarvo):
        '''
        Parsi argumentit ja jos kaikki on ok, aseta argumenttikenttään.
        '''
        # Onhan datatyyppi oikein
        if not isinstance(uusiarvo, (list,tuple)):
            errmsg = f"Odotettiin argumenttilistaa, saatiin {type(uusiarvo)}."
            LOGGER.error(errmsg)
            raise ValueError(errmsg)
        # Onhan toimenpide määritelty ensin
        if self.toimenpide not in Pyynto.ARGUMENTTITYYPIT:
            errmsg = "Toimenpide tulee määritellä ennen argumenttilistaa!"
            LOGGER.error(errmsg)
        datatyypit = Pyynto.ARGUMENTTITYYPIT[self.toimenpide]
        # Jotain pitäisi olla mutta luvut ei täsmää
        if datatyypit and len(uusiarvo) != len(datatyypit):
            errmsg = (
                f"Pyyntö {self.toimenpide} vaatii"
                +f" {len(datatyypit)} argumenttia, saatiin {len(uusiarvo)}."
                )
            LOGGER.error(errmsg)
            raise ValueError(errmsg)
        # Tarkista datatyypin täsmäävyys
        for argind, argumentti in enumerate(datatyypit):
            if not any(
                isinstance(uusiarvo[argind], vaihtoehto)
                for vaihtoehto in argumentti
                ):
                errmsg = (
                    f"Argumentille {argind} odotettiin jotain datatyypeistä"
                    +" {}".format([vaihtoehto.__name__ for vaihtoehto in argumentti])
                    +f", saatiin {type(uusiarvo[argind])}."
                    )
                LOGGER.error(errmsg)
                raise ValueError(errmsg)
        self._argumentit = list(uusiarvo)


    def taydenna_diktista(self, dikti):
        '''
        Lue kenttien arvot diktistä.
        '''
        self.toimenpide = dikti.get("TOIMENPIDE")
        self.argumentit = dikti.get("ARGUMENTIT")

    def taydenna_argumenttilistasta(self, *args):
        '''
        Lue kentät listasta agumentteja.
        '''
        self.toimenpide = args[0]
        self.argumentit = args[1:]

    def diktiksi(self):
        '''
        Muunna diktin muotoon (kutsuihin tuuppaamista varten)
        '''
        dikti = {"TOIMENPIDE": self.toimenpide, "ARGUMENTIT": self.argumentit}
        return  dikti

    def json(self):
        '''
        Käännä diktiesityksen ei-JSONit datat JSON-yhteensopiviksi.
        '''
        dikti = self.diktiksi()
        if self.argumentit is None:
            return dikti
        dikti["ARGUMENTIT"] = [
            argumentti if not isinstance(argumentti, (Tiedostopuu, Hakukriteerit))
            else argumentti.diktiksi()
            for argumentti in dikti["ARGUMENTIT"]
            ]
        if not dikti["ARGUMENTIT"]:
            dikti["ARGUMENTIT"] = None
        return dikti


class Vastaus:
    '''
    Pettanin standardivastaus, läh. parsittu ja paketoitu
    dikti jossa kentät "VASTAUS" ja "VIRHE"
    '''
    SALLITUT_VASTAUSTYYPIT = (
        type(None),
        str,
        list,
        dict,
        bool,
        )
    def __init__(self, *args, **kwargs):
        '''
        Luokan luonti sisäänmenoargumenteilla.
        Hyväksyttävät skenaariot:

        - Vastaus(dikti)
          missä dikti on esim. Vastaus.diktiksi()

        - Vastaus(vastaus, virhe=None)
          toimenpide-stringi ja loput argumentit tulkataan
          argumentti-kentän arvoiksi.

        - Pyynto(VASTAUS=str, VIRHE=str tai None)
          eksplisiittinen formulointi toimenpide-stringistä
          +argumenttilistasta.

        Käytännössä ajatuksena yksinkertaistaa tulostenlukua ja -kirjoittamista
        yhden luokan kanssa leikkimiseksi, ja parsia
        http-paluuarvojen virhekentät VIRHE-kentän alle.
        '''
        self._vastaus = None
        self._virhe = None
        self._koodi = 0
        # Request-Response
        if args and isinstance(args[0], Response):
            self.taydenna_vastauksesta(args[0])
        # Diktisisääntulo
        elif args and isinstance(args[0], dict):
          self.taydenna_diktista(args[0])
        # Argumentti kerrallaan sisääntulo
        elif len(args) == 2:
          self.taydenna_argumenttilistasta(*args)
        # Eksplisiittinen muotoilu
        if kwargs:
          self.taydenna_diktista(kwargs)

    @property
    def vastaus(self):
        '''
        Kerro mikä oli vastaus.
        '''
        return self._vastaus
    @vastaus.setter
    def vastaus(self, uusiarvo):
        '''
        Parsi vastaus, ts. katso että se on jotain sallituista datatyypeistä.
        '''
        if isinstance(uusiarvo, Vastaus.SALLITUT_VASTAUSTYYPIT):
            self._vastaus = uusiarvo
        else:
            errmsg = (
                "Vastaukset voivat olla vain str tai None"
                +f", saatiin {type(uusiarvo)}."
                )
            LOGGER.error(errmsg)
            raise ValueError(errmsg)

    @property
    def virhe(self):
        '''
        Kerro mikä oli virhe.
        '''
        return self._virhe
    @virhe.setter
    def virhe(self, uusiarvo):
        '''
        Parsi virhe, ts. katso että se on joko str tai None.
        '''
        if isinstance(uusiarvo, (str, type(None))):
            self._virhe = uusiarvo
        elif isinstance(uusiarvo, Exception):
            self._virhe = str(uusiarvo)
        else:
            errmsg = (
                "Virheet voivat olla vain str tai None"
                +f", saatiin {type(uusiarvo)}."
                )
            LOGGER.error(errmsg)
            raise ValueError(errmsg)

    @property
    def koodi(self):
        '''
        Anna paluukoodi.
        '''
        return self._koodi
    @koodi.setter
    def koodi(self, uusiarvo):
        '''
        Aseta koodi arvoonsa.
        '''
        if isinstance(uusiarvo, int):
            self._koodi = uusiarvo
        else:
            errmsg = (
                "Paluukoodit saavat olla vain kokonaislukuja"
                +f", saatiin {type(uusiarvo)} {uusiarvo}."
                )
            LOGGER.error(errmsg)
            raise ValueError(errmsg)

    def taydenna_vastauksesta(self, vastausdata):
        '''
        Lue requests-moduulin Response.
        '''
        self.koodi = vastausdata.status_code
        self.taydenna_diktista(vastausdata.json())

    def taydenna_diktista(self, dikti):
        '''
        Lue kenttien arvot diktistä.
        '''
        self.vastaus = dikti.get("VASTAUS")
        if isinstance(dikti.get("message"), str):
            self.virhe = dikti.get("message")
        else:
            self.virhe = dikti.get("VIRHE")

    def taydenna_argumenttilistasta(self, *args):
        '''
        Lue kentät listasta agumentteja.
        '''
        self.vastaus = args[0]
        self.virhe = args[1]

    def diktiksi(self):
        '''
        Muunna diktin muotoon (kutsuihin tuuppaamista varten)
        '''
        dikti = {"VASTAUS": self.vastaus, "VIRHE": self.virhe}
        return  dikti

    def json(self):
        '''
        Datatyypit niin simppeleitä että kääntyvät suoraan JSONiksi.
        '''
        return self.diktiksi()
