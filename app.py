from flask import Flask, render_template, request, jsonify
from main import process_report
from ticketing.ticket_dispatcher import create_and_dispatch_ticket
from ticketing.ticket_model import Ticket
import base64
import tempfile
import os

app = Flask(__name__)

# Create upload directory if it doesn't exist
os.makedirs('static/uploads', exist_ok=True)

# Initialize database
Ticket.init_db()


@app.route('/report', methods=['GET'])
def report_form():
    """Serve the citizen report form."""
    return render_template('index.html')


@app.route('/api/analyze', methods=['POST'])
def analyze_report():
    """
    Receive photo + coordinates, run pipeline, return analysis.

    Expected POST data:
    {
        "image": "base64-encoded-image",
        "latitude": 28.701220,
        "longitude": 77.270935
    }
    """
    try:
        data = request.get_json()

        # Decode base64 image to temporary file
        image_data = base64.b64decode(data['image'].split(',')[1])
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as f:
            f.write(image_data)
            temp_path = f.name

        # Run pipeline
        latitude = data['latitude']
        longitude = data['longitude']
        report = process_report(temp_path, latitude, longitude)

        # Clean up temp file
        os.unlink(temp_path)

        return jsonify({
            "success": True,
            "report": report
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400


@app.route('/api/ticket/create', methods=['POST'])
def create_ticket_route():
    """
    Create ticket from analyzed report.

    Expected POST data:
    {
        "report": {...full report...},
        "latitude": 28.701220,
        "longitude": 77.270935,
        "image": "base64-encoded-image" (optional)
    }
    """
    try:
        data = request.get_json()
        report = data['report']
        latitude = data['latitude']
        longitude = data['longitude']

        # Decode and save image if provided
        image_path = "uploaded_image.jpg"
        if 'image' in data and data['image']:
            try:
                image_data = base64.b64decode(data['image'].split(',')[1])
                image_filename = f"ticket_{Ticket._get_next_ticket_number()}.jpg"
                image_path = f"static/uploads/{image_filename}"
                os.makedirs(os.path.dirname(image_path), exist_ok=True)
                with open(image_path, 'wb') as f:
                    f.write(image_data)
            except Exception:
                image_path = "uploaded_image.jpg"

        # Create ticket
        result = create_and_dispatch_ticket(
            report,
            latitude,
            longitude,
            image_path
        )

        if result['success']:
            return jsonify({
                "success": True,
                "ticket_id": result['ticket_id']
            })
        else:
            return jsonify({
                "success": False,
                "error": result['error']
            }), 400

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/', methods=['GET'])
def home():
    """Redirect to report form."""
    return report_form()


if __name__ == '__main__':
    print("Starting CivicSight server...")
    print("Open your browser to: http://localhost:5000/report")
    app.run(debug=True, host='0.0.0.0', port=5000)
