"""CPU functionality."""

import sys

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.pc = 0
        self.reg[7] = 0xf4
        self.fl = 0

    def ram_read(self, addr):
        return self.ram[addr]

    def ram_write(self, val, addr):
        self.ram[addr] = val

    def load(self):
        """Load a program into memory."""

        address = 0

        try:
            with open(sys.argv[1]) as f:
                for line in f:
                    # The next line is similar to guided project, but I had to check if line == "\n" instead of line == '', since I use Windows
                    if line == '\n' or line[0] == "#":
                        continue
                    try:
                        strVal = line.split("#")[0]
                        value = int(strVal, 2)
                    except ValueError:
                        print(f"Invalid Number: {strVal}")
                        sys.exit(1)
                    self.ram[address] = value
                    address += 1
        except ValueError:
            print(f"File not found: {sys.argv[1]}")
            sys.exit(2)

        # For now, we've just hardcoded a program:

        # program = [
        #     # From print8.ls8
        #     0b10000010, # LDI R0,8
        #     0b00000000,
        #     0b00001000,
        #     0b01000111, # PRN R0
        #     0b00000000,
        #     0b00000001, # HLT
        # ]

        # for instruction in program:
        #     self.ram[address] = instruction
        #     address += 1


    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "AND":
            self.reg[reg_a] &= self.reg[reg_b]
        elif op == "CMP":
            # According to specs, the flag bits are 00000LGE = Less than, Greater than, Equals (1 for true, 0 for false)
            if self.reg[reg_a] == self.reg[reg_b]:
                self.fl = self.fl | 0b00000001 # This binary-or value ensures the "true" flag at the end is enabled
            else:
                self.fl = self.fl & 0b11111110 # This binary-and value ensures the current values for the other flags don't change while turning off the flag at the end

            if self.reg[reg_a] > self.reg[reg_b]:
                self.fl = self.fl | 0b00000100 # See notes above explaining this
            else:
                self.fl = self.fl & 0b11111011 # Again, see notes above for explanations

            if self.reg[reg_a] < self.reg[reg_b]:
                self.fl = self.fl | 0b00000010 # You know the routine by now
            else:
                self.fl = self.fl & 0b11111101 # Yup.
        elif op == "DEC":
            self.reg[reg_a] -= 1
        elif op == "DIV":
            if self.reg[reg_b] != 0:
                self.reg[reg_a] /= self.reg[reg_b]
            else:
                print("Cannot divide by zero!")
                sys.exit(1)
        elif op == "INC":
            self.reg[reg_a] += 1
        elif op == "MOD":
            if self.reg[reg_b] != 0:
                self.reg[reg_a] = self.reg[reg_a] % self.reg[reg_b]
            else:
                print("Cannot mod by zero!")
                sys.exit(1)
        elif op == "NOT":
            self.reg[reg_a] = 0b11111111 - self.reg[reg_a]
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == "OR":
            self.reg[reg_a] |= self.reg[reg_b]
        elif op == "SHL":
            self.reg[reg_a] = self.reg[reg_a] << self.reg[reg_b]
        elif op == "SHR":
            self.reg[reg_a] = self.reg[reg_a] >> self.reg[reg_b]
        elif op == "SUB":
            self.reg[reg_a] -= self.reg[reg_b]
        elif op == "XOR":
            self.reg[reg_a] ^= self.reg[reg_b]
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""
        
        ADD  = 0b10100000
        AND  = 0b10101000
        CALL = 0b01010000
        CMP  = 0b10100111
        DEC  = 0b01100110
        DIV  = 0b10100011
        HLT  = 0b00000001
        INC  = 0b01100101
        INT  = 0b01010010
        IRET = 0b00010011
        JEQ  = 0b01010101
        JGE  = 0b01011010
        JGT  = 0b01010111
        JLE  = 0b01011001
        JLT  = 0b01011000
        JMP  = 0b01010100
        JNE  = 0b01010110
        LD   = 0b10000011
        LDI  = 0b10000010
        MOD  = 0b10100100
        MUL  = 0b10100010
        NOP  = 0b00000000
        NOT  = 0b01101001
        OR   = 0b10101010
        POP  = 0b01000110
        PRA  = 0b01001000
        PRN  = 0b01000111
        PUSH = 0b01000101
        RET  = 0b00010001
        SHL  = 0b10101100
        SHR  = 0b10101101
        ST   = 0b10000100
        SUB  = 0b10100001
        XOR  = 0b10101011

        running = True

        while running:
            inst = self.ram_read(self.pc)
            opA = self.ram_read(self.pc + 1) # There are some instructions that may - at most - need two values following the instruction.
            opB = self.ram_read(self.pc + 2) # Storing in opA & opB, but may not always be needed. Borrowed this idea from def trace() above

            # Listing ALL of the possible instructions found in LS8-spec, but most will likely be filled with "pass" for now
            if inst == ADD:
                self.alu("ADD", opA, opB)
                self.pc += 3
            elif inst == AND:
                self.aly("AND", opA, opB)
                self.pc += 3
            elif inst == CALL:
                self.reg[7] -= 1
                self.ram[self.reg[7]] = self.pc + 2
                self.pc = self.reg[opA]
            elif inst == CMP:
                self.alu("CMP", opA, opB)
                self.pc += 3
            elif inst == DEC:
                self.alu("DEC", opA, 1)
                self.pc += 2
            elif inst == DIV:
                self.alu("DIV", opA, opB)
                self.pc += 3
            elif inst == HLT:
                running = False
            elif inst == INC:
                self.alu("INC", opA, 1)
                self.pc += 2
            elif inst == INT:
                pass
            elif inst == IRET:
                pass
            elif inst == JEQ:
                # Similar to "JMP", but only if flag = 1, otherwise go to next instruction skipping over the address provided in opA
                if self.fl & 0b00000001 == 0b00000001:
                    self.pc = self.reg[opA]
                else:
                    self.pc += 2
            elif inst == JGE:
                pass
            elif inst == JGT:
                # Similar to "JEQ", but checking the Greater-than flag instead of the Equals flag
                if self.fl & 0b00000010 == 0b00000010:
                    self.pc = self.reg[opA]
                else:
                    self.pc += 2
            elif inst == JLE:
                pass
            elif inst == JLT:
                # Similar to "JEQ", but checking the Less-than flag instead of the the Equals flag
                if self.fl & 0b00000100 == 0b00000100:
                    self.pc = self.reg[opA]
                else:
                    self.pc += 2
            elif inst == JMP:
                self.pc = self.reg[opA]
            elif inst == JNE:
                # Similar to "JMP" and "JEQ", but this time only when flag = 0 instead of 1
                if self.fl & 0b00000001 == 0b00000000:
                    self.pc = self.reg[opA]
                else:
                    self.pc += 2
            elif inst == LD:
                self.reg[opA] = self.ram[opB]
                self.pc += 3
            elif inst == LDI:
                # Load value in addr B into addr A
                self.reg[opA] = opB
                self.pc += 3
            elif inst == MOD:
                self.alu("MOD", opA, opB)
                self.pc += 3
            elif inst == MUL:
                self.alu("MUL", opA, opB)
                self.pc += 3
            elif inst == NOP:
                self.pc += 1
            elif inst == NOT:
                self.alu("NOT", opA, 0)
                self.pc += 2
            elif inst == OR:
                self.alu("OR", opA, opB)
                self.pc += 3
            elif inst == POP:
                # Get value from top of stack (self.reg[7])
                value = self.ram[self.reg[7]]

                # Store value in a register
                self.reg[opA] = value

                # Increment stack pointer
                self.reg[7] += 1
                self.pc += 2
            elif inst == PRA:
                # Use flush=True at end of print statement, according to the instructor
                print(chr(self.reg[opA]), end='', flush=True)
                self.pc += 2
            elif inst == PRN:
                print(self.reg[opA])
                self.pc += 2
            elif inst == PUSH:
                # Decrement stack pointer
                self.reg[7] -= 1

                # Grab value from given register (opA)
                value = self.reg[opA]

                # Copy value onto stack
                self.ram[self.reg[7]] = value
                self.pc += 2
            elif inst == RET:
                self.pc = self.ram[self.reg[7]]
                self.reg[7] += 1
            elif inst == SHL:
                self.alu("SHL", opA, opB)
                self.pc += 3
            elif inst == SHR:
                self.alu("SHR", opA, opB)
                self.pc += 3
            elif inst == ST:
                self.reg[opA] = self.reg[opB]
                self.pc += 3
            elif inst == SUB:
                self.alu("SUB", opA, opB)
                self.pc += 3
            elif inst == XOR:
                self.alu("XOR", opA, opB)
                self.pc += 3
            else:
                print(f"I don't know what {i} is!")
                sys.exit(0)
