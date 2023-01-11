import os
import re
import argparse
import ast


class CodeAnalyzer:

    """This is class that analyses PYTHON code according to PEP8.
    This class analyses code by the path."""

    issues_db = {                                           # issues database
              1: "S001 Too long",
              2: "S002 Indentation is not a multiple of four",
              3: "S003 Unnecessary semicolon after a statement",
              4: "S004 Less than two spaces before inline comments",
              5: "S005 TODO found",
              6: "S006 More than two blank lines used before this line",
              7: "S007 Too many spaces after ",
              8: ["S008 Class name ", " should use CamelCase"],
              9: ["S009 Function name ", " should use snake_case"],
              10: ["S010 Argument name ", " should be written in snake_case"],
              11: ["S011 Variable ", " should be written in snake_case"],
              12: "S012 The default argument value is mutable."
              }

    def __init__(self, path):
        self.file_path = path
        with open(self.file_path, "r") as file:
            self.text = file.read()                 # executing text from the file
        self.lines = self.text.split("\n")          # splitting text into the list
        self.lines_n_problems = dict()              # creating dict for incode problems
        self.blank_counter = 0                      # lines counter

    def len_checker(self, clear_line, l_name):

        """Method that checks clear_line's length. If length more than 79,
        adds issue from database to lines_n_problems by lines_name."""

        if len(clear_line) > 79:
            self.lines_n_problems[l_name].append(self.issues_db[1])

    def indent_check(self, clear_line, l_name):

        """Checks line's indentation."""

        c = 0
        for char in clear_line:
            if char == " ":
                c += 1
            elif char != " ":
                break
        if c % 4 != 0:
            self.lines_n_problems[l_name].append(self.issues_db[2])

    def semicolon_check(self, clear_line, l_name):

        """Checking using semicolon in lines with comments and in lines without them."""

        if "#" in clear_line and ";" in clear_line:
            splited_line = clear_line.split("#")
            code = splited_line[0].strip()
            if code.endswith(";"):
                self.lines_n_problems[l_name].append(self.issues_db[3])
        else:
            mc_line = clear_line.strip()
            if mc_line.endswith(";"):
                self.lines_n_problems[l_name].append(self.issues_db[3])

    def spcs_bfr_comment(self, clear_line, l_name):

        """Checking spaces after # mark."""

        if "#" in clear_line:
            split_lst = clear_line.split("#")
            if not split_lst[0].endswith("  ") and split_lst[0] != "":
                self.lines_n_problems[l_name].append(self.issues_db[4])

    def todo_founder(self, clear_line, l_name):

        """Searching 'To do' word in comments."""

        if "#" in clear_line:
            clear_lst = clear_line.split("#")
            finder = re.search(r"[tT][o|O][d|D][o|O]", clear_lst[1])
            if finder:
                self.lines_n_problems[l_name].append(self.issues_db[5])

    def blank_line(self, clear_line, l_name):

        """Counting blank lines between codes lines."""

        if clear_line == "":
            self.blank_counter += 1
        elif clear_line != "":
            if self.blank_counter > 2:
                self.lines_n_problems[l_name].append(self.issues_db[6])
                self.blank_counter = 0
            else:
                self.blank_counter = 0

    def check_spaces(self, clear_line, l_name):

        """Checking spaces after class and def words."""

        if clear_line.find("def") != -1 and re.match(r".*def\b \w+", clear_line) is None:
            self.lines_n_problems[l_name].append(self.issues_db[7] + "'def'")
        if clear_line.find("class") != -1 and re.match(r".*class\b \w+", clear_line) is None:
            self.lines_n_problems[l_name].append(self.issues_db[7] + "'class'")

    def class_name(self, clear_line, l_name):

        """Checking class name for camel case."""

        if clear_line.find("class") != -1 and re.match(r".*class *[A-Z][A-Za-z]+", clear_line) is None:
            line_list = clear_line.split()
            class_name = line_list[1].rstrip("():")
            self.lines_n_problems[l_name].append(self.issues_db[8][0] + f"'{class_name}'" + self.issues_db[8][1])

    def func_name(self, clear_line, l_name):

        """Checking function name for snake case."""

        if clear_line.find("def") != -1 and re.match(r".*def *[a-z\d_]+", clear_line) is None:
            line_list = clear_line.split()
            function_name = line_list[1].rstrip("():")
            self.lines_n_problems[l_name].append(self.issues_db[9][0] + f"'{function_name}'" + self.issues_db[9][1])

    def arg_name(self):

        """Checking functions argument names for snake case."""

        tree = ast.parse(self.text)
        nodes = ast.walk(tree)
        for node in nodes:
            if isinstance(node, ast.FunctionDef):
                argument_names = [a.arg for a in node.args.args]
                for name in argument_names:
                    if re.match(r'^[A-Z]', name):
                        issue = self.issues_db[10][0] + f"'{name}'" + self.issues_db[10][1]
                        self.lines_n_problems[f"Line {node.lineno}"].append(issue)

    def var_name(self):

        """Checking variables names for snake case."""

        tree = ast.parse(self.text)
        nodes = ast.walk(tree)
        for node in nodes:
            if isinstance(node, ast.Name):
                var_name = node.id
                if re.match(r'^[A-Z]', var_name):
                    issue = self.issues_db[11][0] + f"'{var_name}'" + self.issues_db[11][1]
                    mark = True
                    for value in self.lines_n_problems.values():
                        for i in value:
                            if i == issue:
                                mark = False
                    if mark:
                        line_name = f"Line {node.lineno}"
                        self.lines_n_problems[line_name].append(issue)

    def def_arg_mutable(self):

        """Checking argument for mutability."""

        tree = ast.parse(self.text)
        nodes = ast.walk(tree)
        for node in nodes:
            if isinstance(node, ast.FunctionDef):
                defaults = node.args.defaults
                for item in defaults:
                    if isinstance(item, ast.List):
                        line_name = f"Line {node.lineno}"
                        self.lines_n_problems[line_name].append(self.issues_db[12])

    def main_check(self):

        """This method gathers all checking methods. Reading text line by line."""

        for i in range(len(self.lines)):
            line_number = i + 1
            line_name = f"Line {line_number}"
            self.lines_n_problems[line_name] = []
            pure_line = self.lines[i].strip("\n")
            self.len_checker(pure_line, line_name)
            self.indent_check(pure_line, line_name)
            self.semicolon_check(pure_line, line_name)
            self.spcs_bfr_comment(pure_line, line_name)
            self.todo_founder(pure_line, line_name)
            self.blank_line(pure_line, line_name)
            if "class" in pure_line or "def" in pure_line:
                self.check_spaces(pure_line, line_name)
                self.class_name(pure_line, line_name)
                self.func_name(pure_line, line_name)
        self.arg_name()
        self.var_name()
        self.def_arg_mutable()

    def issue_printer(self):

        """Printing issues from lines_n_problems database according to sample:
        [path to the file]: Line [lines number]: [issue from database]
        """

        for line_num, issues in self.lines_n_problems.items():
            for issue in issues:
                print(f"{self.file_path}: {line_num}: {issue}")


def main():

    """Main function that carries file path of the .py file or path containing .py
    files and checks them for issues."""

    parser = argparse.ArgumentParser(description="Checking file or files in directory for following PEP8")
    parser.add_argument("directory_or_file", type=str, help="Input directory or file to analyze code in it.")
    args = parser.parse_args()

    file_path = args.directory_or_file
    if file_path.endswith(".py"):
        analyzer = CodeAnalyzer(file_path)
        analyzer.main_check()
        analyzer.issue_printer()
    else:
        py_files = [file for file in os.listdir(file_path) if file.endswith(".py")]
        for file in py_files:
            full_path = os.path.join(file_path, file)
            analyzer = CodeAnalyzer(full_path)
            analyzer.main_check()
            analyzer.issue_printer()


if __name__ == "__main__":
    main()
