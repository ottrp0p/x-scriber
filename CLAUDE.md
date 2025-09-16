# Claude Code Assistant Rules for X-Scriber

## Project Overview
X-Scriber is a Python-based service that uses OpenAI Whisper for live transcription and OpenAI Chat Completions to generate Technical Requirements Documents (TRDs) from recorded audio.

## Folder Structure Restrictions

### CRITICAL: Data Folder Protection
**The assistant is NEVER allowed to edit, modify, or delete anything under the `data/` folder after initial setup.**

### Protected Directories:
- `data/project_metadata/` - Contains project metadata JSON files
- `data/audio-recordings/` - Contains audio chunk files from recordings
- `data/raw-transcriptions/` - Contains OpenAI Whisper transcription JSON files
- `data/output/` - Contains generated TRD markdown files

### Allowed Data Operations:
- **READ ONLY**: The assistant can read files in data directories for debugging or analysis
- **NO WRITE**: Never create, modify, or delete files in data directories
- **NO CLEANUP**: Never attempt to clean up or organize data directories

### Sample Data Exception:
The only exception is the initial sample project (project_id = "0") which serves as a reference:
- `data/project_metadata/0_metadata.json`
- `data/raw-transcriptions/0_transcription_*.json`
- `data/output/0_trd.md`

These sample files should remain untouched after initial creation.

## Allowed Code Modifications

### Safe to Edit:
- All Python source code in `xscriber/` and `config/`
- Templates in `xscriber/templates/`
- Static files in `xscriber/static/`
- Test files in `xscriber/tests/`
- Configuration files (settings.py, urls.py, etc.)
- Requirements and dependency files
- Documentation files (README.md, etc.)

### Code Quality Guidelines:
- Follow Django conventions and best practices
- Maintain test coverage for all new functionality
- Use type hints where appropriate
- Handle errors gracefully with proper logging
- Ensure all OpenAI API calls include proper error handling

## Development Workflow

### When Making Changes:
1. Always run tests before and after changes: `python manage.py test`
2. Use proper Django migration commands for model changes
3. Test API endpoints manually or with test suite
4. Verify frontend functionality works correctly

### Debugging Data Issues:
- Use read-only access to examine data files
- Check logs for processing errors
- Verify API responses and data flow
- Do NOT attempt to "fix" data files directly

## Security Considerations
- Never commit API keys or sensitive data
- Ensure `.env` file is properly configured
- Verify all API endpoints have proper authentication if needed
- Be cautious with file upload and audio recording permissions

## Emergency Recovery
If the data folder becomes corrupted:
1. Stop the Django server
2. Ask the user to backup their important project data
3. Guide the user through manual data recovery procedures
4. **Do NOT attempt automated data recovery or cleanup**

---

This CLAUDE.md file ensures the integrity of user-generated data while allowing full development access to the application code.