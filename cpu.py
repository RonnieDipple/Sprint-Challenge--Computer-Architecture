import sys



# SPRINT
CMP = 0b10100111
JMP = 0b01010100
JEQ = 0b01010101
JNE = 0b01010110

Dict = {
    "CMP": "0b10100111"

}

# load test # filename = sys.argv[1]
# Instructions
HLT = 0b00000001  # Exit op_code
LDI = 0b10000010  # Set op_a register to value op_b
PRN = 0b01000111  # Print
MUL = 0b10100010  # ALU opcode
PUSH = 0b01000101 # Stack opcode
POP = 0b01000110  # Stack opcode



class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.program_counter = 0  # Program counter
        self.ram = [0] * 256
        self.reg = [0] * 8  # Only vals b/t 0-255, bitwise AND results with 0xFF
        self.reg[7] = 0xf4  # Reserved register: Stack pointer
        # Stacks grow down?
        self.sp = self.reg[7]
        # Flag value set by CMP: 0b00000LGE
        self.fl = 0b00000000
        # SPRINT
        self.dispatch_table[CMP] = self.handle_CMP
        self.dispatch_table[JMP] = self.handle_JMP
        self.dispatch_table[JEQ] = self.handle_JEQ
        self.dispatch_table[JNE] = self.handle_JNE

        self.dispatch_table = {}
        self.dispatch_table[HLT] = self.handle_HLT
        self.dispatch_table[LDI] = self.handle_LDI
        self.dispatch_table[PRN] = self.handle_PRN
        self.dispatch_table[MUL] = self.handle_MUL
        self.dispatch_table[PUSH] = self.handle_PUSH
        self.dispatch_table[POP] = self.handle_POP


    def handle_HLT(self):
        sys.exit(0)  # exit

    def handle_PRN(self):
        op_a = self.ram_read(self.program_counter + 1)
        print(self.ram[op_a])

    def handle_MUL(self):
        # Read values to multiply
        op_a = int(self.ram_read(self.program_counter + 1))  # RAM Register a
        op_b = int(self.ram_read(self.program_counter + 2))  # RAM Register b
        # Copies the values to ALU register
        self.reg[op_a] = self.ram_read(op_a)
        self.reg[op_b] = self.ram_read(op_b)
        # Perform ALU computation, overwrite RAM register op_a
        self.ram_write(op_a, self.alu("MUL", op_a, op_b))

    def handle_LDI(self):
        op_a = int(self.ram_read(self.program_counter + 2))  # val base10
        op_b = int(self.ram_read(self.program_counter + 1))  # Register base10
        self.ram_write(op_b, op_a)

    def handle_PUSH(self):
        # Decrement stack pointer
        self.sp -= 1
        # Copies value in register to SP address
        op_a = self.ram_read(self.ram_read(self.program_counter + 1))
        self.ram_write(self.sp, op_a)

    def handle_POP(self):
        # Copies val from self.sp address to register
        op_a = self.ram_read(self.program_counter + 1)
        self.ram_write(op_a, self.ram_read(self.sp))
        # Increment stack pointer
        self.sp += 1

    def handle_CMP(self):
        # Reads values to compare
        op_a = int(self.ram_read(self.program_counter + 1))  # RAM Register a
        op_b = int(self.ram_read(self.program_counter + 2))  # RAM Register b
        # Copies values to ALU register
        self.reg[op_a] = self.ram_read(op_a)
        self.reg[op_b] = self.ram_read(op_b)
        # Performs ALU computation: compare and set flag
        self.alu("CMP", op_a, op_b)

    def handle_JMP(self):
        # Set PC to address stored in given register
        op_a = int(self.ram_read(self.program_counter + 1))  # Register storing jump addr
        self.program_counter = self.ram_read(op_a)

    def handle_JEQ(self):
        # Jumps if Equality FLAG is True
        op_a = int(self.ram_read(self.program_counter + 1))  # Register storing jump addr
        if self.fl == 0b00000001:
            self.program_counter = self.ram_read(op_a)

    def handle_JNE(self):
        # Jumps if Equality FLAG is False/0
        op_a = int(self.ram_read(self.program_counter + 1))  # Register storing jump addr
        if self.fl == 0b00000100:
            self.program_counter = self.ram_read(op_a)
        elif self.fl == 0b00000010:
            self.program_counter = self.ram_read(op_a)

    def load(self, filename):
        """Load a program into memory."""
        program = []
        with open(filename, 'r') as f:
            for line in f:
                if line[:8].isnumeric():
                    command = int(line[:8], 2)
                    program.append(command)
        f.close()

        address = 0
        for instruction in program:
            self.ram[address] = instruction
            address += 1

    def ram_read(self, MAR):
        return self.ram[MAR]

    def ram_write(self, MAR, MDR):
        self.ram[MAR] = MDR
        return

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""
        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
            return self.reg[reg_a]
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
            return self.reg[reg_a]
        elif op == "CMP":
            if self.reg[reg_a] > self.reg[reg_b]:
                self.fl = 0b00000010
            elif self.reg[reg_a] == self.reg[reg_b]:
                self.fl = 0b00000001
            else:
                self.fl = 0b00000100
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.program_counter,
            #self.fl,
            #self.ie,
            self.ram_read(self.program_counter),
            self.ram_read(self.program_counter + 1),
            self.ram_read(self.program_counter + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    
