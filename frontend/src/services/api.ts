/**
 * Real API client — talks to the FastAPI backend.
 *
 * Every function is async and mirrors the REST endpoints. Components import
 * these functions and never need to know the implementation details.
 */
import type {
  Board,
  BoardDetail,
  Card,
  Column,
  Label,
  Priority,
} from "./types";

const BASE_URL = (import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000") + "/api";

async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json", ...init?.headers },
    ...init,
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(body.detail ?? `API error ${res.status}`);
  }
  if (res.status === 204) return undefined as T;
  return res.json() as Promise<T>;
}

/* ---------------------------------- boards --------------------------------- */

export async function getBoards(): Promise<Board[]> {
  return apiFetch<Board[]>("/boards");
}

export async function createBoard(name: string): Promise<Board> {
  return apiFetch<Board>("/boards", {
    method: "POST",
    body: JSON.stringify({ name }),
  });
}

export async function updateBoard(id: string, data: Partial<Board>): Promise<Board> {
  return apiFetch<Board>(`/boards/${id}`, {
    method: "PATCH",
    body: JSON.stringify({ name: data.name }),
  });
}

export async function deleteBoard(id: string): Promise<void> {
  return apiFetch<void>(`/boards/${id}`, { method: "DELETE" });
}

export async function getBoard(id: string): Promise<BoardDetail> {
  return apiFetch<BoardDetail>(`/boards/${id}`);
}

/* --------------------------------- columns --------------------------------- */

export async function createColumn(boardId: string, name: string): Promise<Column> {
  return apiFetch<Column>(`/boards/${boardId}/columns`, {
    method: "POST",
    body: JSON.stringify({ name }),
  });
}

export async function updateColumn(id: string, data: Partial<Column>): Promise<Column> {
  const body: Record<string, unknown> = {};
  if (data.name !== undefined) body.name = data.name;
  if (data.position !== undefined) body.position = data.position;
  return apiFetch<Column>(`/columns/${id}`, {
    method: "PATCH",
    body: JSON.stringify(body),
  });
}

export async function deleteColumn(id: string): Promise<void> {
  return apiFetch<void>(`/columns/${id}`, { method: "DELETE" });
}

/* ---------------------------------- cards ---------------------------------- */

export async function createCard(
  columnId: string,
  data: Partial<Omit<Card, "id" | "column_id">>,
): Promise<Card> {
  return apiFetch<Card>(`/columns/${columnId}/cards`, {
    method: "POST",
    body: JSON.stringify({
      title: data.title,
      description: data.description,
      assignee_name: data.assignee_name,
      assignee_color: data.assignee_color,
      due_date: data.due_date,
      priority: data.priority,
    }),
  });
}

/** Handles field edits AND moves/reorders (accepts column_id + position). */
export async function updateCard(id: string, data: Partial<Card>): Promise<Card> {
  const body: Record<string, unknown> = {};
  for (const key of [
    "title", "description", "assignee_name", "assignee_color",
    "due_date", "priority", "column_id", "position",
  ] as const) {
    if (data[key] !== undefined) body[key] = data[key];
  }
  return apiFetch<Card>(`/cards/${id}`, {
    method: "PATCH",
    body: JSON.stringify(body),
  });
}

export async function deleteCard(id: string): Promise<void> {
  return apiFetch<void>(`/cards/${id}`, { method: "DELETE" });
}

/* ---------------------------------- labels --------------------------------- */

export async function createLabel(
  boardId: string,
  data: { name: string; color: string },
): Promise<Label> {
  return apiFetch<Label>(`/boards/${boardId}/labels`, {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function deleteLabel(id: string): Promise<void> {
  return apiFetch<void>(`/labels/${id}`, { method: "DELETE" });
}

export async function attachLabelToCard(cardId: string, labelId: string): Promise<void> {
  return apiFetch<void>(`/cards/${cardId}/labels/${labelId}`, { method: "PUT" });
}

export async function removeLabelFromCard(cardId: string, labelId: string): Promise<void> {
  return apiFetch<void>(`/cards/${cardId}/labels/${labelId}`, { method: "DELETE" });
}
