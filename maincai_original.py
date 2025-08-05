import streamlit as st
from keras.models import load_model
from PIL import Image, ImageOps
import numpy as np
import pandas as pd
import os
from datetime import datetime
import time

# --- 1. ฟังก์ชันหลักในการทำงาน ---

@st.cache_resource
def load_classification_model(model_path, labels_path):
    """
    โหลดโมเดล Keras และไฟล์ labels พร้อมการแคชเพื่อประสิทธิภาพ
    """
    try:
        model = load_model(model_path)
        with open(labels_path, 'r', encoding='utf-8') as f:
            # แยกเอาเฉพาะชื่อคลาสออกมา
            class_names = [line.strip().split(' ', 1)[1] for line in f if ' ' in line]
        st.success("✅ โหลดโมเดล AI สำเร็จ!")
        return model, class_names
    except FileNotFoundError:
        st.error(f"🔴 ไม่พบไฟล์โมเดลหรือ labels ที่: {model_path} หรือ {labels_path}")
        return None, None
    except Exception as e:
        st.error(f"🔴 เกิดข้อผิดพลาดในการโหลดโมเดล: {e}")
        return None, None

def classify_image(image, model, class_names):
    """
    ฟังก์ชันสำหรับวิเคราะห์ภาพและคืนค่าประเภทพร้อมคะแนนความมั่นใจ
    """
    # ปรับขนาดภาพให้เป็น (224, 224)
    image = ImageOps.fit(image, (224, 224), Image.Resampling.LANCZOS)

    # แปลงภาพเป็น numpy array
    image_array = np.asarray(image)

    # ทำให้ค่าสีเป็นปกติ (Normalize)
    normalized_image_array = (image_array.astype(np.float32) / 127.5) - 1

    # เตรียมข้อมูลสำหรับ Model
    data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)
    data[0] = normalized_image_array

    # ทำนายผล
    prediction = model.predict(data, verbose=0)
    index = np.argmax(prediction)
    class_name = class_names[index]
    confidence_score = prediction[0][index]

    return class_name, confidence_score

def save_to_excel(data_list, excel_path):
    """
    บันทึกข้อมูลลงในไฟล์ Excel ถ้ามีไฟล์อยู่แล้วจะเขียนต่อท้าย
    """
    df = pd.DataFrame(data_list)
    try:
        if os.path.exists(excel_path):
            # อ่านข้อมูลเดิมและนำมาต่อกับข้อมูลใหม่
            existing_df = pd.read_excel(excel_path)
            updated_df = pd.concat([existing_df, df], ignore_index=True)
        else:
            updated_df = df

        # บันทึกไฟล์ Excel
        updated_df.to_excel(excel_path, index=False, engine='openpyxl')
        return True, None
    except Exception as e:
        return False, str(e)


# --- 2. ฟังก์ชันเกี่ยวกับการแสดงผล (UI) ---

def apply_custom_css():
    """
    ใช้ CSS เพื่อปรับแต่งหน้าตาแอปพลิเคชันให้สวยงาม
    """
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Mitr:wght@300;400;500;600&display=swap');

    html, body, [class*="st-"], input, textarea, button, select {
        font-family: 'Mitr', sans-serif;
    }

    /* 7-Eleven Color Palette */
    :root {
        --seven-green: #008343;
        --seven-red: #EE1C25;
        --seven-orange: #F36F21;
        --background-color: #F0F2F6; /* สีพื้นหลังเทาอ่อน */
        --text-color: #333333;
        --card-bg: #FFFFFF;
    }

    .stApp {
        background-color: var(--background-color);
    }
    
    h1, h2 {
        color: var(--seven-green);
    }

    /* กล่องสำหรับ Input */
    .input-container {
        background-color: var(--card-bg);
        border-radius: 12px;
        padding: 1.5rem 2rem;
        margin-bottom: 2rem;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
        border: 1px solid #E0E0E0;
    }

    /* ปุ่มหลัก */
    .stButton > button {
        background-color: var(--seven-green);
        color: white;
        font-weight: 600;
        border-radius: 8px;
        border: none;
        padding: 0.75rem 1rem;
        transition: background-color 0.3s, transform 0.2s;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        width: 100%; /* ทำให้ปุ่มเต็มความกว้าง */
    }
    .stButton > button:hover {
        background-color: #006a36;
        transform: scale(1.02);
    }

    /* การ์ดแสดงผลลัพธ์ */
    .result-card {
        background-color: var(--card-bg);
        border-radius: 12px;
        padding: 1rem;
        text-align: center;
        margin-bottom: 1rem;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    .result-card img {
        border-radius: 8px;
        margin-bottom: 0.75rem;
        max-height: 200px; /* จำกัดความสูงของภาพ */
    }
    
    /* แถบ Progress */
    .stProgress > div > div > div > div {
        background-color: var(--seven-orange);
    }
    
    /* แจ้งเตือน */
    [data-testid="stAlert"] { border-radius: 8px; }
    [data-testid="stSuccess"] { border-left: 5px solid var(--seven-green); }
    [data-testid="stError"] { border-left: 5px solid var(--seven-red); }

    </style>
    """, unsafe_allow_html=True)

def display_header():
    """
    แสดงโลโก้และหัวข้อของแอปพลิเคชัน
    """
    st.markdown(
        '<div style="text-align: center"><img src="https://upload.wikimedia.org/wikipedia/commons/thumb/4/40/7-eleven_logo.svg/791px-7-eleven_logo.svg.png" alt="7-Eleven Logo" width="150"></div>',
        unsafe_allow_html=True
    )
    st.markdown(
        '<h1 style="text-align: center; color: var(--seven-green);">AI for Preventive Maintenance</h1>',
        unsafe_allow_html=True
    )
    st.markdown('<p style="text-align: center;">ระบบตรวจสอบป้ายสัญลักษณ์ 7-ELEVEN ด้วยภาพถ่าย</p>', unsafe_allow_html=True)
    st.markdown("---")

def display_results(results_list):
    """
    แสดงผลลัพธ์การวิเคราะห์ในรูปแบบคอลัมน์
    """
    st.subheader("🎯 ผลการวิเคราะห์")
    
    # กำหนดจำนวนคอลัมน์ไม่เกิน 3 คอลัมน์ต่อแถว
    num_cols = min(len(results_list), 3)
    cols = st.columns(num_cols)
    
    for i, result in enumerate(results_list):
        with cols[i % num_cols]:
            st.markdown('<div class="result-card">', unsafe_allow_html=True)
            st.image(result['image_object'], caption=f"ภาพที่ {i+1}", use_column_width=True)
            
            # ใช้ st.metric เพื่อแสดงผลลัพธ์ให้ดูน่าสนใจ
            st.metric(
                label="ประเภทป้าย",
                value=result['class_name'],
                delta=f"{result['confidence']:.2%}", # แสดงเป็นเปอร์เซ็นต์
                delta_color="normal" # สีปกติ
            )
            st.markdown('</div>', unsafe_allow_html=True)


# --- 3. ส่วนหลักของแอปพลิเคชัน ---

def main():
    # ตั้งค่าหน้าเว็บและ CSS
    st.set_page_config(
        page_title="7-Connect PM AI",
        page_icon="🔧",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    apply_custom_css()
    display_header()

    # โหลดโมเดล
    model, class_names = load_classification_model("model/keras_model.h5", "model/labels.txt")
    if not model or not class_names:
        st.stop() # หยุดการทำงานถ้าโหลดโมเดลไม่สำเร็จ
    
    # --- ส่วนรับข้อมูล ---
    st.markdown('<div class="input-container">', unsafe_allow_html=True)
    st.subheader("1. กรอกข้อมูล")
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("ชื่อพนักงาน:", placeholder="เช่น สมชาย ใจดี")
        code = st.text_input("รหัสสาขา:", placeholder="เช่น 12345")
    with col2:
        sign_type = st.text_input("ประเภทป้าย:", placeholder="เช่น ป้ายไฟ, ป้ายไวนิล")
        # many = st.slider("จำนวนภาพที่ต้องการอัปโหลด:", 1, 10, 1) # อาจไม่จำเป็นถ้าให้ user อัปโหลดเอง

    st.subheader("2. อัปโหลดรูปภาพ")
    files = st.file_uploader(
        "เลือกไฟล์รูปภาพ (อัปโหลดได้หลายไฟล์)",
        type=['jpeg', 'jpg', 'png'],
        accept_multiple_files=True,
        label_visibility="collapsed"
    )
    st.markdown('</div>', unsafe_allow_html=True)

    # --- ส่วนประมวลผลและแสดงผล ---
    if files:
        # เริ่มการประมวลผล
        progress_bar = st.progress(0, text="เริ่มต้นการวิเคราะห์...")
        st.session_state['analysis_results'] = []
        
        for i, file in enumerate(files):
            # อัปเดต Progress bar
            progress_text = f"กำลังวิเคราะห์ภาพที่ {i+1}/{len(files)}..."
            progress_bar.progress((i + 1) / len(files), text=progress_text)
            
            try:
                image = Image.open(file).convert('RGB')
                
                # ทำนายผล
                class_name, confidence_score = classify_image(image, model, class_names)
                
                # เก็บผลลัพธ์ไว้ใน session_state
                st.session_state['analysis_results'].append({
                    'image_object': image,
                    'class_name': class_name,
                    'confidence': confidence_score
                })

            except Exception as e:
                st.error(f"เกิดข้อผิดพลาดในการวิเคราะห์ภาพ {file.name}: {e}")
        
        progress_bar.empty() # ซ่อน Progress bar เมื่อเสร็จ
        
        # แสดงผลลัพธ์
        if st.session_state['analysis_results']:
            display_results(st.session_state['analysis_results'])

            # --- ส่วนการยืนยันและบันทึกข้อมูล ---
            st.markdown("---")
            st.subheader("3. ยืนยันการส่งข้อมูล")
            
            if st.button("💾 บันทึกและส่งข้อมูล"):
                # ตรวจสอบว่ากรอกข้อมูลครบถ้วนหรือไม่
                if not all([name, code, sign_type]):
                    st.warning("⚠️ กรุณากรอกข้อมูลพนักงาน, รหัสสาขา, และประเภทป้ายให้ครบถ้วน")
                else:
                    with st.spinner("กำลังบันทึกข้อมูล... กรุณารอสักครู่"):
                        # สร้างโฟลเดอร์สำหรับเก็บภาพ
                        image_folder_path = 'images'
                        if not os.path.exists(image_folder_path):
                            os.makedirs(image_folder_path)

                        upload_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        data_to_save = []

                        for i, result in enumerate(st.session_state['analysis_results']):
                            # บันทึกไฟล์ภาพ
                            image_name = f"{code}_{result['class_name']}_{upload_time.replace(':', '-')}_{i+1}.png"
                            image_path = os.path.join(image_folder_path, image_name)
                            result['image_object'].save(image_path)
                            
                            data_to_save.append({
                                'Employee name': name,
                                'Branch code': code,
                                'Sign type': sign_type,
                                'How many images': len(st.session_state['analysis_results']),
                                'Image Filename': image_name,
                                'Phase': result['class_name'],
                                'Confidence': f"{result['confidence']:.4f}",
                                'Upload Time': upload_time
                            })
                        
                        # บันทึกลง Excel
                        success, error_msg = save_to_excel(data_to_save, 'data.xlsx')
                        
                        if success:
                            st.success("🎉 บันทึกข้อมูลเรียบร้อยแล้ว!")
                            st.balloons()
                        else:
                            st.error(f"❌ เกิดข้อผิดพลาดในการบันทึกไฟล์: {error_msg}")

    else:
        st.info("⬆️ กรุณาอัปโหลดรูปภาพเพื่อเริ่มการวิเคราะห์")

if __name__ == "__main__":
    main()