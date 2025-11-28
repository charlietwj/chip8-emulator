import pygame

class Chip8:
    
    def __init__(self):
        self.memory = [0] * 4096
        self.display = [[0] * 64 for _ in range(32)]
        self.PC = 0x200
        self.I = 0
        self.stack = []
        self.delay_timer = 0
        self.sound_timer = 0
        self.registers = [0] * 16

def read_chip8(name: str) -> None:
    lines = []
    with open(name, "rb") as file:
        lines.append(file.readline())

    for line in lines:
        print(line)
        break

if __name__ == "__main__":
    read_chip8("IBMLogo.ch8")