from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import io
import datetime
import random
import base64
from PIL import Image

# Import logic from the existing id_gen.py
# We import the class and constants
try:
    from id_gen import IDCardGenerator, CARD_W, CARD_H, C_WHITE, CORNER_R
except ImportError:
    # If path issues occur during reorganization
    import sys
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from id_gen import IDCardGenerator, CARD_W, CARD_H, C_WHITE, CORNER_R

app = Flask(__name__)
CORS(app) # Enable CORS as requested

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"})

@app.route('/generate', methods=['POST'])
def generate():
    try:
        data = request.json
        company = data.get('company', 'Organization')
        name = data.get('name', '')
        department = data.get('department', 'General')
        gender = data.get('gender', 'N/A')
        address = data.get('address', 'N/A')
        phone = data.get('phone', 'N/A')
        image_data = data.get('image') # Base64 string

        if not name or not image_data:
            return jsonify({"error": "Missing name or image"}), 400

        # Decode image
        header, encoded = image_data.split(",", 1)
        image_bytes = base64.b64decode(encoded)
        photo = Image.open(io.BytesIO(image_bytes))

        # Generate ID and dates
        id_no = str(random.randint(1_000_000, 9_999_999))
        now = datetime.datetime.now()
        issue_date = now.strftime("%d %b %Y")
        valid_date = (now + datetime.timedelta(days=365)).strftime("%d %b %Y")

        # Call the existing logic (using the class methods as functions)
        # Note: We pass None as 'self' since the methods don't use it
        front_pil = IDCardGenerator._render_front(
            None, company, name, id_no, department, gender, phone,
            photo, issue_date, valid_date
        )
        back_pil = IDCardGenerator._render_back(
            None, company, name, id_no, department, address, phone,
            issue_date, valid_date
        )

        # Convert back to base64 to send to frontend
        def pil_to_base64(img):
            buffered = io.BytesIO()
            # Convert to RGB for saving as JPEG/PNG if needed, 
            # but _render functions return RGBA with rounded corners
            img.save(buffered, format="PNG")
            return base64.b64encode(buffered.getvalue()).decode('utf-8')

        return jsonify({
            "success": True,
            "front": pil_to_base64(front_pil),
            "back": pil_to_base64(back_pil),
            "id_no": id_no
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
