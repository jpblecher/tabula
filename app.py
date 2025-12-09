from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import tabula
import pandas as pd
import tempfile
import os

app = FastAPI()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/extract")
async def extract_tables(file: UploadFile = File(...)):
    # Basic content-type check (optional but helpful)
    if file.content_type not in ("application/pdf", "application/octet-stream"):
        raise HTTPException(status_code=400, detail="Uploaded file must be a PDF")

    tmp_path = None

    try:
        # Save uploaded PDF to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp_path = tmp.name
            contents = await file.read()
            tmp.write(contents)

        # Use tabula-py to read all tables from all pages
        # returns a list of pandas DataFrames
        dfs = tabula.read_pdf(
            tmp_path,
            pages="all",
            multiple_tables=True
        )

        tables = []
        for idx, df in enumerate(dfs):
            # Replace NaN with empty string for cleaner JSON
            if isinstance(df, pd.DataFrame):
                df = df.fillna("")
                tables.append({
                    "index": idx,
                    "rows": df.to_dict(orient="records")
                })

        return JSONResponse(
            content={
                "table_count": len(tables),
                "tables": tables
            }
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error while extracting tables: {str(e)}"
        )
    finally:
        # Clean up temp file
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except OSError:
                pass
