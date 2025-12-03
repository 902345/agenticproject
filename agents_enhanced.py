import datetime, os, random
from math import ceil

# Lazy imports for optional libs
def import_genai():
    try:
        import google.genai as genai
        return genai
    except Exception:
        return None

def import_crewai():
    try:
        import crewai
        return crewai
    except Exception:
        return None

# Extended POI database for demo
POI_DB = {
    "Paris": [
        {"name":"Eiffel Tower","time_hr":2,"cost":30,"type":"sight","address":"Champ de Mars, 5 Avenue Anatole France, 75007 Paris","rating":4.7},
        {"name":"Louvre Museum","time_hr":3,"cost":17,"type":"museum","address":"Rue de Rivoli, 75001 Paris","rating":4.8},
        {"name":"Notre-Dame Cathedral","time_hr":1.5,"cost":0,"type":"sight","address":"6 Parvis Notre-Dame - Pl. Jean-Paul II, 75004 Paris","rating":4.6},
        {"name":"Montmartre & Sacré-Cœur","time_hr":2,"cost":0,"type":"neighbourhood","address":"75018 Paris","rating":4.5},
        {"name":"Seine River Cruise","time_hr":1,"cost":15,"type":"experience","address":"Port de la Bourdonnais, 75007 Paris","rating":4.2},
        {"name":"Musée d'Orsay","time_hr":2,"cost":16,"type":"museum","address":"1 Rue de la Légion d'Honneur, 75007 Paris","rating":4.6},
    ],
    "Tokyo": [
        {"name":"Senso-ji Temple","time_hr":1.5,"cost":0,"type":"sight","address":"2 Chome-3-1 Asakusa, Taito City","rating":4.6},
        {"name":"Shibuya Crossing","time_hr":1,"cost":0,"type":"experience","address":"Shibuya City, Tokyo","rating":4.4},
        {"name":"Meiji Shrine","time_hr":1.5,"cost":0,"type":"sight","address":"1-1 Yoyogikamizonocho, Shibuya City","rating":4.7},
        {"name":"Tsukiji Outer Market","time_hr":2,"cost":10,"type":"food","address":"4 Chome-16-2 Tsukiji, Chuo City","rating":4.5},
        {"name":"Akihabara","time_hr":2,"cost":0,"type":"neighbourhood","address":"Chiyoda City, Tokyo","rating":4.3},
    ],
    "New York": [
        {"name":"Statue of Liberty","time_hr":3,"cost":25,"type":"sight","address":"Liberty Island, New York, NY","rating":4.7},
        {"name":"Central Park","time_hr":2,"cost":0,"type":"park","address":"New York, NY","rating":4.8},
        {"name":"Metropolitan Museum of Art","time_hr":3,"cost":25,"type":"museum","address":"1000 5th Ave, New York, NY","rating":4.7},
    ],
    "London": [
        {"name":"Tower of London","time_hr":2.5,"cost":30,"type":"sight","address":"St Katharine's & Wapping, London EC3N 4AB","rating":4.6},
        {"name":"British Museum","time_hr":2.5,"cost":0,"type":"museum","address":"Great Russell St, Bloomsbury, London","rating":4.7},
    ]
}

STYLE_PROFILE = {
    "relaxed": {"daily_hours":6, "packing":["casual clothes","walking shoes","hat"]},
    "adventurous": {"daily_hours":9, "packing":["hiking shoes","daypack","water bottle"]},
    "luxury": {"daily_hours":5, "packing":["smart outfit","charger","sunglasses"]},
    "budget": {"daily_hours":7, "packing":["comfortable clothes","power bank","snacks"]},
}

class GeminiWriter:
    def __init__(self):
        self.genai = import_genai()
        self.api_key = os.environ.get('GEMINI_API_KEY')
        if self.genai and self.api_key:
            try:
                self.client = self.genai.Client(api_key=self.api_key)
            except Exception:
                self.client = None
        else:
            self.client = None

    def enhance_poi(self, poi):
        if not self.client:
            return (f"{poi['name']} — {poi.get('type','attraction').title()} located at {poi.get('address','')}. "
                    f"Estimated visit time: {poi.get('time_hr')} hours. Rating: {poi.get('rating', 'N/A')}. "
                    f"Tip: Best visited in the morning.")
        try:
            response = self.client.generate_text(
                f"Write a friendly 2-sentence travel description for {poi['name']} at {poi.get('address','')}."
            )
            return getattr(response, 'text', str(response)).strip()
        except Exception:
            return f"{poi['name']}: (AI unavailable)"

class Discoverer:
    def __init__(self, writer=None):
        self.writer = writer or GeminiWriter()

    def discover_for_destination(self, destination):
        pois = POI_DB.get(destination, [])
        enriched = []
        log = [f"Discoverer: found {len(pois)} POIs for {destination}."]

        for p in pois:
            np = p.copy()
            np['description'] = self.writer.enhance_poi(p)

            # add simulated opening hours + fixed URL
            np['opening_hours'] = "09:00-18:00" if p['type'] in ['museum', 'sight'] else "Varies"
            np['website'] = f"https://www.google.com/search?q={destination.replace(' ', '+')}+{p['name'].replace(' ', '+')}"
            np['map_link'] = f"https://www.google.com/maps/search/{p['name'].replace(' ', '+')}+{destination.replace(' ', '+')}"

            enriched.append(np)

        return enriched, log

class Scheduler:
    def estimate_travel_time(self, from_poi, to_poi):
        if not from_poi:
            return 0
        seed = (hash(from_poi['name']) ^ hash(to_poi['name'])) & 0xffffffff
        random.seed(seed)
        return random.randint(10, 45)

    def schedule(self, all_pois, start_date, end_date, daily_hours):
        log = []
        days = (end_date - start_date).days + 1
        itinerary = []

        flat = []
        for dest, pois in all_pois.items():
            for p in pois:
                n = p.copy()
                n['destination'] = dest
                flat.append(n)

        flat = sorted(flat, key=lambda x: x.get("rating", 0), reverse=True)

        poi_idx = 0
        for d in range(days):
            date = start_date + datetime.timedelta(days=d)
            hours_left = daily_hours
            events = []
            last_poi = None

            while poi_idx < len(flat):
                p = flat[poi_idx]
                travel = self.estimate_travel_time(last_poi, p) / 60.0
                needed = p['time_hr'] + travel

                if needed <= hours_left:
                    ev = {
                        "name": p["name"],
                        "duration_hr": p["time_hr"],
                        "travel_from_prev_mins": int(travel * 60),
                        "cost": p.get("cost", 0),
                        "type": p.get("type"),
                        "description": p.get("description", ""),
                        "address": p.get("address", ""),
                        "opening_hours": p.get("opening_hours", ""),
                        "website": p.get("website", ""),
                        "map_link": p.get("map_link", ""),
                        "destination": p.get("destination")
                    }
                    events.append(ev)
                    hours_left -= needed
                    last_poi = p
                    poi_idx += 1
                else:
                    break

            itinerary.append({"date": date.strftime("%Y-%m-%d"), "events": events})
            log.append(f"Scheduler: scheduled {len(events)} events for {date.strftime('%Y-%m-%d')}.")

        if poi_idx < len(flat):
            left = [p["name"] for p in flat[poi_idx:]]
            log.append(f"Scheduler: {len(left)} items overflow: {left}")

        return itinerary, log

class Budgeter:
    def estimate(self, itinerary, budget):
        log = []
        total = sum(ev.get('cost', 0) for day in itinerary for ev in day['events'])

        log.append(f"Budgeter: estimated total activity cost = ${total:.2f}.")
        ok = (budget == 0) or (total <= budget)

        if budget == 0:
            log.append("Budgeter: no budget provided.")
        elif ok:
            log.append("Budgeter: within budget.")
        else:
            log.append("Budgeter: WARNING — itinerary exceeds budget.")

        return {"total": total, "within_budget": ok}, log

class Packer:
    def pack(self, style, destinations):
        profile = STYLE_PROFILE.get(style, STYLE_PROFILE["relaxed"])
        packing = profile["packing"][:]

        if any("Paris" in d for d in destinations):
            packing.append("umbrella (Paris weather)")
        if any("Tokyo" in d for d in destinations):
            packing.append("power adapter (Japan)")

        return packing, [f"Packer: suggested {len(packing)} items."]

class EnhancedCrewPlanner:
    def __init__(self):
        self.writer = GeminiWriter()
        self.discoverer = Discoverer(self.writer)
        self.scheduler = Scheduler()
        self.budgeter = Budgeter()
        self.packer = Packer()
        self.crewai = import_crewai()

    def create_plan_multi_destinations(self, destinations, start_date=None, end_date=None, budget=0, style='relaxed', crewai_enabled=False):

        if not start_date or not end_date:
            start = datetime.date.today()
            end = start + datetime.timedelta(days=2)
        else:
            start = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
            end = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()

        log = []

        all_pois = {}
        for d in destinations:
            pois, l = self.discoverer.discover_for_destination(d)
            all_pois[d] = pois
            log.extend(l)

        daily_hours = STYLE_PROFILE.get(style, STYLE_PROFILE["relaxed"])["daily_hours"]

        itinerary, l = self.scheduler.schedule(all_pois, start, end, daily_hours)
        log.extend(l)

        budget_summary, l = self.budgeter.estimate(itinerary, budget)
        log.extend(l)

        packing, l = self.packer.pack(style, destinations)
        log.extend(l)

        result = {
            "destinations": destinations,
            "start_date": start.strftime("%Y-%m-%d"),
            "end_date": end.strftime("%Y-%m-%d"),
            "style": style,
            "itinerary": itinerary,
            "budget": budget_summary,
            "packing": packing
        }

        return result, log
