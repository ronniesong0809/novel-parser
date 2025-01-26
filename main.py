from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from utils.parser import parse_chapters, get_word_count

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
        content = await file.read()
        text = content.decode('utf-8')

        chapters = parse_chapters(text, locale)

        total_chapters = len(chapters)
        chapter_stats = []

        for chapter in chapters:
            word_count = get_word_count(chapter["content"], locale)
            chapter_stats.append({
                "title": chapter["title"],
                "paragraph_count": len(chapter["content"].split('\n')),
                "word_count": word_count,
                "preview": chapter["content"]
            })

        return {
            "total_chapters": total_chapters,
            "chapters": chapter_stats,
            "structure": [chapter["title"] for chapter in chapters]
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
