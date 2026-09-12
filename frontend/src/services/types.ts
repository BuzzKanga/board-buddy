export type Priority = "low" | "medium" | "high";

export interface Board {
  id: string;
  name: string;
  created_at: string;
}

export interface Column {
  id: string;
  board_id: string;
  name: string;
  position: number;
}

export interface Card {
  id: string;
  column_id: string;
  title: string;
  description: string;
  assignee_name: string | null;
  assignee_color: string | null;
  due_date: string | null;
  priority: Priority;
  position: number;
  created_at: string;
  updated_at: string;
}

export interface Label {
  id: string;
  board_id: string;
  name: string;
  color: string;
}

export interface CardLabel {
  card_id: string;
  label_id: string;
}

/** Shape returned by getBoard(id) — mirrors the future REST payload. */
export interface BoardDetail extends Board {
  columns: Column[];
  cards: Card[];
  labels: Label[];
  card_labels: CardLabel[];
}

export interface Person {
  name: string;
  color: string;
}
