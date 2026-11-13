
import streamlit as st
import requests
import xml.etree.ElementTree as ET

# إعداد الصفحة
st.set_page_config(
    page_title="Dental Research Tracker",
    page_icon="🦷",
    layout="wide"
)

st.title("🦷 أحدث الأبحاث العلمية في طب الأسنان")
st.write("منصة للبحث عن أحدث الدراسات والأبحاث العلمية في طب الأسنان.")

# مفتاح PubMed اختياري
PUBMED_API_KEY = st.secrets.get("PUBMED_API_KEY", "")

# التخصصات
specialties = [
    "Orthodontics",
    "Implantology",
    "Oral Surgery",
    "Endodontics",
    "Periodontics",
    "Prosthodontics",
    "Pediatric Dentistry"
]

selected = st.selectbox(
    "اختر التخصص (Specialty):",
    specialties
)

# عدد الأبحاث
number_of_articles = st.selectbox(
    "عدد الأبحاث المطلوب عرضها:",
    [5, 10, 15, 20, 30, 50]
)


# استخراج تاريخ النشر
def get_publication_date(article):

    # محاولة الحصول على تاريخ النشر الإلكتروني
    article_date = article.find(
        ".//ArticleDate"
    )

    if article_date is not None:
        year = article_date.findtext("Year", "")
        month = article_date.findtext("Month", "")
        day = article_date.findtext("Day", "")

        if year:
            return " - ".join(
                part for part in [day, month, year] if part
            )

    # تاريخ النشر في المجلة
    pub_date = article.find(
        ".//JournalIssue/PubDate"
    )

    if pub_date is not None:

        year = pub_date.findtext("Year", "")
        month = pub_date.findtext("Month", "")
        day = pub_date.findtext("Day", "")

        # بعض الأبحاث تستخدم MedlineDate
        medline_date = pub_date.findtext(
            "MedlineDate", ""
        )

        if year:
            return " - ".join(
                part for part in [day, month, year] if part
            )

        if medline_date:
            return medline_date

    return "تاريخ النشر غير متوفر"


# جلب الأبحاث
if st.button("🔍 جلب أحدث الأبحاث"):

    with st.spinner(
        f"جاري جلب أحدث الأبحاث في {selected}..."
    ):

        try:

            # البحث في PubMed
            search_url = (
                "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
            )

            params = {
                "db": "pubmed",
                "term": f"{selected} dental",
                "retmode": "json",
                "retmax": number_of_articles,
                "sort": "pub date"
            }

            if PUBMED_API_KEY:
                params["api_key"] = PUBMED_API_KEY

            response = requests.get(
                search_url,
                params=params,
                timeout=30
            )

            response.raise_for_status()

            search_data = response.json()

            id_list = search_data.get(
                "esearchresult", {}
            ).get("idlist", [])

            if not id_list:

                st.warning(
                    "لم يتم العثور على أبحاث لهذا التخصص."
                )

            else:

                ids = ",".join(id_list)

                # جلب تفاصيل الأبحاث
                fetch_url = (
                    "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
                )

                fetch_params = {
                    "db": "pubmed",
                    "id": ids,
                    "retmode": "xml"
                }

                if PUBMED_API_KEY:
                    fetch_params["api_key"] = PUBMED_API_KEY

                fetch_response = requests.get(
                    fetch_url,
                    params=fetch_params,
                    timeout=30
                )

                fetch_response.raise_for_status()

                root = ET.fromstring(
                    fetch_response.content
                )

                articles = root.findall(
                    ".//PubmedArticle"
                )

                st.success(
                    f"تم العثور على {len(articles)} بحث علمي."
                )

                # عرض الأبحاث
                for index, article in enumerate(
                    articles, 1
                ):

                    title_element = article.find(
                        ".//ArticleTitle"
                    )

                    if title_element is None:
                        continue

                    title_text = "".join(
                        title_element.itertext()
                    ).strip()

                    if not title_text:
                        continue

                    # تاريخ النشر
                    publication_date = get_publication_date(
                        article
                    )

                    # اسم المجلة
                    journal = article.findtext(
                        ".//Journal/Title",
                        "غير متوفر"
                    )

                    # رقم PubMed
                    pmid = article.findtext(
                        ".//PMID",
                        ""
                    )

                    st.divider()

                    st.subheader(
                        f"البحث رقم {index}"
                    )

                    st.markdown("### العنوان الأصلي:")
                    st.write(title_text)

                    st.markdown("### تاريخ النشر:")
                    st.info(publication_date)

                    st.markdown("### المجلة العلمية:")
                    st.write(journal)

                    if pmid:
                        st.markdown("### رابط البحث:")
                        st.link_button(
                            "فتح البحث في PubMed",
                            f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
                        )

        except requests.exceptions.Timeout:

            st.error(
                "انتهت مهلة الاتصال. يرجى المحاولة مرة أخرى."
            )

        except requests.exceptions.RequestException as e:

            st.error(
                f"حدث خطأ في الاتصال بـ PubMed: {e}"
            )

        except ET.ParseError:

            st.error(
                "حدث خطأ أثناء قراءة بيانات الأبحاث."
            )

        except Exception as e:

            st.error(
                f"حدث خطأ غير متوقع: {e}"
            )
