from pymongo import MongoClient
from datetime import datetime, timedelta

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


def mock_patient_case():

    client = MongoClient("mongodb://db:27017/")
    mydb = client["caregiver_app"]

    patient_cases = mydb["patient_cases"]
    patient_records = mydb["patient_records"]
    flag_explanations = mydb["flag_explanations"]

    patient_cases.insert_one({
        "patient_id": '1234', 
        "name": "Denise Shaw", 
        "operation": "masectomy",
        "operation_date": (datetime.now() - timedelta(days=1)).strftime("%d-%m-%Y"),
        "notes": "patient is stubborn and will under report pain levels, strong dislike of pain meds"   
    })


    flag_explanations.insert_one({
        "flag": 'masectomy_week_1_excess_pain', 
        "explanation": """Patient is exhibiting a pain level greater than 5 out of 10 in the first week. 
    This is an indication of incorrect dosage, medication or lack of adherence to medications.
    Consult your physician about current pain medication, pain should remain below a 5 during first week of healing."""
    })