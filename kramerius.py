###################
#
# Skript pro stažení obsahu dokumentu z Digitální knihovny, API v. 5.0
# 
# Dokumentace API: https://github.com/ceskaexpedice/kramerius/wiki/ClientAPIDEV
#
# Stáhne obrázek v plné kvalitě, text OCR a ALTO
#
####################

import requests
import urllib.request
import json
from urllib.parse import urlparse

url_ui = input("Zadej webový odkaz na dokument v Digitální knihovně: ")
url_ui_pars = urlparse(url_ui)

dk = url_ui_pars.hostname
path = url_ui_pars.path
uuid = path.split('/')[-1]

dokument = requests.get(f'https://{dk}/search/api/v5.0/item/{uuid}/children')

count = 0
dokJSON = json.loads(dokument.content)
for page in dokJSON:
	count += 1
	fileCount = '{:04d}'.format(count)
	print(count)
	
	streams = f'https://{dk}/search/api/v5.0/item/{page["pid"]}/streams'

	jpg = requests.get(f'{streams}/IMG_FULL', verify=False)
	with open(f'{fileCount}.jpg', "wb") as f:
		f.write(jpg.content)

	txt = requests.get(f'{streams}/TEXT_OCR')
	with open(f'{fileCount}.txt', 'wb') as f:
		f.write(txt.content)


	alto = requests.get(f'{streams}/alto', verify=False)
	with open(f'{fileCount}.xml', "wb") as f:
		f.write(alto.content)		
		
