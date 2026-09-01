from enum import Enum

class UserRole(str, Enum):
    PERSONNEL = "personnel"
    WELFARE_OFFICER = "welfare_officer"
    MEDICAL_OFFICER = "medical_officer"
    COMMANDER = "commander"
    ADMIN = "admin"

ALL_ROLES = [role.value for role in UserRole]
