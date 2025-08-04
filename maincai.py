import streamlit as st
from keras.models import load_model
from PIL import Image
import pandas as pd
import os
from util import classify, set_background  # ต้องตรวจสอบว่า set_background ใช้งานได้ถูกต้อง
from datetime import datetime

# กำหนดค่าเริ่มต้นของหน้า
st.set_page_config(
    page_title="CP ALL",
    page_icon="📊",  
    layout="centered",   
    initial_sidebar_state="expanded"  
)

# ตั้งค่า background หากมีการนำเข้าถูกต้อง
try:
    set_background("D:/pneumonia-classification-web-app-python-streamlit-main/bgs/AI for preventive maintenance Signage of 7-ELEVEN's with photo inspection..png")
except Exception as e:
    st.error(f"Error setting background: {e}")

# เพิ่มโลโก้และหัวข้อ
st.markdown(
    f'<div style="text-align: center"><img src="https://upload.wikimedia.org/wikipedia/commons/thumb/4/40/7-eleven_logo.svg/791px-7-eleven_logo.svg.png" alt="7-Eleven Logo" width="150"></div>', 
    unsafe_allow_html=True
)

st.markdown(
    f'<div style="text-align: center; color: white;"><h1>AI for Preventive Maintenance Signage of 7-ELEVEN with Photo Inspection</h1></div>', 
    unsafe_allow_html=True
)

# สไตล์ของอินพุตต่างๆ
st.markdown(
    """
    <style>
    .stTextInput label, .stSlider label, .stFileUploader label {
        color: white;
    }
    </style>
    """, 
    unsafe_allow_html=True
)

# กรอกข้อมูลพนักงานและรายละเอียด
name = st.text_input("Employee name:")
code = st.text_input("Branch code:")
sign_type = st.text_input("Sign type:")
many = st.slider("How many pictures:", 1, 6)

# อัปโหลดไฟล์
files = st.file_uploader("Upload images", type=['jpeg', 'jpg', 'png', 'jfif'], accept_multiple_files=True)

# โหลดโมเดลและคลาส
model_path = "model/keras_model.h5"
labels_path = "model/labels.txt"

try:
    model = load_model(model_path)
    with open(labels_path, 'r') as f:
        class_names = [line.strip().split(' ')[1] for line in f]
except Exception as e:
    st.error(f"Error loading model or labels: {e}")

# พาธของไฟล์ Excel และโฟลเดอร์สำหรับบันทึกรูปภาพ
excel_file_path = 'data.xlsx'
image_folder_path = 'images'

# สร้างโฟลเดอร์สำหรับรูปภาพหากยังไม่มี
if not os.path.exists(image_folder_path):
    os.makedirs(image_folder_path)

if files:
    image_data = []
    upload_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    for i, file in enumerate(files):
        image = Image.open(file).convert('RGB')
        st.image(image, use_column_width=True)
        
        # ทำการจัดประเภทและแสดงคะแนนความมั่นใจ
        try:
            class_name, confidence_score = classify(image, model, class_names)
            image_name = f"{code}_{class_name}_{i+1}.png"
            image_path = os.path.join(image_folder_path, image_name)
            image.save(image_path)
            
            # บันทึกข้อมูลรูปภาพ
            image_data.append({
                'Image': image_name,
                'Phase': class_name,
                'Confidence': f"{confidence_score:.2f}",
                'Upload Time': upload_time
            })
            st.write(f"## {class_name} (Confidence: {confidence_score:.2f})")
        except Exception as e:
            st.error(f"Error during classification: {e}")

    # กดปุ่ม Submit เพื่อบันทึกข้อมูลลงใน Excel
    if st.button('Submit'):
        df = pd.DataFrame(image_data)
        df['Employee name'] = name
        df['Branch code'] = code
        df['Sign type'] = sign_type
        df['How many images'] = many
        
        try:
            if os.path.exists(excel_file_path):
                existing_df = pd.read_excel(excel_file_path)
                updated_df = pd.concat([existing_df, df], ignore_index=True)
            else:
                updated_df = df

            with pd.ExcelWriter(excel_file_path, engine='openpyxl', mode='w') as writer:
                updated_df.to_excel(writer, index=False)
                
            st.success('Submission complete')
        except Exception as e:
            st.error(f"An error occurred while saving the file: {e}")
