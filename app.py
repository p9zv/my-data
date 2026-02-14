# ==========================================================
# Arabic Data Cleaner PRO
# منصة احترافية لتنظيف وتوحيد البيانات العربية
# ==========================================================

import streamlit as st
import pandas as pd
import io
import re
from rapidfuzz import fuzz

st.set_page_config(page_title="منصة تنظيف البيانات", page_icon="📊", layout="wide")

# ==========================================================
# CSS واجهة احترافية
# ==========================================================
st.markdown("""
<style>
html, body, [data-testid="stAppViewContainer"]{
    direction: rtl;
    background:#020617;
    color:#e5e7eb;
}
.block-container{
    max-width:1100px;
    margin:auto;
}
h1,h2,h3{
    text-align:center;
}
.stButton>button{
    display:block;
    margin:auto;
    width:320px;
    height:48px;
    border-radius:14px;
    background:linear-gradient(90deg,#2563eb,#1d4ed8);
    color:white;
    font-weight:bold;
}
.stDownloadButton>button{
    display:block;
    margin:auto;
    width:350px;
    height:55px;
    border-radius:16px;
    background:linear-gradient(90deg,#16a34a,#22c55e);
    color:white;
    font-weight:bold;
}
</style>
""", unsafe_allow_html=True)

# ==========================================================
# محرك اللغة العربية (الأهم)
# ==========================================================

def normalize_arabic(text):
    if pd.isna(text):
        return ""
    text=str(text)

    # إزالة التشكيل
    text=re.sub(r'[\u0617-\u061A\u064B-\u0652]','',text)

    # توحيد الحروف
    text=re.sub('[إأآا]','ا',text)
    text=re.sub('ى','ي',text)
    text=re.sub('ؤ','و',text)
    text=re.sub('ئ','ي',text)
    text=re.sub('ة','ه',text)

    # حذف ال التعريف
    text=re.sub(r'\bال','',text)

    # حذف الرموز
    text=re.sub(r'[^\w\s]','',text)

    # مسافات
    text=re.sub(r'\s+',' ',text).strip()

    return text

def smart_similarity(a,b):
    a=normalize_arabic(a)
    b=normalize_arabic(b)

    words_a=set(a.split())
    words_b=set(b.split())

    # مقارنة الكلمات الأساسية
    intersection=len(words_a & words_b)
    union=len(words_a | words_b)

    if union==0:
        return 0

    word_similarity=intersection/union

    char_similarity=fuzz.ratio(a,b)/100

    return (word_similarity*0.7)+(char_similarity*0.3)

# ==========================================================
# العنوان
# ==========================================================
st.title("📊 منصة تنظيف وتوحيد البيانات العربية")

# ==========================================================
# رفع الملف
# ==========================================================
file=st.file_uploader("ارفع ملف Excel او CSV",type=["xlsx","csv"])

if "df" not in st.session_state:
    st.session_state.df=None
if "history" not in st.session_state:
    st.session_state.history=[]

def save_state():
    st.session_state.history.append(st.session_state.df.copy())

if file and st.session_state.df is None:
    if file.name.endswith(".csv"):
        st.session_state.df=pd.read_csv(file)
    else:
        st.session_state.df=pd.read_excel(file)

if st.session_state.df is None:
    st.info("⬆️ ارفع ملف للبدء")
    st.stop()

df=st.session_state.df

# ==========================================================
# البحث
# ==========================================================
st.subheader("البحث داخل الجدول")
search=st.text_input("اكتب كلمة للبحث")

view=df
if search:
    mask=df.astype(str).apply(lambda r:r.str.contains(search,case=False,na=False)).any(axis=1)
    view=df[mask]

st.dataframe(view,use_container_width=True)

# زر التراجع
if st.button("↩️ تراجع عن آخر عملية"):
    if st.session_state.history:
        st.session_state.df=st.session_state.history.pop()
        st.rerun()

st.divider()

# ==========================================================
# التوحيد الذكي
# ==========================================================
st.header("توحيد النصوص المتشابهة")

column=st.selectbox("اختر العمود",df.columns)

if st.button("فحص التكرارات"):

    values=df[column].dropna().astype(str).unique()

    groups=[]
    used=set()

    for val in values:
        if val in used:
            continue
        group=[val]
        used.add(val)

        for other in values:
            if other not in used:
                if smart_similarity(val,other)>0.78:
                    group.append(other)
                    used.add(other)

        if len(group)>1:
            groups.append(group)

    if not groups:
        st.success("لا توجد اختلافات كبيرة")
    else:
        for i,g in enumerate(groups):
            st.write("تم العثور على النصوص التالية:")
            st.code(g)

            canonical=st.text_input(f"اكتب النص المعتمد للمجموعة {i+1}",key=f"canon{i}")

            if st.button(f"تطبيق {i+1}",key=f"apply{i}"):
                save_state()
                for word in g:
                    st.session_state.df[column]=st.session_state.df[column].astype(str).str.replace(word,canonical,regex=False)
                st.success("تم التوحيد")
                st.rerun()

# ==========================================================
# حذف أعمدة
# ==========================================================
st.header("حذف أعمدة")
cols=st.multiselect("اختر الأعمدة",df.columns)
if st.button("تنفيذ حذف الأعمدة"):
    if cols:
        save_state()
        st.session_state.df.drop(columns=cols,inplace=True)
        st.rerun()

# ==========================================================
# استبدال شامل
# ==========================================================
st.header("استبدال شامل داخل عمود")

col2=st.selectbox("العمود",df.columns,key="replace")
old=st.text_input("القيمة القديمة")
new=st.text_input("القيمة الجديدة")

if st.button("تنفيذ الاستبدال"):
    save_state()
    st.session_state.df[col2]=st.session_state.df[col2].astype(str).str.replace(old,new,regex=False)
    st.success("تم الاستبدال")
    st.rerun()

# ==========================================================
# تحميل
# ==========================================================
output=io.BytesIO()
with pd.ExcelWriter(output,engine="xlsxwriter") as writer:
    st.session_state.df.to_excel(writer,index=False)

st.download_button("⬇️ تحميل الملف بعد التنظيف",output.getvalue(),"cleaned_data.xlsx")

st.divider()

# ==========================================================
# مشاركة وحقوق
# ==========================================================
st.markdown("""
### مشاركة الموقع
- واتساب: https://wa.me/?text=جرب%20منصة%20تنظيف%20البيانات
- تويتر: https://twitter.com/intent/tweet?text=منصة%20تنظيف%20البيانات
- تيك توك: https://www.tiktok.com

---
© 2026 منصة تنظيف البيانات العربية - جميع الحقوق محفوظة
""")
