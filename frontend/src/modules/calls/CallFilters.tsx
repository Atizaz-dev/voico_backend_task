import { useState } from "react";
import { Plus, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { CALL_LABELS, type FilterType } from "@/types/calls";

const FILTER_OPTIONS: { type: FilterType; label: string }[] = [
  { type: "caller_name", label: "Caller Name" },
  { type: "phone_number", label: "Phone" },
  { type: "label", label: "Label" },
  { type: "min_duration", label: "Min Duration (sec)" },
  { type: "max_duration", label: "Max Duration (sec)" },
];

const FILTER_LABELS: Record<FilterType, string> = {
  caller_name: "Caller",
  phone_number: "Phone",
  label: "Label",
  min_duration: "Min Duration",
  max_duration: "Max Duration",
};

interface CallFiltersProps {
  filters: Partial<Record<FilterType, string>>;
  onAddFilter: (type: FilterType, value: string) => void;
  onRemoveFilter: (type: FilterType) => void;
}

export function CallFilters({ filters, onAddFilter, onRemoveFilter }: CallFiltersProps) {
  const [showAddMenu, setShowAddMenu] = useState(false);
  const [selectedType, setSelectedType] = useState<FilterType | null>(null);
  const [inputValue, setInputValue] = useState("");

  const activeTypes = Object.keys(filters) as FilterType[];
  const availableOptions = FILTER_OPTIONS.filter((o) => !activeTypes.includes(o.type));

  function handleSelectType(type: FilterType) {
    setSelectedType(type);
    setInputValue("");
    setShowAddMenu(false);
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!selectedType || !inputValue.trim()) return;
    onAddFilter(selectedType, inputValue.trim());
    setSelectedType(null);
    setInputValue("");
  }

  function handleCancel() {
    setSelectedType(null);
    setInputValue("");
  }

  return (
    <div className="flex flex-wrap items-center gap-2 px-6 py-3 border-b border-border">
      {activeTypes.map((type) => (
        <span
          key={type}
          className="inline-flex items-center gap-1 rounded-full border border-border bg-muted px-3 py-1 text-xs font-medium text-foreground"
        >
          <span className="text-muted-foreground">{FILTER_LABELS[type]}:</span>
          <span>{filters[type]}</span>
          <button
            type="button"
            onClick={() => onRemoveFilter(type)}
            className="ml-0.5 rounded-full p-0.5 hover:bg-background transition-colors"
            aria-label={`Remove ${FILTER_LABELS[type]} filter`}
          >
            <X className="h-3 w-3" />
          </button>
        </span>
      ))}

      {selectedType ? (
        <form onSubmit={handleSubmit} className="inline-flex items-center gap-2">
          <span className="text-xs text-muted-foreground">{FILTER_LABELS[selectedType]}:</span>
          {selectedType === "label" ? (
            <select
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              className="rounded-md border border-border bg-background px-2 py-1 text-xs"
              autoFocus
            >
              <option value="">Select label…</option>
              {CALL_LABELS.map((label) => (
                <option key={label} value={label}>
                  {label}
                </option>
              ))}
            </select>
          ) : (
            <input
              type={selectedType === "min_duration" || selectedType === "max_duration" ? "number" : "text"}
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              placeholder={
                selectedType === "min_duration" || selectedType === "max_duration"
                  ? "Seconds"
                  : "Enter value…"
              }
              min={selectedType === "min_duration" || selectedType === "max_duration" ? 0 : undefined}
              className="rounded-md border border-border bg-background px-2 py-1 text-xs w-36"
              autoFocus
            />
          )}
          <Button type="submit" size="sm" variant="outline" className="h-7 text-xs" disabled={!inputValue.trim()}>
            Add
          </Button>
          <Button type="button" size="sm" variant="ghost" className="h-7 text-xs" onClick={handleCancel}>
            Cancel
          </Button>
        </form>
      ) : (
        <div className="relative">
          <Button
            type="button"
            variant="outline"
            size="sm"
            className="h-7 text-xs gap-1"
            onClick={() => setShowAddMenu((v) => !v)}
            disabled={availableOptions.length === 0}
          >
            <Plus className="h-3 w-3" />
            Add filter
          </Button>
          {showAddMenu && availableOptions.length > 0 && (
            <>
              <div className="fixed inset-0 z-10" onClick={() => setShowAddMenu(false)} />
              <div className="absolute left-0 top-full mt-1 z-20 min-w-[160px] rounded-md border border-border bg-white shadow-lg py-1">
                {availableOptions.map((option) => (
                  <button
                    key={option.type}
                    type="button"
                    onClick={() => handleSelectType(option.type)}
                    className="w-full text-left px-3 py-1.5 text-xs hover:bg-muted transition-colors"
                  >
                    {option.label}
                  </button>
                ))}
              </div>
            </>
          )}
        </div>
      )}
    </div>
  );
}
