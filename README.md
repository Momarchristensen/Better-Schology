# Schology

A lightweight Schoology-style course dashboard with a FastAPI backend and a static HTML frontend. It provides course browsing, assignment search, material viewing, document conversion, and assignment submissions through a local web app.

## Features

- Schoology account login through the app's authentication flow
- Course and section browsing
- Assignment search and upcoming/overdue work views
- Material viewing through a local file proxy
- DOCX to HTML conversion
- PPT/PPTX to PDF conversion through the bundled LibreOffice runtime
- Written and file-based assignment submissions
- Draft saving for written submissions

## Requirements

- Windows
- Python 3.10 or newer
- Node.js and npm for linting
- A Schoology account supported by the configured login flow

The project expects LibreOffice at `libreoffice/program/soffice.exe`. Keep that directory available when using PowerPoint conversion.

## Setup

Create and activate a virtual environment, then install the Python dependencies:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install fastapi uvicorn httpx mammoth python-multipart requests beautifulsoup4
```

Install the frontend linting dependencies:

```powershell
npm install
```

## Run

Start the local server:

```powershell
python server.py
```

Open [http://localhost:3498](http://localhost:3498) in a browser.

The server uses an HTTP-only session cookie for the authenticated session. Generated downloaded-file data is stored in `cached_files/` and is ignored by Git.

## Lint

```powershell
npm run lint
npm run lint:css
```

## Project Layout

- `server.py` - FastAPI application and route handlers
- `api_utils.py` - Schoology API requests and data helpers
- `get_token.py` - authentication/session-token handling
- `HTML/` - frontend pages and static assets
- `libreoffice/` - bundled runtime used for presentation conversion
- `cached_files/` - generated local file cache

## Project Name Ideas

- CourseNest
- ClassPort
- StudyDock
- SchoolFlow
- CampusDesk
- CourseOrbit
- LessonLane
- Classboard
- ScholarHub
- Assignment Atlas

Schology is a working title; `CourseNest`, `StudyDock`, and `Classboard` are the strongest alternatives for a friendly, focused dashboard.
