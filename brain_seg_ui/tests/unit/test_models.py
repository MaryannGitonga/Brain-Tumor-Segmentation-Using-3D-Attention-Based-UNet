import pytest
from segmentation.models import User

@pytest.fixture(scope='module')
def new_user():
    user = User(
        medical_id = 100,
        first_name = 'Jean',
        last_name = 'Doe',
        email = 'jean.doe@gmail.com',
        password = '12345678'
    )
    
    user.set_password(user.password)
    
    return user

def test_hashed_password(new_user):
    """Test New User
    
    GIVEN a user model
    WHEN a new user is created
    THEN check the password is hashed
    """
    
    assert new_user.password != '12345678'
    assert new_user.check_password('12345678')    
    

    