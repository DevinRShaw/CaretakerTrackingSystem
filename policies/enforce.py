
async def masectomy_first_week(patient_records, patient_id) -> list[str]:
    flags = []

    cursor = patient_records.find({'patient_id' : patient_id})

    records = []
    async for doc in cursor: 
        records.append(doc)

    print(records)

    

     
    
    
async def masectomy_second_week(patient_records, patient_id) -> list[str]:
    flags = []




operation_policy_map = {
    "masectomy" : [masectomy_first_week, masectomy_second_week]
} 


async def enforce_policies(operation : str, patient_id : str, patient_records) -> list[str]:

    flags = []
    for policy in operation_policy_map[operation]:

        results = await policy(patient_records, patient_id)

        if results: 
            for result in results: 
                flags.append(results)

    return flags 
            


