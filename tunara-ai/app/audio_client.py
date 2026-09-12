import asyncio
import json
import os
from typing import Any
from urllib.parse import quote, urlparse

import httpx

from .vocal_qa_models import VocalQaScore


class AudioClient:
    def __init__(self) -> None:
        self.base_url=os.getenv("ACESTEP_BASE_URL","http://127.0.0.1:8010").rstrip("/")
        self.tunara_audio_url=os.getenv("TUNARA_AUDIO_BASE_URL","http://127.0.0.1:8001").rstrip("/")
        self.timeout=float(os.getenv("ACESTEP_TIMEOUT_SECONDS","1800"))
        self.poll_seconds=float(os.getenv("ACESTEP_POLL_SECONDS","3"))
        self.model=os.getenv("ACESTEP_MODEL","acestep-v15-turbo")
        self.lm_model=os.getenv("ACESTEP_LM_MODEL","acestep-5Hz-lm-1.7B")
        self.lm_backend=os.getenv("ACESTEP_LM_BACKEND","mlx")
        self.max_attempts=int(os.getenv("VOCAL_QA_MAX_ATTEMPTS","5"))

    async def health(self) -> dict[str,Any]:
        async with httpx.AsyncClient(timeout=30) as client:
            response=await client.get(f"{self.base_url}/health")
            response.raise_for_status()
            return response.json()

    async def generate_song(self,request:Any,lyrics:str,batch_size:int=1) -> dict[str,Any]:
        del batch_size
        best=None
        reports=[]
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            for attempt in range(1,self.max_attempts+1):
                result=await self._generate_candidate(client,request,lyrics)
                qa=await self._qa_candidate(client,request.song_id,attempt,lyrics,result["reference"])
                reports.append(qa.model_dump())
                if best is None or qa.score>best["qa"].score:
                    best={"result":result,"qa":qa,"attempt":attempt}
                if qa.accepted:
                    break
            if best is None:
                raise RuntimeError("ACE-Step produced no candidate")
            if not best["qa"].accepted:
                review_id = f"{request.song_id}-needs-review"
                review_url = await self._persist_audio(
                    client,
                    review_id,
                    best["result"]["reference"],
                )
                raise RuntimeError(
                    "Vocal QA rejected all candidates; best candidate preserved at "
                    + review_url
                    + "; report="
                    + json.dumps(reports, ensure_ascii=False)
                )
            wav_url=await self._persist_audio(client,request.song_id,best["result"]["reference"])
            metadata=best["result"]["metadata"]
            return {"task_id":best["result"]["task_id"],"wav_urls":[wav_url],"audio_paths":[best["result"]["reference"]],"bpm":metadata.get("bpm"),"duration":metadata.get("duration"),"keyscale":metadata.get("keyscale","") ,"timesignature":metadata.get("timesignature","") ,"vocal_qa":best["qa"].model_dump(),"attempts":reports}

    async def _generate_candidate(self,client,request,lyrics):
        payload={"prompt":self._build_caption(request),"lyrics":lyrics,"thinking":False,"sample_mode":False,"use_format":False,"model":self.model,"vocal_language":self._language_code(request.language),"audio_duration":request.duration_seconds,"batch_size":1,"audio_format":"wav","inference_steps":8,"guidance_scale":1.0,"shift":3.0,"use_random_seed":True,"task_type":"text2music","lm_model_path":self.lm_model,"lm_backend":self.lm_backend,"allow_lm_batch":False,"use_tiled_decode":True}
        release=await client.post(f"{self.base_url}/release_task",json=payload)
        release.raise_for_status()
        task_id=self._find_value(release.json(),"task_id")
        if not task_id: raise RuntimeError(f"ACE-Step did not return task_id: {release.text}")
        deadline=asyncio.get_running_loop().time()+self.timeout
        while asyncio.get_running_loop().time()<deadline:
            query=await client.post(f"{self.base_url}/query_result",json={"task_id_list":[task_id]})
            query.raise_for_status()
            item=self._find_task_item(query.json(),str(task_id))
            if item:
                status=int(item.get("status",0)); results=self._decode_result(item.get("result","[]"))
                if status==1:
                    refs=[self._result_audio_reference(x) for x in results]; refs=[x for x in refs if x]
                    if not refs: raise RuntimeError("ACE-Step completed without audio files")
                    return {"task_id":str(task_id),"reference":refs[0],"metadata":results[0].get("metas",{}) or {}}
                if status==2: raise RuntimeError("ACE-Step generation failed")
            await asyncio.sleep(self.poll_seconds)
        raise TimeoutError(f"ACE-Step exceeded timeout of {self.timeout} seconds")

    async def _qa_candidate(self,client,song_id,attempt,lyrics,reference):
        source=await client.get(self._internal_audio_url(reference)); source.raise_for_status()
        response=await client.post(f"{self.tunara_audio_url}/api/vocal-qa/{song_id}/candidate/{attempt}",data={"canonical_lyrics":lyrics,"language":"es"},files={"audio":("candidate.wav",source.content,source.headers.get("content-type","audio/wav"))})
        response.raise_for_status()
        return VocalQaScore.model_validate(response.json())

    async def _persist_audio(self,client,song_id,reference):
        source=await client.get(self._internal_audio_url(reference)); source.raise_for_status()
        stored=await client.post(f"{self.tunara_audio_url}/api/permanent-audio/{song_id}",files={"audio":("ace-step-output.wav",source.content,source.headers.get("content-type","audio/wav"))})
        stored.raise_for_status(); url=str(stored.json().get("wav_url","")).strip()
        if not url: raise RuntimeError("Tunara Audio returned no permanent WAV URL")
        return url

    def _build_caption(self,request):
        parts=[request.prompt.strip(),request.genre.strip(),"sing the supplied lyrics in exact order; do not sing section labels; do not invent words"]
        if request.voice.strip(): parts.append(f"vocal style: {request.voice.strip()}")
        return ", ".join(x for x in parts if x)[:900]
    def _language_code(self,value):
        return {"spanish":"Spanish","espanol":"Spanish","español":"Spanish","english":"English","ingles":"English","inglés":"English"}.get(value.strip().lower(),value or "unknown")
    def _result_audio_reference(self,result): return str(result.get("file") or result.get("wave") or "").strip()
    def _internal_audio_url(self,reference):
        if reference.startswith("/v1/audio?"): return f"{self.base_url}{reference}"
        if reference.startswith(("http://","https://")):
            p=urlparse(reference)
            if p.path=="/v1/audio": return f"{self.base_url}{p.path}"+(f"?{p.query}" if p.query else "")
            return reference
        return f"{self.base_url}/v1/audio?path={quote(reference,safe='')}"
    def _find_value(self,value,key):
        if isinstance(value,dict):
            if key in value:return value[key]
            for c in value.values():
                f=self._find_value(c,key)
                if f is not None:return f
        elif isinstance(value,list):
            for c in value:
                f=self._find_value(c,key)
                if f is not None:return f
        return None
    def _find_task_item(self,value,task_id):
        if isinstance(value,dict):
            if str(value.get("task_id",""))==task_id:return value
            for c in value.values():
                f=self._find_task_item(c,task_id)
                if f is not None:return f
        elif isinstance(value,list):
            for c in value:
                f=self._find_task_item(c,task_id)
                if f is not None:return f
        return None
    def _decode_result(self,value):
        if isinstance(value,str):
            try:value=json.loads(value)
            except json.JSONDecodeError:return []
        if isinstance(value,dict):return [value]
        return [x for x in value if isinstance(x,dict)] if isinstance(value,list) else []
