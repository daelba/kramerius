###################
#
# Skript pro stažení obsahu dokumentu z Digitální knihovny, API v. 5.0
# 
# Dokumentace API: https://github.com/ceskaexpedice/kramerius/wiki/ClientAPIDEV
#
# Stáhne obrázek v plné kvalitě, text OCR a ALTO
#
####################

from urllib.parse import urlparse
import requests
import json
import os
from fpdf import FPDF
from PIL import Image

def download_file(url, path, verify=True):
	if not os.path.exists(path):
		response = requests.get(url, verify=verify)
		with open(path, "wb") as f:
			f.write(response.content)

url_ui = input("Zadej webový odkaz na dokument v Digitální knihovně: ")
url_ui_pars = urlparse(url_ui)

dk = url_ui_pars.hostname
path = url_ui_pars.path
uuid = path.split('/')[-1]

dokument = requests.get(f'https://{dk}/search/api/v5.0/item/{uuid}/children')

# Vytvoří složku
dir = uuid.split(":")[-1]
os.makedirs(dir, exist_ok=True)

# Stáhne soubory
print("Stahuji soubory...")
count = 0
dokJSON = json.loads(dokument.content)
for page in dokJSON:
	count += 1
	fileCount = '{:04d}'.format(count)
	print(f'\r{count}', end='')
	
	streams = f'https://{dk}/search/api/v5.0/item/{page["pid"]}/streams'

	jpg_path = f'{dir}/{fileCount}.jpg'
	txt_path = f'{dir}/{fileCount}.txt'
	alto_path = f'{dir}/{fileCount}.xml'

	download_file(f'{streams}/IMG_FULL', jpg_path, verify=False)
	download_file(f'{streams}/TEXT_OCR', txt_path)
	download_file(f'{streams}/alto', alto_path, verify=False)

# Vytvoří PDF
print("\nVytvářím PDF...")
pdf = FPDF()
for i in range(1, count + 1):
	print(f'\r{i}', end='')
	fileCount = '{:04d}'.format(i)
	img_path = f'{dir}/{fileCount}.jpg'
	img = Image.open(img_path)

	# Zmenšit obrázek na polovinu
	img = img.resize((img.width // 2, img.height // 2), Image.LANCZOS)

	pdf.add_page()
	img_width, img_height = img.size
	aspect_ratio = img_width / img_height

	if aspect_ratio > 1:  # Landscape
		pdf_width = 210
		pdf_height = pdf_width / aspect_ratio
	else:  # Portrait
		pdf_height = 297
		pdf_width = pdf_height * aspect_ratio

	# Vytvořit dočasný zmenšený obrázek
	temp_img_path = f'{dir}/temp_{fileCount}.jpg'
	img.save(temp_img_path, quality=85)  # Adjust quality to reduce size further

	pdf.image(temp_img_path, 0, 0, pdf_width, pdf_height)

	# Smazat dočasný soubor
	os.remove(temp_img_path)

pdf.output(f'{dir}/{dir}.pdf', 'F')
		
