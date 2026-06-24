# CivicSight: Project Status & Progress Report

**Project Name:** CivicSight - AI-First Infrastructure Gateway for Automated Municipal Accountability  
**Developer:** Abhyoday Rathore (2nd Year CS Student)  
**Internship Period:** June - July 2026 (~4 weeks remaining)  
**Status:** Core pipeline complete, ticket dispatch in development

---

## 1. Project Overview

CivicSight is a civic-tech platform that simplifies infrastructure issue reporting (potholes, waterlogging, broken lights, etc.) by automating the process of identifying the correct government authority and dispatching complaints.

**Key Innovation:** One-tap reporting with automatic GPS geocoding, AI validation, and jurisdiction routing.

---

## 2. Current Progress

### ✅ COMPLETED MODULES

#### A. Reverse Geocoding (`reverseGeoEncoding/geocode.py`)
- **Technology:** OpenStreetMap Nominatim API + Python `requests`
- **Functionality:** Converts GPS coordinates (lat/lng) → human-readable address + road name
- **Features:**
  - Street-level location detection (road, pedestrian path, highway)
  - Locality fallback for areas without tagged roads
  - Error handling for network failures
  - Returns full Nominatim response for debugging
- **Status:** ✅ Fully functional and tested

#### B. Image Analysis (`imageDescription/imageDesc.py`)
- **Technology:** Google Gemini AI 2.5 Flash with structured JSON output
- **Functionality:** Validates photos and generates professional complaint descriptions
- **Features:**
  - Binary classification: valid civic issue vs. invalid photo
  - Issue type identification (pothole, waterlogging, broken light, etc.)
  - Severity assessment (Low, Medium, High, Critical)
  - Confidence scoring (0.0 - 1.0)
  - Professional descriptions emphasizing practical consequences
  - Handles low-quality, blurry, or poorly-lit images
- **Specialized Instructions:** Tuned for Delhi civic infrastructure context
- **Status:** ✅ Fully functional with advanced prompt engineering

#### C. Authority Resolution (`authorityResolution/authRes.py`)
- **Technology:** Google Gemini AI 2.5 Flash-Lite with structured JSON output
- **Functionality:** Maps road names → responsible government authority
- **Classification Rules:**
  - MCD (Municipal Corporation of Delhi) - residential/local streets
  - NDMC (New Delhi Municipal Council) - Lutyens' Delhi zone
  - PWD (Public Works Department) - major arterial roads
  - NHAI (National Highways Authority) - national highways
  - Delhi Cantt - military cantonment roads
- **Output:** Authority name, confidence score, reasoning
- **Status:** ✅ Fully functional

#### D. Main Orchestrator (`main.py`)
- **Technology:** Modular Python architecture
- **Functionality:** Chains all three modules into a complete pipeline
- **Features:**
  - Single entry point for end-to-end processing
  - Graceful error handling for each module
  - Conditional authority resolution (skips if photo invalid)
  - CLI interface: `python main.py <image_path> <latitude> <longitude>`
  - Pretty-printed terminal output
  - Full JSON output for downstream processing
- **Status:** ✅ Fully functional and production-ready for CLI

---

### 🔄 IN PROGRESS

#### Ticket Generation & Dispatch (`NOT YET IMPLEMENTED`)
- **Scope:** Email-based automated ticket submission to authorities
- **Requirements:**
  - Authority contact database (JSON/CSV mapping)
  - Email sender setup (Gmail with app password)
  - Ticket formatting and transmission
- **Timeline:** Week 1 of remaining 4 weeks

---

### ⏳ PENDING (Next 4 Weeks)

| Task | Priority | Timeline | Notes |
|------|----------|----------|-------|
| Email ticket dispatch | HIGH | Week 1-2 | Gmail or mock implementation |
| Web form UI (Flask) | HIGH | Week 2-3 | Photo upload + coordinate capture |
| Testing & error handling | HIGH | Week 3 | Edge cases, validation |
| Documentation & README | MEDIUM | Week 4 | Demo video + setup guide |
| Database integration | LOW | Optional | If time permits (JSON files sufficient) |
| Real authority API integration | LOW | Out of scope | Too complex for 4-week timeline |

---

## 3. Technology Stack

### Backend
| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Reverse Geocoding** | OpenStreetMap Nominatim API | GPS → Address conversion |
| **Image Analysis** | Google Gemini 2.5 Flash | Photo validation & description |
| **Authority Resolution** | Google Gemini 2.5 Flash-Lite | Road → Authority mapping |
| **Main Pipeline** | Python 3.x | Orchestration & integration |
| **HTTP Client** | Python `requests` | API calls |
| **Gemini SDK** | `google-genai` | AI model integration |

### Dependencies
```
requests          # HTTP requests to Nominatim
google-genai      # Google Gemini API client
python-dotenv     # Environment variable management (for API keys)
```

### APIs Used (External)
1. **OpenStreetMap Nominatim** (Free, no API key required)
   - Rate limited but generous for civic use
   - High geographic accuracy for India

2. **Google Gemini** (API key required)
   - Image analysis with multimodal support
   - Structured JSON output via response_schema
   - Cost: ~$0.075 per 1M input tokens (very affordable)

---

## 4. Architecture

```
User Input (Photo + GPS)
        ↓
    main.py
    ├── reverse_geocode_osm()     [OpenStreetMap Nominatim]
    │   └── Returns: full_address, road, locality
    │
    ├── analyze_image()           [Google Gemini 2.5 Flash]
    │   └── Returns: is_valid, issue_type, severity, description, confidence
    │
    └── resolve_authority()       [Google Gemini 2.5 Flash-Lite]
        └── Returns: authority, confidence_score, reasoning
        
    Merged Result (JSON)
        ↓
    [NEXT: Email Dispatch] → Authority inbox
```

### Module Design Principles
- **Separation of Concerns:** Each module handles one responsibility
- **Error Handling:** Graceful degradation at each layer
- **JSON Integration:** All outputs are JSON-compatible for easy chaining
- **Testability:** Each module can be tested independently
- **Scalability:** Ready for async/parallel processing if needed

---

## 5. Key Features & Implementation Highlights

### 1. Robust Reverse Geocoding
- Falls back to locality when road-level data unavailable
- Handles 10-second timeout for network resilience
- Provides debug-friendly raw API response

### 2. AI-Powered Image Validation
- Filters out false reports (selfies, random objects, non-issues)
- Professional complaint descriptions with inferred consequences
- Confidence scoring for triage/priority
- Delhi-specific infrastructure classification

### 3. Intelligent Authority Routing
- Multi-tier classification (MCD, NDMC, PWD, NHAI, Cantt)
- Reasoning provided for transparency
- Uses AI for handling edge cases (not hardcoded rules)

### 4. Clean Code & Documentation
- Docstrings for all public functions
- Type hints for clarity
- Inline comments for non-obvious logic
- Modular structure for maintainability

---

## 6. Testing & Validation

### Current Test Coverage
- ✅ Reverse geocoding tested with sample Delhi coordinates
- ✅ Image analysis tested with valid/invalid photo samples
- ✅ Authority resolution tested with known Delhi roads
- ✅ End-to-end pipeline validated with sample data

### Sample Data
- `sampleImages/` directory contains test images for validation
- Various issue types: potholes, waterlogging, streetlight damage

---

## 7. Next Steps (4-Week Roadmap)

### Week 1: Ticket Dispatch
- [ ] Build authority contact database (JSON)
- [ ] Implement email dispatch function (Gmail + app password)
- [ ] Add fallback options (console output, file save)
- [ ] Test with sample authorities

### Week 2: Web Frontend
- [ ] Create Flask form for photo upload + GPS input
- [ ] Integrate with main.py backend
- [ ] Display results in browser
- [ ] Basic styling

### Week 3: Testing & Polish
- [ ] End-to-end testing with 20+ samples
- [ ] Error handling & edge cases
- [ ] Performance optimization
- [ ] Bug fixes

### Week 4: Documentation & Demo
- [ ] Comprehensive README with setup instructions
- [ ] API documentation for each module
- [ ] Demo video (5 min walkthrough)
- [ ] Final code cleanup

---

## 8. Deployment & Runtime

### Prerequisites
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set API key
export GEMINI_API_KEY="your_key_here"

# 3. Run pipeline
python main.py sample.jpg 28.701220 77.270935
```

### Current Limitations
- CLI-only interface (web UI coming week 2)
- No persistent database (uses JSON/console output)
- Ticket dispatch not yet implemented
- Real authority integrations not in scope

### Production Readiness
- ✅ Core modules are production-ready
- ⏳ Frontend & dispatch layer in progress
- ⏳ Database & caching layer optional for MVP

---

## 9. Lessons & Design Decisions

### Why Google Gemini?
- Free tier sufficient for student project
- Better multimodal image understanding than competitors
- Structured JSON output via response_schema (no parsing needed)
- Flash model is fast + cheap

### Why OpenStreetMap?
- No API key required
- Community-maintained data for India
- Open-source alignment with civic-tech ethos
- Sufficient accuracy for municipal complaint routing

### Why Modular Architecture?
- Easy to swap geocoding providers (Google Maps, etc.)
- AI models can be upgraded (Gemini → GPT-4V, etc.)
- Each module independently testable
- Clear responsibilities = fewer bugs

### Why Not Include Database Now?
- 4-week timeline is tight
- File-based storage sufficient for MVP demo
- Can add database in future without changing core logic
- Simplifies deployment for demo purposes

---

## 10. Known Issues & Workarounds

| Issue | Workaround | Priority |
|-------|-----------|----------|
| Nominatim rate limiting | Add request delays if needed | Low |
| Gemini API quota exhaustion | Switch to Gemini Lite for authority | Low |
| Invalid image handling | Gracefully skip authority resolution | Done ✅ |
| Missing road tags in OSM | Fall back to locality/neighborhood | Done ✅ |

---

## 11. Impact & Outcomes

### By End of Internship
- ✅ Complete working pipeline (3/3 core modules)
- ✅ Web UI for citizen use (basic Flask form)
- ✅ Automated email dispatch to authorities
- ✅ Professional portfolio project demonstrating:
  - API integration (Gemini + Nominatim)
  - Full-stack development (backend + frontend)
  - AI/ML application
  - Problem-solving for civic-tech

### Scalability Potential
- Can process 100+ reports/day on free tier
- Ready for municipal integration
- Adaptable to other cities (authority classification rule change)
- Mobile-ready architecture for iOS/Android apps

---

## 12. Contact & Documentation

**Student:** Abhyoday Rathore  
**Email:** ishurathore0000@gmail.com  
**GitHub:** [CivicSightProject]  
**API Keys Required:**
- Google Gemini API key (free tier: $300 credit)
- OpenStreetMap API (free, no key needed)

---

**Document Date:** June 24, 2026  
**Last Updated:** June 24, 2026  
**Status:** Active Development
