import pygame

class Chip8:
    pass

def read_chip8(name: str) -> None:
    lines = []
    with open(name, "rb") as file:
        lines.append(file.readline())

    for line in lines:
        print(line)
        break

if __name__ == "__main__":
    read_chip8("IBMLogo.ch8")