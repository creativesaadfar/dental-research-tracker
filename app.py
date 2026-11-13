import streamlit as st
import requests
import xml.etree.ElementTree as ET

st.set_page_config(page_title="Dental Research Tracker", page_icon="🦷", layout="wide")
st.title("🦷 أحدث الأبحاث العلمية في طب الأسنان")

# قراءة مفتاح PubMed من st.secrets (اختياري - PubMedيعمل بدونه ل用量 منخفض)
PUBMED_API_KEY = st.secrets.get("PUBMED_API_KEY", "")

specialties = ["Orthodontics", "Implantology", "Oral Surgery", "Endodontics", "Periodontics", "Prosthodontics", "Pediatric Dentistry"]
selected = st.selectbox("اختر التخصص (Specialty):", specialties)

if st.button("جلب أحدث الأبحاث"):
    st.info(f"جاري جلب أحدث الأبحاث في {selected}...")

    #بحث في PubMed
    search_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term={selected}+dental&retmode=json&retmax=5"
    response = requests.get(search_url).json()

    if 'esearchresult' in response and 'idlist' in response['esearchresult']:
        id_list = response['esearchresult']['idlist']
        if id_list:
            ids = ",".join(id_list)
            fetch_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id={ids}&retmode=xml"
            fetch_res = requests.get(fetch_url)
            root = ET.fromstring(fetch_res.content)

            for article in root.findall('.//PubmedArticle'):
                title = article.find('.//ArticleTitle')
                if title is not None:
                    title_text = title.text
                    st.subheader("العنوان الأصلي:")
                    st.write(title_text)
                    st.divider()
        else:
            st.write("لم يتم العثور على أبحاث حديثة.")