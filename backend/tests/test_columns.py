"""Tests for columns endpoints."""

from __future__ import annotations


class TestCreateColumn:
    def test_create_column(self, client, auth_headers):
        resp = client.post(
            "/boards/board-1/columns",
            json={"name": "In Review"},
            headers=auth_headers,
        )
        assert resp.status_code == 201
        col = resp.json()
        assert col["name"] == "In Review"
        assert col["board_id"] == "board-1"
        assert col["position"] == 3  # appended after existing 3

    def test_create_column_empty_name_defaults(self, client, auth_headers):
        resp = client.post(
            "/boards/board-1/columns",
            json={"name": ""},
            headers=auth_headers,
        )
        assert resp.status_code == 201
        assert resp.json()["name"] == "New column"

    def test_create_column_board_not_found(self, client, auth_headers):
        resp = client.post(
            "/boards/nonexistent/columns",
            json={"name": "X"},
            headers=auth_headers,
        )
        assert resp.status_code == 404


class TestUpdateColumn:
    def test_rename_column(self, client, auth_headers):
        resp = client.patch(
            "/columns/col-1",
            json={"name": "Backlog"},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["name"] == "Backlog"

    def test_reorder_column(self, client, auth_headers):
        # col-1 is at position 0, move it to position 2
        resp = client.patch(
            "/columns/col-1",
            json={"position": 2},
            headers=auth_headers,
        )
        assert resp.status_code == 200

        # Check the new ordering via board detail
        detail = client.get("/boards/board-1", headers=auth_headers).json()
        col_names = [c["name"] for c in detail["columns"]]
        assert col_names == ["In Progress", "Done", "To Do"]

    def test_update_column_404(self, client, auth_headers):
        resp = client.patch(
            "/columns/nonexistent",
            json={"name": "X"},
            headers=auth_headers,
        )
        assert resp.status_code == 404


class TestDeleteColumn:
    def test_delete_column(self, client, auth_headers):
        resp = client.delete("/columns/col-1", headers=auth_headers)
        assert resp.status_code == 204

        resp = client.patch(
            "/columns/col-1",
            json={"name": "test"},
            headers=auth_headers,
        )
        assert resp.status_code == 404

    def test_delete_column_reindexes_siblings(self, client, auth_headers):
        # Delete middle column (col-2, position 1)
        client.delete("/columns/col-2", headers=auth_headers)

        detail = client.get("/boards/board-1", headers=auth_headers).json()
        positions = [c["position"] for c in detail["columns"]]
        assert positions == [0, 1]  # reindexed

    def test_delete_column_cascades_cards(self, client, auth_headers):
        """Cards in deleted column should be gone."""
        # col-1 has card-1 and card-2
        client.delete("/columns/col-1", headers=auth_headers)

        resp = client.patch(
            "/cards/card-1",
            json={"title": "test"},
            headers=auth_headers,
        )
        assert resp.status_code == 404

    def test_delete_column_404(self, client, auth_headers):
        resp = client.delete("/columns/nonexistent", headers=auth_headers)
        assert resp.status_code == 404
