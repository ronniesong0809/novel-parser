from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from utils.parser import parse_chapters, get_word_count
from uuid import uuid4
from utils.mongodb import db

app = FastAPI(
    title="Novel Parser",
    description="API for parsing novels in text format (supports English, Japanese, and Chinese)"
)


@app.post("/parse/")
async def parse_novel(file: UploadFile = File(...), locale: str = "en"):
    print(f"Received file: {locale}")
    if locale not in ["en", "ja", "zh"]:
        return JSONResponse(
            status_code=400,
            content={"error": "Unsupported locale. Use 'en', 'ja', or 'zh'"}
        )

    if not file.filename.endswith('.txt'):
        return JSONResponse(
            status_code=400,
            content={"error": "Only .txt files are supported"}
        )

    try:
        novel_id = str(uuid4())
        content = await file.read()
        text = content.decode('utf-8')
        chapters = parse_chapters(text, locale)

        chapter_stats = []
        for chapter in chapters:
            word_count = get_word_count(chapter["content"], locale)
            chapter_doc = {
                "novel_id": novel_id,
                "novel_name": file.filename.rsplit('.', maxsplit=1)[0],
                "title": chapter["title"],
                "content": chapter["content"],
                "paragraph_count": len(chapter["content"].split('\n')),
                "word_count": word_count,
                "locale": locale
            }
            db.insert_chapter(chapter_doc)
            chapter_stats.append(chapter_doc)

        return {
            "total_chapters": len(chapters),
            "chapters": chapter_stats,
            "structure": [{"id": chapter["id"], "title": chapter["title"]} for chapter in chapter_stats]
        }

    except UnicodeDecodeError:
        return JSONResponse(
            status_code=400,
            content={"error": "File must be encoded in UTF-8"}
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )


@app.get("/")
async def root():
    return {"message": "Welcome to Novel Parser API"}
