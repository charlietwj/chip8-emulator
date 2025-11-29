import pygame
import random

class Chip8:
    
    def __init__(self, size: int):
        self.size = size
        self.memory = [0] * 4096
        self.display = [[False] * 32 for _ in range(64)]
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
        opcode = (self.memory[self.PC] << 8) | self.memory[self.PC+1]
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
            if opcode == 0x00E0:
                for i in range(64):
                    for j in range(32):
                        self.display[i][j] = False
            elif opcode == 0x00EE:
                address = self.stack.pop()
                self.PC = address
        elif instruction == 0x1:
            self.PC = nnn
        elif instruction == 0x2:
            self.stack.append(self.PC)
            self.PC = nnn
        elif instruction == 0x3:
            if self.V[x] == nn:
                self.PC += 2
        elif instruction == 0x4:
            if self.V[x] != nn:
                self.PC += 2
        elif instruction == 0x5:
            if self.V[x] == self.V[y]:
                self.PC += 2
        elif instruction == 0x6:
            self.V[x] = nn
        elif instruction == 0x7:
            self.V[x] += nn
        elif instruction == 0x8:
            if n == 0x0:
                self.V[x] = self.V[y]
            elif n == 0x1:
                self.V[x] |= self.V[y]
            elif n == 0x2:
                self.V[x] &= self.V[y]
            elif n == 0x3:
                self.V[x] ^= self.V[y]
            elif n == 0x4:
                if 0xFF - self.V[x] < self.V[y]:
                    self.V[0xF] = 1
                else:
                    self.V[0xF] = 0
                
                self.V[x] += self.V[y]
            elif n == 0x5:
                if self.V[x] >= self.V[y]:
                    self.V[0xF] = 1
                else:
                    self.V[0xF] = 0

                self.V[x] -= self.V[y]
            elif n == 0x6:
                self.V[x] = self.V[y]
                self.V[0xF] = self.V[x] & 1
                self.V[x] >>= 1
            elif n == 0x7:
                if self.V[x] <= self.Y[y]:
                    self.V[0xF] = 1
                else:
                    self.V[0xF] = 0

                self.V[x] = self.V[y] - self.V[x]
            elif n == 0xE:
                self.V[x] = self.V[y]
                self.V[0xF] = self.V[x] & (1 << 7)
                self.V[x] <<= 1
        elif instruction == 0x9:
            if self.V[x] != self.V[y]:
                self.PC += 2
        elif instruction == 0xA:
            self.I = nnn
        elif instruction == 0xB:
            self.PC = nnn + self.V[0]
        elif instruction == 0xC:
            self.V[x] = random.randint(0x0, 0xFF) & nn
        elif instruction == 0xD:
            x_coord = self.V[x] & 0x3F
            y_coord = self.V[y] & 0x1F
            self.V[0xF] = 0

            for j in range(n):
                if y_coord + j >= 0x20:
                    break

                current_byte = self.memory[self.I + j]

                for i in range(8):
                    if x_coord + i >= 0x40:
                        break

                    current_bit = current_byte & (1 << (7-i))
                    self.display[x_coord + i][y_coord + j] ^= current_bit
        elif instruction == 0xE:
            if nn == 0x9E:
                if self.keypad[self.V[x]]:
                    self.PC += 2
            elif nn == 0xA1:
                if not self.keypad[self.V[x]]:
                    self.PC += 2
        elif instruction == 0xF:
            if nn == 0x07:
                self.V[x] = self.delay_timer
            elif nn == 0x15:
                self.delay_timer = self.V[x]
            elif nn == 0x18:
                self.sound_timer = self.V[x]
            elif nn == 0x1E:
                self.I += self.V[x]
            elif nn == 0x0A:
                key_pressed = None
                for i in range(0x10):
                    if self.keypad[i]:
                        key_pressed = i

                if key_pressed is None:
                    self.PC -= 2
                else:
                    self.V[x] = key_pressed
            elif nn == 0x29:
                value = self.V[x] * 0x000F
                self.I = 0x50 + value * 5
            elif nn == 0x33:
                position = self.I
                number = self.V[x]
                for value in [100, 10, 1]:
                    self.memory[position] = number // value
                    number %= value
                    position += 1
            elif nn == 0x55:
                for i in range(x+1):
                    self.memory[self.I + i] = self.V[i]
            elif nn == 0x65:
                for i in range(x+1):
                    self.V[i] = self.memory[self.I + i]

    def handle_input(self, event: pygame.event.Event) -> None:
        pass

    def draw_graphics(self, screen: pygame.Surface) -> None:
        off_color = (0, 0, 0)
        on_color = (255, 255, 255)

        screen.fill(off_color)
        for i in range(64):
            for j in range(32):
                if not self.display[i][j]:
                    continue
                
                x_coord = i * self.size
                y_coord = j * self.size
                rect = pygame.Rect(x_coord, y_coord, self.size, self.size)
                pygame.draw.rect(screen, on_color, rect)

def game_loop():
    size = 12
    width = 64
    height = 32

    chip8 = Chip8(size)
    chip8.load_rom("roms/IBMLogo.ch8")

    pygame.init()
    screen = pygame.display.set_mode((width * size, height * size))
    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            chip8.handle_input(event)

        chip8.cycle()
        chip8.draw_graphics(screen)

        pygame.display.flip()
        clock.tick(500)

    pygame.quit()

if __name__ == "__main__":
    game_loop()
