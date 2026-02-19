from pymongo import AsyncMongoClient


async def masectomy_first_week() -> list[str]:
    flags = []


async def masectomy_second_week() -> list[str]:
    flags = []


operation_policy_map = {
    "masectomy" : [masectomy_first_week, masectomy_second_week]
} 


async def enforce_policies(operation: str):
    flags = []
    for policy in operation_policy_map[operation]:
        results = await operation()
        if results: 
            for result in results: 
                flags.append(results)

    return flags 
            


