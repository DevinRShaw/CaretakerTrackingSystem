from fastapi import FastAPI, Request, HTTPException, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates 

from pymongo import AsyncMongoClient

from contextlib import asynccontextmanager
import asyncio
from datetime import datetime
from typing import Annotated, Optional
import pprint


from transformers import pipeline
import torch

from utils.mocking import *
from policies.enforce import *

templates = Jinja2Templates(directory="/app/templates")

@asynccontextmanager
async def lifespan(app: FastAPI):
    mock_patient_case()
    yield

app = FastAPI(lifespan=lifespan)



#wellness form 
@app.get("/", response_class=HTMLResponse)
async def root(request : Request):

    return templates.TemplateResponse(
        request=request, name="form.html"
    )



@app.post("/submit_form")
async def intake_form(
    patient_id: Annotated[str, Form()],
    pain_level: Annotated[int, Form()],
    pain_trend: Annotated[str, Form()],
    energy_level: Annotated[int, Form()],
    energy_trend: Annotated[str, Form()],
    drinking: Annotated[str, Form()],
    smoking: Annotated[str, Form()],
    wound_color: Annotated[str, Form()],
    free_response: Annotated[Optional[str], Form()] = None,
):
    
    param_dict = {
        "patient_id": patient_id,
        "pain_level": pain_level,
        "pain_trend": pain_trend,
        "energy_level": energy_level,
        "energy_trend": energy_trend,
        "drinking": drinking,
        "smoking": smoking,
        "wound_color": wound_color,
        "free_response": free_response.strip() if free_response else None,
    }

    flags = await process_form(param_dict)

    if not flags: 
        return ("no explicit flags have been found in patient records")
    
    return flags


#background form processing begins
async def process_form(param_dict : dict[str, str]):

    async with AsyncMongoClient("mongodb://db:27017/") as client:

        db = client["caregiver_app"]

        patient_cases = db["patient_cases"]
        patient_records = db["patient_records"]

        #check user existence  
        patient_case = await patient_cases.find_one({"patient_id" : param_dict["patient_id"]})

        #Non-existant user
        if patient_case is None:
            raise HTTPException(status_code=409, detail="non-existant patient_id")

        #record dating for time series checks 
        date = datetime.now().strftime("%d-%m-%Y")
        param_dict['date'] = date 

        #insert newest record 
        await patient_records.insert_one(param_dict)

        #policy violation flags 
        return await enforce_policies(patient_case, patient_records) 






_hf_pipeline = None
_local_lock = asyncio.Lock()


async def call_local_slm(
    prompt: str,
    model_name: str = "gpt2",
    max_new_tokens: int = 128,
    device: str | int | torch.device = "cpu",
) -> dict:
    """Use `transformers.pipeline` for cached local text generation.

    - `device` can be:
        - a string like 'cpu' or 'cuda'
        - an int device index (0 for first CUDA device)
        - a `torch.device` instance
    Returns a dict with `generated_text`.
    """
    global _hf_pipeline

    # normalize device to pipeline's `device` arg (int: -1 for CPU)
    if isinstance(device, torch.device):
        device = -1 if device.type == "cpu" else 0
    elif isinstance(device, str):
        device = -1 if device == "cpu" else 0

    async with _local_lock:
        if _hf_pipeline is None:
            def _make_pipeline():
                return pipeline("text-generation", model=model_name, device=device)

            _hf_pipeline_local = await asyncio.to_thread(_make_pipeline)
            _hf_pipeline = _hf_pipeline_local

    def _generate():
        outputs = _hf_pipeline(prompt, max_new_tokens=max_new_tokens, do_sample=False)
        # pipeline returns list of dicts with 'generated_text'
        return outputs[0]["generated_text"] if outputs else ""

    generated = await asyncio.to_thread(_generate)
    return {"generated_text": generated}
