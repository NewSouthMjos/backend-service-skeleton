from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, condecimal, validator


class UserIn(BaseModel):
    name: str

    @validator('name')
    def validate_name(cls, v):
        if len(v) > 30:
            raise ValueError('Name string should be not longer then 30')
        return v


class TransactionIn(BaseModel):
    uid: UUID
    user_id: int
    type: str
    amount: condecimal(decimal_places=2)
    timestamp: datetime

    @validator('type')
    def validate_type(cls, v):
        proper_types = {'DEPOSIT': 1, 'WITHDRAW': 2}
        if v.upper() not in proper_types.keys():
            raise ValueError(f'Transaction type should be one of: {list(proper_types.keys())}')
        return proper_types[v.upper()]
