# Quilty Screenplay Analysis - Complete Setup Guide

## 🚀 System Overview

Quilty is a comprehensive AI-powered screenplay analysis platform that provides:
- Multi-AI analysis (Claude Opus 4.1, Grok 4, OpenAI GPT-5, GPT-5 Writing Excellence)
- Source material detection and IP analysis
- Hollywood-quality movie poster generation from multiple sources
- Professional development executive insights
- Commercial viability assessments

## 📋 Prerequisites

- Node.js 18+ and npm
- Python 3.12+
- MySQL 8.0+
- Git

## 🗄️ Database Configuration

### Database Credentials
```env
DB_HOST=localhost
DB_USER=lolita
DB_PASSWORD="jCv4pX3Lr4bf$ap@"
DB_NAME=lolita
```

### Database Setup
1. **Create MySQL Database:**
```sql
CREATE DATABASE lolita CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'lolita'@'localhost' IDENTIFIED BY 'jCv4pX3Lr4bf$ap@';
GRANT ALL PRIVILEGES ON lolita.* TO 'lolita'@'localhost';
FLUSH PRIVILEGES;
```

2. **Initialize Database Schema:**
```bash
cd /home/dwood/lolita
node scripts/init-db.js
node scripts/create-analysis-tables.js
node scripts/add-poster-fields.js
node scripts/add-source-material-fields.js
```

## 🐍 Python Service Setup

### Virtual Environment Setup
```bash
cd /home/dwood/lolita/python-ai-service

# Create virtual environment
python3.12 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Python Service Dependencies
The `requirements.txt` should include:
```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-multipart==0.0.6
anthropic==0.7.8
openai==1.3.6
httpx==0.25.2
python-dotenv==1.0.0
mysql-connector-python==8.2.0
PyPDF2==3.0.1
pdfplumber==0.9.0
pypdfium2==4.24.0
```

### Environment Variables (.env)
Create `.env` file in project root:
```env
# Database Configuration
DB_HOST=localhost
DB_USER=lolita
DB_PASSWORD="jCv4pX3Lr4bf$ap@"
DB_NAME=lolita

# AI API Keys
ANTHROPIC_API_KEY=your_anthropic_key_here
OPENAI_API_KEY=your_openai_key_here
XAI_API_KEY=your_xai_grok_key_here
REPLICATE_API_TOKEN=your_replicate_token_here
PIAPI_API_KEY=your_piapi_key_here

# Service Configuration
PYTHON_SERVICE_URL=http://127.0.0.1:8001
```

## 🎨 AI Services Configuration

### 1. Claude Opus 4.1 (Primary Analysis)
- **Purpose:** Core screenplay analysis, structure, craft evaluation
- **API:** Anthropic Claude
- **Cost:** ~$0.015 per analysis
- **Required:** ANTHROPIC_API_KEY

### 2. Grok 4 (Reality Check)
- **Purpose:** Brutal honesty, cultural analysis, controversy assessment
- **API:** xAI Grok
- **Cost:** ~$0.01 per analysis
- **Required:** XAI_API_KEY

### 3. OpenAI GPT-5 (Commercial Analysis)
- **Purpose:** Commercial viability, market assessment, poster generation
- **API:** OpenAI
- **Cost:** ~$0.02 per analysis + $0.04 per poster
- **Required:** OPENAI_API_KEY

### 4. GPT-5 Writing Excellence (Craft Focus)
- **Purpose:** Deep writing craft analysis, technical evaluation
- **API:** OpenAI GPT-5
- **Cost:** ~$0.025 per analysis
- **Required:** OPENAI_API_KEY

### 5. Source Material Analyzer (IP Detection)
- **Purpose:** Detect and analyze source material, IP considerations
- **API:** OpenAI GPT-4o
- **Cost:** ~$0.005 per analysis
- **Required:** OPENAI_API_KEY

## 🎬 Poster Generation Sources

### 1. OpenAI DALL-E 3
- **Quality:** High-quality, consistent results
- **Cost:** $0.04 per image
- **Aspect Ratio:** 1024x1792 (movie poster)
- **Style:** Hollywood theatrical posters

### 2. Flux Pro (via Replicate)
- **Quality:** Exceptional detail and realism
- **Cost:** $0.055 per image
- **Aspect Ratio:** 1024x1792
- **Style:** Cinematic, professional grade

### 3. PiAPI (Flux-1.1-Pro)
- **Quality:** High-quality alternative
- **Cost:** $0.02 per image
- **Aspect Ratio:** 1024x1792
- **Style:** Artistic, creative variations

## 🚀 Service Startup

### 1. Start Python AI Service
```bash
cd /home/dwood/lolita/python-ai-service
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

### 2. Start SvelteKit Frontend
```bash
cd /home/dwood/lolita
npm install
npm run dev -- --host 0.0.0.0 --port 5174
```

### 3. Production Deployment
```bash
# Build frontend
npm run build

# Start production services
./start.sh
```

## 📁 Project Structure

```
/home/dwood/lolita/
├── python-ai-service/           # AI Analysis Backend
│   ├── venv/                   # Python Virtual Environment
│   ├── main.py                 # FastAPI Main Service
│   ├── claude_analyzer.py      # Claude Opus 4.1 Integration
│   ├── grok_analyzer.py        # Grok 4 Integration
│   ├── openai_analyzer.py      # OpenAI GPT-5 Integration
│   ├── gpt5_analyzer.py        # GPT-5 Writing Excellence
│   ├── source_material_analyzer.py # Source Material Detection
│   ├── flux_analyzer.py        # Flux Pro Poster Generation
│   ├── piapi_analyzer.py       # PiAPI Poster Generation
│   ├── poster_manager.py       # Poster Collection Manager
│   ├── pdf_processor.py        # PDF Text Extraction
│   ├── database.py             # Database Operations
│   ├── cost_tracker.py         # Cost Tracking
│   ├── uploads/                # File Storage
│   └── requirements.txt        # Python Dependencies
├── src/                        # SvelteKit Frontend
│   ├── routes/                 # Page Routes
│   ├── lib/                    # Shared Components
│   └── app.html                # Main App Template
├── scripts/                    # Database Migration Scripts
├── static/                     # Static Assets
├── .env                        # Environment Variables
├── package.json                # Node.js Dependencies
└── README.md                   # Project Documentation
```

## 🔧 Development Workflow

### Adding New AI Features
Follow the `AI_INTEGRATION_CHECKLIST.md`:

1. **API Implementation** - Create analyzer class
2. **Database Integration** - Add schema fields
3. **Main Service Integration** - Add to parallel processing
4. **API Endpoints** - Update response data
5. **Frontend Integration** - Add UI components
6. **Testing & Validation** - End-to-end testing

### Database Migrations
```bash
# Create migration script
node scripts/create-migration.js

# Run migration
node scripts/run-migration.js
```

### Virtual Environment Management
```bash
# Activate venv
cd /home/dwood/lolita/python-ai-service
source venv/bin/activate

# Deactivate venv
deactivate

# Update requirements
pip freeze > requirements.txt
```

## 🧪 Testing

### Test Analysis Pipeline
```bash
# Test Python service
cd /home/dwood/lolita/python-ai-service
source venv/bin/activate
python -m pytest tests/

# Test frontend
cd /home/dwood/lolita
npm test
```

### Manual Testing
1. Upload a screenplay PDF
2. Monitor analysis progress
3. Verify all AI analyses complete
4. Check poster generation
5. Validate source material detection
6. Review database persistence

## 🚨 Troubleshooting

### Common Issues

1. **Database Connection Failed**
   - Verify MySQL is running
   - Check credentials in `.env`
   - Ensure database exists

2. **Python Service Won't Start**
   - Activate virtual environment
   - Install missing dependencies
   - Check API keys in `.env`

3. **AI Analysis Fails**
   - Verify API keys are valid
   - Check API rate limits
   - Monitor service logs

4. **Poster Generation Issues**
   - Confirm OPENAI_API_KEY is set
   - Check REPLICATE_API_TOKEN
   - Verify image storage permissions

### Log Locations
- Python Service: `python-ai-service/logs/python-service.log`
- Frontend: `logs/frontend-dev.log`
- Database: MySQL error logs

## 💰 Cost Estimation

### Per Analysis Costs:
- **Claude Analysis:** ~$0.015
- **Grok Analysis:** ~$0.01
- **OpenAI Analysis:** ~$0.02
- **GPT-5 Writing:** ~$0.025
- **Source Material:** ~$0.005
- **Poster Collection:** ~$0.12 (3 posters)

**Total per analysis:** ~$0.195

### Monthly Estimates (100 analyses):
- **AI Analysis:** ~$7.50
- **Poster Generation:** ~$12.00
- **Total:** ~$19.50/month

## 🔐 Security Notes

- Store API keys securely in `.env`
- Use environment-specific configurations
- Implement rate limiting for production
- Regular security updates for dependencies
- Database credentials should be rotated periodically

## 📞 Support

For technical issues:
1. Check logs for error messages
2. Verify all services are running
3. Confirm database connectivity
4. Validate API key configurations
5. Review recent code changes

---

**Last Updated:** January 2025
**Version:** 2.0.0
**Python Version:** 3.12+
**Node Version:** 18+
