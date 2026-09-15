"""Tests for labels and card↔label endpoints."""

from __future__ import annotations


class TestCreateLabel:
    def test_create_label(self, client):
        resp = client.post(
            "/boards/board-1/labels",
            json={"name": "Testing", "color": "#facc15"},
        )
        assert resp.status_code == 201
        label = resp.json()
        assert label["name"] == "Testing"
        assert label["color"] == "#facc15"
        assert label["board_id"] == "board-1"

    def test_create_label_board_not_found(self, client):
        resp = client.post(
            "/boards/nonexistent/labels",
            json={"name": "X", "color": "#000"},
        )
        assert resp.status_code == 404


class TestDeleteLabel:
    def test_delete_label(self, client):
        resp = client.delete("/labels/lbl-1")
        assert resp.status_code == 204

    def test_delete_label_removes_card_associations(self, client):
        """lbl-1 is attached to card-1 and card-3; deleting it should remove those."""
        client.delete("/labels/lbl-1")

        detail = client.get("/boards/board-1").json()
        associations_with_lbl1 = [
            cl for cl in detail["card_labels"] if cl["label_id"] == "lbl-1"
        ]
        assert len(associations_with_lbl1) == 0

    def test_delete_label_404(self, client):
        resp = client.delete("/labels/nonexistent")
        assert resp.status_code == 404


class TestAttachLabel:
    def test_attach_label(self, client):
        # card-4 has no labels, attach lbl-2
        resp = client.put(
            "/cards/card-4/labels/lbl-2",
        )
        assert resp.status_code == 204

        detail = client.get("/boards/board-1").json()
        attached = [
            cl for cl in detail["card_labels"]
            if cl["card_id"] == "card-4" and cl["label_id"] == "lbl-2"
        ]
        assert len(attached) == 1

    def test_attach_label_idempotent(self, client):
        # card-1 already has lbl-1 attached
        resp = client.put(
            "/cards/card-1/labels/lbl-1",
        )
        assert resp.status_code == 204

        # Should not duplicate
        detail = client.get("/boards/board-1").json()
        attached = [
            cl for cl in detail["card_labels"]
            if cl["card_id"] == "card-1" and cl["label_id"] == "lbl-1"
        ]
        assert len(attached) == 1

    def test_attach_label_card_not_found(self, client):
        resp = client.put(
            "/cards/nonexistent/labels/lbl-1",
        )
        assert resp.status_code == 404

    def test_attach_label_label_not_found(self, client):
        resp = client.put(
            "/cards/card-1/labels/nonexistent",
        )
        assert resp.status_code == 404


class TestRemoveLabel:
    def test_remove_label_from_card(self, client):
        # card-1 has lbl-1 attached
        resp = client.delete(
            "/cards/card-1/labels/lbl-1",
        )
        assert resp.status_code == 204

        detail = client.get("/boards/board-1").json()
        attached = [
            cl for cl in detail["card_labels"]
            if cl["card_id"] == "card-1" and cl["label_id"] == "lbl-1"
        ]
        assert len(attached) == 0

    def test_remove_label_card_not_found(self, client):
        resp = client.delete(
            "/cards/nonexistent/labels/lbl-1",
        )
        assert resp.status_code == 404

    def test_remove_label_label_not_found(self, client):
        resp = client.delete(
            "/cards/card-1/labels/nonexistent",
        )
        assert resp.status_code == 404
