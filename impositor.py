import os
import sys
import subprocess
import time

# Check requirements to install
requirements = "./requirements.txt"

try:
    # Use subprocess.run to capture the output and return code
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", "-r", requirements],
        capture_output=True,
        text=True,
        check=True  # This will raise a CalledProcessError if the command fails
    )
    
    # Print the output of the pip command
    print(result.stdout)

except subprocess.CalledProcessError as e:
    print("Error installing requirements:")
    print(e.stderr)  # Print the error message if the command failed

except Exception as e:
    print("An unexpected error occurred:")
    print(str(e))

# Imports
import PyPDF2
import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox

# Set up GUI
# ... (previous code)

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

        # Display total number of pages in manuscript
        self.pages_label = tk.Label(frame, text="Number of pages in manuscript:")
        self.pages_label.grid(row=1, column=0, padx=5, pady=5)
        self.total_pages_label = tk.Label(frame, text="")
        self.total_pages_label.grid(row=1, column=1, padx=5, pady=5)

        # Enter # of quires and pages per quire
        self.quires_label = tk.Label(frame, text="Number of quires:")
        self.quires_label.grid(row=2, column=0, padx=5, pady=5)
        self.quires_entry_var = tk.StringVar()
        self.quires_entry = tk.Entry(frame, width=10, textvariable=self.quires_entry_var)
        self.quires_entry.grid(row=2, column=1, padx=5, pady=5)
        self.quires_entry_var.trace_add('write', self.update_values)

        self.quire_pages_label = tk.Label(frame, text="Number of pages per quire:")
        self.quire_pages_label.grid(row=3, column=0, padx=5, pady=5)
        self.quire_pages_entry_var = tk.StringVar()
        self.quire_pages_entry = tk.Entry(frame, width=10, textvariable=self.quire_pages_entry_var)
        self.quire_pages_entry.grid(row=3, column=1, padx=5, pady=5)
        self.quire_pages_entry_var.trace_add('write', self.update_values)

        # OK button
        self.submit_button = tk.Button(frame, text="Confirm", command=self.submit)
        self.submit_button.grid(row=4, columnspan=2, pady=20)

        # Initialize file path and total pages
        self.file_path = None
        self.total_pages = None

    # Class functions
    def select_file(self):
        self.file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if self.file_path:
            file_title = self.file_path.split("/")[-1]
            self.file_label.config(text=f"File title: {file_title}")

            # Display total number of pages in manuscript
            original_pdf = PyPDF2.PdfFileReader(self.file_path)
            self.total_pages = original_pdf.getNumPages()
            self.total_pages_label.config(text=f"{self.total_pages} pages")

            # Update quires and quire pages if one is already entered
            self.update_values()

    def update_values(self, *args):
        try:
            quires = int(self.quires_entry_var.get()) if self.quires_entry_var.get() else None
            quire_pages = int(self.quire_pages_entry_var.get()) if self.quire_pages_entry_var.get() else None

            if quires is not None and quire_pages is None:
                # Calculate and update quire pages
                quire_pages = self.total_pages // quires
                self.quire_pages_entry_var.set(str(quire_pages))
            elif quires is None and quire_pages is not None:
                # Calculate and update quires
                quires = self.total_pages // quire_pages
                self.quires_entry_var.set(str(quires))

            if quires is not None:
                if quires <= 0 or quires != int(self.quires_entry_var.get()):
                    self.quires_entry.config(bg="red")
                    self.quires_entry_var.set("!")
                else:
                    self.quires_entry.config(bg="white")

            if quire_pages is not None:
                if quire_pages <= 0 or quire_pages % 2 != 0 or quire_pages != int(self.quire_pages_entry_var.get()):
                    self.quire_pages_entry.config(bg="red")
                    self.quire_pages_entry_var.set("!")
                else:
                    self.quire_pages_entry.config(bg="white")

        except ValueError:
            pass

    def submit(self):
        quires = self.quires_entry_var.get()
        quire_pages = self.quire_pages_entry_var.get()

        if not self.file_path or not quires or not quire_pages:
            messagebox.showerror("Error", "Please fill in all fields.")
            return

        try:
            quires = int(quires)
            quire_pages = int(quire_pages)

            if quires <= 0 or quire_pages <= 0 or quire_pages % 2 != 0:
                messagebox.showerror("Error", "Quires and pages per quire must be positive integers. Pages per quire must be even.")
                return

            # Validate the number of pages in the original script
            original_pdf = PyPDF2.PdfFileReader(self.file_path)
            total_pages_original = original_pdf.getNumPages()
            if quires * quire_pages != total_pages_original:
                messagebox.showerror("Error", "The product of quire number and pages per quire must equal the total number of pages in the original script.")
                return

            print("File path:", self.file_path)
            print("Number of quires:", quires)
            print("Number of pages per quire:", quire_pages)

            # process_pdf(self.file_path, quires, quire_pages)  # Uncomment this line to enable the processing
            self.destroy()

        except ValueError:
            messagebox.showerror("Error", "Please enter valid numerical values.")



# Set up PDF processing
def process_pdf(file_path, quires, pages):
    try:
        # start clock
        start_time = time.time()

        print("Now processing PDF")

        quires = int(quires)
        pages = int(pages)
        if pages % 2 != 0:
            raise ValueError("Total number of pages must be even.")
        
        pages_per_quire = pages // quires
        # print(str(pages_per_quire))
        
        pdf = PyPDF2.PdfFileReader(file_path)
        impositioned_pdf = PyPDF2.PdfFileWriter()
        for q in range(quires):
            print("Working on quire #:" + str(q + 1))
            # iterate through each pair of pages within current quire
            for i in range(pages_per_quire // 2):
                # set up if i even
                if i % 2 != 0:
                    left_page = pdf.pages[q * pages_per_quire + i]
                    right_page = pdf.pages[q * pages_per_quire + pages_per_quire - i - 1]
                else:
                    right_page = pdf.pages[q * pages_per_quire + i]
                    left_page = pdf.pages[q * pages_per_quire + pages_per_quire - i - 1]
                concat_page = PyPDF2.pdf.PageObject.createBlankPage(
                    width=left_page.mediaBox.getWidth() + right_page.mediaBox.getWidth(),
                    height=left_page.mediaBox.getHeight()
                )
                concat_page.mergeTranslatedPage(left_page, 0, 0)
                concat_page.mergeTranslatedPage(right_page, left_page.mediaBox.getWidth(), 0)
                impositioned_pdf.addPage(concat_page)
        # save pdf
        # parse new file path
        input_dir, input_filename = os.path.split(file_path)
        input_name, input_ext = os.path.splitext(input_filename)

        # Create the new file path for the output PDF
        new_file_name = f"{input_name}_impositioned.pdf"
        new_file_path = os.path.join(input_dir, new_file_name)

        with open(new_file_path, "wb") as new_pdf_file:
            impositioned_pdf.write(new_pdf_file)
            messagebox.showinfo("Operations", "Saved to folder.")

        end_time = time.time()
        runtime = end_time - start_time
        print(f"Elapsed Time: {runtime:.2f} seconds")

    except Exception as e:
        print(f"Error processing page {i}: {str(e)}")
        messagebox.showerror("Error", str(e))

# Main function to create and manage the GUI
def main():
    while True:
        user_input = Dialogue("Options")
        user_input.mainloop()

        response = messagebox.askyesno("Continue?", "Do you want to imposit another file?")
        if not response:
            messagebox.showinfo("Thanks!", "Thanks for using!")
            break  # Exit the loop if the user doesn't want to continue
        # user_input.destroy()

# start program
if __name__ == "__main__":
    main()
