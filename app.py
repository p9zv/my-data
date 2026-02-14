# ======================================================
# Arabic Data Cleaner PRO (Final Working Version)
# توحيد عربي حقيقي + قوائم منسدلة + تطبيق فعلي
# ======================================================

import streamlit as st
import pandas as pd
import io
import re
from rapidfuzz import fuzz
st.set_page_config(
    page_title="محلل ومنظف ملفات اكسل",
    page_icon="📊",
    layout="wide"
)

st.markdown('<meta name="google-site-verification" content="kdYmC-Gk08HXb0lYrjANPExaGbPf9zbnQt4OklBDVew" />', unsafe_allow_html=True)
# ================= CSS =================
st.markdown("""
<style>
html, body, [data-testid="stAppViewContainer"]{
    direction: rtl;
    background:#020617;
    color:#e5e7eb;
}
.block-container{max-width:1100px;margin:auto;}
h1,h2,h3{text-align:center;}

.stButton>button{
    display:block;
    margin:auto;
    width:300px;
    height:48px;
    border-radius:14px;
    background:linear-gradient(90deg,#2563eb,#1d4ed8);
    color:white;
    font-weight:bold;
}

.stDownloadButton>button{
    display:block;
    margin:auto;
    width:340px;
    height:55px;
    border-radius:16px;
    background:linear-gradient(90deg,#16a34a,#22c55e);
    color:white;
    font-weight:bold;
}
</style>
""", unsafe_allow_html=True)

# ================= محرك العربية =================
def normalize_arabic(text):
    if pd.isna(text):
        return ""
    text=str(text)

    text=re.sub(r'[\u0617-\u061A\u064B-\u0652]','',text)
    text=re.sub('[إأآا]','ا',text)
    text=re.sub('ى','ي',text)
    text=re.sub('ؤ','و',text)
    text=re.sub('ئ','ي',text)
    text=re.sub('ة','ه',text)
    text=re.sub(r'\bال','',text)
    text=re.sub(r'[^\w\s]','',text)
    text=re.sub(r'\s+',' ',text).strip()

    return text

def smart_similarity(a,b):
    a=normalize_arabic(a)
    b=normalize_arabic(b)

    words_a=set(a.split())
    words_b=set(b.split())

    inter=len(words_a & words_b)
    union=len(words_a | words_b)

    if union==0:
        return 0

    word_ratio=inter/union
    char_ratio=fuzz.ratio(a,b)/100

    return (word_ratio*0.7)+(char_ratio*0.3)

# ================= Session =================
if "df" not in st.session_state:
    st.session_state.df=None
if "history" not in st.session_state:
    st.session_state.history=[]

def save_state():
    st.session_state.history.append(st.session_state.df.copy())

# ================= رفع الملف =================
st.title("📊 منصة تنظيف وتوحيد البيانات العربية")

file=st.file_uploader("ارفع ملف Excel او CSV",type=["xlsx","csv"])

if file and st.session_state.df is None:
    if file.name.endswith(".csv"):
        st.session_state.df=pd.read_csv(file)
    else:
        st.session_state.df=pd.read_excel(file)

if st.session_state.df is None:
    st.info("⬆️ ارفع ملف للبدء")
    st.stop()

df=st.session_state.df

# ================= البحث =================
st.subheader("البحث داخل الجدول")
search=st.text_input("اكتب كلمة للبحث")

view=df
if search:
    mask=df.astype(str).apply(lambda r:r.str.contains(search,case=False,na=False)).any(axis=1)
    view=df[mask]

st.dataframe(view,use_container_width=True)

if st.button("↩️ تراجع عن آخر عملية"):
    if st.session_state.history:
        st.session_state.df=st.session_state.history.pop()
        st.rerun()

st.divider()

# =================================================
# توحيد النصوص (القائمة المنسدلة)
# =================================================
with st.expander("🧠 توحيد النصوص المتشابهة", expanded=False):

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

        st.session_state.groups=groups

    if "groups" in st.session_state:

        for i,g in enumerate(st.session_state.groups):

            st.write("القيم المتشابهة:")
            st.code(g)

            canonical=st.text_input("النص المعتمد",key=f"canon{i}")

            if st.button("تطبيق التوحيد",key=f"apply{i}"):

                save_state()

                # التوحيد الحقيقي (خلية خلية)
                new_column=[]
                for cell in st.session_state.df[column]:

                    replaced=False
                    for word in g:
                        if smart_similarity(cell,word)>0.80:
                            new_column.append(canonical)
                            replaced=True
                            break

                    if not replaced:
                        new_column.append(cell)

                st.session_state.df[column]=new_column
                st.success("تم توحيد القيم بنجاح")
                st.rerun()

# =================================================
# حذف الأعمدة
# =================================================
with st.expander("🧹 حذف أعمدة"):

    cols=st.multiselect("اختر الأعمدة المراد حذفها",df.columns)

    if st.button("تنفيذ الحذف"):
        if cols:
            save_state()
            st.session_state.df.drop(columns=cols,inplace=True)
            st.success("تم حذف الأعمدة")
            st.rerun()

# =================================================
# استبدال شامل
# =================================================
with st.expander("🔁 استبدال شامل داخل عمود"):

    col2=st.selectbox("العمود",df.columns,key="replace")
    old=st.text_input("القيمة القديمة")
    new=st.text_input("القيمة الجديدة")

    if st.button("تنفيذ الاستبدال"):
        save_state()

        st.session_state.df[col2]=[
            new if str(x)==old else x
            for x in st.session_state.df[col2]
        ]

        st.success("تم الاستبدال")
        st.rerun()

# ================= تحميل =================
output=io.BytesIO()
with pd.ExcelWriter(output,engine="xlsxwriter") as writer:
    st.session_state.df.to_excel(writer,index=False)

st.download_button(
    label="⬇️ تحميل الملف بعد التنظيف",
    data=output.getvalue(),
    file_name="cleaned_data.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
                   # =====================================================
# Footer + مشاركة + تواصل مع المطور
# =====================================================

st.markdown("---")

APP_URL = "https://my-data-p9zv-anl.streamlit.app"
EMAIL = "a7traf92@gmail.com"

st.markdown(f"""
<div style="text-align:center; padding:30px">

<h2>💙 أعجبك الموقع؟ ساعدنا بنشره</h2>
<p style="color:#94a3b8">مشاركتك تساعد الآخرين في تنظيف بياناتهم بسهولة</p>

<br>

<a href="https://wa.me/?text=جرب هذه الأداة المجانية لتنظيف ملفات الإكسل {APP_URL}" target="_blank">
<img src="https://cdn-icons-png.flaticon.com/512/733/733585.png" width="55">
</a>

&nbsp;&nbsp;&nbsp;

<a href="https://www.instagram.com/" target="_blank">
<img src="https://cdn-icons-png.flaticon.com/512/2111/2111463.png" width="55">
</a>

&nbsp;&nbsp;&nbsp;

<a href="https://www.tiktok.com/" target="_blank">
<img src="https://cdn-icons-png.flaticon.com/512/3046/3046121.png" width="55">
</a>

<br><br><br>

<h3>📩 تواصل مع المطور</h3>

<a href="mailto:{EMAIL}?subject=استفسار حول منصة تنظيف البيانات&body=مرحباً، أرغب بالاستفسار عن الموقع">
<button style="
background: linear-gradient(90deg,#f59e0b,#f97316);
border:none;
color:white;
padding:14px 28px;
border-radius:14px;
font-size:16px;
cursor:pointer;
">
راسل المطور
</button>
</a>

<p style="margin-top:10px; color:#94a3b8">{EMAIL}</p>

<br>

<p style="font-size:13px; color:#64748b">
© 2026 منصة تنظيف البيانات العربية<br>
تم تطوير هذه الأداة لمساعدة الباحثين والشركات على توحيد البيانات قبل رفعها إلى Google و Excel و CRM
</p>

</div>
""", unsafe_allow_html=True)
