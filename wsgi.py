from keymg import create_app
import os
import sys
app_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(app_path)

app = create_app()
