import pygame

class Chip8:
    
    def __init__(self):
        self.memory = [0] * 4096
        self.display = [[False] * 64 for _ in range(32)]
        self.PC = 0x200
        self.I = 0
        self.stack = []
        self.delay_timer = 0
        self.sound_timer = 0
        self.V = [0] * 16
        self.keypad = [False] * 16

        font = [
            0xF0, 0x90, 0x90, 0x90, 0xF0, # 0
            0x20, 0x60, 0x20, 0x20, 0x70, # 1
            0xF0, 0x10, 0xF0, 0x80, 0xF0, # 2
            0xF0, 0x10, 0xF0, 0x10, 0xF0, # 3
            0x90, 0x90, 0xF0, 0x10, 0x10, # 4
            0xF0, 0x80, 0xF0, 0x10, 0xF0, # 5
            0xF0, 0x80, 0xF0, 0x90, 0xF0, # 6
            0xF0, 0x10, 0x20, 0x40, 0x40, # 7
            0xF0, 0x90, 0xF0, 0x90, 0xF0, # 8
            0xF0, 0x90, 0xF0, 0x10, 0xF0, # 9
            0xF0, 0x90, 0xF0, 0x90, 0x90, # A
            0xE0, 0x90, 0xE0, 0x90, 0xE0, # B
            0xF0, 0x80, 0x80, 0x80, 0xF0, # C
            0xE0, 0x90, 0x90, 0x90, 0xE0, # D
            0xF0, 0x80, 0xF0, 0x80, 0xF0, # E
            0xF0, 0x80, 0xF0, 0x80, 0x80  # F
        ]

        for i in range(len(font)):
            self.memory[i+0x50] = font[i]

    def load_rom(self, name: str) -> None:
        with open(name, "rb") as file:
            data = file.read()

        for i, byte_value in enumerate(data):
            self.memory[0x200 + i] = byte_value

    def cycle(self) -> None:
        # fetch opcode
        opcode = self.memory[self.PC << 8] | self.memory[self.PC+1]
        self.PC += 2

        # decode and execute
        self.execute_opcode(opcode)

        # update timers
        if self.delay_timer > 0:
            self.delay_timer -= 1
        
        if self.sound_timer > 0:
            self.sound_timer -= 1

    def execute_opcode(self, opcode: int) -> None:
        instruction = (opcode & 0xF000) >> 12
        x = (opcode & 0x0F00) >> 8
        y = (opcode & 0x00F0) >> 4
        n = opcode & 0x000F
        nn = opcode & 0x00FF
        nnn = opcode & 0x0FFF

        if instruction == 0x0:
            if nn == 0xE0:
                for i in range(32):
                    for j in range(64):
                        self.display[i][j] = False
        elif instruction == 0x1:
            self.PC = nnn
        elif instruction == 0x6:
            self.V[x] = nn
        elif instruction == 0x7:
            self.V[x] += nn
        elif instruction == 0xA:
            self.I = nnn
        

if __name__ == "__main__":
    chip8 = Chip8()
    chip8.load_rom("roms/IBMLogo.ch8")
