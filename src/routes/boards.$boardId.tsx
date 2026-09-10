import { useMemo, useState } from "react";
import { createFileRoute, Link } from "@tanstack/react-router";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { ArrowLeft, GripVertical, MoreHorizontal, Pencil, Plus, Trash2 } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { CardTile } from "@/components/kanban/CardTile";
import { CardDetailDialog } from "@/components/kanban/CardDetailDialog";
import { IdentityGate } from "@/components/kanban/IdentityGate";
import { AssigneeAvatar } from "@/components/kanban/AssigneeAvatar";
import {
  attachLabelToCard,
  createCard,
  createColumn,
  createLabel,
  deleteCard,
  deleteColumn,
  deleteLabel,
  getBoard,
  removeLabelFromCard,
  updateCard,
  updateColumn,
} from "@/services/api";
import { getMe, getPeople } from "@/services/people";
import type { Card, Column, Person } from "@/services/types";
import { cn } from "@/lib/utils";

export const Route = createFileRoute("/boards/$boardId")({
  head: () => ({
    meta: [
      { title: "Board — Mini Kanban" },
      {
        name: "description",
        content:
          "Drag cards between columns, set priorities, labels, due dates and assignees on this kanban board.",
      },
      { property: "og:title", content: "Board — Mini Kanban" },
      {
        property: "og:description",
        content:
          "Drag cards between columns, set priorities, labels, due dates and assignees.",
      },
    ],
  }),
  component: BoardPage,
});

type Drag =
  | { type: "card"; id: string; columnId: string }
  | { type: "column"; id: string }
  | null;

function BoardPage() {
  const { boardId } = Route.useParams();
  const queryClient = useQueryClient();

  const [me, setMeState] = useState<Person | null>(() => getMe());
  const [identityOpen, setIdentityOpen] = useState(false);
  const [people, setPeople] = useState<Person[]>(() => getPeople());
  const [drag, setDrag] = useState<Drag>(null);
  const [dropColumn, setDropColumn] = useState<string | null>(null);
  const [openCardId, setOpenCardId] = useState<string | null>(null);
  const [newColumnName, setNewColumnName] = useState("");
  const [renamingColumn, setRenamingColumn] = useState<Column | null>(null);
  const [columnRenameValue, setColumnRenameValue] = useState("");
  const [deletingColumn, setDeletingColumn] = useState<Column | null>(null);

  const boardQuery = useQuery({
    queryKey: ["board", boardId],
    queryFn: () => getBoard(boardId),
  });

  const refresh = () => {
    setPeople(getPeople());
    return queryClient.invalidateQueries({ queryKey: ["board", boardId] });
  };

  const mutate = <TArgs,>(fn: (args: TArgs) => Promise<unknown>) =>
    useMutation({ mutationFn: fn, onSuccess: () => refresh() });

  const addColumn = mutate((name: string) => createColumn(boardId, name));
  const editColumn = mutate(({ id, data }: { id: string; data: Partial<Column> }) =>
    updateColumn(id, data),
  );
  const removeColumn = mutate((id: string) => deleteColumn(id));
  const addCard = mutate(({ columnId, title }: { columnId: string; title: string }) =>
    createCard(columnId, { title }),
  );
  const editCard = mutate(({ id, data }: { id: string; data: Partial<Card> }) =>
    updateCard(id, data),
  );
  const removeCard = mutate((id: string) => deleteCard(id));
  const addLabel = mutate((data: { name: string; color: string }) =>
    createLabel(boardId, data),
  );
  const removeLabel = mutate((id: string) => deleteLabel(id));
  const attachLabel = mutate(({ cardId, labelId }: { cardId: string; labelId: string }) =>
    attachLabelToCard(cardId, labelId),
  );
  const detachLabel = mutate(({ cardId, labelId }: { cardId: string; labelId: string }) =>
    removeLabelFromCard(cardId, labelId),
  );

  const board = boardQuery.data;

  const cardsByColumn = useMemo(() => {
    const map = new Map<string, Card[]>();
    board?.columns.forEach((column) => map.set(column.id, []));
    board?.cards.forEach((card) => map.get(card.column_id)?.push(card));
    map.forEach((list) => list.sort((a, b) => a.position - b.position));
    return map;
  }, [board]);

  const labelsForCard = (cardId: string) =>
    (board?.card_labels ?? [])
      .filter((cl) => cl.card_id === cardId)
      .map((cl) => board?.labels.find((l) => l.id === cl.label_id))
      .filter((l): l is NonNullable<typeof l> => Boolean(l));

  const openCard = board?.cards.find((c) => c.id === openCardId) ?? null;

  if (boardQuery.isLoading) {
    return <p className="p-10 text-sm text-muted-foreground">Loading board…</p>;
  }

  if (boardQuery.isError || !board) {
    return (
      <div className="p-10">
        <p className="text-sm text-muted-foreground">This board no longer exists.</p>
        <Link to="/" className="mt-3 inline-block text-sm font-medium text-primary">
          Back to boards
        </Link>
      </div>
    );
  }

  const moveCard = (cardId: string, columnId: string, position: number) =>
    editCard.mutate({ id: cardId, data: { column_id: columnId, position } });

  const handleColumnDrop = (targetColumn: Column) => {
    if (!drag) return;
    if (drag.type === "column" && drag.id !== targetColumn.id) {
      editColumn.mutate({ id: drag.id, data: { position: targetColumn.position } });
    }
    if (drag.type === "card") {
      const count = cardsByColumn.get(targetColumn.id)?.length ?? 0;
      moveCard(drag.id, targetColumn.id, count);
    }
    setDrag(null);
    setDropColumn(null);
  };

  return (
    <main className="min-h-screen">
      <IdentityGate
        me={me}
        onChange={(person) => {
          setMeState(person);
          setPeople(getPeople());
        }}
        open={identityOpen || undefined}
        onOpenChange={setIdentityOpen}
      />

      <header className="sticky top-0 z-10 border-b border-border bg-card/85 backdrop-blur">
        <div className="flex flex-wrap items-center justify-between gap-3 px-6 py-4">
          <div className="flex items-center gap-3">
            <Link
              to="/"
              className="inline-flex size-8 items-center justify-center rounded-md border border-border transition hover:bg-secondary"
              aria-label="Back to boards"
            >
              <ArrowLeft className="size-4" />
            </Link>
            <h1 className="text-2xl font-semibold">{board.name}</h1>
            <span className="rounded-full bg-secondary px-2.5 py-0.5 text-xs font-medium text-secondary-foreground">
              {board.cards.length} cards
            </span>
          </div>
          {me && (
            <button
              onClick={() => setIdentityOpen(true)}
              className="flex items-center gap-2 rounded-full border border-border px-3 py-1.5 text-sm font-medium transition hover:bg-secondary"
            >
              <AssigneeAvatar name={me.name} color={me.color} />
              {me.name}
            </button>
          )}
        </div>
      </header>

      <div className="flex items-start gap-4 overflow-x-auto p-6">
        {board.columns.map((column) => {
          const cards = cardsByColumn.get(column.id) ?? [];
          return (
            <section
              key={column.id}
              onDragOver={(e) => {
                e.preventDefault();
                setDropColumn(column.id);
              }}
              onDragLeave={() => setDropColumn((c) => (c === column.id ? null : c))}
              onDrop={() => handleColumnDrop(column)}
              className={cn(
                "board-column flex w-[300px] shrink-0 flex-col gap-3 p-3",
                dropColumn === column.id && "drop-target",
              )}
            >
              <div
                draggable
                onDragStart={(e) => {
                  e.stopPropagation();
                  setDrag({ type: "column", id: column.id });
                }}
                onDragEnd={() => setDrag(null)}
                className="flex cursor-grab items-center gap-1.5"
              >
                <GripVertical className="size-4 text-muted-foreground" />
                <h2 className="flex-1 text-sm font-semibold tracking-wide uppercase">
                  {column.name}
                </h2>
                <span className="text-xs text-muted-foreground">{cards.length}</span>
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="size-7"
                      aria-label={`Column actions for ${column.name}`}
                    >
                      <MoreHorizontal className="size-4" />
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end">
                    <DropdownMenuItem
                      onClick={() => {
                        setRenamingColumn(column);
                        setColumnRenameValue(column.name);
                      }}
                    >
                      <Pencil className="size-4" /> Rename
                    </DropdownMenuItem>
                    <DropdownMenuItem
                      className="text-destructive"
                      onClick={() => {
                        if (cards.length > 0) setDeletingColumn(column);
                        else removeColumn.mutate(column.id);
                      }}
                    >
                      <Trash2 className="size-4" /> Delete
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              </div>

              <div className="flex flex-col gap-2.5">
                {cards.map((card) => (
                  <CardTile
                    key={card.id}
                    card={card}
                    labels={labelsForCard(card.id)}
                    isDragging={drag?.type === "card" && drag.id === card.id}
                    onOpen={() => setOpenCardId(card.id)}
                    onDragStart={(e) => {
                      e.stopPropagation();
                      setDrag({ type: "card", id: card.id, columnId: column.id });
                    }}
                    onDragEnd={() => setDrag(null)}
                    onDropBefore={(e) => {
                      e.stopPropagation();
                      e.preventDefault();
                      if (drag?.type !== "card" || drag.id === card.id) return;
                      moveCard(drag.id, column.id, card.position);
                      setDrag(null);
                      setDropColumn(null);
                    }}
                  />
                ))}
              </div>

              <AddCardForm onAdd={(title) => addCard.mutate({ columnId: column.id, title })} />
            </section>
          );
        })}

        <form
          className="board-column flex w-[280px] shrink-0 flex-col gap-2 p-3"
          onSubmit={(e) => {
            e.preventDefault();
            if (!newColumnName.trim()) return;
            addColumn.mutate(newColumnName);
            setNewColumnName("");
          }}
        >
          <Input
            value={newColumnName}
            placeholder="New column name…"
            onChange={(e) => setNewColumnName(e.target.value)}
          />
          <Button type="submit" variant="secondary" disabled={!newColumnName.trim()}>
            <Plus className="size-4" /> Add column
          </Button>
        </form>
      </div>

      <CardDetailDialog
        card={openCard}
        labels={board.labels}
        cardLabelIds={openCard ? labelsForCard(openCard.id).map((l) => l.id) : []}
        people={people}
        open={Boolean(openCard)}
        onOpenChange={(o) => !o && setOpenCardId(null)}
        handlers={{
          onSave: (id, data) => editCard.mutate({ id, data }),
          onDelete: (id) => removeCard.mutate(id),
          onAttachLabel: (cardId, labelId) => attachLabel.mutate({ cardId, labelId }),
          onRemoveLabel: (cardId, labelId) => detachLabel.mutate({ cardId, labelId }),
          onCreateLabel: (data) => addLabel.mutate(data),
          onDeleteLabel: (labelId) => removeLabel.mutate(labelId),
        }}
      />

      <AlertDialog
        open={Boolean(renamingColumn)}
        onOpenChange={(o) => !o && setRenamingColumn(null)}
      >
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Rename column</AlertDialogTitle>
          </AlertDialogHeader>
          <Input
            value={columnRenameValue}
            onChange={(e) => setColumnRenameValue(e.target.value)}
            autoFocus
          />
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={() => {
                if (renamingColumn)
                  editColumn.mutate({
                    id: renamingColumn.id,
                    data: { name: columnRenameValue },
                  });
                setRenamingColumn(null);
              }}
            >
              Save
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

      <AlertDialog
        open={Boolean(deletingColumn)}
        onOpenChange={(o) => !o && setDeletingColumn(null)}
      >
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete “{deletingColumn?.name}”?</AlertDialogTitle>
            <AlertDialogDescription>
              This column still has{" "}
              {deletingColumn ? (cardsByColumn.get(deletingColumn.id)?.length ?? 0) : 0}{" "}
              card(s). Deleting it removes those cards too.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={() => {
                if (deletingColumn) removeColumn.mutate(deletingColumn.id);
                setDeletingColumn(null);
              }}
            >
              Delete column
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </main>
  );
}

function AddCardForm({ onAdd }: { onAdd: (title: string) => void }) {
  const [title, setTitle] = useState("");
  const [open, setOpen] = useState(false);

  if (!open) {
    return (
      <button
        onClick={() => setOpen(true)}
        className="flex items-center gap-1.5 rounded-lg px-2 py-1.5 text-sm font-medium text-muted-foreground transition hover:bg-secondary hover:text-foreground"
      >
        <Plus className="size-4" /> Add a card
      </button>
    );
  }

  return (
    <form
      className="space-y-2"
      onSubmit={(e) => {
        e.preventDefault();
        if (!title.trim()) return;
        onAdd(title.trim());
        setTitle("");
        setOpen(false);
      }}
    >
      <Input
        autoFocus
        value={title}
        placeholder="Card title"
        onChange={(e) => setTitle(e.target.value)}
        onBlur={() => !title.trim() && setOpen(false)}
      />
      <div className="flex gap-2">
        <Button type="submit" size="sm" disabled={!title.trim()}>
          Add card
        </Button>
        <Button type="button" size="sm" variant="ghost" onClick={() => setOpen(false)}>
          Cancel
        </Button>
      </div>
    </form>
  );
}
