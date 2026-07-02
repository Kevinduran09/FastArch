from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel
from fastarch import controller,get,include_controllers,post


class PetCreateRequest(BaseModel):
    name: str
    type: str
    
@controller(prefix="/pets")
class PetsController:
    @get("/dogs")
    async def get_dogtypes(self):
        return [
            "Border Collie",
            "Golden Retriever",
            "German Shepherd",
            "French Bulldog",
            "Poodle"
        ]

    @get("/cats")
    async def get_cattypes(self):
        return [
            "Persian",
            "Siamese",
            "Maine Coon",
            "Bengal",
            "Ragdoll"
        ]
    @post("/")
    async def create_cat(self,data:PetCreateRequest):
        return {
            "message":"Pet created",
            "pet":data.model_dump()
        } 
    


def test_controller_route_work():
    app = FastAPI()
    
    include_controllers(app,[PetsController],prefix="/api/v1")
    
    client = TestClient(app)
    
    response = client.get("/api/v1/pets/dogs")
    
    assert response.status_code == 200
    assert response.json() ==   [
            "Border Collie",
            "Golden Retriever",
            "German Shepherd",
            "French Bulldog",
            "Poodle"
        ]  

def test_controller_bad_route():
    app = FastAPI()
    
    include_controllers(app,[PetsController],prefix="/api/v1")
    
    client = TestClient(app)
    
    response = client.get("/api/v1/pets/raccons")
    
    assert response.status_code == 404
    
    
def test_controller_create():
    app = FastAPI()

    include_controllers(app, [PetsController], prefix="/api/v1")

    client = TestClient(app)

    response = client.post(
        "/api/v1/pets/",
        json={
            "name": "Firulais",
            "type": "dog"
        }
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": "Pet created",
        "pet": {
            "name": "Firulais",
            "type": "dog"
        }
    }

def test_self_is_not_exposed_in_openapi():
    app = FastAPI()

    include_controllers(app, [PetsController], prefix="/api/v1")

    client = TestClient(app)

    schema = client.get("/openapi.json").json()

    parameters = schema["paths"]["/api/v1/pets/dogs"]["get"].get("parameters", [])

    assert all(parameter["name"] != "self" for parameter in parameters)
