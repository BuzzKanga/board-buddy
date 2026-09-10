import { useEffect, useState } from "react";
import { Check, Plus, Trash2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label as FieldLabel } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { AssigneeAvatar } from "./AssigneeAvatar";
import { PERSON_COLORS } from "@/services/people";
import type { Card, Label, Person, Priority } from "@/services/types";
import { cn } from "@/lib/utils";

const UNASSIGNED = "__unassigned__";

export interface CardDetailHandlers {
  onSave: (id: string, data: Partial<Card>) => void;
  onDelete: (id: string) => void;
  onAttachLabel: (cardId: string, labelId: string) => void;
  onRemoveLabel: (cardId: string, labelId: string) => void;
  onCreateLabel: (data: { name: string; color: string }) => void;
  onDeleteLabel: (labelId: string) => void;
}

export function CardDetailDialog({
  card,
  labels,
  cardLabelIds,
  people,
  open,
  onOpenChange,
  handlers,
}: {
  card: Card | null;
  labels: Label[];
  cardLabelIds: string[];
  people: Person[];
  open: boolean;
  onOpenChange: (open: boolean) => void;
  handlers: CardDetailHandlers;
}) {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [priority, setPriority] = useState<Priority>("medium");
  const [dueDate, setDueDate] = useState("");
  const [assignee, setAssignee] = useState<string>(UNASSIGNED);
  const [newLabelName, setNewLabelName] = useState("");
  const [newLabelColor, setNewLabelColor] = useState(PERSON_COLORS[1]);

  useEffect(() => {
    if (!card) return;
    setTitle(card.title);
    setDescription(card.description);
    setPriority(card.priority);
    setDueDate(card.due_date ? card.due_date.slice(0, 10) : "");
    setAssignee(card.assignee_name ?? UNASSIGNED);
    setNewLabelName("");
  }, [card]);

  if (!card) return null;

  const save = () => {
    const person = people.find((p) => p.name === assignee);
    handlers.onSave(card.id, {
      title: title.trim() || card.title,
      description,
      priority,
      due_date: dueDate || null,
      assignee_name: assignee === UNASSIGNED ? null : assignee,
      assignee_color: assignee === UNASSIGNED ? null : (person?.color ?? "#475569"),
    });
    onOpenChange(false);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-h-[90vh] overflow-y-auto sm:max-w-2xl">
        <DialogHeader>
          <DialogTitle>Card details</DialogTitle>
        </DialogHeader>

        <div className="grid gap-5 sm:grid-cols-[1.4fr_1fr]">
          <div className="space-y-4">
            <div className="space-y-1.5">
              <FieldLabel htmlFor="card-title">Title</FieldLabel>
              <Input
                id="card-title"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
              />
            </div>
            <div className="space-y-1.5">
              <FieldLabel htmlFor="card-desc">Description</FieldLabel>
              <Textarea
                id="card-desc"
                rows={7}
                placeholder="Add more detail…"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
              />
            </div>
          </div>

          <div className="space-y-4">
            <div className="space-y-1.5">
              <FieldLabel>Priority</FieldLabel>
              <Select value={priority} onValueChange={(v) => setPriority(v as Priority)}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="low">Low</SelectItem>
                  <SelectItem value="medium">Medium</SelectItem>
                  <SelectItem value="high">High</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-1.5">
              <FieldLabel>Assignee</FieldLabel>
              <Select value={assignee} onValueChange={setAssignee}>
                <SelectTrigger>
                  <SelectValue placeholder="Unassigned" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value={UNASSIGNED}>Unassigned</SelectItem>
                  {people.map((person) => (
                    <SelectItem key={person.name} value={person.name}>
                      <span className="flex items-center gap-2">
                        <AssigneeAvatar name={person.name} color={person.color} />
                        {person.name}
                      </span>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-1.5">
              <FieldLabel htmlFor="card-due">Due date</FieldLabel>
              <Input
                id="card-due"
                type="date"
                value={dueDate}
                onChange={(e) => setDueDate(e.target.value)}
              />
            </div>

            <div className="space-y-2">
              <FieldLabel>Labels</FieldLabel>
              <div className="flex flex-wrap gap-1.5">
                {labels.map((label) => {
                  const active = cardLabelIds.includes(label.id);
                  return (
                    <span key={label.id} className="group inline-flex items-center">
                      <button
                        type="button"
                        onClick={() =>
                          active
                            ? handlers.onRemoveLabel(card.id, label.id)
                            : handlers.onAttachLabel(card.id, label.id)
                        }
                        className={cn(
                          "inline-flex items-center gap-1 rounded-full px-2.5 py-1 text-[11px] font-semibold transition",
                          active ? "text-white" : "text-foreground/70",
                        )}
                        style={
                          active
                            ? { backgroundColor: label.color }
                            : { backgroundColor: `${label.color}22` }
                        }
                      >
                        {active && <Check className="size-3" />}
                        {label.name}
                      </button>
                      <button
                        type="button"
                        aria-label={`Delete label ${label.name}`}
                        onClick={() => handlers.onDeleteLabel(label.id)}
                        className="ml-0.5 text-muted-foreground opacity-0 transition group-hover:opacity-100"
                      >
                        <Trash2 className="size-3" />
                      </button>
                    </span>
                  );
                })}
              </div>
              <div className="flex items-center gap-1.5">
                <Input
                  value={newLabelName}
                  placeholder="New label"
                  className="h-8"
                  onChange={(e) => setNewLabelName(e.target.value)}
                />
                <input
                  type="color"
                  aria-label="Label colour"
                  value={newLabelColor}
                  onChange={(e) => setNewLabelColor(e.target.value)}
                  className="h-8 w-10 cursor-pointer rounded-md border border-input bg-background p-1"
                />
                <Button
                  size="icon"
                  variant="secondary"
                  className="size-8"
                  disabled={!newLabelName.trim()}
                  onClick={() => {
                    handlers.onCreateLabel({
                      name: newLabelName.trim(),
                      color: newLabelColor,
                    });
                    setNewLabelName("");
                  }}
                >
                  <Plus className="size-4" />
                </Button>
              </div>
            </div>
          </div>
        </div>

        <DialogFooter className="sm:justify-between">
          <Button
            variant="ghost"
            className="text-destructive hover:text-destructive"
            onClick={() => {
              handlers.onDelete(card.id);
              onOpenChange(false);
            }}
          >
            <Trash2 className="size-4" /> Delete card
          </Button>
          <Button onClick={save}>Save changes</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
