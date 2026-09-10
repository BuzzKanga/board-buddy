import type { Priority } from "@/services/types";
import { cn } from "@/lib/utils";

const styles: Record<Priority, string> = {
  low: "bg-priority-low/25 text-priority-low-foreground",
  medium: "bg-priority-medium/30 text-priority-medium-foreground",
  high: "bg-priority-high text-priority-high-foreground",
};

const labels: Record<Priority, string> = {
  low: "Low",
  medium: "Medium",
  high: "High",
};

export function PriorityBadge({
  priority,
  className,
}: {
  priority: Priority;
  className?: string;
}) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-[11px] font-semibold uppercase tracking-wide",
        styles[priority],
        className,
      )}
    >
      <span className="size-1.5 rounded-full bg-current opacity-70" />
      {labels[priority]}
    </span>
  );
}
