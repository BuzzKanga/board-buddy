import { initials } from "@/services/people";
import { cn } from "@/lib/utils";

export function AssigneeAvatar({
  name,
  color,
  size = "sm",
  className,
}: {
  name: string;
  color?: string | null;
  size?: "sm" | "md";
  className?: string;
}) {
  return (
    <span
      title={name}
      className={cn(
        "inline-flex shrink-0 items-center justify-center rounded-full font-semibold text-white",
        size === "sm" ? "size-6 text-[10px]" : "size-9 text-xs",
        className,
      )}
      style={{ backgroundColor: color ?? "#475569" }}
    >
      {initials(name) || "?"}
    </span>
  );
}
