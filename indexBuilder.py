#!/usr/bin/env python3
def main():
    #open the file for parsing
    with open("AP_Coll_Parsed_9/AP880212", "r") as file:
        content = file.read()
        print(content)


if __name__ == "__main__":
    main()
