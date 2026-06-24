from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db

TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
TEST_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Tell FastAPI to use the test database instead of the real one
app.dependency_overrides[get_db] = override_get_db

# Create tables in the test database
Base.metadata.create_all(bind=engine)



client = TestClient(app)

#   Test that the endpoint returns a welcome message
def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "Tech Jobs API" in response.json()["message"]


#   Test that api/jobs returns 404 when the test database is empty
def test_get_jobs_empty():
    response = client.get("/api/jobs/")
    assert response.status_code == 404


#   Test that requesting a non-existent job returns 404
def test_get_single_job_not_found():
    response = client.get("/api/jobs/999")
    assert response.status_code == 404


#   Test that location filter returns 404 when no matching jobs exist
def test_get_jobs_with_location_filter():
    response = client.get("/api/jobs/?location=lagos")
    assert response.status_code == 404


#   Test that role filter returns 404 when no matching jobs exist
def test_get_jobs_with_role_filter():
    response = client.get("/api/jobs/?role=backend")
    assert response.status_code == 404