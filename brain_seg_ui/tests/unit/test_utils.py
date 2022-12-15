from segmentation.utils import util_get_patient, util_get_scans
from segmentation.models import User
from segmentation import create_app

app = create_app()

def test_util_get_patient():
    with app.app_context():
        # ID of existing patient
        correct_patient_id = 2
        # wrong patient ID
        wrong_patient_id = 200
        
        patient_1 = util_get_patient(correct_patient_id)
        patient_2 = util_get_patient(wrong_patient_id)
        
        assert isinstance(patient_1, User) == True
        assert patient_2 == None 
    
    
def test_util_get_scans():
    with app.app_context():
        # ID of existing patient
        correct_patient_id = 2
        # wrong patient ID
        wrong_patient_id = 3
        
        response_1 = util_get_scans(correct_patient_id)
        response_2 = util_get_scans(wrong_patient_id)
        
        assert response_1['status'] == 200    
        assert response_2['status'] == 400
    
    
    
    