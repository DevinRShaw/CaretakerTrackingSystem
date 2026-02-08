from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates 
import asyncio

app = FastAPI()
templates = Jinja2Templates(directory="/home/devin/caregive/caregive/templates")

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
async def process_form(param_dict : dict):
    client = AsyncMongoClient("mongodb://localhost:27017/")
    mydb = client["caregiver_app"]
    mycol = mydb["patient_cases"]

    #check user existence  
    patient_record = mycol.find_one({"patientID" : param_dict["patientID"]})

    #Non-existant user
    if patient_record is None:
        raise HTTPException(status_code=409, detail="Non-existant patientID")
    
    
    

    #mongodb retreive the previous 5 wellness entries or less with patientID

    #branch based on time since operation in patient record (healing period)
        #apply healing period dependant checks
            #if warning flag    
                #create warning message
    
    #pass any warnings and questions/concerns into tinyllama1.1b as context
        '''prompt
            Given that our patient has had {operation} and is experiencing {warning},
            use {5 previous reports} to give a warning to their caregiver 
            emphasize contacting primary care providers with questions relevant to issue
        '''

        
    

    return param_dict
