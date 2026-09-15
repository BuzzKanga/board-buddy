"""Tests for columns endpoints."""

from __future__ import annotations


class TestCreateColumn:
    def test_create_column(self, client):
        resp = client.post(
            "/boards/board-1/columns",
            json={"name": "In Review"},
        )
        assert resp.status_code == 201
        col = resp.json()
        assert col["name"] == "In Review"
        assert col["board_id"] == "board-1"
        assert col["position"] == 3  # appended after existing 3

    def test_create_column_empty_name_defaults(self, client):
        resp = client.post(
            "/boards/board-1/columns",
            json={"name": ""},
        )
        assert resp.status_code == 201
        assert resp.json()["name"] == "New column"

    def test_create_column_board_not_found(self, client):
        resp = client.post(
            "/boards/nonexistent/columns",
            json={"name": "X"},
        )
        assert resp.status_code == 404


class TestUpdateColumn:
    def test_rename_column(self, client):
        resp = client.patch(
            "/columns/col-1",
            json={"name": "Backlog"},
        )
        assert resp.status_code == 200
        assert resp.json()["name"] == "Backlog"

    def test_reorder_column(self, client):
        # col-1 is at position 0, move it to position 2
        resp = client.patch(
            "/columns/col-1",
            json={"position": 2},
        )
        assert resp.status_code == 200

        # Check the new ordering via board detail
        detail = client.get("/boards/board-1").json()
        col_names = [c["name"] for c in detail["columns"]]
        assert col_names == ["In Progress", "Done", "To Do"]

    def test_update_column_404(self, client):
        resp = client.patch(
            "/columns/nonexistent",
            json={"name": "X"},
        )
        assert resp.status_code == 404


class TestDeleteColumn:
    def test_delete_column(self, client):
        resp = client.delete("/columns/col-1")
        assert resp.status_code == 204

        resp = client.patch(
            "/columns/col-1",
            json={"name": "test"},
        )
        assert resp.status_code == 404

    def test_delete_column_reindexes_siblings(self, client):
        # Delete middle column (col-2, position 1)
        client.delete("/columns/col-2")

        detail = client.get("/boards/board-1").json()
        positions = [c["position"] for c in detail["columns"]]
        assert positions == [0, 1]  # reindexed

    def test_delete_column_cascades_cards(self, client):
        """Cards in deleted column should be gone."""
        # col-1 has card-1 and card-2
        client.delete("/columns/col-1")

        resp = client.patch(
            "/cards/card-1",
            json={"title": "test"},
        )
        assert resp.status_code == 404

    def test_delete_column_404(self, client):
        resp = client.delete("/columns/nonexistent")
        assert resp.status_code == 404
