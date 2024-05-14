from bs4 import BeautifulSoup
import urllib.parse
import warnings
import requests
import urllib3
import os

warnings.filterwarnings("ignore", category=UserWarning)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def parse_and_extract(url):
    try:
        response = requests.get(url, verify=False)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        links = soup.find_all('a', href=True)

        base_url = response.url

        pdf_links = [urllib.parse.urljoin(base_url, link['href']) for link in links if link['href'].endswith('.pdf')]

        extracted_data = []
        for pdf_link in pdf_links:
            try:
                pdf_response = requests.head(pdf_link, verify=False)
                if pdf_response.status_code == 200:
                    filename = os.path.basename(pdf_link)
                    folder_path = "Schedule"
                    if not os.path.exists(folder_path):
                        os.makedirs(folder_path)
                    file_path = os.path.join(folder_path, filename)
                    with open(file_path, "wb") as f:
                        f.write(requests.get(pdf_link, verify=False).content)
                    extracted_data.append(file_path)
                    print(f"Файл {filename} успешно сохранен в папку 'Schedule'.")
                else:
                    print(f"Файл {pdf_link} недоступен. Пропускаем его.")
            except Exception as pdf_error:
                print(f"Ошибка при обработке PDF {pdf_link}: {pdf_error}")

        return extracted_data
    except Exception as e:
        print(f"Ошибка при парсинге страницы и извлечении данных из PDF: {e}")
        return None

url = "https://philology.bsu.by/ru/studjentu/raspisanie/1379-raspisanie-zanyatij-studentov-dnevnogo-otdeleniya"
pdf_filenames = parse_and_extract(url)
