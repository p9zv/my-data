import streamlit as st
import pandas as pd
import io
from difflib import SequenceMatcher

# 1. إعدادات الصفحة
st.set_page_config(page_title="Excel Advanced Processor", page_icon="📊", layout="wide")

# 2. تصميم CSS مستوحى من الصورة (ألوان زاهية وواجهة نظيفة)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Cairo', sans-serif; text-align: right; direction: rtl; }
    
    /* تصميم البطاقة العلوية */
    .main-header {
        background: white; padding: 30px; border-radius: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05); text-align: center;
        margin-bottom: 25px; border: 1px solid #e0e0e0;
    }
    
    /* أزرار لوحة التحكم */
    .stButton>button { border-radius: 12px !important; font-weight: 700 !important; height: 60px !important; border: none !important; color: white !important; }
    
    /* تخصيص ألوان الأزرار حسب الطلب */
    div[data-testid="column"]:nth-of-type(1) .stButton>button { background: #6c5ce7 !important; } /* استبدال */
    div[data-testid="column"]:nth-of-type(2) .stButton>button { background: #ff7675 !important; } /* حذف */
    div[data-testid="column"]:nth-of-type(3) .stButton>button { background: #fdcb6e !important; } /* نصوص متشابهة */
    div[data-testid="column"]:nth-of-type(4) .stButton>button { background: #74b9ff !important; } /* متكررات */
    .export-btn button { background: #00b894 !important; height: 50px !important; } /* تصدير */

    /* إحصائيات الملف */
    .file-info { color: #636e72; font-weight: 600; font-size: 0.9rem; margin-top: 10px; }
    </style>
    """, unsafe_allow_html=True)

# 3. الدوال البرمجية
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
st.markdown("""
    <div class="main-header">
        <h1 style='color: #4834d4;'>📊 محلل ملفات Excel المتقدم</h1>
        <p>أداة شاملة لقراءة وتحليل وتعديل ملفات Excel</p>
    </div>
    """, unsafe_allow_html=True)

uploaded_file = st.file_uploader("", type=["xlsx", "csv"])

if uploaded_file:
    if st.session_state.df is None:
        st.session_state.df = pd.read_excel(uploaded_file) if not uploaded_file.name.endswith('.csv') else pd.read_csv(uploaded_file)
        save_step()

    df = st.session_state.df

    # لوحة الأزرار الملونة (نفس ترتيب الصورة)
    col1, col2 = st.columns(2)
    col3, col4 = st.columns(2)
    
    with col1:
        replace_clicked = st.button("🔄 استبدال", use_container_width=True)
    with col2:
        delete_clicked = st.button("🗑️ حذف المحدد", use_container_width=True)
    with col3:
        similar_clicked = st.button("🔍 النصوص المتشابهة", use_container_width=True)
    with col4:
        dup_clicked = st.button("📑 المتكررات", use_container_width=True)
    
    st.markdown('<div class="export-btn">', unsafe_allow_html=True)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    st.download_button("📥 تصدير", data=output.getvalue(), file_name="Edited_File.xlsx", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # عرض إحصائيات الملف بشكل مرتب
    rows, cols = df.shape
    st.markdown(f"<p class='file-info' style='text-align:center;'>الملف: {uploaded_file.name} | الصفوف: {rows} | الأعمدة: {cols}</p>", unsafe_allow_html=True)

    st.divider()

    # قسم التحكم التفاعلي (يظهر حسب الزر المضغوط)
    if delete_clicked:
        st.info("اختر الأعمدة التي تريد حذفها نهائياً:")
        cols_to_del = st.multiselect("الأعمدة:", df.columns)
        if st.button("تأكيد الحذف النهائي"):
            save_step()
            st.session_state.df.drop(columns=cols_to_del, inplace=True)
            st.rerun()

    if replace_clicked:
        c_r1, c_r2 = st.columns(2)
        old_v = c_r1.text_input("القيمة القديمة")
        new_v = c_r2.text_input("القيمة الجديدة")
        if st.button("تطبيق الاستبدال"):
            save_step()
            st.session_state.df.replace(old_v, new_v, inplace=True)
            st.rerun()

    if similar_clicked:
        target = st.selectbox("اختر العمود لفحص تشابه النصوص:", df.columns)
        unique_vals = df[target].dropna().unique().astype(str)
        for i, v1 in enumerate(unique_vals[:50]): # فحص أول 50 قيمة للسرعة
            group = [v1] + [v2 for v2 in unique_vals[i+1:i+20] if are_similar(v1, v2)]
            if len(group) > 1:
                st.warning(f"مجموعة متشابهة: {', '.join(group)}")
                new_name = st.text_input(f"اسم موحد لـ {v1}:", value=v1, key=v1)
                if st.button(f"توحيد {v1}"):
                    save_step()
                    st.session_state.df[target].replace(group, new_name, inplace=True)
                    st.rerun()

    if dup_clicked:
        target_dup = st.selectbox("اختر العمود لرؤية المتكررات:", df.columns)
        st.write(df[target_dup].value_counts())

    # الجدول التفاعلي (المهم جداً)
    st.markdown("### 📋 معاينة البيانات التفاعلية")
    st.write("يمكنك فرز الأعمدة أو البحث داخل الجدول مباشرة:")
    
    # استخدام st.dataframe مع إمكانيات التحديد
    event = st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        on_select="rerun",
        selection_mode="multi_column"
    )

    # إذا قام المستخدم بتحديد أعمدة من الجدول مباشرة
    if len(event.selection.columns) > 0:
        st.warning(f"لقد قمت بتحديد {len(event.selection.columns)} أعمدة.")
        if st.button("🗑️ حذف الأعمدة المحددة من الجدول"):
            save_step()
            cols_to_remove = [df.columns[i] for i in event.selection.columns]
            st.session_state.df.drop(columns=cols_to_remove, inplace=True)
            st.rerun()
