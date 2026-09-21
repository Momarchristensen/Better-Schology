# Better Schology

Better Schology is a lightweight Schoology-style course dashboard with a FastAPI backend and a static HTML frontend. It provides course browsing, assignment search, material viewing, document conversion, and assignment submissions through a local web app.

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

## Schoology Server Configuration

The default Schoology server is `https://ca-net.schoology.com`. To use another Schoology server, edit the generated `config.json` file beside `server.py` when running Python, or at `%APPDATA%\Better-Schology\config.json` when using the packaged Windows executable:

```json
{
	"schoology_base_url": "https://your-schoology-server.example.com"
}
```

You can copy [config.example.json](config.example.json) as a starting point. The URL must use HTTPS and must not include a query string or fragment. Restart the app after changing the file. The configured server must support the same Schoology API and login flow.

## Setup

Create and activate a virtual environment:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install the Python dependencies:

```powershell
python -m pip install -r requirements.txt
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

The server uses an HTTP-only session cookie for the authenticated session. Generated downloaded-file data is stored in `cached_files/` and is ignored by Git. When running from Python, that directory is beside `server.py`. The packaged Windows executable stores it in `%TEMP%\Better-Schology\cached_files` so it is separate from the executable and persists between normal runs. Windows may remove files from its temporary directory during cleanup.

## Lint

```powershell
npm run lint
npm run lint:css
```

## Project Layout

- `server.py` - FastAPI application and route handlers
- `requirements.txt` - Python dependencies
- `api_utils.py` - Schoology API requests and data helpers
- `get_token.py` - authentication/session-token handling
- `HTML/` - frontend pages and static assets
- `libreoffice/` - bundled runtime used for presentation conversion
- `cached_files/` - generated local file cache for Python runs; packaged executable caches use `%TEMP%\Better-Schology\cached_files`

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

Better Schology is the project name; `CourseNest`, `StudyDock`, and `Classboard` remain alternative names for a friendly, focused dashboard.
