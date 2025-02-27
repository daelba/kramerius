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
uuid_full = path.split('/')[-1]
uuid = uuid_full.split(":")[-1]

print(f'https://{dk}/search/api/v5.0/info')
print(requests.get(f'https://{dk}/search/api/v5.0/info').content)
print(f'https://{dk}/search/api/client/v7.0/info')
headers = {
	'Content-Type': 'application/json'
}

response_v7 = requests.get(f'https://{dk}/search/api/client/v7.0/info', headers=headers)
print(response_v7.content)

dokument = requests.get(f'https://{dk}/search/api/v5.0/item/{uuid_full}/children')

# Vytvoří složku
os.makedirs(uuid, exist_ok=True)

# Metadata
meta = {
	"document": {
		"uuid": uuid,
		"url": f"https://{dk}/view/uuid:{uuid}"
	},
	"parts": []
}

# Stáhne soubory
print("Stahuji soubory...")
count = 0
dokJSON = json.loads(dokument.content)
for page in dokJSON:
	count += 1
	fileCount = '{:04d}'.format(count)
	print(f'\r{count}', end='')
	
	streams = f'https://{dk}/search/api/v5.0/item/{page["pid"]}/streams'

	download_file(f'{streams}/IMG_FULL', f'{uuid}/JPG/{fileCount}.jpg', verify=False)
	download_file(f'{streams}/TEXT_OCR', f'{uuid}/TXT/{fileCount}.txt')
	download_file(f'{streams}/alto', f'{uuid}/ALTO/{fileCount}.xml', verify=False)
 
	pageMeta = {
		"uuid": f'{page["pid"]}',
		"url": f'https://{dk}/view/uuid:{uuid}?page={page["pid"]}',
		"file": f'{fileCount}.jpg'
	}
	meta["parts"].append(pageMeta)

with open(f'{uuid}/uuid.json','w') as f:
	json.dump(meta,f,indent=4,ensure_ascii=False)

# Vytvoří PDF
print("\nVytvářím PDF...")
pdf = FPDF()
for i in range(1, count + 1):
	print(f'\r{i}', end='')
	fileCount = '{:04d}'.format(i)
	img_path = f'{uuid}/{fileCount}.jpg'
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
	temp_img_path = f'{uuid}/temp_{fileCount}.jpg'
	img.save(temp_img_path, quality=85)  # Adjust quality to reduce size further

	pdf.image(temp_img_path, 0, 0, pdf_width, pdf_height)

	# Smazat dočasný soubor
	os.remove(temp_img_path)

pdf.output(f'{uuid}/{uuid}.pdf', 'F')
		
