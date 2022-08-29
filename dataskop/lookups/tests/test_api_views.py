import base64

import pytest
from rest_framework_api_key.models import APIKey

pytestmark = pytest.mark.django_db


def test_lookup_api(client):
    r = client.post(
        "/api/internallookups/",
        data={"lookups": ["id1", "id2", "id3"]},
        content_type="application/json",
    )
    assert r.status_code == 403

    _, key = APIKey.objects.create_key(name="key-for-testing")
    headers = {"HTTP_X_DATASKOP_API_KEY": key}

    # Create new lookups
    r = client.post(
        "/api/internallookups/",
        data={"lookups": ["id1", "id2", "id3"]},
        content_type="application/json",
        **headers,
    )
    assert r.status_code == 202

    # Ensure null values are not visible
    r = client.get(f"/api/lookups/?l=id1&l=id2&l=id3")
    assert r.status_code == 200
    assert r.data == []

    # Update values
    r = client.put(
        "/api/internallookups/1312/",
        data={
            "id1": base64.b64encode("data1".encode("ascii")).decode("ascii"),
            "id2": base64.b64encode("data2".encode("ascii")).decode("ascii"),
        },
        content_type="application/json",
        **headers,
    )
    assert r.status_code == 204

    # Check for updated values
    r = client.get(f"/api/lookups/?l=id1&l=id2&l=id3")
    assert r.status_code == 200
    assert list(r.data[0].values()) == [
        "id1",
        base64.b64encode("data1".encode("ascii")).decode("ascii"),
    ]
    assert list(r.data[1].values()) == [
        "id2",
        base64.b64encode("data2".encode("ascii")).decode("ascii"),
    ]
    assert len(r.data) == 2
