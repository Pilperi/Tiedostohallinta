'''
Funktiot logien käsittelyyn ja kirjoittamiseen.
Lähinnä kiva että on erillinen funktio jolla saa systemaattisesti
aikaleimat tiedoston riveihin.
'''

import os
import shutil
import time
from . import vakiot_kansiovakiot as kvak

def kirjaa(tiedosto, rivi, sisennys=0):
	'''
	Kirjoita logitiedostoon rivi niin että siinä on mukana aikaleima.
	'''
	if tiedosto is not None:
		aikaleimarivi = "{}[{}] {}\n".format(" "*sisennys, time.asctime(), str(rivi))
		tiedosto.write(aikaleimarivi)

def kopsaa_logit():
	'''
	Varmuuskopioi edelliset logit ennen päälle kirjoittamista.
	'''
	if os.path.exists(kvak.LOGITIEDOSTO):
		shutil.copy(kvak.LOGITIEDOSTO, "{}.bk".format(kvak.LOGITIEDOSTO))
