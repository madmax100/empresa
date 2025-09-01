import * as React from "react"
import { DayPicker } from "react-day-picker"
import { cn } from "../../../lib/utils"

type CalendarProps = React.ComponentProps<typeof DayPicker>

function Calendar({
  className,
  classNames,
  showOutsideDays = true,
  ...props
}: CalendarProps) {
  return (
    <DayPicker
      showOutsideDays={showOutsideDays}
      className={cn("p-4", className)}
      classNames={{
        months: "flex flex-col sm:flex-row space-y-4 sm:space-x-4 sm:space-y-0",
        month: "space-y-4",
        caption: "flex justify-center pt-1 relative items-center mb-4",
        caption_label: "text-lg font-semibold text-foreground",
        nav: "space-x-1 flex items-center",
        nav_button: cn(
          "h-8 w-8 bg-transparent p-0 text-muted-foreground hover:text-foreground",
          "hover:bg-muted rounded-md transition-colors",
          "border border-input"
        ),
        nav_button_previous: "absolute left-1",
        nav_button_next: "absolute right-1",
        table: "w-full border-collapse",
        head_row: "flex w-full mb-2",
        head_cell: "text-muted-foreground rounded-md w-10 font-medium text-sm flex-1 text-center py-2",
        row: "flex w-full mt-1",
        cell: cn(
          "relative p-0 text-center text-sm flex-1",
          "focus-within:relative focus-within:z-20"
        ),
        day: cn(
          "h-10 w-10 p-0 font-normal text-sm rounded-md transition-all duration-200",
          "hover:bg-accent hover:text-accent-foreground",
          "focus:bg-accent focus:text-accent-foreground focus:outline-none",
          "disabled:pointer-events-none disabled:opacity-50"
        ),
        day_selected:
          "bg-primary text-primary-foreground hover:bg-primary/90 focus:bg-primary/90 font-medium shadow-sm",
        day_today: "bg-accent text-accent-foreground font-semibold border-2 border-primary/50",
        day_outside: "text-muted-foreground/60 hover:bg-muted/50",
        day_disabled: "text-muted-foreground/30 line-through",
        day_range_middle: "aria-selected:bg-accent/50 aria-selected:text-accent-foreground rounded-none",
        day_range_start: "rounded-r-none bg-primary text-primary-foreground",
        day_range_end: "rounded-l-none bg-primary text-primary-foreground",
        day_hidden: "invisible",
        ...classNames,
      }}
      {...props}
    />
  )
}
Calendar.displayName = "Calendar"

export { Calendar }