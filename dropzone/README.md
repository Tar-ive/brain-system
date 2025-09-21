Dropzone for agentic processing.

Place JSON records here (optionally with media) and push.
GitHub Actions processes new JSON files and moves them to `dropzone/processed/`.

Minimal JSON schema (flexible):
{
  "mood": 7,
  "tags": ["ocr","voice"],
  "notes": "optional free text",
  "transcript": "text from audio",     // optional
  "ocr_text": "text from image",       // optional
  "files": {                            // optional
    "audio": "clip.wav",
    "image": "photo.jpg"
  }
}

If you include files, place them alongside the JSON in this folder.
