# Lolita Screenplay Analysis Tool

A professional screenplay analysis and evaluation platform powered by Claude Opus 4.1, built with SvelteKit, Python FastAPI, and MySQL.

## Features

- **AI-Powered Analysis**: Claude Opus 4.1 for superior narrative understanding and character psychology
- **Professional PDF Processing**: Advanced text extraction with multiple fallback methods
- **User Authentication**: Secure signup and login with session-based authentication
- **Cost Tracking**: Monitor API usage and costs per user
- **Analysis Library**: Complete library to view all uploaded scripts and results
- **Professional UI**: Modern, responsive design with Tailwind CSS
- **Dual Architecture**: SvelteKit frontend + Python FastAPI backend for optimal performance

## Tech Stack

- **Frontend**: SvelteKit 2.x, TypeScript, Tailwind CSS 4.x
- **Backend**: 
  - SvelteKit API routes (Node.js) for user management
  - Python FastAPI for AI processing and analysis
- **AI**: Claude Opus 4.1 (Anthropic API)
- **Database**: MySQL with connection pooling
- **Authentication**: Session-based auth with secure cookies
- **Security**: Argon2 password hashing, CSRF protection

## Getting Started

### Prerequisites

- Node.js 18+ 
- Python 3.8+
- MySQL 8.0+
- npm or yarn

### Quick Start

1. Clone the repository:
```bash
git clone <repository-url>
cd lolita
```

2. Set up your environment variables:
```bash
cp .env.example .env
```

Edit the `.env` file with your database credentials and Anthropic API key.

3. **One-Command Startup** (recommended):
```bash
./start.sh dev
```

This unified script will:
- Install all Node.js and Python dependencies
- Set up Python virtual environment
- Initialize database tables
- Start both frontend and backend services

The application will be available at:
- **Frontend**: http://localhost:5174
- **Backend API**: http://localhost:8001

### Advanced Usage

**Development mode** (both services):
```bash
./start.sh dev
```

**Production mode** (both services):
```bash
./start.sh prod
```

**Frontend only**:
```bash
./start.sh dev --frontend-only
```

**Backend only**:
```bash
./start.sh dev --backend-only
```

## Environment Variables

Key environment variables you need to configure:

**Database Configuration:**
- `DB_HOST`: MySQL host (default: localhost)
- `DB_USER`: MySQL username
- `DB_PASSWORD`: MySQL password  
- `DB_NAME`: MySQL database name
- `DB_PORT`: MySQL port (default: 3306)

**Application Security:**
- `SESSION_SECRET`: Secret key for session encryption
- `APP_URL`: Your application URL (important for remote servers)

**AI Service:**
- `ANTHROPIC_API_KEY`: Your Anthropic API key for Claude Opus 4.1
- `MAX_COST_PER_USER`: Maximum API cost per user (default: 100.00)

## Database Schema

The application creates the following tables:

**User Management:**
- `users`: User accounts with email and hashed passwords
- `sessions`: User sessions for authentication

**Screenplay Analysis:**
- `screenplays`: Basic screenplay metadata and file information
- `screenplay_analyses`: Detailed Claude Opus 4.1 analysis results with scores
- `api_costs`: API usage tracking and cost monitoring per user

## Development

### Available Scripts

**Unified Startup (Recommended):**
- `./start.sh dev`: Start both frontend and backend in development mode
- `./start.sh prod`: Start both services in production mode
- `./start.sh dev --frontend-only`: Start only the SvelteKit frontend
- `./start.sh dev --backend-only`: Start only the Python AI backend

**Individual Commands:**
- `npm run dev`: Start SvelteKit development server only
- `npm run build`: Build SvelteKit for production
- `npm run preview`: Preview SvelteKit production build
- `npm run check`: Run TypeScript checking
- `npm run lint`: Run linting
- `npm run format`: Format code with Prettier
- `npm run db:init`: Initialize database tables

### Project Structure

```
├── src/                           # SvelteKit Frontend
│   ├── lib/
│   │   ├── components/            # Reusable Svelte components
│   │   └── server/
│   │       ├── auth.ts           # Authentication logic
│   │       └── db/index.ts       # Database connection
│   ├── routes/
│   │   ├── api/                  # SvelteKit API routes (proxy to Python)
│   │   ├── auth/                 # Authentication pages
│   │   ├── dashboard/            # User dashboard
│   │   ├── screenplays/          # Screenplay management & analysis
│   │   └── +layout.svelte        # Main layout
│   └── app.html                  # HTML template
├── python-ai-service/            # Python FastAPI Backend
│   ├── main.py                   # FastAPI application
│   ├── database.py               # Database models and connections
│   ├── claude_analyzer.py        # Claude Opus 4.1 integration
│   ├── pdf_processor.py          # PDF text extraction
│   ├── cost_tracker.py           # API cost monitoring
│   └── requirements.txt          # Python dependencies
├── scripts/                      # Database initialization scripts
├── start.sh                      # Unified startup script
└── .env                          # Environment configuration
```

## Security Features

- **Password Security**: Argon2 hashing with secure parameters
- **Session Management**: Secure HTTP-only cookies with expiration
- **CSRF Protection**: Built-in SvelteKit CSRF protection
- **Input Validation**: Server-side validation for all user inputs
- **SQL Injection Prevention**: Parameterized queries throughout

## Current Features

✅ **Complete AI Analysis Pipeline**
- Claude Opus 4.1 integration for superior narrative understanding
- Advanced PDF processing with multiple extraction methods
- Real-time analysis status tracking with polling
- Comprehensive analysis results with scores and recommendations

✅ **User Management & Cost Tracking**
- Secure authentication and session management
- Per-user API cost tracking and usage limits
- Complete analysis library with search and filtering

✅ **Professional UI/UX**
- Modern, responsive design inspired by enterprise applications
- Drag-and-drop file upload with validation
- Real-time progress indicators and status updates
- Professional analysis results presentation

## Future Enhancements

This platform is ready for extending with:

- **Multi-format Support**: Word documents, Final Draft files, Fountain format
- **Collaboration Features**: Shared analyses, team workspaces, comments
- **Advanced Analytics**: Trend analysis, comparative scoring, industry benchmarks
- **Payment Integration**: Subscription tiers, pay-per-analysis options
- **Admin Dashboard**: User management, system monitoring, cost analytics
- **API Integration**: Third-party screenplay databases, industry tools

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## License

[Add your license information here]
