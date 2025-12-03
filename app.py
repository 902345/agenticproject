from flask import Flask, render_template, request, jsonify
from agents_enhanced import EnhancedCrewPlanner
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__, template_folder='templates', static_folder='static')
planner = EnhancedCrewPlanner()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/plan', methods=['POST'])
def plan():
    data = request.json
    dest_input = data.get('destinations','').strip()
    # allow comma-separated or newline-separated
    parts = [p.strip() for p in dest_input.replace('\n',',').split(',') if p.strip()]
    if len(parts) == 0:
        return jsonify({"error":"Please enter at least one destination in the search box."}), 400
    crewai_enabled = bool(data.get('crewai_enabled', False))
    itinerary, log = planner.create_plan_multi_destinations(destinations=parts,
                                                           start_date=data.get('start_date'),
                                                           end_date=data.get('end_date'),
                                                           budget=float(data.get('budget') or 0),
                                                           style=data.get('style') or 'relaxed',
                                                           crewai_enabled=crewai_enabled)
    return jsonify({"itinerary": itinerary, "log": log})

if __name__ == '__main__':
    if not os.environ.get('GEMINI_API_KEY'):
        print('WARNING: GEMINI_API_KEY environment variable is not set. Gemini-dependent features will be disabled.')
    app.run(host='0.0.0.0', port=7860, debug=True)
