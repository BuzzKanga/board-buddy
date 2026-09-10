/**
 * Local "who am I" store. No auth — a display name + color kept in this
 * browser, plus the list of people seen on this browser for assignee picking.
 */
import type { Person } from "./types";

const ME_KEY = "mini-kanban/me/v1";
const PEOPLE_KEY = "mini-kanban/people/v1";

export const PERSON_COLORS = [
  "#0f766e",
  "#0ea5e9",
  "#f59e0b",
  "#ef4444",
  "#10b981",
  "#6366f1",
  "#db2777",
  "#475569",
];

function readJson<T>(key: string, fallback: T): T {
  if (typeof window === "undefined") return fallback;
  try {
    const raw = window.localStorage.getItem(key);
    return raw ? (JSON.parse(raw) as T) : fallback;
  } catch {
    return fallback;
  }
}

function writeJson(key: string, value: unknown) {
  if (typeof window === "undefined") return;
  try {
    window.localStorage.setItem(key, JSON.stringify(value));
  } catch {
    /* ignore */
  }
}

export function getMe(): Person | null {
  return readJson<Person | null>(ME_KEY, null);
}

export function setMe(person: Person): Person {
  writeJson(ME_KEY, person);
  rememberPerson(person);
  return person;
}

export function getPeople(): Person[] {
  return readJson<Person[]>(PEOPLE_KEY, []);
}

export function rememberPerson(person: Person): Person[] {
  const people = getPeople().filter(
    (p) => p.name.toLowerCase() !== person.name.toLowerCase(),
  );
  const next = [...people, person].sort((a, b) => a.name.localeCompare(b.name));
  writeJson(PEOPLE_KEY, next);
  return next;
}

export function initials(name: string): string {
  return name
    .trim()
    .split(/\s+/)
    .slice(0, 2)
    .map((part) => part[0]?.toUpperCase() ?? "")
    .join("");
}
