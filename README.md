# Smart Trip Planner — Enhanced

Features added:
- Multi-destination search box (comma-separated). Enter one or more destinations, e.g.,: Paris, Tokyo
- Richer POI output: descriptions, address, opening hours, rating, map/search links, estimated travel time between activities.
- CrewAI orchestration toggle (if you install crewai) — experimental.
- Gemini enhancement (if you install google-genai and set GEMINI_API_KEY) — optional.

How to run:
1. Create virtualenv and install deps:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
2. Copy `.env.example` to `.env` and set GEMINI_API_KEY if you want Gemini descriptions.
3. (Optional) install google-genai and/or crewai if desired.
4. Run:
   ```bash
   python app.py
   ```
5. Open http://localhost:7860

Notes:
- This project uses simulated travel times and a sample POI DB for demo purposes. Replace POI_DB in `agents_enhanced.py` with actual API data (Google Places, Foursquare) for production.
- Do not commit your real `.env` file into source control.
