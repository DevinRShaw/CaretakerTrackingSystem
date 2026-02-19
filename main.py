from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates 
from contextlib import asynccontextmanager
import asyncio
from datetime import datetime

#synthetic data utlities 
from utils.mocking import *
from policies.enforce import *

templates = Jinja2Templates(directory="/app/templates")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # INSERT THE FAKE PATIENT CASE ENTRY   
    # yield not needed unless we want clean up behavior 
    mock_patient_case()
    yield

app = FastAPI(lifespan=lifespan)



#wellness form 
@app.get("/", response_class=HTMLResponse)
async def root(request : Request):

    return templates.TemplateResponse(
        request=request, name="form.html"
    )


#form submission 
@app.post("/submit_form")
async def intake_form(request : Request):
    body = await request.body()
    str_body = body.decode("utf-8")

    params = str_body.split("&")

    param_dict = {}
    for param in params: 
        param_tuple = param.split("=")
        param_dict[param_tuple[0]] = param_tuple[1]

    if param_dict['patientID'] == "":
        raise HTTPException(status_code=404, detail="Missing Patient ID")
    
    
    if param_dict['freeResponse'] != "":
        concern = param_dict['freeResponse']
        param_dict['freeResponse'] = " ".join(concern.split("+"))

    
    return await process_form(param_dict)



#TODO swap for async mongo client for fastapi best use 
from pymongo import AsyncMongoClient

#background form processing begins
async def process_form(param_dict : dict[str, str]):
    client = AsyncMongoClient("mongodb://db:27017/")
    mydb = client["caregiver_app"]

    patient_cases = mydb["patient_cases"]
    patient_records = mydb["patient_records"]

    #check user existence  
    patient_existence = await patient_cases.find_one({"patient_id" : int(param_dict["patientID"])})

    #Non-existant user
    if patient_existence is None:
        raise HTTPException(status_code=409, detail="non-existant patientID")

    #record dating for time series checks 
    date = datetime.now().strftime("%d-%m-%Y")
    param_dict['date'] = date 

    #insert newest record 
    patient_records.insert_one(param_dict)

    flags = await enforce_policies(patient_existence['operation'])  

    if not flags: 
        return ("no explicit flags have been found in patient records")
    
    return flags 