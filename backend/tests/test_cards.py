"""Tests for cards endpoints."""

from __future__ import annotations


class TestCreateCard:
    def test_create_card(self, client):
        resp = client.post(
            "/columns/col-1/cards",
            json={"title": "New task", "priority": "high"},
        )
        assert resp.status_code == 201
        card = resp.json()
        assert card["title"] == "New task"
        assert card["priority"] == "high"
        assert card["column_id"] == "col-1"
        assert card["position"] == 2  # after existing 2 cards in col-1

    def test_create_card_defaults(self, client):
        resp = client.post(
            "/columns/col-1/cards",
            json={},
        )
        assert resp.status_code == 201
        card = resp.json()
        assert card["title"] == "Untitled card"
        assert card["priority"] == "medium"
        assert card["description"] == ""

    def test_create_card_column_not_found(self, client):
        resp = client.post(
            "/columns/nonexistent/cards",
            json={"title": "X"},
        )
        assert resp.status_code == 404


class TestUpdateCard:
    def test_update_fields(self, client):
        resp = client.patch(
            "/cards/card-1",
            json={"title": "Updated title", "priority": "low"},
        )
        assert resp.status_code == 200
        card = resp.json()
        assert card["title"] == "Updated title"
        assert card["priority"] == "low"

    def test_move_card_cross_column(self, client):
        # card-1 is in col-1, move to col-2
        resp = client.patch(
            "/cards/card-1",
            json={"column_id": "col-2", "position": 0},
        )
        assert resp.status_code == 200
        card = resp.json()
        assert card["column_id"] == "col-2"
        assert card["position"] == 0

    def test_reorder_card_within_column(self, client):
        # col-1 has card-1 (pos 0) and card-2 (pos 1)
        # Move card-1 to position 1
        resp = client.patch(
            "/cards/card-1",
            json={"position": 1},
        )
        assert resp.status_code == 200

        # Check card-2 is now at position 0
        detail = client.get("/boards/board-1").json()
        col1_cards = sorted(
            [c for c in detail["cards"] if c["column_id"] == "col-1"],
            key=lambda c: c["position"],
        )
        assert col1_cards[0]["id"] == "card-2"
        assert col1_cards[1]["id"] == "card-1"

    def test_update_card_404(self, client):
        resp = client.patch(
            "/cards/nonexistent",
            json={"title": "X"},
        )
        assert resp.status_code == 404


class TestDeleteCard:
    def test_delete_card(self, client):
        resp = client.delete("/cards/card-1")
        assert resp.status_code == 204

        resp = client.patch(
            "/cards/card-1",
            json={"title": "test"},
        )
        assert resp.status_code == 404

    def test_delete_card_reindexes(self, client):
        # Delete card-1 (pos 0 in col-1), card-2 should become pos 0
        client.delete("/cards/card-1")

        detail = client.get("/boards/board-1").json()
        col1_cards = [c for c in detail["cards"] if c["column_id"] == "col-1"]
        assert len(col1_cards) == 1
        assert col1_cards[0]["position"] == 0

    def test_delete_card_removes_label_associations(self, client):
        """Card-1 has labels attached; after delete, those associations should be gone."""
        client.delete("/cards/card-1")

        detail = client.get("/boards/board-1").json()
        card1_labels = [cl for cl in detail["card_labels"] if cl["card_id"] == "card-1"]
        assert len(card1_labels) == 0

    def test_delete_card_404(self, client):
        resp = client.delete("/cards/nonexistent")
        assert resp.status_code == 404
