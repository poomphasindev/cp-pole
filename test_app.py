#!/usr/bin/env python3
"""
Test script for 7-Eleven AI Preventive Maintenance System
This script tests the core functionality without running the full Streamlit app
"""

import os
import sys
import numpy as np
from PIL import Image
import pandas as pd

def test_imports():
    """Test if all required packages can be imported"""
    print("🔍 Testing imports...")
    try:
        import streamlit as st
        print("✅ Streamlit imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import Streamlit: {e}")
        return False
    
    try:
        from keras.models import load_model
        print("✅ Keras imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import Keras: {e}")
        return False
    
    try:
        import tensorflow as tf
        print("✅ TensorFlow imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import TensorFlow: {e}")
        return False
    
    return True

def test_model_files():
    """Test if model files exist"""
    print("\n🔍 Testing model files...")
    
    model_path = "model/keras_model.h5"
    labels_path = "model/labels.txt"
    
    if os.path.exists(model_path):
        print(f"✅ Model file found: {model_path}")
    else:
        print(f"❌ Model file not found: {model_path}")
        return False
    
    if os.path.exists(labels_path):
        print(f"✅ Labels file found: {labels_path}")
        # Read and display labels
        with open(labels_path, 'r', encoding='utf-8') as f:
            labels = [line.strip() for line in f]
        print(f"   Labels: {labels}")
    else:
        print(f"❌ Labels file not found: {labels_path}")
        return False
    
    return True

def test_model_loading():
    """Test if the model can be loaded"""
    print("\n🔍 Testing model loading...")
    try:
        from keras.models import load_model
        model = load_model("model/keras_model.h5")
        print("✅ Model loaded successfully")
        print(f"   Model input shape: {model.input_shape}")
        print(f"   Model output shape: {model.output_shape}")
        return True
    except Exception as e:
        print(f"❌ Failed to load model: {e}")
        return False

def test_image_processing():
    """Test image processing functionality"""
    print("\n🔍 Testing image processing...")
    try:
        # Create a dummy image
        dummy_image = Image.new('RGB', (224, 224), color='red')
        
        # Test image resizing
        from PIL import ImageOps
        resized_image = ImageOps.fit(dummy_image, (224, 224), Image.Resampling.LANCZOS)
        print("✅ Image resizing works")
        
        # Test numpy conversion
        image_array = np.asarray(resized_image)
        print(f"✅ Image to numpy conversion works (shape: {image_array.shape})")
        
        # Test normalization
        normalized_array = (image_array.astype(np.float32) / 127.5) - 1
        print("✅ Image normalization works")
        
        return True
    except Exception as e:
        print(f"❌ Image processing failed: {e}")
        return False

def test_excel_functionality():
    """Test Excel file operations"""
    print("\n🔍 Testing Excel functionality...")
    try:
        # Test creating a simple DataFrame
        test_data = [
            {'Employee name': 'Test User', 'Branch code': '12345', 'Phase': 'P1', 'Confidence': '0.95'}
        ]
        df = pd.DataFrame(test_data)
        print("✅ DataFrame creation works")
        
        # Test Excel writing
        test_excel_path = "test_output.xlsx"
        df.to_excel(test_excel_path, index=False, engine='openpyxl')
        print("✅ Excel writing works")
        
        # Clean up test file
        if os.path.exists(test_excel_path):
            os.remove(test_excel_path)
            print("✅ Test file cleaned up")
        
        return True
    except Exception as e:
        print(f"❌ Excel functionality failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 7-Eleven AI Preventive Maintenance - System Test")
    print("=" * 60)
    
    tests = [
        test_imports,
        test_model_files,
        test_model_loading,
        test_image_processing,
        test_excel_functionality
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The app is ready for deployment.")
        return True
    else:
        print("⚠️  Some tests failed. Please fix the issues before deployment.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 