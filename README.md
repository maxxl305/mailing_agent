# 🔍 Company Research Tool with Web Frontend

**Automatisierte Unternehmensanalyse mit Meta Ad Intelligence und personalisierter E-Mail-Generierung**

Ein vollständiges Web-Tool für Marketing-Agenturen, das Websites crawlt, Meta-Advertising analysiert und personalisierte Cold-E-Mails generiert.

![Company Research Tool](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)
![Python](https://img.shields.io/badge/Python-3.11+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Latest-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

## 🚀 Features

### 📊 **Umfassende Website-Analyse**
- **Vollständiger Website-Crawl** mit Firecrawl API
- **SEO-Performance** Bewertung
- **User Experience** Rating
- **Marketing-Kanäle** Identifikation
- **Competitive Landscape** Analyse
- **SWOT-Analyse** automatisch generiert

### 🎯 **Meta Ad Intelligence**
- **Echte Meta API Integration** mit graceful Fallback
- **Advertising Status** Detection (aktive Kampagnen, Budget, etc.)
- **Creative Strategy** Analyse
- **Targeting Insights** 
- **Budget Assessment**
- **Optimization Opportunities** Identifikation
- **Competitive Analysis**

### 📧 **Personalisierte E-Mail-Generierung**
- **Automatische Cold-E-Mails** basierend auf Research
- **Personalisierung** mit Website + Meta Ad Insights
- **Professional Templates** für Marketing-Agenturen
- **Configurable Sender** Details

### 📄 **Export & Reporting**
- **PDF Export** für Client-Reports
- **Word Export** für weitere Bearbeitung
- **Quality Scoring** für Datenqualität
- **Structured JSON** Output

### 🖥️ **Web Frontend**
- **Bootstrap UI** - Professional & Responsive
- **Live Progress** Updates via WebSocket
- **Error Handling** mit detailliertem Feedback
- **Ein-Klick-Start** - Keine Tech-Kenntnisse nötig

## 📋 Voraussetzungen

### API Keys erforderlich:
- **OpenAI API Key** - Für LLM Analysis
- **Firecrawl API Key** - Für Website Crawling  
- **Meta API Access Token** - Für echte Meta Ad Intelligence
- **Tavily API Key** - Für Web Search (optional)

### System Requirements:
- **Python 3.11+**
- **Internet-Verbindung**
- **Moderne Browser** (Chrome, Firefox, Safari, Edge)

## ⚡ Quick Start

### 1. Repository clonen
```bash
git clone https://github.com/your-repo/company-researcher-tool.git
cd company-researcher-tool
```

### 2. API Keys konfigurieren
Erstelle eine `.env` Datei im Hauptverzeichnis:

```bash
# .env Datei
OPENAI_API_KEY=sk-your-openai-key-here
FIRECRAWL_API_KEY=your-firecrawl-key-here
META_API_ACCESS_TOKEN=your-meta-api-token-here
TAVILY_API_KEY=your-tavily-key-here  # Optional
```

### 3. Tool starten
```bash
python start_tool.py
```

**Das war's!** 🎉
- Browser öffnet sich automatisch
- Dependencies werden automatisch installiert
- Tool läuft auf `http://localhost:8000`

## 🎯 Verwendung

### 1. **Website analysieren**
- URL eingeben (z.B. `https://example-company.com`)
- Sender-Details anpassen (Name, Firma, Service)
- "Analyse starten" klicken

### 2. **Fortschritt verfolgen**
- Live-Updates während der Analyse
- Fortschrittsbalken zeigt aktuellen Status
- Bei Fehlern: Detaillierte Fehlermeldungen

### 3. **Ergebnisse exportieren**
- **Website-Analyse** mit USP, UX-Rating, Marketing-Kanälen
- **Meta Ad Intelligence** mit Targeting, Budget, Opportunities
- **Generierte E-Mail** personalisiert auf Ihre Agentur
- **PDF/Word Export** für Client-Präsentationen

## 🏗️ Architektur

```
┌─────────────────┐    HTTP/WS   ┌──────────────────┐
│   Web Frontend  │ ◄──────────► │  FastAPI Server  │
│  (HTML/CSS/JS)  │              │                  │
└─────────────────┘              │  ┌─────────────┐ │
                                 │  │ LangGraph   │ │
┌─────────────────┐              │  │ Agent       │ │
│   API Services  │ ◄────────────┤  └─────────────┘ │
│                 │              │                  │
│ • Firecrawl     │              │  ┌─────────────┐ │
│ • OpenAI        │              │  │ Meta Ad     │ │
│ • Tavily        │              │  │ Intelligence│ │
│ • Meta API      │              │  └─────────────┘ │
└─────────────────┘              └──────────────────┘
```

### Komponenten:
- **FastAPI Backend** - REST API + WebSocket für Live-Updates
- **LangGraph Agent** - Orchestriert die komplette Analyse
- **Meta Ad Client** - Echte Meta API mit graceful Fallback
- **Export Engine** - PDF/Word Generierung mit ReportLab/python-docx

## 📁 Projektstruktur

```
company-researcher-tool/
├── app.py                     # 🚀 FastAPI Web Server
├── start_tool.py              # 🔧 Ein-Klick-Startskript
├── requirements_fastapi.txt   # 📦 Web Frontend Dependencies
├── .env                       # 🔑 API Keys (erstellen!)
├── exports/                   # 📄 Generierte PDFs/Word Docs
│
├── src/agent/
│   ├── graph.py              # 🧠 LangGraph Workflow
│   ├── state.py              # 📊 Data Schema mit Meta Ad Intelligence
│   ├── prompts.py            # 💬 LLM Prompts für Analyse
│   ├── configuration.py     # ⚙️  Tool Configuration
│   ├── meta_ad_client.py     # 📱 Echter Meta API Client
│   ├── meta_api_utils.py     # 🔗 Meta API Utilities
│   └── debug_utils.py        # 🔍 Quality Analysis Tools
│
├── enhanced_analysis_*.json  # 📋 Beispiel-Outputs
└── README.md                 # 📖 Diese Datei
```

## ⚙️ Meta API Setup

### Meta Developer Account erstellen:
1. Gehe zu [Meta for Developers](https://developers.facebook.com/)
2. Erstelle eine neue App
3. Füge "Ad Library API" hinzu
4. Generiere Access Token
5. Setze Token in `.env` Datei

### Graceful Fallback:
- **Mit Meta Token:** Vollständige Ad Intelligence
- **Ohne Meta Token:** Website-Analyse läuft trotzdem weiter
- **API Error:** Detaillierte Fehlermeldungen im Frontend

## 🔧 Konfiguration

### Sender-Details anpassen
Die Default-Werte können in `app.py` geändert werden:

```python
# app.py - Zeile ~38
email_config: Dict[str, str] = {
    "sender_company": "Mobile Fusion",
    "sender_name": "Jonas Kremser", 
    "sender_role": "Digital Marketing Consultant",
    "service_offering": "SEO & Meta Ad Optimierung",
    # ...
}
```

### Analyse-Parameter
```python
# src/agent/configuration.py
max_search_queries: int = 4      # Max Web-Searches
max_reflection_steps: int = 0    # Reflection Iterationen
enable_meta_ad_analysis: bool = True  # Meta API nutzen
meta_ad_limit: int = 50          # Max Ads pro Company
```

## 🔧 Troubleshooting

### ❌ **"Meta API Token invalid"**
→ **Fix:** 
1. Prüfe Token in `.env`: `META_API_ACCESS_TOKEN=your-token-here`
2. Teste Token: `python -c "from src.agent.meta_ad_client import test_meta_api; import asyncio; asyncio.run(test_meta_api())"`
3. Ohne Token läuft Website-Analyse trotzdem

### ❌ **"Firecrawl API Error"**
→ **Fix:** API Key in `.env` prüfen:
```bash
FIRECRAWL_API_KEY=your-real-api-key-here
```

### ❌ **"OpenAI API Error"**
→ **Fix:** OpenAI Key + Guthaben prüfen:
```bash
OPENAI_API_KEY=sk-your-real-openai-key
```

### ❌ **"WebSocket Connection Failed"**
→ **Fix:** Server neu starten:
```bash
python start_tool.py
```

### 🐛 **Debug Mode**
Für detaillierte Logs:
```bash
# Terminal 1: Server starten
python start_tool.py

# Terminal 2: Debug-Test
python -c "
import asyncio
from src.agent.graph import graph
result = asyncio.run(graph.ainvoke({'urls': ['https://example.com']}))
print('Backend funktioniert:', bool(result))
"
```

## 🎯 Für Entwickler

### Dependencies installieren
```bash
pip install -r requirements_fastapi.txt
```

### Development Server
```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

### Meta API Test
```bash
python src/agent/meta_ad_client.py
```

## 📈 Roadmap

### ✅ **Fertig (v1.0)**
- Web Frontend mit Bootstrap UI
- Website-Crawling mit Firecrawl
- **Echte Meta API Integration** mit Fallback
- E-Mail-Generierung
- PDF/Word Export
- Professional Error Handling

### 🔄 **Nächste Version (v1.1)**
- [ ] Batch-Processing (mehrere URLs)
- [ ] Enhanced Meta API Features
- [ ] Template-System für E-Mails
- [ ] User-Management
- [ ] Results-Datenbank

### 🚀 **Zukunft (v2.0)**
- [ ] Multi-Language Support
- [ ] Advanced Analytics Dashboard
- [ ] API für Integration
- [ ] Cloud Deployment
- [ ] White-Label Lösung

## 📞 Support

### Für Marketing-Agenturen:
- **Einfach zu bedienen** - Keine Tech-Kenntnisse nötig
- **Ein-Klick-Start** - `python start_tool.py`
- **Professional Output** - Client-Ready Reports
- **Echte Meta API** - Competitive Intelligence

### Für Entwickler:
- **Modulare Architektur** - LangGraph + FastAPI
- **Erweiterbar** - Einfach neue Features hinzufügen
- **Production-Ready** - Echte APIs mit Error Handling

## 📄 Lizenz

MIT License - Siehe LICENSE Datei für Details.

## 🤝 Contributing

Pull Requests sind willkommen! Für größere Änderungen bitte zuerst ein Issue erstellen.

---

**Made with ❤️ for Marketing Agencies**

*Automatisierte Company Research • Echte Meta Ad Intelligence • Personalisierte Cold E-Mails*