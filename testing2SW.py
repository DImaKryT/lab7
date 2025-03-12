import tkinter as tk
from tkinter import simpledialog, messagebox
import threading
import pickle
import json
test_cases = [
    # Тест для дії assign
    ({"V1": 0, "V2": 5}, {"V1": 5, "V2": 5}),
    # Тест для дії input (припускаємо, що введене значення - 10)
    ({"V1": 0}, {"V1": 10}),
    # Тест для дії print
    ({"V1": 5}, {"V1": 5}),
    # Тест для дії condition з оператором ==
    ({"V1": 5, "V2": 5}, {"V1": 5, "V2": 5}),
    # Тест для дії condition з оператором <
    ({"V1": 5, "V2": 10}, {"V1": 5, "V2": 10}),
]

class Block:
    def __init__(self, block_type, value=None):
        self.block_type = block_type
        self.value = value

    def to_dict(self):
        return {"block_type": self.block_type, "value": self.value}

    @staticmethod
    def from_dict(data):
        return Block(data["block_type"], data.get("value"))

class BlockScheme:
    def __init__(self):
        self.blocks = []

    def add_block(self, block):
        if len(self.blocks) < 100:
            self.blocks.append(block)
        else:
            raise Exception("Maximum number of blocks reached")

    def to_dict(self):
        return {"blocks": [block.to_dict() for block in self.blocks]}

    @staticmethod
    def from_dict(data):
        scheme = BlockScheme()
        for block_data in data["blocks"]:
            scheme.add_block(Block.from_dict(block_data))
        return scheme

class PythonCodeGenerator:
    def __init__(self, schemes):
        self.schemes = schemes

    def generate_code(self):
        code = []
        code.append("import threading")
        code.append("import queue")
        code.append("\nvariables = {f'V{i}': 0 for i in range(1, 101)}\n")
        
        for i, scheme in enumerate(self.schemes):
            code.append(f"def thread_{i}():")
            for block in scheme.blocks:
                if block.block_type == "assign":
                    if "=" not in block.value:
                        raise ValueError(f"Invalid assign block value: {block.value}")
                    V1, V2 = block.value.split("=")
                    code.append(f"    variables['{V1.strip()}'] = variables['{V2.strip()}']")
                elif block.block_type == "input":
                    V = block.value
                    code.append(f"    variables['{V}'] = int(input('Enter value for {V}: '))")
                elif block.block_type == "print":
                    V = block.value
                    code.append(f"    print(variables['{V}'])")
                elif block.block_type == "condition":
                    if "==" in block.value:
                        V, C = block.value.split("==")
                        code.append(f"    if variables['{V.strip()}'] == {int(C.strip())}:")
                        code.append("        pass")
                    elif "<" in block.value:
                        V, C = block.value.split("<")
                        code.append(f"    if variables['{V.strip()}'] < {int(C.strip())}:")
                        code.append("        pass")
            code.append("")

        code.append("threads = []")
        for i in range(len(self.schemes)):
            code.append(f"threads.append(threading.Thread(target=thread_{i}))")
        code.append("")
        code.append("for thread in threads:")
        code.append("    thread.start()")
        code.append("")
        code.append("for thread in threads:")
        code.append("    thread.join()")
        
        return "\n".join(code)

    def save_to_file(self, filename):
        code = self.generate_code()
        with open(filename, 'w') as file:
            file.write(code)
        print(f"Code saved to {filename}")

class BlockSchemeEditor:
    def __init__(self, master):
        self.master = master
        self.master.title("Block Scheme Editor")
        self.scheme = BlockScheme()
        self.schemes = []
        self.create_widgets()

    def create_widgets(self):
        self.block_listbox = tk.Listbox(self.master)
        self.block_listbox.pack()

        self.block_type_var = tk.StringVar(self.master)
        self.block_type_var.set("assign")  # Default value
        self.block_type_menu = tk.OptionMenu(self.master, self.block_type_var, "assign", "input", "print", "condition")
        self.block_type_menu.pack()

        self.add_block_button = tk.Button(self.master, text="Add Block", command=self.add_block)
        self.add_block_button.pack()

        self.save_button = tk.Button(self.master, text="Save Scheme", command=self.save_scheme)
        self.save_button.pack()

        self.load_button = tk.Button(self.master, text="Load Scheme", command=self.load_scheme)
        self.load_button.pack()

        self.add_scheme_button = tk.Button(self.master, text="Add Scheme", command=self.add_scheme)
        self.add_scheme_button.pack()

        self.generate_code_button = tk.Button(self.master, text="Generate Code", command=self.generate_code)
        self.generate_code_button.pack()

        self.run_tests_button = tk.Button(self.master, text="Run Tests", command=self.run_tests)
        self.run_tests_button.pack()

    def add_block(self):
        block_type = self.block_type_var.get()
        value = simpledialog.askstring("Input", f"Enter value for {block_type} block (if applicable):")
        if block_type == "assign" and "=" not in value:
            messagebox.showerror("Error", "Assign block value must be in the format 'V1=V2'.")
            return
        if block_type == "condition" and not any(op in value for op in ["==", "<"]):
            messagebox.showerror("Error", "Condition block value must contain '==' or '<'.")
            return
        block = Block(block_type, value)
        self.scheme.add_block(block)
        self.block_listbox.insert(tk.END, f"{block_type}: {value}")

    def save_scheme(self):
        filename = simpledialog.askstring("Input", "Enter filename:")
        with open(filename, 'wb') as f:
            pickle.dump(self.scheme.to_dict(), f)
        messagebox.showinfo("Info", "Scheme saved successfully")

    def load_scheme(self):
        filename = simpledialog.askstring("Input", "Enter filename:")
        with open(filename, 'rb') as f:
            data = pickle.load(f)
            self.scheme = BlockScheme.from_dict(data)
        self.update_listbox()

    def add_scheme(self):
        self.schemes.append(self.scheme)
        self.scheme = BlockScheme()
        self.block_listbox.delete(0, tk.END)
        messagebox.showinfo("Info", "Scheme added. You can start creating a new scheme.")

    def generate_code(self):
        filename = simpledialog.askstring("Input", "Enter filename for the generated code:")
        generator = PythonCodeGenerator(self.schemes)
        generator.save_to_file(filename)

    def update_listbox(self):
        self.block_listbox.delete(0, tk.END)
        for block in self.scheme.blocks:
            self.block_listbox.insert(tk.END, f"{block.block_type}: {block.value}")

    def run_tests(self):
        program = MultithreadedProgram(self.schemes)
        tester = Tester(program, test_cases)
        max_operations = int(simpledialog.askstring("Input", "Enter maximum number of operations for testing: "))
        success_rate = tester.run_tests(max_operations)
        messagebox.showinfo("Test Results", f"Success rate: {success_rate}%")

class MultithreadedProgram:
    def __init__(self, schemes):
        self.schemes = schemes
        self.variables = {f"V{i}": 0 for i in range(1, 101)}

    def run_scheme(self, scheme):
        for block in scheme.blocks:
            if block.block_type == "assign":
                V1, V2 = block.value.split("=")
                self.variables[V1.strip()] = self.variables[V2.strip()]
            elif block.block_type == "input":
                V = block.value
                self.variables[V] = int(input(f"Enter value for {V}: "))
            elif block.block_type == "print":
                V = block.value
                print(self.variables[V])
            elif block.block_type == "condition":
                if "==" in block.value:
                    V, C = block.value.split("==")
                    if self.variables[V.strip()] == int(C.strip()):
                        continue
                    else:
                        break
                elif "<" in block.value:
                    V, C = block.value.split("<")
                    if self.variables[V.strip()] < int(C.strip()):
                        continue
                    else:
                        break

    def run(self):
        threads = []
        for scheme in self.schemes:
            thread = threading.Thread(target=self.run_scheme, args=(scheme,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

    def reset_variables(self, initial_values):
        for key, value in initial_values.items():
            self.variables[key] = value

class Tester:
    def __init__(self, program, test_cases):
        self.program = program
        self.test_cases = test_cases

    def run_tests(self, max_operations=20):
        total_tests = len(self.test_cases)
        successful_tests = 0

        for input_data, expected_output in self.test_cases:
            self.program.reset_variables(input_data)  # Встановлення вхідних значень
            operations_count = 0

            for scheme in self.program.schemes:
                self.program.run_scheme(scheme)
                operations_count += len(scheme.blocks)

                if operations_count > max_operations:
                    break  # Перевищено ліміт операцій

            actual_output = {key: self.program.variables[key] for key in expected_output.keys()}  # Отримання значень змінних

            if actual_output == expected_output:
                successful_tests += 1
            else:
                print(f"Test failed: input {input_data}, expected {expected_output}, but got {actual_output}")

        success_rate = (successful_tests / total_tests) * 100
        return success_rate

    def is_action_present(self, block_type):
        for scheme in self.program.schemes:
            for block in scheme.blocks:
                if block.block_type == block_type:
                    return True
        return False

def main():
    root = tk.Tk()
    editor = BlockSchemeEditor(root)
    root.mainloop()

if __name__ == "__main__":
    main()