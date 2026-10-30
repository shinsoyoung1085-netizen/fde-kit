"""실행 중인 서버의 CRUD와 검증을 확인한다."""
import httpx


def main():
    with httpx.Client(base_url="http://127.0.0.1:8000", timeout=10) as client:
        response = client.get("/")
        assert response.status_code == 200 and '<html lang="ko">' in response.text
        for asset, content_type in (("app.js", "javascript"), ("style.css", "text/css")):
            response = client.get(f"/static/{asset}")
            assert response.status_code == 200 and content_type in response.headers["content-type"]
        print("root/static assets -> PASS")
        response = client.get("/api/meta")
        assert response.status_code == 200, response.text
        assert response.json()["item"]["label"] == "품목"
        print("GET /api/meta -> 200")
        response = client.post("/api/item", json={"name": "테스트 품목", "qty": 3})
        assert response.status_code == 201, response.text
        item = response.json()
        assert item["min_qty"] == 0 and item["unit"] == "개"
        assert item["created_at"] and item["updated_at"]
        print(f"POST /api/item -> 201, id={item['id']}, qty=3, defaults OK")
        path = f"/api/item/{item['id']}"
        try:
            response = client.get(path)
            assert response.status_code == 200 and response.json() == item
            print(f"GET {path} -> 200, created item matches")
            response = client.get("/api/item")
            assert response.status_code == 200 and item in response.json()
            response = client.put(path, json={"qty": 5})
            assert response.status_code == 200 and response.json()["qty"] == 5
            assert response.json()["name"] == item["name"]
            for payload in ({}, {"name": " "}, {"name": "x", "qty": "3"},
                            {"name": "x", "qty": True}, {"name": "x", "extra": 1}):
                response = client.post("/api/item", json=payload)
                assert response.status_code == 422, response.text
                assert any("가" <= char <= "힣" for char in response.json()["detail"])
            assert client.get("/api/missing").status_code == 404
            assert client.post("/api/missing", json={}).status_code == 404
            print("list/update/required/type/unknown-field/unknown-entity checks -> PASS")
        finally:
            response = client.delete(path)
            assert response.status_code == 204, response.text
        assert client.get(path).status_code == 404
        assert client.delete(path).status_code == 404
        print("DELETE -> 204, subsequent GET/DELETE -> 404")
        print("PASS")


if __name__ == "__main__":
    main()
