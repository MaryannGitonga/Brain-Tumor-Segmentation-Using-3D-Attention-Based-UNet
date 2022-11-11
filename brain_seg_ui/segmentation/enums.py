import enum

class Roles(enum.Enum):
    neurologist = 'neurologist'
    sonographer = 'sonographer'
    patient = 'patient'
    
    
class ScanTypes(enum.Enum):
    combined = 'combined'
    predicted = 'predicted'