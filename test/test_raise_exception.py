def can_drive(age):
    if age < 16:
        raise ValueError, 'Not old enough to drive'
    return True

if CONDITION == True:
    raise ValueError, HELPING_EXPLANATION