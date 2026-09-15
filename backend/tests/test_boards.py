"""Tests for boards endpoints."""

from __future__ import annotations


class TestListBoards:
    def test_lists_seeded_boards(self, client):
        resp = client.get("/boards")
        assert resp.status_code == 200
        boards = resp.json()
        assert len(boards) == 2
        names = [b["name"] for b in boards]
        assert "Product Launch" in names
        assert "Bug Tracker" in names

    def test_boards_sorted_by_created_at(self, client):
        resp = client.get("/boards")
        boards = resp.json()
        dates = [b["created_at"] for b in boards]
        assert dates == sorted(dates)


class TestCreateBoard:
    def test_create_with_name(self, client):
        resp = client.post(
            "/boards",
            json={"name": "Sprint 12"},
        )
        assert resp.status_code == 201
        board = resp.json()
        assert board["name"] == "Sprint 12"
        assert "id" in board
        assert "created_at" in board

    def test_create_with_empty_name_defaults(self, client):
        resp = client.post(
            "/boards",
            json={"name": "  "},
        )
        assert resp.status_code == 201
        assert resp.json()["name"] == "Untitled board"

    def test_create_board_creates_default_columns(self, client):
        resp = client.post(
            "/boards",
            json={"name": "Test Board"},
        )
        board_id = resp.json()["id"]

        detail = client.get(f"/boards/{board_id}")
        columns = detail.json()["columns"]
        assert len(columns) == 3
        assert [c["name"] for c in columns] == ["To Do", "In Progress", "Done"]


class TestGetBoard:
    def test_get_board_detail(self, client):
        resp = client.get("/boards/board-1")
        assert resp.status_code == 200
        data = resp.json()
        assert data["name"] == "Product Launch"
        assert "columns" in data
        assert "cards" in data
        assert "labels" in data
        assert "card_labels" in data

    def test_columns_sorted_by_position(self, client):
        resp = client.get("/boards/board-1")
        columns = resp.json()["columns"]
        positions = [c["position"] for c in columns]
        assert positions == sorted(positions)

    def test_get_board_404(self, client):
        resp = client.get("/boards/nonexistent")
        assert resp.status_code == 404


class TestUpdateBoard:
    def test_rename_board(self, client):
        resp = client.patch(
            "/boards/board-1",
            json={"name": "Renamed"},
        )
        assert resp.status_code == 200
        assert resp.json()["name"] == "Renamed"

    def test_update_board_404(self, client):
        resp = client.patch(
            "/boards/nonexistent",
            json={"name": "X"},
        )
        assert resp.status_code == 404


class TestDeleteBoard:
    def test_delete_board(self, client):
        resp = client.delete("/boards/board-1")
        assert resp.status_code == 204

        # Verify it's gone
        resp = client.get("/boards/board-1")
        assert resp.status_code == 404

    def test_delete_cascades(self, client):
        """Deleting a board should remove its columns, cards, labels."""
        detail = client.get("/boards/board-1").json()
        col_ids = [c["id"] for c in detail["columns"]]

        client.delete("/boards/board-1")

        # Columns should be gone
        for cid in col_ids:
            resp = client.patch(
                f"/columns/{cid}",
                json={"name": "test"},
            )
            assert resp.status_code == 404

    def test_delete_board_404(self, client):
        resp = client.delete("/boards/nonexistent")
        assert resp.status_code == 404
