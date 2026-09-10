/**
 * Mock data-access layer.
 *
 * Every function is async and mirrors the REST endpoints the real
 * Node/Express + Postgres backend will expose. Components must never touch
 * localStorage directly — swapping these bodies for fetch() calls later
 * requires no component changes.
 */
import type {
  Board,
  BoardDetail,
  Card,
  CardLabel,
  Column,
  Label,
  Priority,
} from "./types";

const STORAGE_KEY = "mini-kanban/db/v1";

interface Db {
  boards: Board[];
  columns: Column[];
  cards: Card[];
  labels: Label[];
  card_labels: CardLabel[];
}

const uid = () => Math.random().toString(36).slice(2, 10) + Date.now().toString(36);
const now = () => new Date().toISOString();
const delay = (ms = 90) => new Promise((r) => setTimeout(r, ms));
const clone = <T>(value: T): T => JSON.parse(JSON.stringify(value)) as T;

let memory: Db | null = null;

function emptyDb(): Db {
  return { boards: [], columns: [], cards: [], labels: [], card_labels: [] };
}

function seed(): Db {
  const db = emptyDb();
  const boardId = uid();
  db.boards.push({ id: boardId, name: "Product Launch", created_at: now() });

  const labels: Label[] = [
    { id: uid(), board_id: boardId, name: "Design", color: "#6366f1" },
    { id: uid(), board_id: boardId, name: "Bug", color: "#ef4444" },
    { id: uid(), board_id: boardId, name: "Research", color: "#0ea5e9" },
  ];
  db.labels.push(...labels);

  const colNames = ["To Do", "In Progress", "Done"];
  const cols = colNames.map((name, i) => ({
    id: uid(),
    board_id: boardId,
    name,
    position: i,
  }));
  db.columns.push(...cols);

  const sample: Array<[number, string, Priority, string, string | null, number[]]> = [
    [0, "Draft landing page copy", "high", "Short punchy hero and three benefits.", "2026-09-18", [0]],
    [0, "Collect competitor pricing", "low", "", null, [2]],
    [1, "Fix column drag flicker", "medium", "Happens when dropping on the last column.", "2026-09-12", [1]],
    [2, "Pick brand colors", "low", "Settled on slate + teal.", null, [0]],
  ];

  sample.forEach(([colIdx, title, priority, description, due, labelIdxs], i) => {
    const cardId = uid();
    db.cards.push({
      id: cardId,
      column_id: cols[colIdx].id,
      title,
      description,
      assignee_name: null,
      assignee_color: null,
      due_date: due,
      priority,
      position: i,
      created_at: now(),
      updated_at: now(),
    });
    labelIdxs.forEach((li) =>
      db.card_labels.push({ card_id: cardId, label_id: labels[li].id }),
    );
  });

  return db;
}

function read(): Db {
  if (memory) return memory;
  if (typeof window === "undefined") {
    memory = emptyDb();
    return memory;
  }
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    memory = raw ? (JSON.parse(raw) as Db) : seed();
  } catch {
    memory = seed();
  }
  write(memory);
  return memory;
}

function write(db: Db) {
  memory = db;
  if (typeof window === "undefined") return;
  try {
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(db));
  } catch {
    /* ignore quota errors */
  }
}

function reindex(items: Array<{ position: number }>) {
  items
    .slice()
    .sort((a, b) => a.position - b.position)
    .forEach((item, i) => {
      item.position = i;
    });
}

/* ---------------------------------- boards --------------------------------- */

export async function getBoards(): Promise<Board[]> {
  await delay();
  const db = read();
  return clone(
    db.boards.slice().sort((a, b) => a.created_at.localeCompare(b.created_at)),
  );
}

export async function createBoard(name: string): Promise<Board> {
  await delay();
  const db = read();
  const board: Board = { id: uid(), name: name.trim() || "Untitled board", created_at: now() };
  db.boards.push(board);
  ["To Do", "In Progress", "Done"].forEach((colName, i) =>
    db.columns.push({ id: uid(), board_id: board.id, name: colName, position: i }),
  );
  write(db);
  return clone(board);
}

export async function updateBoard(id: string, data: Partial<Board>): Promise<Board> {
  await delay();
  const db = read();
  const board = db.boards.find((b) => b.id === id);
  if (!board) throw new Error("Board not found");
  Object.assign(board, { name: data.name?.trim() || board.name });
  write(db);
  return clone(board);
}

export async function deleteBoard(id: string): Promise<void> {
  await delay();
  const db = read();
  const columnIds = db.columns.filter((c) => c.board_id === id).map((c) => c.id);
  const cardIds = db.cards.filter((c) => columnIds.includes(c.column_id)).map((c) => c.id);
  db.boards = db.boards.filter((b) => b.id !== id);
  db.columns = db.columns.filter((c) => c.board_id !== id);
  db.cards = db.cards.filter((c) => !cardIds.includes(c.id));
  db.labels = db.labels.filter((l) => l.board_id !== id);
  db.card_labels = db.card_labels.filter((cl) => !cardIds.includes(cl.card_id));
  write(db);
}

export async function getBoard(id: string): Promise<BoardDetail> {
  await delay();
  const db = read();
  const board = db.boards.find((b) => b.id === id);
  if (!board) throw new Error("Board not found");
  const columns = db.columns
    .filter((c) => c.board_id === id)
    .sort((a, b) => a.position - b.position);
  const columnIds = columns.map((c) => c.id);
  const cards = db.cards
    .filter((c) => columnIds.includes(c.column_id))
    .sort((a, b) => a.position - b.position);
  const cardIds = cards.map((c) => c.id);
  return clone({
    ...board,
    columns,
    cards,
    labels: db.labels.filter((l) => l.board_id === id),
    card_labels: db.card_labels.filter((cl) => cardIds.includes(cl.card_id)),
  });
}

/* --------------------------------- columns --------------------------------- */

export async function createColumn(boardId: string, name: string): Promise<Column> {
  await delay();
  const db = read();
  const siblings = db.columns.filter((c) => c.board_id === boardId);
  const column: Column = {
    id: uid(),
    board_id: boardId,
    name: name.trim() || "New column",
    position: siblings.length,
  };
  db.columns.push(column);
  write(db);
  return clone(column);
}

export async function updateColumn(id: string, data: Partial<Column>): Promise<Column> {
  await delay();
  const db = read();
  const column = db.columns.find((c) => c.id === id);
  if (!column) throw new Error("Column not found");
  if (data.name !== undefined) column.name = data.name.trim() || column.name;

  if (data.position !== undefined && data.position !== column.position) {
    const siblings = db.columns
      .filter((c) => c.board_id === column.board_id)
      .sort((a, b) => a.position - b.position);
    const rest = siblings.filter((c) => c.id !== column.id);
    const target = Math.max(0, Math.min(data.position, rest.length));
    rest.splice(target, 0, column);
    rest.forEach((c, i) => {
      c.position = i;
    });
  }
  write(db);
  return clone(column);
}

export async function deleteColumn(id: string): Promise<void> {
  await delay();
  const db = read();
  const column = db.columns.find((c) => c.id === id);
  const cardIds = db.cards.filter((c) => c.column_id === id).map((c) => c.id);
  db.columns = db.columns.filter((c) => c.id !== id);
  db.cards = db.cards.filter((c) => c.column_id !== id);
  db.card_labels = db.card_labels.filter((cl) => !cardIds.includes(cl.card_id));
  if (column) reindex(db.columns.filter((c) => c.board_id === column.board_id));
  write(db);
}

/* ---------------------------------- cards ---------------------------------- */

export async function createCard(
  columnId: string,
  data: Partial<Omit<Card, "id" | "column_id">>,
): Promise<Card> {
  await delay();
  const db = read();
  const siblings = db.cards.filter((c) => c.column_id === columnId);
  const card: Card = {
    id: uid(),
    column_id: columnId,
    title: (data.title ?? "").trim() || "Untitled card",
    description: data.description ?? "",
    assignee_name: data.assignee_name ?? null,
    assignee_color: data.assignee_color ?? null,
    due_date: data.due_date ?? null,
    priority: data.priority ?? "medium",
    position: siblings.length,
    created_at: now(),
    updated_at: now(),
  };
  db.cards.push(card);
  write(db);
  return clone(card);
}

/** Handles field edits AND moves/reorders (accepts column_id + position). */
export async function updateCard(id: string, data: Partial<Card>): Promise<Card> {
  await delay();
  const db = read();
  const card = db.cards.find((c) => c.id === id);
  if (!card) throw new Error("Card not found");

  const fromColumn = card.column_id;
  const toColumn = data.column_id ?? fromColumn;

  (
    ["title", "description", "assignee_name", "assignee_color", "due_date", "priority"] as const
  ).forEach((key) => {
    if (data[key] !== undefined) {
      // @ts-expect-error narrow assignment across the union of field types
      card[key] = data[key];
    }
  });

  if (toColumn !== fromColumn || data.position !== undefined) {
    card.column_id = toColumn;
    const target = db.cards
      .filter((c) => c.column_id === toColumn && c.id !== card.id)
      .sort((a, b) => a.position - b.position);
    const index = Math.max(0, Math.min(data.position ?? target.length, target.length));
    target.splice(index, 0, card);
    target.forEach((c, i) => {
      c.position = i;
    });
    if (toColumn !== fromColumn) {
      reindex(db.cards.filter((c) => c.column_id === fromColumn));
    }
  }

  card.updated_at = now();
  write(db);
  return clone(card);
}

export async function deleteCard(id: string): Promise<void> {
  await delay();
  const db = read();
  const card = db.cards.find((c) => c.id === id);
  db.cards = db.cards.filter((c) => c.id !== id);
  db.card_labels = db.card_labels.filter((cl) => cl.card_id !== id);
  if (card) reindex(db.cards.filter((c) => c.column_id === card.column_id));
  write(db);
}

/* ---------------------------------- labels --------------------------------- */

export async function createLabel(
  boardId: string,
  data: { name: string; color: string },
): Promise<Label> {
  await delay();
  const db = read();
  const label: Label = {
    id: uid(),
    board_id: boardId,
    name: data.name.trim() || "Label",
    color: data.color,
  };
  db.labels.push(label);
  write(db);
  return clone(label);
}

export async function deleteLabel(id: string): Promise<void> {
  await delay();
  const db = read();
  db.labels = db.labels.filter((l) => l.id !== id);
  db.card_labels = db.card_labels.filter((cl) => cl.label_id !== id);
  write(db);
}

export async function attachLabelToCard(cardId: string, labelId: string): Promise<void> {
  await delay();
  const db = read();
  if (!db.card_labels.some((cl) => cl.card_id === cardId && cl.label_id === labelId)) {
    db.card_labels.push({ card_id: cardId, label_id: labelId });
  }
  write(db);
}

export async function removeLabelFromCard(cardId: string, labelId: string): Promise<void> {
  await delay();
  const db = read();
  db.card_labels = db.card_labels.filter(
    (cl) => !(cl.card_id === cardId && cl.label_id === labelId),
  );
  write(db);
}
