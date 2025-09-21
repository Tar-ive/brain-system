#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_ROOT = REPO_ROOT / "mvp" / "data"
DROP_ROOT = REPO_ROOT / "dropzone"

DATE_FMT = "%Y-%m-%d"
STAMP_FMT = "%Y%m%d_%H%M%S"


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class EntryPaths:
    base: Path
    note: Path
    meta: Path
    transcript: Path
    entry_id: str
    date_str: str

    @classmethod
    def from_now(cls, data_root: Path, t: datetime) -> "EntryPaths":
        date_str = t.strftime(DATE_FMT)
        entry_id = t.strftime(STAMP_FMT)
        base = data_root / "raw" / date_str
        base.mkdir(parents=True, exist_ok=True)
        (data_root / "notes").mkdir(parents=True, exist_ok=True)
        return cls(
            base=base,
            note=data_root / "notes" / f"{date_str}.md",
            meta=base / f"{entry_id}.json",
            transcript=base / f"{entry_id}_transcript.txt",
            entry_id=entry_id,
            date_str=date_str,
        )


def append_note(note_path: Path, when: datetime, *, mood: Any, tags: Any, transcript: Optional[str], image_name: Optional[str], ocr_text: Optional[str]) -> None:
    header = f"# Temporal Log {when.strftime(DATE_FMT)}\n\n"
    if not note_path.exists():
        note_path.write_text(header, encoding="utf-8")
    local_time = when.astimezone().strftime("%H:%M")
    lines = [f"## {local_time} Entry", f"- mood: {mood if mood is not None else ''}"]
    if tags:
        if isinstance(tags, (list, tuple)):
            tags_str = ", ".join(map(str, tags))
        else:
            tags_str = str(tags)
        lines.append(f"- tags: {tags_str}")
    if image_name:
        lines.append(f"- image: {image_name}")
    snippet = (transcript or "").strip()
    preview = snippet[:180] + ("…" if len(snippet) > 180 else "") if snippet else "—"
    lines.append(f"- transcript snippet: {preview}")
    if ocr_text:
        p2 = ocr_text[:180] + ("…" if len(ocr_text) > 180 else "")
        lines.append(f"- image text snippet: {p2}")
    with note_path.open("a", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n\n")


def process_one(json_path: Path) -> str:
    t = now_utc()
    paths = EntryPaths.from_now(DATA_ROOT, t)
    data = json.loads(json_path.read_text(encoding="utf-8"))

    files = data.get("files") or {}
    image_file = files.get("image")
    image_src = json_path.parent / image_file if image_file else None

    image_name = None
    if image_src and image_src.exists():
        image_name = f"{paths.entry_id}_image{Path(image_src.name).suffix or '.jpg'}"
        shutil.copy2(image_src, paths.base / image_name)

    transcript = data.get("transcript")
    if transcript:
        paths.transcript.write_text(transcript, encoding="utf-8")

    record = {
        "entry_id": paths.entry_id,
        "received_at": t.isoformat(),
        "language": data.get("language", "en"),
        "metadata": {
            "mood": data.get("mood"),
            "tags": data.get("tags"),
            "notes": data.get("notes"),
        },
        "transcript": transcript,
        "files": {
            "audio": files.get("audio"),
            "transcript": str(paths.transcript.relative_to(DATA_ROOT)) if transcript else None,
            "image": image_name,
        },
        "whisper": None,
        "ocr_text": data.get("ocr_text"),
    }
    paths.meta.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")

    append_note(
        paths.note,
        t,
        mood=record["metadata"]["mood"],
        tags=record["metadata"]["tags"],
        transcript=transcript,
        image_name=image_name,
        ocr_text=record["ocr_text"],
    )
    return paths.entry_id


def summarise(data_root: Path) -> Dict[str, Any]:
    raw_root = data_root / "raw"
    per_day: Dict[str, Dict[str, Any]] = {}
    for day_dir in sorted(raw_root.glob("*/")):
        date = day_dir.name
        day = per_day.setdefault(date, {"entry_count": 0, "mood_values": [], "words_total": 0})
        for jf in day_dir.glob("*.json"):
            meta = json.loads(jf.read_text(encoding="utf-8"))
            day["entry_count"] += 1
            mood = meta.get("metadata", {}).get("mood")
            try:
                if mood is not None:
                    day["mood_values"].append(float(mood))
            except Exception:
                pass
            words = len((meta.get("transcript") or "").split())
            day["words_total"] += words
    ordered: List[Tuple[str, Dict[str, Any]]] = []
    for d in sorted(per_day.keys()):
        dd = per_day[d]
        mv = dd.pop("mood_values")
        mood_avg = sum(mv) / len(mv) if mv else None
        ordered.append((d, {"entry_count": dd["entry_count"], "mood_avg": (round(mood_avg, 2) if mood_avg is not None else None), "words_total": dd["words_total"]}))
    prev = None
    for _, st in ordered:
        if prev:
            st["entry_delta"] = st["entry_count"] - prev.get("entry_count", 0)
            pm, cm = prev.get("mood_avg"), st.get("mood_avg")
            if pm is not None and cm is not None:
                st["mood_delta"] = round(cm - pm, 2)
        prev = st
    summary = {
        "updated_at": now_utc().isoformat(),
        "days": {d: s for d, s in ordered},
        "latest": (ordered[-1][1] if ordered else None),
    }
    (data_root / "temporal_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    return summary


def main() -> None:
    DATA_ROOT.mkdir(parents=True, exist_ok=True)
    (DATA_ROOT / "notes").mkdir(parents=True, exist_ok=True)
    (DATA_ROOT / "raw").mkdir(parents=True, exist_ok=True)
    (DROP_ROOT / "processed").mkdir(parents=True, exist_ok=True)

    json_files = [p for p in DROP_ROOT.glob("*.json") if p.is_file()]
    processed: List[Path] = []
    for jf in sorted(json_files):
        try:
            eid = process_one(jf)
            print(f"[ok] processed {jf.name} -> entry {eid}")
            processed.append(jf)
        except Exception as e:
            print(f"[err] failed {jf}: {e}")
    summarise(DATA_ROOT)
    for jf in processed:
        ts = now_utc().strftime(STAMP_FMT)
        target = DROP_ROOT / "processed" / f"{ts}_{jf.name}"
        shutil.move(str(jf), str(target))


if __name__ == "__main__":
    main()
