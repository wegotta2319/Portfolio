import pandas as pd
import tkinter as tk
import numpy as np
from tkinter import ttk
from tkinterdnd2 import TkinterDnD, DND_FILES
from datetime import datetime, timedelta


def validate_dates_and_cost():
    try:
        sheet_name = entry_sheet_name.get()
        start_date_input = entry_start_date.get()
        end_date_input = entry_end_date.get()
        min_cost_input = entry_min_cost.get()
        max_cost_input = entry_max_cost.get()

        min_cost_input = round(float(min_cost_input), 3)
        max_cost_input = round(float(max_cost_input), 3)
         
        if not file_path.get():
            raise ValueError("No file selected. Please drag and drop a file.")

        df = pd.read_excel(file_path.get(), sheet_name=sheet_name)

        # Default start and end dates if fields are blank
        start_date = datetime.strptime(start_date_input, "%m/%d/%Y").date() if start_date_input else None
        end_date = datetime.strptime(end_date_input, "%m/%d/%Y").date() if end_date_input else None

        # Default cost range if fields are blank
        min_cost = round(float(min_cost_input), 2) if min_cost_input else 0
        max_cost = round(float(max_cost_input), 2) if max_cost_input else float('inf')

        # Initialize all variables
        num_of_wrong_start_date = 0
        num_of_correct_start_date = 0
        num_of_wrong_end_date = 0
        num_of_correct_end_date = 0
        num_of_both_out_of_bounds = 0
        num_of_way_after_start_date = 0
        num_of_way_before_end_date = 0
        num_of_invalid_cost = 0
        num_of_valid_cost = 0

        results_text = "Validation Results:\n\n"

        # Convert the 'Start date' and 'End date' columns to datetime objects in the dataframe
        df['Start date'] = pd.to_datetime(df['Start date'], format='%m/%d/%Y')
        df['End date'] = pd.to_datetime(df['End date'], format='%m/%d/%Y')

        # Define thresholds (e.g., 30 days difference for "way after" or "way before")
        threshold = timedelta(days=7)

        for i, row in df.iterrows():
            row_start_date = row['Start date'].date()
            row_end_date = row['End date'].date()
            row_cost = row['Cost']  # Changed to 'Cost' as per your specification

            # Check if both dates are out of bounds, only if start_date and end_date are provided
            if start_date and end_date:
                if row_start_date < start_date and row_end_date > end_date:
                    results_text += (
                        f"{df.loc[i, 'Activity']} has both start and end dates out of bounds "
                        f"(Start: {row_start_date}, End: {row_end_date}).\n"
                    )
                    num_of_both_out_of_bounds += 1
                else:
                    # Validate start date
                    if row_start_date < start_date:
                        results_text += (
                            f"{df.loc[i, 'Activity']} start date is before the desired start date "
                            f"(Start: {row_start_date}).\n"
                        )
                        num_of_wrong_start_date += 1
                    elif row_start_date > start_date + threshold:
                        results_text += (
                            f"{df.loc[i, 'Activity']} start date is way after the desired start date "
                            f"(Start: {row_start_date}).\n"
                        )
                        num_of_way_after_start_date += 1
                    else:
                        num_of_correct_start_date += 1

                    # Validate end date
                    if row_end_date > end_date:
                        results_text += (
                            f"{df.loc[i, 'Activity']} end date is after the desired end date "
                            f"(End: {row_end_date}).\n"
                        )
                        num_of_wrong_end_date += 1
                    elif row_end_date < end_date - threshold:
                        results_text += (
                            f"{df.loc[i, 'Activity']} end date is way before the desired end date "
                            f"(End: {row_end_date}).\n"
                        )
                        num_of_way_before_end_date += 1
                    else:
                        num_of_correct_end_date += 1
            else:
                # Skip date validation if the dates are not provided
                num_of_correct_start_date += 1
                num_of_correct_end_date += 1

            # Validate cost
            if row_cost < min_cost or row_cost > max_cost:
                results_text += (
                    f"{df.loc[i, 'Activity']} has an invalid cost (Cost: {row_cost}). "
                    f"Expected cost between {min_cost} and {max_cost}.\n"
                )
                num_of_invalid_cost += 1
            else:
                num_of_valid_cost += 1

        results_text += (
            f"\nSummary:\n"
            f"Number of valid start dates: {num_of_correct_start_date}\n"
            f"Number of invalid start dates: {num_of_wrong_start_date}\n"
            f"Number of start dates way after the desired start date: {num_of_way_after_start_date}\n"
            f"Number of valid end dates: {num_of_correct_end_date}\n"
            f"Number of invalid end dates: {num_of_wrong_end_date}\n"
            f"Number of end dates way before the desired end date: {num_of_way_before_end_date}\n"
            f"Number of activities with both dates out of bounds: {num_of_both_out_of_bounds}\n"
            f"Number of valid costs: {num_of_valid_cost}\n"
            f"Number of invalid costs: {num_of_invalid_cost}\n"
        )

        text_output.delete(1.0, tk.END)
        text_output.insert(tk.END, results_text)

    except Exception as e:
        text_output.delete(1.0, tk.END)
        text_output.insert(tk.END, f"Error: {str(e)}")


def on_file_drop(event):
    file_path.set(event.data)
    label_file_path.config(text=f"Selected File: {event.data}")

def clear_fields():
    #clears all fields and the file path
    entry_start_date.delete(0,tk.END)
    entry_end_date.delete(0,tk.END)
    entry_sheet_name.delete(0,tk.END)
    file_path.set("")
    label_file_path.config(text = "Drag and Drop a file here")
    text_output.delete(1.0,tk.END)

def quit_program():
    #Quits the program
    window.quit()


# GUI setup
window = TkinterDnD.Tk()
window.title("Amilia Date and Cost Checker")

# Set theme colors
window.configure(bg="white")

# Configure grid layout
window.rowconfigure(0, weight=1)
window.rowconfigure(1, weight=1)
window.columnconfigure(0, weight=1)

# Frame for input fields
frame_inputs = tk.Frame(window, bg="white")
frame_inputs.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

# Frame for output
frame_output = tk.Frame(window, bg="white")
frame_output.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

# File path label
file_path = tk.StringVar()
label_file_path = tk.Label(frame_inputs, text="Drag and drop a file here", bg="lightblue", fg="black", anchor="w", relief="solid")
label_file_path.grid(row=0, column=0, columnspan=2, sticky="ew", pady=5, ipadx=10, ipady=10)

# Enable drag-and-drop
label_file_path.drop_target_register(DND_FILES)
label_file_path.dnd_bind('<<Drop>>', on_file_drop)

# Input labels and entry fields
label_start_date = tk.Label(frame_inputs, text="Start Date (MM/DD/YYYY):", bg="white", fg="blue")
label_start_date.grid(row=1, column=0, sticky="w", pady=5)
entry_start_date = tk.Entry(frame_inputs, width=30, fg="black")
entry_start_date.grid(row=1, column=1, sticky="ew", pady=5)

label_end_date = tk.Label(frame_inputs, text="End Date (MM/DD/YYYY):", bg="white", fg="blue")
label_end_date.grid(row=2, column=0, sticky="w", pady=5)
entry_end_date = tk.Entry(frame_inputs, width=30, fg="black")
entry_end_date.grid(row=2, column=1, sticky="ew", pady=5)

label_sheet_name = tk.Label(frame_inputs, text="Sheet Name (Required):", bg="white", fg="blue")
label_sheet_name.grid(row=3, column=0, sticky="w", pady=5)
entry_sheet_name = tk.Entry(frame_inputs, width=30, fg="black")
entry_sheet_name.grid(row=3, column=1, sticky="ew", pady=5)

label_min_cost = tk.Label(frame_inputs, text="Minimum Cost:", bg="white", fg="blue")
label_min_cost.grid(row=4, column=0, sticky="w", pady=5)
entry_min_cost = tk.Entry(frame_inputs, width=30, fg="black")
entry_min_cost.grid(row=4, column=1, sticky="ew", pady=5)

label_max_cost = tk.Label(frame_inputs, text="Maximum Cost:", bg="white", fg="blue")
label_max_cost.grid(row=5, column=0, sticky="w", pady=5)
entry_max_cost = tk.Entry(frame_inputs, width=30, fg="black")
entry_max_cost.grid(row=5, column=1, sticky="ew", pady=5)

# Buttons
button_validate = tk.Button(frame_inputs, text="Validate", bg="lightgreen", fg="black", command=validate_dates_and_cost, height=2, width=2)
button_validate.grid(row=6, column=0, sticky="ew", pady=5, padx=5)

button_clear = tk.Button(frame_inputs, text="Clear", bg="lightcoral", fg="black", command=clear_fields, height=2, width=2)
button_clear.grid(row=6, column=1, sticky="ew", pady=5, padx=5)

button_quit = tk.Button(frame_inputs, text="Quit", bg="salmon", fg="black", command=quit_program, height=2, width=5)
button_quit.grid(row=6, column=2, columnspan=2, sticky="ew", pady=5, padx=5)

# Output Textbox
text_output = tk.Text(frame_output, wrap="word", height=15, width=40)
text_output.grid(row=0, column=0, padx=10, pady=10)

# Start the Tkinter loop
window.mainloop()
