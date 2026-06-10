import { useEffect, useRef, useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { format } from "date-fns";
import { X, Phone, User, Clock, Calendar, FileText, Sparkles, StickyNote } from "lucide-react";
import { StatusBadge } from "./CallsTable";
import { callsApi } from "@/services/api";
import type { Call } from "@/types/calls";

interface CallDetailDrawerProps {
  call: Call | null;
  onClose: () => void;
  onCallUpdate: (call: Call) => void;
}

function DetailRow({
  icon,
  label,
  value,
}: {
  icon: React.ReactNode;
  label: string;
  value: React.ReactNode;
}) {
  return (
    <div className="flex items-start gap-3 py-3 border-b border-border last:border-0">
      <div className="mt-0.5 text-muted-foreground">{icon}</div>
      <div className="flex-1 min-w-0">
        <p className="text-xs text-muted-foreground mb-0.5">{label}</p>
        <div className="text-sm font-medium text-foreground break-words">{value}</div>
      </div>
    </div>
  );
}

function formatDuration(seconds: number | null): string {
  if (seconds === null) return "Not available";
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return m > 0 ? `${m} min ${s} sec` : `${s} sec`;
}

export function CallDetailDrawer({ call, onClose, onCallUpdate }: CallDetailDrawerProps) {
  const [isEditingNotes, setIsEditingNotes] = useState(false);
  const [draftNotes, setDraftNotes] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const notesMutation = useMutation({
    mutationFn: (notes: string | null) => callsApi.updateNotes(call!.id, notes),
    onSuccess: (updatedCall) => {
      onCallUpdate(updatedCall);
      setIsEditingNotes(false);
    },
  });

  useEffect(() => {
    setIsEditingNotes(false);
    setDraftNotes(call?.notes ?? "");
  }, [call?.id, call?.notes]);

  useEffect(() => {
    if (isEditingNotes) {
      textareaRef.current?.focus();
    }
  }, [isEditingNotes]);

  if (!call) return null;

  function startEditing() {
    setDraftNotes(call!.notes ?? "");
    setIsEditingNotes(true);
  }

  function cancelEditing() {
    setDraftNotes(call!.notes ?? "");
    setIsEditingNotes(false);
  }

  function saveNotes() {
    const trimmed = draftNotes.trim();
    const value = trimmed === "" ? null : trimmed;
    if (value === call!.notes) {
      setIsEditingNotes(false);
      return;
    }
    notesMutation.mutate(value);
  }

  return (
    <>
      <div
        className="fixed inset-0 bg-black/20 z-40 transition-opacity"
        onClick={onClose}
        aria-hidden="true"
      />

      <aside className="fixed right-0 top-0 h-full w-full max-w-md bg-white shadow-2xl z-50 flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-border">
          <div>
            <h2 className="text-base font-semibold text-foreground">Call Details</h2>
            <p className="text-xs text-muted-foreground font-mono mt-0.5">#{call.id.slice(0, 8)}</p>
          </div>
          <button
            onClick={onClose}
            className="rounded-md p-1.5 text-muted-foreground hover:text-foreground hover:bg-muted transition-colors"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        {/* Status banner */}
        <div className="px-6 py-3 bg-muted/50 border-b border-border flex items-center justify-between">
          <StatusBadge status={call.status} />
          {call.label && (
            <span className="inline-flex items-center rounded-md px-2 py-1 text-xs font-medium border border-border bg-white text-foreground">
              {call.label}
            </span>
          )}
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto px-6 py-4">
          <DetailRow
            icon={<Phone className="h-4 w-4" />}
            label="Phone Number"
            value={<span className="font-mono">{call.phone_number}</span>}
          />
          <DetailRow
            icon={<User className="h-4 w-4" />}
            label="Caller Name"
            value={call.caller_name ?? "Unknown"}
          />
          <DetailRow
            icon={<Clock className="h-4 w-4" />}
            label="Duration"
            value={formatDuration(call.duration_seconds)}
          />
          <DetailRow
            icon={<Calendar className="h-4 w-4" />}
            label="Started At"
            value={format(new Date(call.started_at), "PPpp")}
          />
          {call.ended_at && (
            <DetailRow
              icon={<Calendar className="h-4 w-4" />}
              label="Ended At"
              value={format(new Date(call.ended_at), "PPpp")}
            />
          )}

          {/* Notes */}
          <div className="py-3 border-b border-border">
            <div className="flex items-center gap-2 mb-2">
              <StickyNote className="h-4 w-4 text-muted-foreground" />
              <h3 className="text-xs text-muted-foreground font-medium">Notes</h3>
            </div>
            {isEditingNotes ? (
              <div className="space-y-2">
                <textarea
                  ref={textareaRef}
                  value={draftNotes}
                  onChange={(e) => setDraftNotes(e.target.value)}
                  onBlur={saveNotes}
                  onKeyDown={(e) => {
                    if (e.key === "Escape") {
                      e.preventDefault();
                      cancelEditing();
                    }
                  }}
                  disabled={notesMutation.isPending}
                  rows={4}
                  className="w-full rounded-md border border-border bg-background px-3 py-2 text-sm text-foreground resize-none focus:outline-none focus:ring-2 focus:ring-[#FDDF5C]"
                  placeholder="Add notes about this call..."
                />
                {notesMutation.isError && (
                  <p className="text-xs text-red-500">Failed to save notes. Try again.</p>
                )}
              </div>
            ) : (
              <button
                type="button"
                onClick={startEditing}
                className="w-full text-left rounded-md px-3 py-2 text-sm hover:bg-muted transition-colors min-h-[2.5rem]"
              >
                {call.notes ? (
                  <span className="text-foreground whitespace-pre-wrap">{call.notes}</span>
                ) : (
                  <span className="text-muted-foreground italic">Click to add notes…</span>
                )}
              </button>
            )}
          </div>
        </div>

        {/* AI Summary */}
        {call.summary && (
          <div className="px-6 py-4 border-t border-border">
            <div className="flex items-center gap-2 mb-2">
              <Sparkles className="h-4 w-4" style={{ color: "#FDDF5C" }} />
              <h3 className="text-sm font-semibold text-foreground">AI Summary</h3>
            </div>
            <p className="text-sm text-muted-foreground leading-relaxed">{call.summary}</p>
          </div>
        )}

        {/* Transcript */}
        {call.raw_transcript && (
          <div className="px-6 py-4 border-t border-border">
            <div className="flex items-center gap-2 mb-2">
              <FileText className="h-4 w-4 text-muted-foreground" />
              <h3 className="text-sm font-semibold text-foreground">Transcript</h3>
            </div>
            <div className="bg-muted rounded-lg p-3 max-h-48 overflow-y-auto">
              <pre className="text-xs text-muted-foreground whitespace-pre-wrap font-mono leading-relaxed">
                {call.raw_transcript}
              </pre>
            </div>
          </div>
        )}

        {/* Footer */}
        <div className="px-6 py-3 border-t border-border bg-muted/30">
          <p className="text-xs text-muted-foreground">
            Created {format(new Date(call.created_at), "PPpp")}
          </p>
        </div>
      </aside>
    </>
  );
}
