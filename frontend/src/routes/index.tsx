import { useState } from "react";
import { createFileRoute, Link, useNavigate } from "@tanstack/react-router";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { KanbanSquare, MoreHorizontal, Pencil, Plus, Trash2 } from "lucide-react";
import { format } from "date-fns";

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
import { IdentityGate } from "@/components/kanban/IdentityGate";
import { AssigneeAvatar } from "@/components/kanban/AssigneeAvatar";
import { createBoard, deleteBoard, getBoards, updateBoard } from "@/services/api";
import { getMe } from "@/services/people";
import type { Board, Person } from "@/services/types";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "Mini Kanban — Boards" },
      {
        name: "description",
        content:
          "A fast, no-login kanban board: create boards, drag cards across columns, and tag work with labels, priorities and assignees.",
      },
      { property: "og:title", content: "Mini Kanban — Boards" },
      {
        property: "og:description",
        content:
          "Create boards, drag cards across columns, and tag work with labels, priorities and assignees.",
      },
    ],
  }),
  component: BoardsPage,
});

function BoardsPage() {
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const [me, setMeState] = useState<Person | null>(() => getMe());
  const [identityOpen, setIdentityOpen] = useState(false);
  const [newName, setNewName] = useState("");
  const [renaming, setRenaming] = useState<Board | null>(null);
  const [renameValue, setRenameValue] = useState("");
  const [deleting, setDeleting] = useState<Board | null>(null);

  const { data: boards = [], isLoading } = useQuery({
    queryKey: ["boards"],
    queryFn: getBoards,
  });

  const invalidate = () => queryClient.invalidateQueries({ queryKey: ["boards"] });

  const create = useMutation({
    mutationFn: (name: string) => createBoard(name),
    onSuccess: (board) => {
      setNewName("");
      invalidate();
      navigate({ to: "/boards/$boardId", params: { boardId: board.id } });
    },
  });

  const rename = useMutation({
    mutationFn: ({ id, name }: { id: string; name: string }) => updateBoard(id, { name }),
    onSuccess: () => {
      setRenaming(null);
      invalidate();
    },
  });

  const remove = useMutation({
    mutationFn: (id: string) => deleteBoard(id),
    onSuccess: () => {
      setDeleting(null);
      invalidate();
    },
  });

  return (
    <main className="mx-auto min-h-screen w-full max-w-5xl px-6 py-12">
      <IdentityGate
        me={me}
        onChange={setMeState}
        open={identityOpen || undefined}
        onOpenChange={setIdentityOpen}
      />

      <header className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <p className="inline-flex items-center gap-2 text-xs font-semibold tracking-widest text-primary uppercase">
            <KanbanSquare className="size-4" /> Mini Kanban
          </p>
          <h1 className="mt-2 text-4xl font-semibold">Your boards</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            No accounts, no setup — everything lives in this browser for now.
          </p>
        </div>
        {me && (
          <button
            onClick={() => setIdentityOpen(true)}
            className="flex items-center gap-2 rounded-full border border-border bg-card px-3 py-1.5 text-sm font-medium transition hover:bg-secondary"
          >
            <AssigneeAvatar name={me.name} color={me.color} />
            {me.name}
          </button>
        )}
      </header>

      <form
        className="mt-8 flex gap-2"
        onSubmit={(e) => {
          e.preventDefault();
          if (newName.trim()) create.mutate(newName);
        }}
      >
        <Input
          value={newName}
          placeholder="New board name…"
          onChange={(e) => setNewName(e.target.value)}
        />
        <Button type="submit" disabled={!newName.trim() || create.isPending}>
          <Plus className="size-4" /> Create board
        </Button>
      </form>

      <section className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {isLoading && <p className="text-sm text-muted-foreground">Loading boards…</p>}
        {!isLoading && boards.length === 0 && (
          <p className="text-sm text-muted-foreground">
            No boards yet — create your first one above.
          </p>
        )}
        {boards.map((board) => (
          <div key={board.id} className="kanban-card hover:kanban-card-hover relative p-5">
            <Link
              to="/boards/$boardId"
              params={{ boardId: board.id }}
              className="block pr-8"
            >
              <h2 className="text-lg font-semibold">{board.name}</h2>
              <p className="mt-1 text-xs text-muted-foreground">
                Created {format(new Date(board.created_at), "d MMM yyyy")}
              </p>
            </Link>
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button
                  variant="ghost"
                  size="icon"
                  className="absolute top-3 right-3 size-8"
                  aria-label={`Board actions for ${board.name}`}
                >
                  <MoreHorizontal className="size-4" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuItem
                  onClick={() => {
                    setRenaming(board);
                    setRenameValue(board.name);
                  }}
                >
                  <Pencil className="size-4" /> Rename
                </DropdownMenuItem>
                <DropdownMenuItem
                  className="text-destructive"
                  onClick={() => setDeleting(board)}
                >
                  <Trash2 className="size-4" /> Delete
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        ))}
      </section>

      <AlertDialog open={Boolean(renaming)} onOpenChange={(o) => !o && setRenaming(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Rename board</AlertDialogTitle>
          </AlertDialogHeader>
          <Input
            value={renameValue}
            onChange={(e) => setRenameValue(e.target.value)}
            autoFocus
          />
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={() =>
                renaming && rename.mutate({ id: renaming.id, name: renameValue })
              }
            >
              Save
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

      <AlertDialog open={Boolean(deleting)} onOpenChange={(o) => !o && setDeleting(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete “{deleting?.name}”?</AlertDialogTitle>
            <AlertDialogDescription>
              This removes the board with all of its columns, cards and labels. It can't be
              undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction onClick={() => deleting && remove.mutate(deleting.id)}>
              Delete board
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </main>
  );
}
