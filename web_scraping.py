import re
from PIL import Image
import fitz
import pytesseract
import os

import requests


def get_urls(query):
    headers = {
        'accept': "application/json",
        'content-type': "application/json",
        'authorization': "Enter your Bing Search API here"
    }


    payload = {
                "q": query,
                "domain": "google.com",
                "loc": "Abernathy,Texas,United States",
                "lang": "en",
                "page": "1",
                "verbatim": "0",
                }

    response = requests.get('https://api.serphouse.com/serp/live', headers=headers, params=payload)
    results = []
    if response.status_code == 200:
        data = response.json()
        for i in range(3):
            results.append(data['results']['results']['organic'][i]['link'])
        #json_formatted_str = json.dumps(chat_data, indent=2)
        # for result in chat_data['webPages']['value']:
        #     print(result['name'], result['url'])
    else:
        print("Error:", response.status_code, response.text)
    return results


def text_extractor(img, page):
    text = str(pytesseract.image_to_string(img))
    text = text.replace('\n\n', ' ').replace('\n', ' ').replace('–', ' ').replace('_', ' ').replace('\t', ' ').encode(
        'ascii', errors='replace').decode('utf-8').replace("\x0c", "").replace('\\', "").replace('/', "").replace('\r',"").replace(
        "-", " ").replace(".......*", " ")
    return  text.lower()

def scrape_text(url: str) -> str:
    if url.split('.')[-1] == 'pdf':
        text = ''
        with open('temp_store/pages.pdf', "wb") as file:
            response = requests.get(url)
            file.write(response.content)


        pdf_file = fitz.open('temp_store/pages.pdf')
        for i in range(0, pdf_file.page_count):
            page = pdf_file.load_page(i)
            pix = page.get_pixmap(dpi=200)
            mode = "RGBA" if pix.alpha else "RGB"
            # set the mode depending on alpha
            img = Image.frombytes(mode, [pix.width, pix.height], pix.samples)
            text = text + text_extractor(img, i)
        os.remove("temp_store/pages.pdf")
        return text[:6000]

    else:
        try:
            response = requests.get(url)
            response.raise_for_status()
            html = response.text
            text = extract_body_text(html)
            return text
        except requests.exceptions.RequestException as e:
            print(f"Error fetching URL {url}: {e}")
            return ""

def extract_body_text(html: str) -> str:
    body_start_tag = "<body"
    body_end_tag = "</body>"
    body_start_index = html.find(body_start_tag)
    body_end_index = html.find(body_end_tag, body_start_index)
    if body_start_index != -1 and body_end_index != -1:
        body_content = html[body_start_index:body_end_index + len(body_end_tag)]
        body_text = re.sub(r"<script[\s\S]*?</script>", "", body_content)
        body_text = re.sub(r"<style[\s\S]*?</style>", "", body_text)
        body_text = re.sub(r"<[^>]+>", "", body_text)
        body_text = re.sub(r"\s+", " ", body_text).strip()
        return body_text[:3000]
    return ""


def extract_text(urls):
    text = map(lambda x: '{url}\n Website chat_data: {scrapped_data}'.format(url = x, scrapped_data = scrape_text(x)), urls)
    text = "\n\n".join(text)
    return text
        #[{"URL": i, "Summary":scrape_text(i)} for i in urls]


