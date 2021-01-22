# ////////////////////////////////////////////////////////////
# |||||||||||||||||||Welcome to optiMIPS||||||||||||||||||||||
# Designers : Baris Guzel 2315935
#             Ilgar Sahin Kocak 2316024
#             Tugberk Ozden Ergonca 2243889
# Developed at python3 version 3.8.5
# ||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\


# importing numpy library functions for base conversion operations
from numpy import binary_repr

# Takes register and returns 5bit binary(str) or Error
def binaryRegisters(registerName):
    return {
        "$zero": "00000",
        "$at": "00001",
        "$v0": "00010",
        "$v1": "00011",
        "$a0": "00100",
        "$a1": "00101",
        "$a2": "00110",
        "$a3": "00111",
        "$t0": "01000",
        "$t1": "01001",
        "$t2": "01010",
        "$t3": "01011",
        "$t4": "01100",
        "$t5": "01101",
        "$t6": "01110",
        "$t7": "01111",
        "$s0": "10000",
        "$s1": "10001",
        "$s2": "10010",
        "$s3": "10011",
        "$s4": "10100",
        "$s5": "10101",
        "$s6": "10110",
        "$s7": "10111",
        "$t8": "11000",
        "$t9": "11001",
        "$k0": "11010",
        "$k1": "11011",
        "$gp": "11100",
        "$sp": "11101",
        "$fp": "11110",
        "$ra": "11111",
    }.get(registerName, "Error")


# Takes opcode and returns 6bit binary or Error
def binaryOpcode(Opcode):
    return {
        "add": "000000",
        "addi": "001000",
        "lw": "100011",
        "sw": "101011",
        "slt": "000000",
        "slti": "001010",
        "sll": "000000",
        "move": "000000",
        "beq": "000100",
        "bne": "000101",
        "j": "000010",
        "jal": "000011",
        "jr": "000000",
    }.get(Opcode, "Error")


# Takes op and returns type of the instr more elif statements can be added to define new types
def insType(Opcode):
    if Opcode == "000000":
        return "0"  # R type
    elif (
        Opcode == "001000"
        or Opcode == "100011"
        or Opcode == "101011"
        or Opcode == "001010"
        or Opcode == "000100"
        or Opcode == "000101"
    ):
        return "1"  # I type
    elif Opcode == "000010" or Opcode == "000011":
        return "2"  # J type


# Takes op and returns funct field in binary
def binaryFunct(Funct):
    return {"add": "100000", "slt": "101010", "sll": "000000", "jr": "001000"}.get(
        Funct, "Error"
    )


# Checks if the op is psudo or not in this code only move is being used others are just examples
def pseudoCheck(Opcode):
    return {"move": False, "li": False, "clear": False, "blt": False}.get(Opcode, True)


# Distinguises register order in the I type instruction
def ItypeSelect(op):
    return {"beq": 1, "bne": 1, "sw": 2, "lw": 2, "addi": 3, "slti": 3}.get(op, 0)


# Label dictionary: Default label is arbitrary data if there is a label called Default its
# value will be changed to the label address
labelDict = {"Default": "Error"}

# At the start of batch mode reads program.src and records label names and addresses to labelDict
def findLabelLine(programPath):
    f = open(programPath, "r")
    f1 = f.readlines()
    counter = 2147487744  # starting address 0x80001000 in decimal
    # Search for labels and if it isnt a duplicate writes it to labelDict
    for x in f1:
        if x.split(":").__len__() == 2:
            if x.split(":")[0] in labelDict.keys():
                print("Same label used twice or more")
                return "0"
            else:
                label = x.split(":")[0]
                labelDict[label] = counter
        counter += 4


# Checks required fields are created inside instr[] list This being called before constructing each instruction
# For Rtype and Itype there are 4 spaces needed to be created for J it is 2.
# Returns False when the case is true!!!!
def instrFormat(instrType, instr):
    if (instrType == "Rtype" and instr[0] != "jr") or instrType == "Itype":
        if instr.__len__() == 4:
            return False
        else:
            return True
    elif instrType == "Jtype" or (instrType == "Rtype" and instr[0] == "jr"):
        if instr.__len__() == 2:
            return False
        else:
            return True


# Common function to convert 32 bit binary input to hex and for each mode prints
# or writes to file
def constructHex(binarycode, mode):
    output = "0x%0*X" % (8, int(binarycode, 2))
    return output


# If instruction in R type doesnt match with the op rd rs rt shamt func format
# Add fix algorithms here if needed
def RtypeFormatFix(instr, counter):
    if instr[0] == "jr":
        instr.append("$zero")
        instr.append("$zero")
        instr.append("")
        instr[1], instr[2] = instr[2], instr[1]
        instr[1], instr[4] = instr[4], instr[1]
        return instr
    elif instr[0] == "sll":
        instr[4] = instr[3].strip()
        instr[3] = instr[2]
        instr[2] = "$zero"
        if instr[4][:2] == "0x" and int(instr[4][2:], 16) < 32:
            instr[4] = binary_repr(int(instr[4], 16), width=5)
        else:
            try:
                instr[4] = int(instr[4])
                if instr[4] < 32 and instr[4] >= 0:
                    instr[4] = binary_repr(instr[4], width=5)
                else:
                    print(
                        "Enter a shift value between 32 and 0 in line:" + str(counter)
                    )
                    return "0"
            except:
                print(
                    "Invalid shift amount. Enter hex or decimal in line:" + str(counter)
                )
                return "0"
        return instr
    else:  # if not returns the same instr array
        return instr


# Handling Rtype Instruction
# Takes instr array converts each term to binary
# Starts by checking if its psudo instruction converts it to rtype then checks if instruction taken corretly with instrFormat()
# Function converts special Rtype cases to default Rtype with RtypeFormatFix() and sends it to constructHex function
# To add new pseudo instruction: add its conversion algorithm to else case of pseudoCheck(instr[0])
# To add special case Rtype attach new algorithms to required fields (Follow sll as example) inside RtypeFormatFix()
# Default R type list instr[] consists these fields in order: opcode rd rs rt shamt funct
def Rtype(instr, mode, counter):
    if pseudoCheck(instr[0]):
        if instrFormat("Rtype", instr):
            return "Invalid R type instruction usage in line:" + str(counter)

        # Adds func field as 00000 default
        instr.append("00000")

        instr = RtypeFormatFix(instr, counter)

        if binaryOpcode(instr[0]) != "Error":
            opcode = binaryOpcode(instr[0])
            shamt = instr[4]
            funct = binaryFunct(instr[0])
        else:
            return "Invalid opcode definition in line:" + str(counter)

        if binaryRegisters(instr[1]) != "Error":
            rd = binaryRegisters(instr[1])
        else:
            return "Invalid rd register definition in line :" + str(counter)

        if binaryRegisters(instr[2].strip()) != "Error":
            rs = binaryRegisters(instr[2].strip())
        else:
            return "Invalid rs register definition in line:" + str(counter)

        if binaryRegisters(instr[3].strip()) != "Error":
            rt = binaryRegisters(instr[3].strip())
        else:
            return "Invalid rt register definition in line:" + str(counter)

        return constructHex(opcode + rs + rt + rd + shamt + funct, mode)

    else:  # For this code defining move is enough but one can add more psuedo instructions to psudoCheck dictionary and add if else case here to convert
        if instr[0] == "move":
            instr[0] = "add"
            instr.append("$zero")
            return Rtype(instr, mode, counter)
        else:
            return "Not defined Instruction"


# Handling J Type Instruction
# Takes instr array converts each term to binary
# Starts by checking if its psudo instruction converts it to jtype format
# First takes opcode then checks jump address type: hex, decimal, label
# For label uses labelDict dictionary to find address of the label. Check findLabelLine()
# To add new pseudo instruction: add its conversion algorithm to else case of pseudoCheck(instr[0])
# To add special case Jtype attach new algorithms to required fields
# Default J type list instr[] consists these fields in order: opcode jumpaddress
def Jtype(instr, mode, counter):
    if pseudoCheck(instr[0]):
        if instrFormat("Jtype", instr):
            return "Invalid J type instruction usage"

        if binaryOpcode(instr[0]) != "Error":
            opcode = binaryOpcode(instr[0])
        else:
            return "Invalid opcode definition"

        if instr[1][:2] == "0x" and int(instr[1][2:], 16) <= 67108863:
            addr = binary_repr(int(instr[1], 16), width=26)
        else:
            try:
                instr[1] = int(instr[1])
                if instr[1] <= 33554431 and instr[1] >= -33554432:
                    addr = binary_repr(instr[1], width=26)
                else:
                    return "Value is out of reach"
            except ValueError:
                if mode == "2":
                    return "In interactive mode enter hex or decimal"
                elif mode == "1":
                    if instr[1].strip() in labelDict.keys():
                        addr = binary_repr(labelDict[instr[1].strip()], width=32)[4:30]
                    else:
                        return "Jump location not defined in line:" + counter

    else:
        print("There is no such instruction defined as" + instr[0])
        return 0  # if there is a psuedo instruction add conversion here

    return constructHex(opcode + addr, mode)


# For Lw and Sw instructions gets rid of ( and )
def memoryTypeFix(instr, counter):
    if ItypeSelect(instr[0]) == 2:
        try:
            lwSplit = instr[2].split("(")[:1] + instr[2].split("(")[1].split(")")[:1]
            instr = instr[0:2] + lwSplit
            instr[2], instr[3] = instr[3], instr[2]
            return instr
        except IndexError:
            return "0"
    else:
        return instr


# Handling I Type Instruction
# Takes instr array converts each term to binary
# Starts by checking if its psudo instruction and converts it to Itype format
# For label uses labelDict dictionary to find address of the label
# To add new pseudo instruction: add its conversion algorithm to else case of pseudoCheck(instr[0])
# There are 3 types setted inside ItypeSelect() function. (lw,sw/aritmetic/branch)
# If wanted to use different order than default add more types and instructions to ItypeSelect
# And define a function similar to memoryTypeFix() to convert it to default I type construct
# Default I type list instr[] consists these fields in order: opcode rs rt address/offset
def Itype(instr, mode, counter):
    if pseudoCheck(instr[0]):

        # Additional function for Lw Sw dependencies
        instr = memoryTypeFix(instr, counter)

        if instrFormat("Itype", instr):
            return "Invalid I type instruction usage in Line: " + str(counter)

        if binaryOpcode(instr[0]) != "Error":
            opcode = binaryOpcode(instr[0])
        else:
            return "Invalid opcode definition in Line: " + str(counter)

        if binaryRegisters(instr[1]) != "Error":
            rt = binaryRegisters(instr[1])
        else:
            if ItypeSelect(instr[0]) == 1:
                return "Invalid rs register definition in Line: " + str(counter)
            else:
                return "Invalid rt register definition in Line: " + str(counter)
        if binaryRegisters(instr[2].lstrip()) != "Error":
            rs = binaryRegisters(instr[2].lstrip())
        else:
            if ItypeSelect(instr[0]) == 1:
                return "Invalid rt register definition in Line: " + str(counter)
            else:
                return "Invalid rs register definition in Line: " + str(counter)

        # Checks if branch address is written as hex decimal or a label
        try:
            instr[3] = instr[3].strip()
            if instr[3][:2] == "0x" and int(instr[3][2:], 16) <= 65534:
                addr = binary_repr(int(instr[3], 16), width=16)
            else:
                try:
                    instr[3] = int(instr[3])
                    if instr[3] <= 32767 and instr[3] >= -32768:
                        addr = binary_repr(instr[3], width=16)
                    else:
                        return "Out of reach"
                except:
                    if mode == "2":
                        return "In interactive mode enter hex or decimal"
                    elif mode == "1":
                        if instr[3].strip() in labelDict.keys():
                            instrLocation = counter * 4 + 2147487744
                            branchAddr = int(labelDict[instr[3].strip()])
                            branchDistance = branchAddr - instrLocation
                            addr = binary_repr(int(branchDistance), width=32)[14:30]
                            return constructHex(opcode + rt + rs + addr, mode)
                        else:
                            return "Branch location not defined in line:" + str(counter)
        except ValueError:
            return "I type format is instr reg, reg, addr in line:" + str(counter)

        if ItypeSelect(instr[0]) == 1:  # branch instructions
            return constructHex(opcode + rt + rs + addr, mode)
        elif ItypeSelect(instr[0]) == 3 or ItypeSelect(instr[0]) == 2:
            return constructHex(opcode + rs + rt + addr, mode)
        else:
            return "There were an internal Error!"
    else:
        return "There is no such instruction defined as" + instr[0]
    # Add pseudo instructions here if wanted to include. Check move definition inside Rtype func


# Common builder
# Clears whitespaces gets rid of comments and splits instruction to each field then
# Sends the splittedInstruction array to corresponding type's function
# There are 3 types defined: R type, I type, J type if another type needed to be added:
# Add new instructions opcodes to binarycode(), define the new type inside insType() and thoes instructions to insType()
def builder(instr, mode, counter):
    try:
        instruction = instr.strip().lower()
        instruction = instruction.split("#")[0]
        if instruction.split(":").__len__() == 2:
            instruction = instruction.split(":")[1]
        elif instruction.split(":").__len__() > 2:
            return "More than one ':' in line:" + str(counter)
        splittedInstruction = (
            instruction.split(",")[0].split() + instruction.split(",")[1:]
        )
        # uncomment below line to print each elements send to construction functions
        # print(splittedInstruction)
        if insType(binaryOpcode(splittedInstruction[0])) == "0":
            return Rtype(splittedInstruction, mode, counter)
        elif insType(binaryOpcode(splittedInstruction[0])) == "1":
            return Itype(splittedInstruction, mode, counter)
        elif insType(binaryOpcode(splittedInstruction[0])) == "2":
            return Jtype(splittedInstruction, mode, counter)
        else:
            return "Invalid or not defined instruction!"
    except IndexError:
        return ("Code should be written without empty lines In line:", +str(counter))


# This will be initialized when program started. Asks batch mode or interactive mode
if __name__ == "__main__":
    a = "default"
    print("Disclaimer: for batch mode create a file called program.src in the same dir")

    while a != "q":
        mode = input("Enter 1 for batch 2 for interact1ive mode \n")
        if mode == "1":
            programPath = "program.src"
            f = open(programPath, "r")
            programFile = f.readlines()
            results = open("output.obj", "w")
            counter = 0  # line counter
            try:
                findLabelLine(programPath)
            except:
                print("Error occured from label definitions" + str(counter))
            try:
                # Uncomment below line to print collected labels
                # print(labelDict)
                for x in programFile:
                    counter += 1
                    if "0x" in builder(x, mode, counter):
                        results.writelines(str(builder(x, mode, counter)) + "\n")
                    else:
                        print(str(builder(x, mode, counter)))
                        exit()
                print("File is written")
            except:
                print("Error occured program terminated")
            a = input("Press 'q' to quit or press 's' to select mode again \n")
        elif mode == "2":
            a = "default"
            while a != "q" and a != "s":
                try:
                    instruction = input("Enter one line of instruction \n")
                    print(builder(instruction, mode, "0") + "\n")
                    a = input("Press 'q' to quit or press 's' to select mode again \n")
                except TypeError:
                    print("Error occured program terminated")
        else:
            print("Invalid  mode number!!\n", "Try 1 or 2")
