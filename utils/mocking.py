"""
Healthcare Patient Management System - MongoDB Schema

Collections:
    
    PatientCase:
        {
            "_id": ObjectId,
            "patient_id": str,
            "name": str,
            "operation": str,
            "operation_date": datetime,
            "notes": str
        }
    
    PatientReports:
        {
            "_id": ObjectId,
            "patient_id": str,
            "case_id": ObjectId,  # Reference to PatientCase
            "date": datetime,
            "responses_fields": dict
        }
    
    RecordFlagging:
        {
            "_id": ObjectId,
            "patient_id": str,
            "report_id": ObjectId,  # Reference to PatientReports
            "date": datetime,
            "policy_violation": str
        }

Relationships:
    - PatientCase → PatientReports (one-to-many via case_id)
    - PatientReports → RecordFlagging (one-to-many via report_id)
"""

#start up code does not need an async but patient records may 
from pymongo import MongoClient
from datetime import datetime

def mock_patient_case():

    client = MongoClient("mongodb://db:27017/")
    mydb = client["caregiver_app"]
    mycol = mydb["patient_cases"]


    mycol.insert_one({
                "patient_id": 1234, 
                "name": "Denise Shaw", 
                "operation": "masectomy",
                "operation_date": "12-17-2025",
                "notes": "patient is stubborn and will under report pain levels, strong dislike of pain meds"   
            })


    

    

