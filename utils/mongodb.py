from pymongo import MongoClient
import os
from typing import Dict, List
from dotenv import load_dotenv

load_dotenv()


class MongoDB:
    def __init__(self):
        self.client = MongoClient(
            os.getenv("MONGODB_URI", "mongodb://localhost:27017"))
        self.db = self.client.novel_parser
        self.chapters = self.db.chapters

    def insert_chapter(self, chapter_doc: Dict) -> str:
        result = self.chapters.insert_one(chapter_doc)
        print(f"Chapter {chapter_doc['title']} inserted successfully with ID: {result.inserted_id}")
        return str(result.inserted_id)

    def get_chapter(self, chapter_id: str) -> Dict:
        return self.chapters.find_one({"_id": chapter_id})

    def get_chapters_by_filename(self, filename: str) -> List[Dict]:
        return list(self.chapters.find({"filename": filename}))

    def close(self):
        self.client.close()


# Create a singleton instance
db = MongoDB()
