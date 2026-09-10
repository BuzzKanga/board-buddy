import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { AssigneeAvatar } from "./AssigneeAvatar";
import { PERSON_COLORS, getMe, setMe } from "@/services/people";
import type { Person } from "@/services/types";
import { cn } from "@/lib/utils";

/**
 * First-visit display name + color picker. Purely local — no auth.
 * Also usable as a "change my name" dialog via the open/onOpenChange props.
 */
export function IdentityGate({
  me,
  onChange,
  open,
  onOpenChange,
}: {
  me: Person | null;
  onChange: (person: Person) => void;
  open?: boolean;
  onOpenChange?: (open: boolean) => void;
}) {
  const [firstVisitOpen, setFirstVisitOpen] = useState(false);
  const [name, setName] = useState(me?.name ?? "");
  const [color, setColor] = useState(me?.color ?? PERSON_COLORS[0]);

  useEffect(() => {
    if (!getMe()) setFirstVisitOpen(true);
  }, []);

  useEffect(() => {
    if (me) {
      setName(me.name);
      setColor(me.color);
    }
  }, [me, open]);

  const isOpen = open ?? firstVisitOpen;
  const close = (next: boolean) => {
    onOpenChange?.(next);
    if (open === undefined) setFirstVisitOpen(next);
  };

  const save = () => {
    const trimmed = name.trim();
    if (!trimmed) return;
    onChange(setMe({ name: trimmed, color }));
    close(false);
  };

  return (
    <Dialog open={isOpen} onOpenChange={(next) => (me ? close(next) : undefined)}>
      <DialogContent showCloseButton={Boolean(me)} className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Who's working the board?</DialogTitle>
          <DialogDescription>
            Pick a display name and colour. It stays in this browser and is used to tag
            cards you assign to yourself.
          </DialogDescription>
        </DialogHeader>
        <div className="space-y-4">
          <div className="flex items-center gap-3">
            <AssigneeAvatar name={name || "?"} color={color} size="md" />
            <div className="flex-1 space-y-1.5">
              <Label htmlFor="identity-name">Display name</Label>
              <Input
                id="identity-name"
                value={name}
                placeholder="e.g. Steve C"
                onChange={(e) => setName(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && save()}
              />
            </div>
          </div>
          <div className="space-y-1.5">
            <Label>Colour</Label>
            <div className="flex flex-wrap gap-2">
              {PERSON_COLORS.map((option) => (
                <button
                  key={option}
                  type="button"
                  aria-label={`Choose colour ${option}`}
                  onClick={() => setColor(option)}
                  className={cn(
                    "size-7 rounded-full ring-offset-2 transition",
                    color === option && "ring-2 ring-ring",
                  )}
                  style={{ backgroundColor: option }}
                />
              ))}
            </div>
          </div>
        </div>
        <DialogFooter>
          <Button onClick={save} disabled={!name.trim()}>
            Save
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
