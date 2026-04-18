import sys
import json
import time
import re
import pandas as pd  # type: ignore

# Harus pake ini katanya bisa di chrome gatau aneh juga
from webdriver_manager.chrome import ChromeDriverManager  # type: ignore
from selenium import webdriver  # type: ignore
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

#region PREPOCESSING
def bersihkan_teks(teksnya):
    teksnya = str(teksnya).lower()

    teksnya = re.sub(r"[^a-z\s]", "", teksnya)

    kata_kata = teksnya.split()

    kata_dibuang = [
        #Stopword bahasa Inggris
        "a", "about", "above", "after", "again", "against", "ain",
        "all", "am", "an", "and", "any", "are", "aren",
        "aren't", "as", "at", "be", "because", "been", "before",
        "being", "below", "between", "both", "but", "by", "can",
        "couldn", "couldn't", "d", "did", "didn", "didn't", "do",
        "does", "doesn", "doesn't", "doing", "don", "don't", "down",
        "during", "each", "few", "for", "from", "further", "had",
        "hadn", "hadn't", "has", "hasn", "hasn't", "have", "haven",
        "haven't", "having", "he", "he'd", "he'll", "her", "here",
        "hers", "herself", "he's", "him", "himself", "his", "how",
        "i", "i'd", "if", "i'll", "i'm", "in", "into",
        "is", "isn", "isn't", "it", "it'd", "it'll", "it's",
        "its", "itself", "i've", "just", "ll", "m", "ma",
        "me", "mightn", "mightn't", "more", "most", "mustn", "mustn't",
        "my", "myself", "needn", "needn't", "no", "nor", "not",
        "now", "o", "of", "off", "on", "once", "only",
        "or", "other", "our", "ours", "ourselves", "out", "over",
        "own", "re", "s", "same", "shan", "shan't", "she",
        "she'd", "she'll", "she's", "should", "shouldn", "shouldn't", "should've",
        "so", "some", "such", "t", "than", "that", "that'll",
        "the", "their", "theirs", "them", "themselves", "then", "there",
        "these", "they", "they'd", "they'll", "they're", "they've", "this",
        "those", "through", "to", "too", "under", "until", "up",
        "ve", "very", "was", "wasn", "wasn't", "we", "we'd",
        "we'll", "we're", "were", "weren", "weren't", "we've", "what",
        "when", "where", "which", "while", "who", "whom", "why",
        "will", "with", "won", "won't", "wouldn", "wouldn't", "y",
        "you", "you'd", "you'll", "your", "you're", "yours", "yourself",
        "yourselves", "you've",
        #Stopword bahasa Indonesia
        "yang", "untuk", "pada", "ke", "para",
        "namun", "menurut", "antara", "dia", "dua", "ia", "seperti",
        "jika", "sehingga", "kembali", "dan", "tidak", "ini", "karena",
        "kepada", "oleh", "saat", "harus", "sementara", "setelah", "belum",
        "kami", "sekitar", "bagi", "serta", "di", "dari", "telah",
        "sebagai", "masih", "hal", "ketika", "adalah", "itu", "dalam",
        "bisa", "bahwa", "atau", "hanya", "kita", "dengan", "akan",
        "juga", "ada", "mereka", "sudah", "saya", "terhadap", "secara",
        "agar", "lain", "anda", "begitu", "mengapa", "kenapa", "yaitu",
        "yakni", "daripada", "itulah", "lagi", "maka", "tentang", "demi",
        "dimana", "kemana", "pula", "sambil", "sebelum", "sesudah", "supaya",
        "guna", "kah", "pun", "sampai", "sedangkan", "selagi", "tetapi",
        "apakah", "kecuali", "sebab", "selain", "seolah", "seraya", "seterusnya",
        "tanpa", "agak", "boleh", "dapat", "dsb", "dst", "dll",
        "dahulu", "dulunya", "anu", "demikian", "tapi", "ingin", "nggak",
        "mari", "nanti", "melainkan", "oh", "ok", "seharusnya", "sebetulnya",
        "setiap", "setidaknya", "sesuatu", "pasti", "saja", "toh", "ya",
        "walau", "tolong", "tentu", "amat", "apalagi", "bagaimanapun",
    ]

    hasil_bersih = []
    for k in kata_kata:
        if k not in kata_dibuang:
            hasil_bersih.append(k)

    return " ".join(hasil_bersih)

#endregion

#region CRAWLING GS
def jalankan_crawling(penulis, batas):
    opsi = Options()
    opsi.add_argument("--headless=new")
    opsi.add_argument("--no-sandbox")
    opsi.add_argument("--disable-dev-shm-usage")
    opsi.add_argument("--log-level=3")
    opsi.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    )

    try:
        servis = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=servis, options=opsi)
    except:
        driver = webdriver.Chrome(options=opsi)

    # region CARI ID PENULIS

    link = 'https://scholar.google.com/scholar?q=author:"' + penulis + '"&hl=en'
    id_penulis = ""
    try:
        driver.get(link)
        time.sleep(5)

        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        kotak_artikel = soup.select(".gs_r")

        if len(kotak_artikel) > 0:
            item = kotak_artikel[0]
            link_tag = item.select_one(".gs_rt2 a")

            if link_tag and "href" in link_tag.attrs:
                id_penulis = link_tag["href"].split("user=")[1].split("&")[0]

    except:
        pass

    # endregion
    # region CARI ID ARTIKEL

    link_author = "https://scholar.google.com/citations?hl=en&user=" + id_penulis
    list_linkArtikel = []
    try:
        driver.get(link_author)
        time.sleep(5)

        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        kotak_artikel = soup.select(".gsc_a_tr")

        for item in kotak_artikel[:batas]:
            link_tag = item.select_one(".gsc_a_t a")
            if link_tag and "href" in link_tag.attrs:
                id_artikel = link_tag["href"].split("citation_for_view=")[1]
                list_linkArtikel.append(id_artikel)
    except:
        pass

    # endregion

    # region AMBIL DATA ARTIKEL
    data_hasil = []
    for i in range(len(list_linkArtikel)):
        link_view = (
            "https://scholar.google.com/citations?view_op=view_citation&hl=en&user="
            + id_penulis
            + "&citation_for_view="
            + list_linkArtikel[i]
        )
        try:
            driver.get(link_view)
            time.sleep(5)
            html = driver.page_source
            soup = BeautifulSoup(html, "html.parser")

            judul = ""
            link_artikel = ""
            title_tag = soup.select_one(".gsc_oci_title_link")
            if title_tag:
                judul = title_tag.text.strip()
                link_artikel = title_tag["href"]

            autor = ""
            tanggal_publikasi = ""
            jurnal = ""
            sitasi = 0

            for row in soup.select(".gs_scl"):
                field = row.select_one(".gsc_oci_field")
                value = row.select_one(".gsc_oci_value")
                if field and value:
                    if field.text.strip() == "Authors":
                        autor = value.text.strip()
                    elif field.text.strip() == "Publication date":
                        tanggal_gs = value.text.strip()
                        parts = tanggal_gs.split("/")
                        if len(parts) == 3:
                            tanggal_publikasi = (
                                parts[2] + "/" + parts[1] + "/" + parts[0]
                            )
                        elif len(parts) == 2:
                            tanggal_publikasi = parts[1] + "/" + parts[0]
                        else:
                            tanggal_publikasi = tanggal_gs
                    elif field.text.strip() == "Journal":
                        jurnal = value.text.strip()
                    elif field.text.strip() == "Total citations":
                        a_tag = value.select_one("a")
                        if a_tag:
                            try:
                                sitasi = int(a_tag.text.strip().split("by")[1].strip())
                            except:
                                sitasi = 0
            data_hasil.append(
                {
                    "title": judul,
                    "link": link_artikel,
                    "author": autor,
                    "publication_date": tanggal_publikasi,
                    "journal": jurnal,
                    "citations": sitasi,
                }
            )
        except Exception as e:
            print("Error:", e)
            continue

    driver.quit()
    return data_hasil


# endregion
# endregion

# region MAIN PROGRAM

if len(sys.argv) > 3:
    input_penulis = sys.argv[1]
    input_keyword = sys.argv[2]
    input_batas = int(sys.argv[3])

    hasil_crawling = jalankan_crawling(input_penulis, input_batas)

    if len(hasil_crawling) == 0:
        print(json.dumps([]))
    else:
        dokumen = [input_keyword]
        for h in hasil_crawling:
            dokumen.append(h["title"])

        dokumen_bersih = []
        for d in dokumen:
            bersih = bersihkan_teks(d)
            dokumen_bersih.append(bersih)

        try:
            tfidf = TfidfVectorizer()
            matrix = tfidf.fit_transform(dokumen_bersih)
            nilai_cosine = cosine_similarity(matrix[0:1], matrix[1:]).flatten()

            no = 0
            for nilai in nilai_cosine:
                hasil_crawling[no]["similarity"] = round(nilai, 4)
                no = no + 1
            hasil_akhir = sorted(
                hasil_crawling, key=lambda x: x["similarity"], reverse=True
            )

            print(json.dumps(hasil_akhir))

        except:
            for h in hasil_crawling:
                h["similarity"] = 0.0
            print(json.dumps(hasil_crawling))
else:
    print(json.dumps([]))

# endregion
