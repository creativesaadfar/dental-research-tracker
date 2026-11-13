import streamlit as st
import requests
import xml.etree.ElementTree as ET
import deepl

st.set_page_config(page_title="Dental Research Tracker", page_icon="🦷", layout="wide")
st.title("🦷 أحدث الأبحاث العلمية في طب الأسنان")

# قراءة مفاتيح API من st.secrets (آمن - لا تُخزن في الكود)
DEEPL_API_KEY = st.secrets.get("DEEPL_API_KEY", "")
PUBMED_API_KEY = st.secrets.get("PUBMED_API_KEY", "")

# إعداد المترجم
translator = deepl.Translator(DEEPL_API_KEY) if DEEPL_API_KEY else None

specialties = ["Orthodontics", "Implantology", "Oral Surgery", "Endodontics", "Periodontics", "Prosthodontics", "Pediatric Dentistry"]
selected = st.selectbox("اختر التخصص (Specialty):", specialties)

if st.button("جلب أحدث الأبحاث"):
    if not translator:
        st.warning("تحذير: مفتاح DeepL غير مفعل بعد.")
    else:
        st.info(f"جاري جلب أحدث الأبحاث في {selected}...")
        
        # بحث في PubMed
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
                        
                        try:
                            translated_title = translator.translate_text(title_text, target_lang="AR").text
                            st.subheader("الترجمة العربية:")
                            st.write(translated_title)
                        except Exception as e:
                            st.error("لم يتم تكوين الترجمة بشكل صحيح بعد.")
                        st.divider()
            else:
                st.write("لم يتم العثور على أبحاث حديثة.")