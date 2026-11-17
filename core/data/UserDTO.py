"""
Legacy UserDTO Dataclass.
"""
from dataclasses import dataclass


@dataclass
class UserDTO:
    user_name: str
    user_password: str

