# Learning_Repository-
I post my learning projects here

## excel-model-converter-mvp
Minimal prototype that converts an Excel model into canonical and external JSON
representations with patching support for formula changes.

### Setup
```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

### Run the API
```bash
uvicorn excel_model_converter_mvp.main:app --reload
```

### Endpoints
- `POST /models/upload` (or `/models/convert`) with `file` (multipart)
- `POST /models/patch` with `file` and `previous_canonical` (JSON string)
