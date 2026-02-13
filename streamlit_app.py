import streamlit as st
import pandas as pd
import io
import streamlit.components.v1 as components
from rapidfuzz import fuzz
from st_aggrid import AgGrid, GridOptionsBuilder

# ---------------- الصفحة ----------------
st.set_page_config(page_title="PRO DATA ANALYZER", page_icon="💎", layout="wide")

# تحميل FontAwesome (يعمل على Streamlit Cloud)
components.html("""
<link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
""", height=0)

# ---------------- تصميم احترافي ----------------
st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');

html, body, [data-testid="stAppViewContainer"]{
    background: radial-gradient(circle at 20% 20%, #020617, #000000 70%);
    color:#e5e7eb;
    font-family:'Cairo',sans-serif !important;
    direction:rtl;
}

.main-box{
    background:#020617;
    border:1px solid #1f2937;
    border-radius:25px;
    padding:30px;
}

.stats-card{
    background:#0f172a;
    border:1px solid #1f2937;
    border-radius:20px;
    padding:25px;
    margin-top:20px;
}

h1,h2,h3,label,p{color:#e5e7eb !important;}

</style>
""", unsafe_allow_html=True)

# ---------------- session ----------------
if "df" not in st.session_state:
    st.session_state.df=None

if "history" not in st.session_state:
    st.session_state.history=[]

if "file" not in st.session_state:
    st.session_state.file=None

def record():
    if st.session_state.df is not None:
        st.session_state.history.append(st.session_state.df.copy())
        if len(st.session_state.history)>20:
            st.session_state.history.pop(0)

# ---------------- العنوان ----------------
st.markdown("<h1><i class='fas fa-chart-line'></i> PRO DATA ANALYZER</h1>",unsafe_allow_html=True)

uploaded=st.file_uploader("📂 ارفع ملف Excel أو CSV",type=["xlsx","csv"])

# ---------------- قراءة الملف ----------------
if uploaded is not None and uploaded.name!=st.session_state.file:
    try:
        if uploaded.name.endswith(".csv"):
            st.session_state.df=pd.read_csv(uploaded)
        else:
            st.session_state.df=pd.read_excel(uploaded)

        st.session_state.file=uploaded.name
        st.session_state.history=[]
    except Exception as e:
        st.error(e)

# ---------------- عند وجود بيانات ----------------
if st.session_state.df is not None:

    df=st.session_state.df

    # أدوات أعلى
    c1,c2=st.columns(2)

    with c1:
        if st.button("↩️ تراجع"):
            if st.session_state.history:
                st.session_state.df=st.session_state.history.pop()
                st.rerun()

    with c2:
        buffer=io.BytesIO()
        df.to_excel(buffer,index=False)
        st.download_button("📥 تصدير Excel",buffer.getvalue(),"Pro_Data.xlsx")

    # ---------------- البحث ----------------
    st.markdown("### 🔎 البحث داخل البيانات")
    search=st.text_input("اكتب كلمة للبحث")

    if search:
        mask=df.astype(str).apply(lambda col: col.str.contains(search,case=False,na=False))
        filtered_df=df[mask.any(axis=1)].copy()
    else:
        filtered_df=df.copy()

    filtered_df.reset_index(drop=True,inplace=True)

    # ---------------- تحليل التكرارات ----------------
    st.markdown("### 📊 تحليل التكرار")
    analyze_col=st.selectbox("اختر عمود للتحليل",filtered_df.columns)

    series=filtered_df[analyze_col].astype(str).str.strip()
    series=series.replace("", "فارغ")
    series=series.fillna("فارغ")

    counts=series.value_counts().reset_index()
    counts.columns=["القيمة","عدد التكرارات"]

    st.dataframe(counts,use_container_width=True,hide_index=True)

    # ---------------- كشف التشابه ----------------
    st.markdown("### 🔍 كشف النصوص المتشابهة")

    sim_col=st.selectbox("اختر عمود فحص التشابه",filtered_df.columns,key="similar")

    values=filtered_df[sim_col].dropna().astype(str).unique()
    similar_pairs=[]

    for i in range(len(values)):
        for j in range(i+1,len(values)):
            ratio=fuzz.ratio(values[i],values[j])
            if ratio>=85:
                similar_pairs.append((values[i],values[j],ratio))

    if similar_pairs:
        sim_df=pd.DataFrame(similar_pairs,columns=["النص الأول","النص الثاني","نسبة التشابه"])
        st.dataframe(sim_df,use_container_width=True,hide_index=True)
    else:
        st.success("لا يوجد نصوص متشابهة")

    # ---------------- الجدول التفاعلي ----------------
    st.markdown("<h3><i class='fas fa-table'></i> مدير الأعمدة التفاعلي</h3>",unsafe_allow_html=True)

    gb=GridOptionsBuilder.from_dataframe(filtered_df)
    gb.configure_default_column(editable=False,filter=True,sortable=True,resizable=True)
    gb.configure_side_bar()
    grid_options=gb.build()

    AgGrid(
        filtered_df,
        gridOptions=grid_options,
        theme="alpine-dark",
        height=500,
        fit_columns_on_grid_load=True
    )

    # ---------------- حذف أعمدة ----------------
    st.markdown("### 🗑️ حذف أعمدة")

    selected_cols=st.multiselect("اختر الأعمدة التي تريد حذفها",filtered_df.columns)

    if st.button("حذف الأعمدة المحددة"):
        if selected_cols:
            record()
            st.session_state.df.drop(columns=selected_cols,inplace=True)
            st.rerun()
        else:
            st.warning("لم يتم اختيار أعمدة")

    # ---------------- الأعمدة الفارغة ----------------
    if st.button("📉 إظهار الأعمدة الفارغة"):
        empty_cols=[col for col in df.columns if df[col].isna().all()]
        if empty_cols:
            st.info(empty_cols)
        else:
            st.success("لا يوجد أعمدة فارغة بالكامل")
