# 7-Eleven AI Preventive Maintenance System

<p align="center">
    <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/4/40/7-eleven_logo.svg/791px-7-eleven_logo.svg.png" alt="7-Eleven Logo" width="200">
</p>

## 🎯 Project Overview

This is an AI-powered preventive maintenance system for 7-Eleven stores that uses computer vision to classify and monitor store signage conditions. The system can analyze uploaded images of store signs and classify them into different maintenance phases (P1, P2, P3, P4).

## 🚀 Features

- **AI Image Classification**: Automatically classifies store signage images
- **Multi-file Upload**: Support for uploading multiple images at once
- **Real-time Analysis**: Instant classification results with confidence scores
- **Data Export**: Automatic Excel export with detailed analysis results
- **User-friendly Interface**: Clean, modern UI with 7-Eleven branding
- **Responsive Design**: Works on desktop and mobile devices

## 🛠️ Technology Stack

- **Frontend**: Streamlit
- **AI/ML**: TensorFlow, Keras
- **Image Processing**: Pillow (PIL)
- **Data Processing**: Pandas, NumPy
- **File Handling**: OpenPyXL

## 📦 Installation & Setup

### Local Development

1. **Clone the repository**

   ```bash
   git clone <your-repo-url>
   cd <your-repo-name>
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   streamlit run maincai.py
   ```

### Streamlit Cloud Deployment

1. **Push your code to GitHub**

   ```bash
   git add .
   git commit -m "Initial commit"
   git push origin main
   ```

2. **Deploy on Streamlit Cloud**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Sign in with your GitHub account
   - Click "New app"
   - Select your repository
   - Set the main file path to: `maincai.py`
   - Click "Deploy"

## 📁 Project Structure

```
├── maincai.py              # Main Streamlit application
├── requirements.txt        # Python dependencies
├── .streamlit/config.toml  # Streamlit configuration
├── model/                  # AI model files
│   ├── keras_model.h5     # Trained Keras model
│   └── labels.txt         # Class labels
├── images/                 # Uploaded images storage
├── data.xlsx              # Analysis results export
└── README.md              # Project documentation
```

## 🎮 How to Use

1. **Enter Employee Information**

   - Fill in employee name, branch code, and sign type

2. **Upload Images**

   - Click "Browse files" to upload sign images
   - Support for JPEG, JPG, and PNG formats
   - Multiple files can be uploaded simultaneously

3. **View Analysis Results**

   - AI automatically classifies each image
   - Results show sign phase and confidence score
   - Images are displayed with analysis results

4. **Save Data**
   - Click "บันทึกและส่งข้อมูล" to export results
   - Data is saved to Excel file with timestamps
   - Images are stored locally for reference

## 🔧 Model Information

The AI model classifies store signage into 4 phases:

- **P1**: Good condition
- **P2**: Minor maintenance needed
- **P3**: Moderate maintenance required
- **P4**: Immediate attention required

## 📊 Data Export

The system automatically exports analysis results to `data.xlsx` with the following columns:

- Employee name
- Branch code
- Sign type
- Number of images analyzed
- Image filename
- Phase classification
- Confidence score
- Upload timestamp

## 🌐 Deployment Notes

- **Streamlit Cloud**: Fully compatible with Streamlit Cloud deployment
- **File Storage**: Images and Excel files are stored locally
- **Model Loading**: Uses `@st.cache_resource` for efficient model loading
- **Error Handling**: Comprehensive error handling for robust deployment

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support or questions, please contact the development team or create an issue in the repository.
