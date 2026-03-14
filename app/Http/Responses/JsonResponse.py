from pydantic import BaseModel


def JsonResponse(
    message: str = None, data: dict | BaseModel = None, status: bool = True
):
    if message and data:
        # Create a combined response
        return {"message": message, "data": data, "status": status}
    elif message:
        return {"message": message, "status": status}
    elif data:
        return {"data": data, "status": status}
    else:
        raise ValueError("Must provide either message or data")
