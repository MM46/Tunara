import json
import os
import re
import tempfile
import unicodedata
from collections import Counter
from difflib import SequenceMatcher
from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

router=APIRouter(prefix="/api/vocal-qa",tags=["vocal-qa"])
MODEL=os.getenv("VOCAL_QA_WHISPER_MODEL","mlx-community/whisper-small-mlx")
REPORTS=Path(os.getenv("VOCAL_QA_REPORT_DIRECTORY","generated-vocal-qa")).resolve()
WORD=re.compile(r"[a-záéíóúüñ]+")
LABELS={"verse","verso","pre","coro","chorus","bridge","puente","outro","intro","instrumental"}


def norm(text):
    text=unicodedata.normalize("NFKD",text.lower())
    text="".join(c for c in text if not unicodedata.combining(c))
    return WORD.findall(text)

def lyric_words(text):
    return norm("\n".join(line for line in text.splitlines() if not line.strip().startswith("[")))

def score_qa(canonical,transcript):
    expected=lyric_words(canonical); actual=norm(transcript)
    if not expected:return {"accepted":False,"score":0,"coverage":0,"order_score":0,"hallucination_rate":1,"sung_section_labels":[],"transcript":transcript,"missing_words":[],"extra_words":actual}
    expected_counter=Counter(expected); actual_counter=Counter(actual)
    matched=sum(min(expected_counter[w],actual_counter[w]) for w in expected_counter)
    coverage=matched/len(expected)
    hallucinated=sum(max(0,count-expected_counter[word]) for word,count in actual_counter.items())
    hallucination=hallucinated/max(1,len(actual))
    order=SequenceMatcher(None,expected,actual,autojunk=False).ratio()
    transcript_start = " ".join(actual[:3])
    header_phrases = {
        "verse", "verso", "pre chorus", "pre coro", "chorus",
        "bridge", "puente", "outro", "intro", "instrumental",
        "final chorus", "coro final",
    }
    sung = [transcript_start] if transcript_start in header_phrases else []
    total=max(0,min(1,coverage*.55+order*.35+(1-hallucination)*.10-(.25 if sung else 0)))
    accepted=coverage>=.65 and order>=.62 and hallucination<=.28 and not sung
    missing=list((expected_counter-actual_counter).elements())[:40]
    extra=list((actual_counter-expected_counter).elements())[:40]
    return {"accepted":accepted,"score":round(total,4),"coverage":round(coverage,4),"order_score":round(order,4),"hallucination_rate":round(hallucination,4),"sung_section_labels":sung,"transcript":transcript.strip(),"missing_words":missing,"extra_words":extra}

@router.post("/{song_id}/candidate/{candidate}")
async def vocal_qa(song_id:str,candidate:int,canonical_lyrics:str=Form(...),language:str=Form("es"),audio:UploadFile=File(...)):
    safe=re.sub(r"[^A-Za-z0-9_-]","",song_id)
    if not safe: raise HTTPException(400,"Invalid song ID")
    with tempfile.NamedTemporaryFile(suffix=Path(audio.filename or "x.wav").suffix or ".wav",delete=False) as f:
        path=Path(f.name)
        while chunk:=await audio.read(1024*1024):f.write(chunk)
    try:
        import mlx_whisper
        result=mlx_whisper.transcribe(str(path),path_or_hf_repo=MODEL,language=language,word_timestamps=True,temperature=0.0)
        report=score_qa(canonical_lyrics,result.get("text", ""))
        report.update({"song_id":safe,"candidate":candidate,"model":MODEL})
        REPORTS.mkdir(parents=True,exist_ok=True)
        (REPORTS/f"{safe}-candidate-{candidate}.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        return report
    finally:
        path.unlink(missing_ok=True); await audio.close()
