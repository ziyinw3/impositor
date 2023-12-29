import os
import sys
import subprocess
import time
import PyPDF2
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

# Set up GUI
class Dialogue(tk.Tk):
    def __init__(self, title):
        super().__init__()
        self.title(title)

        # Create a frame to hold the widgets
        frame = tk.Frame(self, padx=100, pady=20)
        frame.pack()

        # File selection
        self.file_label = tk.Label(frame, text="Select a file:")
        self.file_label.grid(row=0, column=0, padx=5, pady=5)
        self.file_button = tk.Button(frame, text="Browse", command=self.select_file)
        self.file_button.grid(row=0, column=1, padx=5, pady=5)

        # Display number of pages
        self.pages_label = tk.Label(frame, text="Number of pages in manuscript:")
        self.pages_label.grid(row=1, column=0, padx=5, pady=5)
        self.pages_display = tk.Label(frame, text="")
        self.pages_display.grid(row=1, column=1, padx=5, pady=5)

        # Enter # of quires and pages
        self.quires_label = tk.Label(frame, text="Number of quires:")
        self.quires_label.grid(row=2, column=0, padx=5, pady=5)
        self.quires_entry = tk.Entry(frame, width=10)
        self.quires_entry.grid(row=2, column=1, padx=5, pady=5)

        self.pages_label = tk.Label(frame, text="Number of pages per quire:")
        self.pages_label.grid(row=3, column=0, padx=5, pady=5)
        self.pages_entry = tk.Entry(frame, width=10)
        self.pages_entry.grid(row=3, column=1, padx=5, pady=5)

        # Progress bar
        self.progress_label = tk.Label(frame, text="Progress:")
        self.progress_label.grid(row=4, column=0, padx=5, pady=5)
        self.progress_bar = ttk.Progressbar(frame, mode='determinate', length=200)
        self.progress_bar.grid(row=4, column=1, padx=5, pady=5)

        # OK button
        self.submit_button = tk.Button(frame, text="Confirm", command=self.submit)
        self.submit_button.grid(row=5, columnspan=2, pady=20)
        self.number_of_pages = 0

        # Bind the Escape key to the end_program function
        self.bind("<Escape>", self.end_program)

    # Class functions
    def select_file(self):
        self.file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if self.file_path:
            file_title = self.file_path.split("/")[-1]
            self.file_label.config(text=f"File title: {file_title}")

            # Retrieve the number of pages directly within the select_file method
            try:
                pdf = PyPDF2.PdfFileReader(self.file_path)
                self.number_of_pages = pdf.getNumPages()
                self.pages_display.config(text=f"{self.number_of_pages}")
            except Exception as e:
                print(f"Error getting number of pages: {str(e)}")
                self.pages_display.config(text="Number of Pages: Error")

        else:
            self.file_label.config(text="File Title:")

    def submit(self):
        quires = self.quires_entry.get()
        pages = self.pages_entry.get()

        if self.file_path:
            if quires:
                quires = int(quires)
            if pages:
                pages = int(pages)
            if quires:
                if quires <= 0 or self.number_of_pages % quires != 0:
                    messagebox.showerror("Error", "Number of quires not divisible by manuscript length.")
                else:
                    pages = self.number_of_pages // quires
            if pages:
                if pages <= 0 or pages % 2 != 0 or self.number_of_pages % pages != 0:
                    messagebox.showerror("Error", "Manuscript length not divisible by quire size, or quire size is odd.")
                else:
                    quires = self.number_of_pages // pages

            if quires and pages:
                if quires * pages != self.number_of_pages:
                    messagebox.showerror("Error", "Quires times pages per quire does not equal manuscript length. Tip: Clear both fields and put in only an even value for number of pages per quire.")

            if not quires and not pages:
                messagebox.showerror("Error", "Please fill at least one field.")

            print("File path:", self.file_path)
            print("Total number of pages:", self.number_of_pages)
            print("Number of quires:", quires)
            print("Number of pages per quire:", pages)

            process_pdf(self, self.file_path, quires, pages)
            self.destroy()

        else:
            messagebox.showerror("Error", "Please select a file.")

    def end_program(self, event):
        print("Escape key pressed")
        self.destroy()

# Set up PDF processing
def process_pdf(dialogue, file_path, quires, pages):
    if quires and pages:
        # start clock
        start_time = time.time()

        print("Now processing PDF")

        pdf = PyPDF2.PdfFileReader(file_path)
        impositioned_pdf = PyPDF2.PdfFileWriter()
        total_pages = pdf.getNumPages()

        # Update progress bar settings
        progress_step = 100 / total_pages * 2
        progress_value = 0
        dialogue.progress_bar.config(mode='determinate', maximum=100, value=progress_value)

        for q in range(quires):
            print("Working on quire #:" + str(q + 1))
            # iterate through each pair of pages within the current quire
            for i in range(pages // 2):
                # set up if i even
                if i % 2 != 0:
                    left_page = pdf.pages[q * pages + i]
                    right_page = pdf.pages[q * pages + pages - i - 1]
                else:
                    right_page = pdf.pages[q * pages + i]
                    left_page = pdf.pages[q * pages + pages - i - 1]
                concat_page = PyPDF2.pdf.PageObject.createBlankPage(
                    width=left_page.mediaBox.getWidth() + right_page.mediaBox.getWidth(),
                    height=left_page.mediaBox.getHeight()
                )
                concat_page.mergeTranslatedPage(left_page, 0, 0)
                concat_page.mergeTranslatedPage(right_page, left_page.mediaBox.getWidth(), 0)
                impositioned_pdf.addPage(concat_page)

                # Update progress bar value
                progress_value += progress_step
                dialogue.progress_bar['value'] = progress_value
                dialogue.update_idletasks()

        # save pdf
        # parse the new file path
        input_dir, input_filename = os.path.split(file_path)
        input_name, input_ext = os.path.splitext(input_filename)

        # Create the new file path for the output PDF
        new_file_name = f"{input_name}_impositioned.pdf"
        new_file_path = os.path.join(input_dir, new_file_name)

        with open(new_file_path, "wb") as new_pdf_file:
            impositioned_pdf.write(new_pdf_file)
            messagebox.showinfo("Operations", f"Saved to folder: {new_file_name}")

        end_time = time.time()
        runtime = end_time - start_time
        print(f"Elapsed Time: {runtime:.2f} seconds")

# Main function to create and manage the GUI
def main():
    while True:
        user_input = Dialogue("Options")
        user_input.mainloop()

        response = messagebox.askyesno("Continue?", "Do you want to imposit another file?")
        if not response:
            break  # Exit the loop if the user doesn't want to continue

# start program
if __name__ == "__main__":
    main()
