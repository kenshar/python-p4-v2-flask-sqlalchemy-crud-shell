import pytest
from models import db, Pet
from app import app


@pytest.fixture
def client():
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test_app.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['TESTING'] = True
    
    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.drop_all()


@pytest.fixture
def init_database(client):
    """Fixture to set up initial pets for testing"""
    with app.app_context():
        pet1 = Pet(name="Fido", species="Dog")
        pet2 = Pet(name="Whiskers", species="Cat")
        db.session.add(pet1)
        db.session.add(pet2)
        db.session.commit()
        return [pet1, pet2]


class TestPetModel:
    """Test suite for Pet model CRUD operations"""

    def test_create_pet(self, client):
        """Test creating a new pet and persisting to database"""
        with app.app_context():
            pet = Pet(name="Buddy", species="Dog")
            db.session.add(pet)
            db.session.commit()
            
            assert pet.id is not None
            assert pet.name == "Buddy"
            assert pet.species == "Dog"
            
            # Verify it's in the database
            fetched_pet = Pet.query.filter_by(name="Buddy").first()
            assert fetched_pet is not None
            assert fetched_pet.name == "Buddy"

    def test_read_all_pets(self, client, init_database):
        """Test querying all pets"""
        with app.app_context():
            pets = Pet.query.all()
            assert len(pets) == 2
            assert any(p.name == "Fido" for p in pets)
            assert any(p.species == "Cat" for p in pets)

    def test_read_first_pet(self, client, init_database):
        """Test querying first pet"""
        with app.app_context():
            pet = Pet.query.first()
            assert pet is not None
            assert pet.id == 1

    def test_filter_by_species(self, client, init_database):
        """Test filtering pets by species"""
        with app.app_context():
            cats = Pet.query.filter_by(species="Cat").all()
            assert len(cats) == 1
            assert cats[0].name == "Whiskers"

    def test_filter_by_id(self, client, init_database):
        """Test filtering pets by id"""
        with app.app_context():
            pet = Pet.query.filter_by(id=1).first()
            assert pet is not None
            assert pet.name == "Fido"

    def test_filter_with_expression(self, client, init_database):
        """Test filtering with boolean expressions"""
        with app.app_context():
            # Filter for cats
            cats = Pet.query.filter(Pet.species == 'Cat').all()
            assert len(cats) == 1
            assert cats[0].name == "Whiskers"
            
            # Filter for names starting with F
            f_pets = Pet.query.filter(Pet.name.startswith('F')).all()
            assert len(f_pets) == 1
            assert f_pets[0].name == "Fido"

    def test_get_pet_by_id(self, client, init_database):
        """Test getting pet by primary key using session.get"""
        with app.app_context():
            pet = db.session.get(Pet, 1)
            assert pet is not None
            assert pet.name == "Fido"
            
            # Test non-existent ID
            pet_none = db.session.get(Pet, 999)
            assert pet_none is None

    def test_order_by_species(self, client, init_database):
        """Test ordering query results"""
        with app.app_context():
            pets = Pet.query.order_by('species').all()
            # Cats should come before Dogs alphabetically
            assert pets[0].species == "Cat"
            assert pets[1].species == "Dog"

    def test_update_pet(self, client, init_database):
        """Test updating a pet's attributes"""
        with app.app_context():
            pet = Pet.query.filter_by(name="Fido").first()
            original_id = pet.id
            
            pet.name = "Fido the mighty"
            db.session.commit()
            
            # Verify update persisted
            updated_pet = Pet.query.filter_by(id=original_id).first()
            assert updated_pet.name == "Fido the mighty"

    def test_delete_pet(self, client, init_database):
        """Test deleting a specific pet"""
        with app.app_context():
            pet = Pet.query.filter_by(name="Fido").first()
            db.session.delete(pet)
            db.session.commit()
            
            # Verify deletion
            pets = Pet.query.all()
            assert len(pets) == 1
            assert not any(p.name == "Fido" for p in pets)

    def test_delete_all_pets(self, client, init_database):
        """Test deleting all pets using query.delete()"""
        with app.app_context():
            result = Pet.query.delete()
            assert result == 2
            db.session.commit()
            
            # Verify all deleted
            pets = Pet.query.all()
            assert len(pets) == 0

    def test_count_pets(self, client, init_database):
        """Test counting pets using func.count"""
        from sqlalchemy import func
        
        with app.app_context():
            count = db.session.query(func.count(Pet.id)).first()
            assert count[0] == 2

    def test_repr_method(self):
        """Test the __repr__ method of Pet"""
        pet = Pet(id=1, name="Fido", species="Dog")
        assert repr(pet) == "<Pet 1, Fido, Dog>"


class TestCodeGradePlaceholder:
    """Original placeholder test"""
    def test_codegrade_placeholder(self):
        assert 1 == 1
