import pprint
from datetime import datetime

async def masectomy_first_week(patient_case, patient_records) -> list[str]:

    policy_flags = []

    #patient records sorted by most recent 
    cursor = patient_records.find({'patient_id' : patient_case['patient_id']}).sort({'_id' : -1})

    #date comparison checks
    operation_date = datetime.strptime(patient_case['operation_date'], "%d-%m-%Y")

    #one off checks during aggregation 
    async for doc in cursor: 

        doc_date = datetime.strptime(doc['date'], "%d-%m-%Y")

        #date range check 
        if (doc_date - operation_date ).days > 7: 
            continue

        if int(doc['pain_level']) >= 5:
            policy_flags.append({'week_1_excess_pain' : doc['pain_level']})

    return policy_flags




operation_policy_map = {
    "masectomy" : [(masectomy_first_week, (1,7))]
} 


async def enforce_policies(patient_case : dict[str], patient_records) -> list[str]:

    flags = []
    for policy in operation_policy_map[patient_case['operation']]:

        policy_function = policy[0]
        date_range = policy[1]

        operation_date = datetime.strptime(patient_case['operation_date'], "%d-%m-%Y")

        days_since = (datetime.now() - operation_date).days
        if not (days_since >= date_range[0] and days_since <= date_range[1]):
           continue  

        results = await policy_function(patient_case, patient_records)

        if not results: 
            continue

        for result in results: 
            flags.append(result)

    return flags 
            


