# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the **Intelligent Patent Analysis System** repository. The system is designed to automate patent analysis using AI and various APIs.

**Current Status**: Full system implementation completed - API server, frontend, and all integrations are functional. System is ready for testing.

## Technology Stack

- **Backend**: Supabase (PostgreSQL, Auth, Storage, Realtime)
- **API Service**: 
  - Standard Mode: Supabase Edge Functions
  - Advanced Mode: Python API on Railway (with LangGraph)
- **Frontend**: Next.js 14 + Vercel
- **Workflow Engine**: LangGraph (Python) - for advanced analysis
- **AI Services**: Google Gemini API + SERP API for patent searches
- **Patent Data**: Google Patent API

## Development Roadmap

The project follows a phased approach outlined in TODO.md:

1. **Phase 1**: Supabase infrastructure setup
2. **Phase 2**: Core API integrations (SERP, Gemini)
3. **Phase 3**: LangGraph workflow implementation
4. **Phase 4**: Frontend development
5. **Phase 5**: Advanced features and optimization

## Key Project Documents

- **PRD.md**: Comprehensive product requirements covering all system features
- **TODO.md**: Detailed development tasks organized by phase
- **supabase_architecture.md**: Database schema and architecture design
- **pricing_strategy.md**: SaaS pricing tiers ($299-$2,999/month)

## Architecture Highlights

### Database Design (Supabase)

- Multi-tenant architecture with RLS policies
- Vector embeddings for patent similarity search
- Real-time collaboration features
- Comprehensive audit logging

### Workflow System (LangGraph)

Key workflows to implement:

- Patent search and retrieval
- Prior art analysis
- Novelty assessment
- Inventive step evaluation
- Professional report generation

### API Integrations

- Google Patent API for patent database access
- SERP API for non-patent literature searches
- Gemini API for AI analysis and report generation

## Development Guidelines

When implementing this system:

1. Start with Supabase setup as per TODO.md Phase 1
2. Follow the database schema in supabase_architecture.md
3. Implement Python API service using FastAPI on Cloud Run
4. Use LangGraph for complex multi-step analysis workflows
5. Ensure all API keys and secrets are properly managed
6. Implement comprehensive error handling for external API calls
7. Follow the subscription tier limits defined in pricing_strategy.md

## Deployment Architecture

### Recommended: Vercel + Railway
- Frontend: Vercel (Next.js)
- Backend: Railway (Python + LangGraph)
- Database: Supabase

### Alternative: Vercel + Supabase Only
- Frontend: Vercel (Next.js)
- Backend: Supabase Edge Functions
- Database: Supabase

## Common Commands

### Backend (Python API)

```bash
cd api
# Install dependencies
pip install -r requirements.txt
# Start the API server
python main.py
# Or run in background
nohup python main.py > api.log 2>&1 &
```

### Railway Deployment
```bash
# Login to Railway
railway login

# Deploy to Railway
railway up

# View logs
railway logs

# Open Railway dashboard
railway open
```

### Frontend (Next.js)

```bash
cd frontend
# Install dependencies
npm install
# Start development server
npm run dev
# Build for production
npm run build
npm start
```

### Database Setup

1. Visit Supabase SQL Editor: https://supabase.com/dashboard/project/grjslrfvlarfslgtoeqi/editor
2. Execute the SQL script from `database/schema.sql`

### API Endpoints

- Health Check: http://localhost:8000/
- API Documentation: http://localhost:8000/docs
- Test Endpoint: http://localhost:8000/api/test

### Environment Variables

All required API keys are configured in `.env.local`:

- `NEXT_PUBLIC_SUPABASE_URL`
- `NEXT_PUBLIC_SUPABASE_ANON_KEY`
- `SUPABASE_SERVICE_ROLE_KEY`
- `GEMINI_API_KEY`
- `SERPAPI_KEY`
- `NEXT_PUBLIC_API_URL` (for Railway deployment)

### Current Implementation Status

- ✅ FastAPI backend with all endpoints
- ✅ Next.js frontend with complete UI
- ✅ Database schema designed
- ✅ Full Supabase integration (Auth, DB, Storage)
- ✅ User authentication system
- ✅ SERP API integration for patent searches
- ✅ Gemini API integration for AI analysis
- ✅ Complete patent analysis workflow
- ⏳ Email verification disabled (see SUPABASE_SETUP.md)
- ✅ LangGraph workflows (implemented with multi-agent system)
- ✅ Dual-mode analysis system (Standard/Advanced)
- ⏳ File upload functionality

## Testing Guide

See `TESTING_GUIDE.md` for complete testing instructions.

**Quick Start**:

1. Execute database scripts in Supabase SQL Editor:
   - First: `database/schema.sql`
   - Then: `database/rls_policies.sql`
2. Disable email verification in Supabase (see `SUPABASE_SETUP.md`)
3. Register with real email format (e.g., user@gmail.com)
4. Login and create patent analysis
5. View results in dashboard

## Important Files

- `TESTING_GUIDE.md` - Complete testing instructions
- `SUPABASE_SETUP.md` - Supabase configuration guide
- `database/schema.sql` - Database initialization script

## Known Issues and Solutions

### RLS Policy Errors

If you encounter "row-level security policy" errors:

1. Execute `database/schema.sql` in Supabase SQL Editor first
2. Then execute `database/rls_policies.sql` to set up proper permissions
3. Ensure you're using the service role key in `.env.local`

### Email Verification

- Must be disabled in Supabase for testing (Authentication → Providers → Email → Turn off "Confirm email")
- Once disabled, users can login immediately after registration

## Important Deployment Files

- `DEPLOYMENT_GUIDE.md` - Complete deployment instructions
- `RAILWAY_DEPLOYMENT.md` - Railway-specific deployment guide
- `vercel.json` - Vercel configuration
- `railway.json` & `railway.toml` - Railway configuration
- `Procfile` - Railway startup command

## Analysis Modes

### Standard Mode (Supabase Edge Functions)
- Fast analysis (1-2 minutes)
- Basic patent analysis (novelty, inventiveness, utility)
- Suitable for quick assessments

### Advanced Mode (Python + LangGraph)
- Deep analysis (5-10 minutes)
- Multi-agent collaboration system
- Market analysis and risk assessment
- Professional comprehensive reports
- Requires Railway deployment

## Memories

- Email verification must be disabled in Supabase for testing
- Use real email formats (e.g., user@gmail.com) for registration
- Frontend runs on port 3002 (if 3000/3001 are occupied)
- API runs on port 8000
- Database tables and RLS policies must be created before using the system
- Test account: testuser2@gmail.com / testuser123
- Advanced mode requires `NEXT_PUBLIC_API_URL` environment variable
