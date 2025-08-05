import streamlit as st
from PIL import Image, ImageOps
import numpy as np
import pandas as pd
import os
from datetime import datetime
import time
import pickle
import joblib

# --- 1. ฟังก์ชันหลักในการทำงาน (Lightweight Version) ---

@st.cache_resource
def load_lightweight_model():
    """
    โหลดโมเดลแบบ Lightweight หรือใช้ fallback method
    """
    try:
        # ลองโหลด TensorFlow Lite หรือ model อื่นๆ
        try:
            import tensorflow as tf
            if tf.__version__ >= "2.15.0":
                # ใช้ TensorFlow 2.15+ ที่ support Python 3.13
                model = tf.keras.models.load_model("model/keras_model.h5")
                st.success("✅ โหลดโมเดล TensorFlow สำเร็จ!")
                return model, ["P1", "P2", "P3", "P4"], "tensorflow"
        except ImportError:
            pass
        
        # Fallback: ใช้ model ที่แปลงเป็น pickle หรือ joblib
        try:
            if os.path.exists("model/model_lightweight.pkl"):
                with open("model/model_lightweight.pkl", 'rb') as f:
                    model = pickle.load(f)
                st.success("✅ โหลดโมเดล Lightweight สำเร็จ!")
                return model, ["P1", "P2", "P3", "P4"], "pickle"
        except:
            pass
            
        # Fallback: ใช้ joblib
        try:
            if os.path.exists("model/model_lightweight.joblib"):
                model = joblib.load("model/model_lightweight.joblib")
                st.success("✅ โหลดโมเดล Joblib สำเร็จ!")
                return model, ["P1", "P2", "P3", "P4"], "joblib"
        except:
            pass
        
        # Final fallback: ใช้ simple ML model
        st.warning("⚠️ ไม่สามารถโหลดโมเดล AI ได้ ใช้ Simple ML Algorithm แทน")
        return None, ["P1", "P2", "P3", "P4"], "simple"
        
    except Exception as e:
        st.error(f"🔴 เกิดข้อผิดพลาดในการโหลดโมเดล: {e}")
        return None, ["P1", "P2", "P3", "P4"], "simple"

def classify_image_lightweight(image, model, class_names, model_type):
    """
    ฟังก์ชันสำหรับวิเคราะห์ภาพแบบ Lightweight
    """
    # ปรับขนาดภาพให้เป็น (224, 224)
    image = ImageOps.fit(image, (224, 224), Image.Resampling.LANCZOS)
    image_array = np.asarray(image)
    
    # ทำให้ค่าสีเป็นปกติ (Normalize)
    normalized_image_array = (image_array.astype(np.float32) / 127.5) - 1
    
    if model_type == "tensorflow" and model is not None:
        # ใช้ TensorFlow model
        data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)
        data[0] = normalized_image_array
        prediction = model.predict(data, verbose=0)
        index = np.argmax(prediction)
        confidence_score = prediction[0][index]
        
    elif model_type in ["pickle", "joblib"] and model is not None:
        # ใช้ Lightweight model
        # Flatten image for simple models
        flattened = normalized_image_array.flatten().reshape(1, -1)
        prediction = model.predict_proba(flattened)[0]
        index = np.argmax(prediction)
        confidence_score = prediction[index]
        
    else:
        # Simple ML algorithm (fallback)
        # ใช้ feature engineering แบบง่าย
        features = extract_simple_features(normalized_image_array)
        index, confidence_score = simple_classifier(features)
    
    class_name = class_names[index]
    return class_name, confidence_score

def extract_simple_features(image_array):
    """
    สกัด features แบบง่ายจากภาพ
    """
    # คำนวณ features ต่างๆ
    features = {
        'mean_brightness': np.mean(image_array),
        'std_brightness': np.std(image_array),
        'mean_red': np.mean(image_array[:, :, 0]),
        'mean_green': np.mean(image_array[:, :, 1]),
        'mean_blue': np.mean(image_array[:, :, 2]),
        'contrast': np.max(image_array) - np.min(image_array),
        'entropy': calculate_entropy(image_array)
    }
    return features

def calculate_entropy(image_array):
    """
    คำนวณ entropy ของภาพ
    """
    hist, _ = np.histogram(image_array.flatten(), bins=256, range=[-1, 1])
    hist = hist[hist > 0]
    prob = hist / hist.sum()
    entropy = -np.sum(prob * np.log2(prob))
    return entropy

def simple_classifier(features):
    """
    Simple classifier ใช้ features แบบง่าย
    """
    # ใช้ rules-based classification
    brightness = features['mean_brightness']
    contrast = features['contrast']
    entropy = features['entropy']
    
    # Classification rules
    if brightness < -0.5 and contrast < 0.5:
        index = 0  # P1 - ภาพมืดและ contrast ต่ำ
    elif brightness < 0 and entropy < 4:
        index = 1  # P2 - ภาพมืดปานกลาง
    elif brightness > 0 and contrast > 1.0:
        index = 2  # P3 - ภาพสว่างและ contrast สูง
    else:
        index = 3  # P4 - ภาพสว่างมาก
    
    # Confidence based on feature strength
    confidence = min(0.95, 0.7 + abs(brightness) * 0.2 + contrast * 0.1)
    
    return index, confidence

def save_to_excel(data_list, excel_path):
    """
    บันทึกข้อมูลลงในไฟล์ Excel
    """
    df = pd.DataFrame(data_list)
    try:
        if os.path.exists(excel_path):
            existing_df = pd.read_excel(excel_path)
            updated_df = pd.concat([existing_df, df], ignore_index=True)
        else:
            updated_df = df

        updated_df.to_excel(excel_path, index=False, engine='openpyxl')
        return True, None
    except Exception as e:
        return False, str(e)

# --- 2. ฟังก์ชันเกี่ยวกับการแสดงผล (UI) ---

def apply_custom_css():
    """
    ใช้ CSS เพื่อปรับแต่งหน้าตาแอปพลิเคชัน
    """
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Mitr:wght@300;400;500;600&display=swap');

    html, body, [class*="st-"], input, textarea, button, select {
        font-family: 'Mitr', sans-serif;
    }

    :root {
        --seven-green: #008343;
        --seven-red: #EE1C25;
        --seven-orange: #F36F21;
        --background-color: #F0F2F6;
        --text-color: #333333;
        --card-bg: #FFFFFF;
    }

    .stApp {
        background-color: var(--background-color);
    }
    
    h1, h2 {
        color: var(--seven-green);
    }

    .input-container {
        background-color: var(--card-bg);
        border-radius: 12px;
        padding: 1.5rem 2rem;
        margin-bottom: 2rem;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
        border: 1px solid #E0E0E0;
    }

    .stButton > button {
        background-color: var(--seven-green);
        color: white;
        font-weight: 600;
        border-radius: 8px;
        border: none;
        padding: 0.75rem 1rem;
        transition: background-color 0.3s, transform 0.2s;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        width: 100%;
    }
    .stButton > button:hover {
        background-color: #006a36;
        transform: scale(1.02);
    }

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
        max-height: 200px;
    }
    
    .stProgress > div > div > div > div {
        background-color: var(--seven-orange);
    }
    
    [data-testid="stAlert"] { border-radius: 8px; }
    [data-testid="stSuccess"] { border-left: 5px solid var(--seven-green); }
    [data-testid="stError"] { border-left: 5px solid var(--seven-red); }

    .model-info {
        background-color: #e3f2fd;
        border: 1px solid #2196f3;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 1rem;
        color: #1976d2;
    }

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

def display_model_info(model_type):
    """
    แสดงข้อมูลเกี่ยวกับโมเดลที่ใช้
    """
    if model_type == "tensorflow":
        st.markdown(
            '<div class="model-info">🤖 <strong>AI Model:</strong> TensorFlow Deep Learning Model (Real AI)</div>',
            unsafe_allow_html=True
        )
    elif model_type in ["pickle", "joblib"]:
        st.markdown(
            '<div class="model-info">⚡ <strong>AI Model:</strong> Lightweight ML Model (Optimized)</div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            '<div class="model-info">⚠️ <strong>AI Model:</strong> Simple ML Algorithm (Fallback)</div>',
            unsafe_allow_html=True
        )

def display_results(results_list, model_type):
    """
    แสดงผลลัพธ์การวิเคราะห์
    """
    st.subheader("🎯 ผลการวิเคราะห์")
    
    # แสดงข้อมูลโมเดล
    display_model_info(model_type)
    
    num_cols = min(len(results_list), 3)
    cols = st.columns(num_cols)
    
    for i, result in enumerate(results_list):
        with cols[i % num_cols]:
            st.markdown('<div class="result-card">', unsafe_allow_html=True)
            st.image(result['image_object'], caption=f"ภาพที่ {i+1}", use_column_width=True)
            
            st.metric(
                label="ประเภทป้าย",
                value=result['class_name'],
                delta=f"{result['confidence']:.2%}",
                delta_color="normal"
            )
            st.markdown('</div>', unsafe_allow_html=True)

# --- 3. ส่วนหลักของแอปพลิเคชัน ---

def main():
    st.set_page_config(
        page_title="7-Connect PM AI (Lightweight)",
        page_icon="🔧",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    apply_custom_css()
    display_header()

    # โหลดโมเดล
    model, class_names, model_type = load_lightweight_model()
    if not class_names:
        st.stop()
    
    # --- ส่วนรับข้อมูล ---
    st.markdown('<div class="input-container">', unsafe_allow_html=True)
    st.subheader("1. กรอกข้อมูล")
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("ชื่อพนักงาน:", placeholder="เช่น สมชาย ใจดี")
        code = st.text_input("รหัสสาขา:", placeholder="เช่น 12345")
    with col2:
        sign_type = st.text_input("ประเภทป้าย:", placeholder="เช่น ป้ายไฟ, ป้ายไวนิล")

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
        progress_bar = st.progress(0, text="เริ่มต้นการวิเคราะห์...")
        st.session_state['analysis_results'] = []
        
        for i, file in enumerate(files):
            progress_text = f"กำลังวิเคราะห์ภาพที่ {i+1}/{len(files)}..."
            progress_bar.progress((i + 1) / len(files), text=progress_text)
            
            try:
                image = Image.open(file).convert('RGB')
                
                # ทำนายผล
                class_name, confidence_score = classify_image_lightweight(image, model, class_names, model_type)
                
                st.session_state['analysis_results'].append({
                    'image_object': image,
                    'class_name': class_name,
                    'confidence': confidence_score
                })

            except Exception as e:
                st.error(f"เกิดข้อผิดพลาดในการวิเคราะห์ภาพ {file.name}: {e}")
        
        progress_bar.empty()
        
        if st.session_state['analysis_results']:
            display_results(st.session_state['analysis_results'], model_type)

            # --- ส่วนการยืนยันและบันทึกข้อมูล ---
            st.markdown("---")
            st.subheader("3. ยืนยันการส่งข้อมูล")
            
            if st.button("💾 บันทึกและส่งข้อมูล"):
                if not all([name, code, sign_type]):
                    st.warning("⚠️ กรุณากรอกข้อมูลพนักงาน, รหัสสาขา, และประเภทป้ายให้ครบถ้วน")
                else:
                    with st.spinner("กำลังบันทึกข้อมูล... กรุณารอสักครู่"):
                        image_folder_path = 'images'
                        if not os.path.exists(image_folder_path):
                            os.makedirs(image_folder_path)

                        upload_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        data_to_save = []

                        for i, result in enumerate(st.session_state['analysis_results']):
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
                                'Upload Time': upload_time,
                                'Model Type': model_type
                            })
                        
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