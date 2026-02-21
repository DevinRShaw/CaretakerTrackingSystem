from fastapi import FastAPI, Request, HTTPException, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates 

from pymongo import AsyncMongoClient

from contextlib import asynccontextmanager
import asyncio
from datetime import datetime
from typing import Annotated, Optional
import pprint

from utils.mocking import *
from logic.enforce import *
from logic.ai_response import * 

templates = Jinja2Templates(directory="/app/templates")

@asynccontextmanager
async def lifespan(app: FastAPI):
    mock_patient_case()
    yield

app = FastAPI(lifespan=lifespan)

#survey form 
@app.get("/", response_class=HTMLResponse)
async def root(request : Request):

    return templates.TemplateResponse(
        request=request, name="form.html"
    )

@app.post("/submit_form")
async def intake_form(
    request : Request,
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

    lm_response = await process_form(param_dict)

    return templates.TemplateResponse(
        "response.html",
        {"request": request, "response_text": lm_response}
    )
     


#background form processing begins
async def process_form(param_dict : dict[str, str]) -> str:

    async with AsyncMongoClient("mongodb://db:27017/") as client:

        db = client["caregiver_app"]

        patient_cases = db["patient_cases"]
        patient_records = db["patient_records"]
        flag_explanations = db["flag_explanations"]  

        #check user existence  
        patient_case = await patient_cases.find_one({"patient_id" : param_dict["patient_id"]})

        #record dating for time series checks 
        date = datetime.now().strftime("%d-%m-%Y")
        param_dict['date'] = date 

        #insert newest record 
        await patient_records.insert_one(param_dict)

        #policy violation flags 
        flags = await enforce_policies(patient_case, patient_records) 

        #small language model response w/ flag explanations, patient details 
        explanations = []
        for flag in flags: 
            print(flag) 
            explanation_doc = await flag_explanations.find_one({'flag' : flag[0]}) 
            explanations.append(explanation_doc['explanation']) 

        response = await construct_response(explanations, patient_case) 
