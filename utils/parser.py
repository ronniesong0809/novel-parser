from typing import List, Tuple, Dict
import re
import jieba
import MeCab


def find_chapter_positions(text: str, locale: str = "en") -> List[Tuple[int, str]]:
    patterns = {
        "en": r'(?:^|\n)\s*(?:Chapter|CHAPTER)\s+(?:[0-9]+|[A-Z]+|[IVXLCDM]+).*?(?=\n|$)',
        "zh": r'(?:^|\n)\s*第[一二三四五六七八九十百千万\d]{1,5}[章].*?(?=\n|$)',
        "ja": r'(?:^|\n)\s*第[一二三四五六七八九十百千万\d]{1,5}[章話].*?(?=\n|$)',
    }

    pattern = patterns.get(locale, patterns["en"])
    matches = []
    for match in re.finditer(pattern, text):
        start = match.start()
        if text[start] == '\n':
            start += 1
        title = match.group().strip()
        matches.append((start, title))

    return matches


def get_word_count(text: str, locale: str = "en") -> int:
    if locale == "zh":
        return len(list(jieba.cut(text)))
    elif locale == "ja":
        mecab = MeCab.Tagger("-Owakati")
        return len(mecab.parse(text).strip().split())
    else:
        return len(text.split())


def extract_chapter_content(text: str, start: int, end: int, skip_first_line: bool = True) -> str:
    content = text[start:end]
    paragraphs = [p.strip() for p in content.split('\n') if p.strip()]
    if skip_first_line and paragraphs:
        paragraphs = paragraphs[1:]
    return '\n'.join(paragraphs)


def fallback_chapter_split(text: str, locale: str = "en", avg_chapter_size: int = 3000) -> List[Dict]:
    chapters = []
    text_length = len(text)
    start = 0
    chapter_num = 1

    chapter_titles = {
        "en": lambda n: f"Chapter {n}",
        "zh": lambda n: f"第{n}章",
        "ja": lambda n: f"第{n}章",
    }

    get_title = chapter_titles.get(locale, chapter_titles["en"])

    while start < text_length:
        end = min(start + avg_chapter_size, text_length)
        if end < text_length:
            next_newline = text.find('\n', end)
            if next_newline != -1:
                end = next_newline

        content = extract_chapter_content(
            text, start, end, skip_first_line=False)
        if content:
            chapters.append({
                "title": get_title(chapter_num),
                "content": content
            })
            chapter_num += 1
        start = end

    return chapters


def parse_chapters(text: str, locale: str = "en") -> List[Dict]:
    chapter_positions = find_chapter_positions(text, locale)

    if len(chapter_positions) < 4:
        return fallback_chapter_split(text, locale)

    chapters = []
    text_length = len(text)

    preface_titles = {
        "zh": "前言",
        "ja": "はじめに",
        "en": "Preface"
    }

    if chapter_positions and chapter_positions[0][0] > 0:
        preface_content = extract_chapter_content(
            text, 0, chapter_positions[0][0], skip_first_line=False)
        if preface_content:
            chapters.append({
                "title": preface_titles.get(locale, preface_titles["en"]),
                "content": preface_content
            })

    for i, (start_pos, title) in enumerate(chapter_positions):
        end_pos = text_length if i == len(
            chapter_positions) - 1 else chapter_positions[i + 1][0]
        content = extract_chapter_content(text, start_pos, end_pos)

        if not content:
            continue

        chapters.append({
            "title": title,
            "content": content
        })

    return chapters
