import sys
import os
import streamlit as st

# Add src to path so imports work
src_path = os.path.join(os.path.dirname(__file__), 'src')
if src_path not in sys.path:
    sys.path.append(src_path)

# Import and run the app
from dashboard.app import main

if __name__ == "__main__":
    main()
