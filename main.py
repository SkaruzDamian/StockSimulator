#!/usr/bin/env python3

import sys
import os
import tkinter as tk
from tkinter import messagebox
import warnings

warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings('ignore', category=UserWarning)

def check_dependencies():
    missing_packages = []
    
    try:
        import pandas
    except ImportError:
        missing_packages.append('pandas')
    
    try:
        import numpy
    except ImportError:
        missing_packages.append('numpy')
    
    try:
        import yfinance
    except ImportError:
        missing_packages.append('yfinance')
    
    try:
        import talib
    except ImportError:
        missing_packages.append('TA-Lib')
    
    try:
        import sklearn
    except ImportError:
        missing_packages.append('scikit-learn')
    
    try:
        import matplotlib
    except ImportError:
        missing_packages.append('matplotlib')
    
    if missing_packages:
        error_msg = f"Missing required packages: {', '.join(missing_packages)}\n\n"
        error_msg += "Please install them using:\n"
        error_msg += "pip install -r requirements.txt"
        
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Missing Dependencies", error_msg)
        sys.exit(1)

def setup_matplotlib():
    try:
        import matplotlib
        matplotlib.use('TkAgg')
        import matplotlib.pyplot as plt
        plt.style.use('default')
    except Exception as e:
        print(f"Warning: Could not setup matplotlib properly: {e}")

def main():
    try:
        check_dependencies()
        setup_matplotlib()
        
        from main_window import MainWindow
        
        app = MainWindow()
        app.run()
        
    except ImportError as e:
        error_msg = f"Import error: {str(e)}\n\n"
        error_msg += "Please make sure all required packages are installed:\n"
        error_msg += "pip install -r requirements.txt"
        
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Import Error", error_msg)
        sys.exit(1)
        
    except Exception as e:
        error_msg = f"An unexpected error occurred: {str(e)}\n\n"
        error_msg += "Please check your installation and try again."
        
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Error", error_msg)
        sys.exit(1)

if __name__ == "__main__":
    main()