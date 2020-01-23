"""
INI FILE MANAGEMENT
"""


def get(path):  # return ini dict from given ini file path
    with open(path, "r") as file:
        file = file.readlines()

    ini = {}

    def isolate_string(string):
        # remove "\n"
        if "\n" in string:
            string = string[:string.find("\n")] + string[string.find("\n") + 2:]
        # convert to list
        string_as_list = []
        for char in string:
            string_as_list.append(char)
        # remove spaces
        i = 0
        for char in string_as_list:
            if char == " ":
                string_as_list.pop(i)
            i += 1
        string = ""
        # reconvert to string
        for char in string_as_list:
            string += char
        return string

    for line in file:
        if "=" in line:
            ini[isolate_string(line[:line.find("=")])] = isolate_string(line[line.find("=")+1:])
    return ini


def write(path, ini):  # write ini file to given path from given ini dict
    with open(path, "w") as file:
        for variable in ini:
            file.write(variable + " = " + ini[variable] + "\n")
