import streamlit as st
import pandas as pd
import io
from difflib import SequenceMatcher

# 1. إعدادات الصفحة
st.set_page_config(page_title="Excel Advanced Processor", page_icon="📊", layout="wide")

# 2. إدارة الوضع (الداكن/الفاتح)
if 'theme' not in st.session_state:
    st.session_state.theme = 'light'

def toggle_theme():
    st.session_state.theme = 'dark' if st.session_state.theme == 'light' else 'light'

# 3. تعريف مصفوفة الألوان الدقيقة لكل وضع
if st.session_state.theme == 'light':
    bg_color = "#FFFFFF"      # خلفية الصفحة
    text_main = "#1E293B"     # النص الأساسي (كحلي غامق)
    card_bg = "#F1F5F9"       # خلفية البطاقات والأزرار الثانوية
    border_col = "#E2E8F0"    # الحدود
    table_bg = "#FFFFFF"      # خلفية الجدول
else:
    bg_color = "#0F172A"      # خلفية الصفحة (كحلي ليلي)
    text_main = "#F8FAFC"     # النص الأساسي (أبيض ناصع)
    card_bg = "#1E293B"       # خلفية البطاقات (كحلي متوسط)
    border_col = "#334155"    # الحدود
    table_bg = "#1E293B"      # خلفية الجدول

# 4. تطبيق CSS الموحد
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap');
    
    /* تثبيت خلفية التطبيق بالكامل */
    .stApp {{
        background-color: {bg_color} !important;
        color: {text_main} !important;
        font-family: 'Cairo', sans-serif;
    }}

    /* الهيدر الرئيسي */
    .main-header {{
        background-color: {card_bg};
        padding: 25px;
        border-radius: 20px;
        text-align: center;
        border: 1px solid {border_col};
        margin-bottom: 25px;
    }}

    /* الألوان الثابتة للأزرار حسب طلبك (لا تتغير بتغير الثيم لتظل مميزة) */
    div[data-testid="column"]:nth-of-type(1) button {{ background-color: #6c5ce7 !important; color: white !important; }} /* بنفسجي */
    div[data-testid="column"]:nth-of-type(2) button {{ background-color: #ff7675 !important; color: white !important; }} /* أحمر */
    div[data-testid="column"]:nth-of-type(3) button {{ background-color: #fdcb6e !important; color: white !important; }} /* أصفر */
    div[data-testid="column"]:nth-of-type(4) button {{ background-color: #74b9ff !important; color: white !important; }} /* أزرق */
    
    .stButton>button {{
        border-radius: 12px !important;
        font-weight: 700 !important;
        height: 55px !important;
        border: none !important;
    }}

    /* زر التصدير الأخضر */
    .export-btn button {{ background-color: #00b894 !important; color: white !important; }}

    /* تحسين شكل الجداول والمدخلات في الوضعين */
    div[data-testid="stDataFrame"] {{ background-color: {table_bg} !important; border: 1px solid {border_col}; }}
    input, select, textarea {{ 
        background-color: {table_bg} !important; 
        color: {text_main} !important; 
        border: 1px solid {border_col} !important; 
    }}

    h1, h2, h3, h4, p, label, span {{ color: {text_main} !important; }}
    </style>
    """, unsafe_allow_html=True)

# 5. الدوال المنطقية
def are_similar(str1, str2, threshold=0.75):
    s1 = str(str1).strip().lower().replace("أ", "ا").replace("إ", "ا").replace("ة", "ه")
    s2 = str(str2).strip().lower().replace("أ", "ا").replace("إ", "ا").replace("ة", "ه")
    return SequenceMatcher(None, s1, s2).ratio() > threshold

if 'df' not in st.session_state: st.session_state.df = None
if 'history' not in st.session_state: st.session_state.history = []

def save_step():
    st.session_state.history.append(st.session_state.df.copy())
    if len(st.session_state.history) > 15: st.session_state.history.pop(0)

# --- الواجهة ---

# زر التبديل في الأعلى بشكل أنيق
c_mode1, c_mode2 = st.columns([8, 2])
with c_mode2:
    mode_icon = "☀️" if st.session_state.theme == 'dark' else "🌙"
    if st.button(f"{mode_icon} تبديل"):
        toggle_theme()
        st.rerun()

st.markdown(f"""
    <div class="main-header">
        <h1 style="margin:0;">📊 محلل البيانات المتقدم</h1>
        <p style="opacity: 0.8;">تحكم كامل ببياناتك بذكاء وسهولة</p>
    </div>
    """, unsafe_allow_html=True)

uploaded_file = st.file_uploader("ارفع الملف (Excel/CSV)", type=["xlsx", "csv"])

if uploaded_file:
    if st.session_state.df is None:
        st.session_state.df = pd.read_excel(uploaded_file) if not uploaded_file.name.endswith('.csv') else pd.read_csv(uploaded_file)
        save_step()

    df = st.session_state.df

    # لوحة التحكم
    col1, col2 = st.columns(2)
    col3, col4 = st.columns(2)
    
    with col1:
        with st.popover("🔄 استبدال"):
            old = st.text_input("القيمة القديمة")
            new = st.text_input("القيمة الجديدة")
            if st.button("تحديث"):
                save_step(); st.session_state.df.replace(old, new, inplace=True); st.rerun()
    
    with col2:
        with st.popover("🗑️ حذف أعمدة"):
            to_del = st.multiselect("اختر الأعمدة:", df.columns)
            if st.button("حذف الآن"):
                save_step(); st.session_state.df.drop(columns=to_del, inplace=True); st.rerun()

    with col3:
        with st.popover("🔍 نصوص مشابهة"):
            target = st.selectbox("العمود المستهدف:", df.columns)
            vals = df[target].dropna().unique().astype(str)
            found = False
            for i, v1 in enumerate(vals[:15]):
                group = [v1] + [v2 for v2 in vals[i+1:i+10] if are_similar(v1, v2)]
                if len(group) > 1:
                    found = True
                    st.write(f"تشابه: {', '.join(group)}")
                    new_n = st.text_input(f"توحيد لـ {v1}:", value=v1, key=v1)
                    if st.button(f"تثبيت {v1}"):
                        save_step(); st.session_state.df[target].replace(group, new_n, inplace=True); st.rerun()
            if not found: st.write("لا يوجد تشابه حالياً")

    with col4:
        with st.popover("📑 المتكررات"):
            st.write(f"الصفوف المتكررة بالكامل: {df.duplicated().sum()}")
            if st.button("إزالة كافة التكرارات"):
                save_step(); st.session_state.df.drop_duplicates(inplace=True); st.rerun()

    st.markdown('<div class="export-btn">', unsafe_allow_html=True)
    out = io.BytesIO()
    with pd.ExcelWriter(out, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    st.download_button("📥 تصدير النتائج", data=out.getvalue(), file_name="Cleaned.xlsx", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.divider()

    # الإحصائيات والمعاينة
    st.write(f"**عدد الصفوف:** {df.shape[0]} | **عدد الأعمدة:** {df.shape[1]}")
    st.dataframe(df, use_container_width=True, hide_index=True)
