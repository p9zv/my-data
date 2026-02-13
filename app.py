import streamlit as st
import pandas as pd
import io
import streamlit.components.v1 as components

# ---------------- إعداد الصفحة ----------------
st.set_page_config(page_title="PRO DATA ANALYZER", page_icon="💎", layout="wide")

# ---------------- CSS + Icons ----------------
st.markdown("""
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');

html, body, [data-testid="stAppViewContainer"] {
    direction: rtl;
    text-align: right;
    font-family: 'Cairo', sans-serif !important;
    background: #030712 !important;
}

.main-glass-box {
    background: rgba(31, 41, 55, 0.4);
    backdrop-filter: blur(15px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 28px;
    padding: 30px;
    margin-bottom: 25px;
}

.buttons-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 15px;
    background: rgba(15, 23, 42, 0.6);
    padding: 20px;
    border-radius: 20px;
    border: 1px solid rgba(255,255,255,0.05);
    margin-bottom: 25px;
}

div[data-testid="column"]:nth-of-type(1) button { background: #6366f1 !important; }
div[data-testid="column"]:nth-of-type(2) button { background: #ef4444 !important; }
div[data-testid="column"]:nth-of-type(3) button { background: #f59e0b !important; color:#111827 !important;}
div[data-testid="column"]:nth-of-type(4) button { background: #3b82f6 !important; }

.stButton>button {
    border-radius: 14px !important;
    height: 75px !important;
    font-weight: 700 !important;
    width: 100%;
    border: none !important;
    font-size: 1.1rem !important;
    color: white !important;
}

.stats-card {
    background: rgba(17, 24, 39, 0.85);
    border-right: 5px solid #6366f1;
    padding: 25px;
    border-radius: 18px;
    margin: 20px 0;
    border: 1px solid rgba(255,255,255,0.1);
}

h1, h2, h3, p, label { color: #f8fafc !important; }
</style>
""", unsafe_allow_html=True)

# ---------------- Session State ----------------
if 'df' not in st.session_state:
    st.session_state.df = None

if 'history' not in st.session_state:
    st.session_state.history = []

if 'loaded_file' not in st.session_state:
    st.session_state.loaded_file = None

def record():
    """حفظ نسخة للتراجع"""
    if st.session_state.df is not None:
        st.session_state.history.append(st.session_state.df.copy())
        if len(st.session_state.history) > 20:
            st.session_state.history.pop(0)

# ---------------- واجهة ----------------
st.markdown('<div class="main-glass-box">', unsafe_allow_html=True)
st.markdown("<h1 style='text-align:center;'><i class='fas fa-shield-halved'></i> المحلل الذكي الاحترافي</h1>", unsafe_allow_html=True)

uploaded_file = st.file_uploader("📂 ارفع ملف Excel أو CSV", type=["xlsx", "csv"])

# -------- قراءة الملف بشكل صحيح --------
if uploaded_file is not None:
    if st.session_state.loaded_file != uploaded_file.name:
        try:
            if uploaded_file.name.endswith(".csv"):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)

            st.session_state.df = df
            st.session_state.loaded_file = uploaded_file.name
            st.session_state.history = []

        except Exception as e:
            st.error(f"خطأ في قراءة الملف: {e}")

# ---------------- في حال وجود بيانات ----------------
if st.session_state.df is not None:

    df = st.session_state.df

    # أدوات أعلى الصفحة
    c1, c2 = st.columns(2)

    with c1:
        if st.button("↩️ تراجع"):
            if st.session_state.history:
                st.session_state.df = st.session_state.history.pop()
                st.rerun()

    with c2:
        buffer = io.BytesIO()
        df.to_excel(buffer, index=False)
        st.download_button("📥 تصدير Excel", buffer.getvalue(), "Pro_Data.xlsx")

    # ---------------- الأزرار ----------------
    st.markdown('<div class="buttons-grid">', unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)

    # استبدال
    with col1:
        with st.popover("🔄 استبدال القيم"):
            old = st.text_input("القيمة القديمة")
            new = st.text_input("القيمة الجديدة")

            if st.button("تنفيذ الاستبدال"):
                record()
                st.session_state.df = st.session_state.df.applymap(
                    lambda x: new if str(x) == old else x
                )
                st.rerun()

    # حذف الأعمدة
    with col2:
        with st.popover("🗑️ حذف أعمدة"):
            cols = st.multiselect("اختر الأعمدة", df.columns)
            if st.button("تأكيد الحذف"):
                record()
                st.session_state.df.drop(columns=cols, inplace=True)
                st.rerun()

    # إزالة التكرار
    with col3:
        with st.popover("📑 إزالة التكرار"):
            st.write("عدد الصفوف المكررة:", df.duplicated().sum())
            if st.button("حذف المكرر"):
                record()
                st.session_state.df = st.session_state.df.drop_duplicates().reset_index(drop=True)
                st.rerun()

    # تحليل عمود
    with col4:
        analyze_col = st.selectbox("📊 تحليل عمود", df.columns)

    st.markdown('</div>', unsafe_allow_html=True)

    # ---------------- الفلترة ----------------
    st.markdown('<div class="stats-card">', unsafe_allow_html=True)

    search = st.text_input("🔎 بحث داخل الجدول")

    filtered_df = df.copy()

    if search:
        filtered_df = filtered_df[
            filtered_df.apply(lambda r: r.astype(str).str.contains(search, case=False).any(), axis=1)
        ]

    # -------- تحليل التكرار الصحيح --------
    if analyze_col in filtered_df.columns:
        counts = (
            filtered_df[analyze_col]
            .astype(str)
            .fillna("فارغ")
            .value_counts(dropna=False)
            .reset_index()
        )

        counts.columns = ["القيمة", "عدد التكرارات"]

        st.markdown(
            f"<h3><i class='fas fa-chart-column'></i> أكثر القيم تكراراً في ({analyze_col})</h3>",
            unsafe_allow_html=True
        )

        st.dataframe(counts.head(10), use_container_width=True, hide_index=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # ---------------- عرض الجدول ----------------
    st.markdown("### <i class='fas fa-table'></i> استعراض البيانات", unsafe_allow_html=True)
    st.dataframe(filtered_df, use_container_width=True, hide_index=True)

st.markdown('</div>', unsafe_allow_html=True)

# ---------------- تحسين ضغط الأزرار ----------------
components.html("""
<script>
const buttons = window.parent.document.querySelectorAll('button');
buttons.forEach(btn => {
    btn.addEventListener('mousedown', () => btn.style.transform = 'scale(0.96)');
    btn.addEventListener('mouseup', () => btn.style.transform = 'scale(1)');
});
</script>
""", height=0)
