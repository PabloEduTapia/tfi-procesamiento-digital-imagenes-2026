from pathlib import Path

from fastapi.testclient import TestClient

from api.main import app


ROOT_DIR = Path(__file__).resolve().parents[1]


def test_process_endpoint_returns_png():
    client = TestClient(app)

    with (ROOT_DIR / "input" / "imagen.jpg").open("rb") as image:
        response = client.post(
            "/v1/images/process",
            files={"file": ("imagen.jpg", image, "image/jpeg")},
            data={
                "result": "simulated",
                "types": "protan",
                "severity": "7",
                "output_format": "png",
            },
        )

    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"
    assert len(response.content) > 0
