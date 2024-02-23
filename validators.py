from fastapi import HTTPException


def check_strong_password(password):
    if len(password) < 8:
        raise HTTPException(status_code=400, detail="Password is very small")
    digit = False
    lower = False
    upper = False
    for i in password:
        if i.isupper():
            upper = True
        elif i.isdigit():
            digit = True
        elif i.islower():
            lower = True
    return upper and lower and digit


def check_phone_number(phone_number: str):
    if len(phone_number) != 13:
        raise HTTPException(status_code=400, detail="Phone number is invalid")
    if not phone_number.startswith('+998'):
        raise HTTPException(status_code=400, detail="The phone number must start with +998")
    phone_number_ = phone_number[4:]
    for i in phone_number_:
        if not i.isdigit():
            raise HTTPException(status_code=400, detail="Phone number is invalid")
    return True
