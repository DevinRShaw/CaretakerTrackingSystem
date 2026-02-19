from pymongo import AsyncMongoClient


async def masectomy_first_week(patient_records) -> list[str]:
    flags = []


    
    
async def masectomy_second_week(patient_records) -> list[str]:
    flags = []


operation_policy_map = {
    "masectomy" : [masectomy_first_week, masectomy_second_week]
} 


async def enforce_policies(operation: str) -> list[str]:

    client = AsyncMongoClient("mongodb://db:27017/")
    mydb = client["caregiver_app"]
    patient_records = mydb["patient_records"]

    flags = []
    for policy in operation_policy_map[operation]:
        results = await operation(patient_records)
        if results: 
            for result in results: 
                flags.append(results)

    return flags 
            


