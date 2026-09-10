import { CalendarDays } from "lucide-react";
import { format, isBefore, startOfToday } from "date-fns";
import type { Card, Label } from "@/services/types";
import { PriorityBadge } from "./PriorityBadge";
import { AssigneeAvatar } from "./AssigneeAvatar";
import { cn } from "@/lib/utils";

export function CardTile({
  card,
  labels,
  onOpen,
  onDragStart,
  onDragEnd,
  onDropBefore,
  isDragging,
}: {
  card: Card;
  labels: Label[];
  onOpen: () => void;
  onDragStart: (e: React.DragEvent) => void;
  onDragEnd: () => void;
  onDropBefore: (e: React.DragEvent) => void;
  isDragging: boolean;
}) {
  const due = card.due_date ? new Date(card.due_date) : null;
  const overdue = due ? isBefore(due, startOfToday()) : false;

  return (
    <article
      draggable
      onDragStart={onDragStart}
      onDragEnd={onDragEnd}
      onDragOver={(e) => e.preventDefault()}
      onDrop={onDropBefore}
      onClick={onOpen}
      className={cn(
        "kanban-card hover:kanban-card-hover cursor-pointer space-y-2.5 p-3 text-left",
        isDragging && "opacity-40",
      )}
    >
      {labels.length > 0 && (
        <div className="flex flex-wrap gap-1">
          {labels.map((label) => (
            <span
              key={label.id}
              className="rounded-full px-2 py-0.5 text-[10px] font-semibold text-white"
              style={{ backgroundColor: label.color }}
            >
              {label.name}
            </span>
          ))}
        </div>
      )}

      <h3 className="text-sm leading-snug font-medium text-card-foreground">{card.title}</h3>

      {card.description && (
        <p className="line-clamp-2 text-xs text-muted-foreground">{card.description}</p>
      )}

      <div className="flex items-center justify-between gap-2 pt-0.5">
        <div className="flex items-center gap-2">
          <PriorityBadge priority={card.priority} />
          {due && (
            <span
              className={cn(
                "inline-flex items-center gap-1 text-[11px] font-medium",
                overdue ? "text-destructive" : "text-muted-foreground",
              )}
            >
              <CalendarDays className="size-3" />
              {format(due, "d MMM")}
            </span>
          )}
        </div>
        {card.assignee_name && (
          <AssigneeAvatar name={card.assignee_name} color={card.assignee_color} />
        )}
      </div>
    </article>
  );
}
