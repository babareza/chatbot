import os
import pandas as pd
import streamlit as st
import google.generativeai as genai

# ==========================================
# تنظیمات صفحه Streamlit
# ==========================================
st.set_page_config(
    page_title="دستیار هوشمند پژوهش معماری و انرژی",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# بارگذاری پایگاه دانش از فایل اکسل
# ==========================================
@st.cache_data
def load_knowledge_base():
    file_path = "07_Architecture_Energy_Knowledge_Base_v02.xlsx"
    
    if not os.path.exists(file_path):
        return "پایگاه دانش معماری و انرژی فعال است.", {}

    xls = pd.ExcelFile(file_path)
    knowledge_text = "### پایگاه دانش جامع معماری و انرژی:\n\n"
    sheets_dict = {}

    for sheet_name in xls.sheet_names:
        df = pd.read_excel(xls, sheet_name).dropna(how='all')
        sheets_dict[sheet_name] = df
        knowledge_text += f"==== شیت: {sheet_name} ====\n"
        knowledge_text += df.to_markdown(index=False)
        knowledge_text += "\n\n"

    return knowledge_text, sheets_dict

# ==========================================
# نوار جانبی (Sidebar) برای ورود کلید جمنای
# ==========================================
with st.sidebar:
    st.title("تنظیمات دستیار هوشمند")
    
    api_key_input = st.text_input(
        "کلید API گوگل (Gemini API Key):",
        type="password",
        help="کلید رایگان خود را از Google AI Studio دریافت کنید."
    )
    
    selected_model = st.selectbox(
        "انتخاب مدل هوش مصنوعی:",
        ["gemini-3.8-flash", "gemini-3.6-flash"],
        index=0
    )
    
    temperature = st.slider(
        "دقت پاسخ‌دهی (Temperature):",
        min_value=0.0,
        max_value=1.0,
        value=0.2,
        step=0.05
    )
    
    st.divider()
    knowledge_text, sheets_dict = load_knowledge_base()
    if sheets_dict:
        st.success(f"پایگاه دانش با {len(sheets_dict)} شیت با موفقیت بارگذاری شد.")
    else:
        st.warning("فایل اکسل دیتابیس در ریپازیتوری یافت نشد.")

# ==========================================
# رابط کاربری اصلی (تَب‌بندی شده)
# ==========================================
st.title("🏛️ دستیار پژوهشی تخصصی معماری و انرژی")
st.caption("متصل به موتور هوش مصنوعی Gemini و پایگاه داده علمی")

tab_chat, tab_database = st.tabs(["💬 چت و پرسش تحقیقاتی", "📂 مرور پایگاه دانش"])

# ------------------------------------------
# تب ۱: چت با جمنای
# ------------------------------------------
with tab_chat:
    SYSTEM_INSTRUCTIONS = """
    شما یک دستیار ارشد تحقیقاتی و پژوهشگر تخصصی در حوزه «معماری و انرژی» هستید.
    پاسخ‌های شما باید دقیق، علمی و مستند به پایگاه دانش ارائه شده باشد.
    """

    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "سلام! من دستیار پژوهشی معماری و انرژی هستم. پرسش خود را مطرح کنید."}
        ]

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if user_query := st.chat_input("پرسش خود را درباره بهینه‌سازی انرژی، نماهای تطبیق‌پذیر و... بنویسید"):
        if not api_key_input:
            st.warning("لطفاً ابتدا کلید Gemini API را در نوار جانبی (Sidebar) وارد کنید.")
            st.stop()
            
        st.session_state.messages.append({"role": "user", "content": user_query})
        with st.chat_message("user"):
            st.markdown(user_query)

        with st.chat_message("assistant"):
            with st.spinner("در حال تحلیل داده‌های پایگاه دانش با جمنای..."):
                try:
                    genai.configure(api_key=api_key_input)
                    full_prompt = f"{knowledge_text}\n\n==== پرسش کاربر ====\n{user_query}"
                    
                    model = genai.GenerativeModel(
                        model_name=selected_model,
                        system_instruction=SYSTEM_INSTRUCTIONS,
                        generation_config=genai.types.GenerationConfig(
                            temperature=temperature,
                            top_p=0.95,
                        )
                    )
                    
                    response = model.generate_content(full_prompt)
                    response_text = response.text
                    
                    st.markdown(response_text)
                    st.session_state.messages.append({"role": "assistant", "content": response_text})
                    
                except Exception as e:
                    st.error(f"خطا در پردازش درخواست: {str(e)}")

# ------------------------------------------
# تب ۲: نمایش جدول‌های دیتابیس
# ------------------------------------------
with tab_database:
    st.subheader("📋 اطلاعات پایگاه دانش")
    if sheets_dict:
        selected_sheet = st.selectbox("انتخاب جدول:", list(sheets_dict.keys()))
        st.dataframe(sheets_dict[selected_sheet], use_container_width=True)
    else:
        st.warning("فایل اکسل در پوشه یافت نشد.")
