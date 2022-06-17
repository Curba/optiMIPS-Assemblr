# ////////////////////////////////////////////////////////////
# |||||||||||||||||||Welcome to optiRISC||||||||||||||||||||||
# Forked from optiMIPS
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
        "r0": "00000",
        "r1": "00001",
        "r2": "00010",
        "r3": "00011",
        "r4": "00100",
        "r5": "00101",
        "r6": "00110",
        "r7": "00111",
        "r8": "01000",
        "r9": "01001",
        "r10": "01010",
        "r11": "01011",
        "r12": "01100",
        "r13": "01101",
        "r14": "01110",
        "r15": "01111",
        "r16": "10000",
        "r17": "10001",
        "r18": "10010",
        "r19": "10011",
        "r20": "10100",
        "r21": "10101",
        "r22": "10110",
        "r23": "10111",
        "r24": "11000",
        "r25": "11001",
        "r26": "11010",
        "r27": "11011",
        "r28": "11100",
        "r29": "11101",
        "r30": "11110",
        "ra": "11111",
    }.get(registerName, "Error")


# Takes opcode and returns 6bit binary or Error
def binaryOpcode(Opcode):
    return {
        "nop": "00000000",
        "add": "00001000",
        "sub": "00010000",
        "mul": "00011000",
        "div": "00100000",
        "and": "00101000",
        "or" : "00110000",
        "xor": "00111000",
        "slt": "01000000",
        "sll": "01001000",
        "srl": "01010000",
        "sra": "01011000",
        "mula": "00000111",
        "sb": "00001001",
        "sh": "00010001",
        "sw": "00011001",
        "lb": "00100001",
        "lbs": "01001001",
        "lh": "00101001",
        "lhs": "01010001",
        "lw": "00110001",
        "beq": "00111001",
        "bne": "01000001",
        "addi": "00000011",
        "subi": "00001011",
        "muli": "00010011",
        "ori": "00011011",
        "xori": "00100011",
        "andi": "00101011",
        "slti": "00110011",
        "ssld": "00111011",
        "jal": "00000100",
    }.get(Opcode, "Error")


# Takes op and returns type of the instr more elif statements can be added to define new types
def insType(Opcode):
    if ((Opcode[5]+Opcode[6]+Opcode[7]) == "000") or ((Opcode[5]+Opcode[6]+Opcode[7]) == "111"):
        return "0"  # R type
    elif ((Opcode[5]+Opcode[6]+Opcode[7]) == "001") or (Opcode[5]+Opcode[6]+Opcode[7]) == "011":
                # 001 load store 011 rest
        return "1"  # I type
    elif (Opcode[5]+Opcode[6]+Opcode[7]) == "100":
        return "2"  # J type

# Distinguises register order in the I type instruction
def ItypeSelect(op):
    return {"beq": 1, "bne": 1, "sw": 2, "lhs": 2, "lh": 2, "lb": 2, "lbs":2, "sh":2, "sb":2, "lw": 2, "addi": 3, "slti": 3}.get(op, 0)


# Label dictionary: Default label is arbitrary data if there is a label called Default its
# value will be changed to the label address
labelDict = {"Default": "Error"}

# At the start of batch mode reads program.src and records label names and addresses to labelDict
def findLabelLine(programPath):
    f = open(programPath, "r")
    f1 = f.readlines()
    counter = 0  # starting address 0x80001000 in decimal
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
    if (instrType == "Rtype" and instr[0] != "mula" and instr[0] != "nop" ) or (instrType == "Itype" and instr[0] != "ssld"):
        if instr.__len__() == 4:
            return False
        else:
            return True
    elif instrType == "Jtype":
        if instr.__len__() == 2:
            return False
        else:
            return True
    elif (instrType == "Itype" and instr[0] == "ssld"):
        if instr.__len__() == 3:
            return False
        else:
            return True
    elif (instrType == "Rtype" and instr[0] == "mula"):
        if instr.__len__() == 5:
            return False
        else:
            return True
    elif (instrType == "Rtype" and instr[0] == "nop"):
        if instr.__len__() == 1:
            return False
        else:
            return True


# Common function to convert 32 bit binary input to hex and for each mode prints
# or writes to file
def constructHex(binarycode, mode):
    output = "%0*X" % (8, int(binarycode, 2))
    outputSpace = output[0] + output[1] + " " + output[2] + output[3] + " " + output[4] + output[5] + " " + output[6] + output[7]
    return outputSpace


# If instruction in R type doesnt match with the op rd rs rt shamt func format
# Add fix algorithms here if needed
def RtypeFormatFix(instr, counter):
    if instr[0] == "sll":
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
    if instrFormat("Rtype", instr):
        return "Invalid R type instruction usage in line:" + str(counter)


    if binaryOpcode(instr[0]) != "Error":
        opcode = binaryOpcode(instr[0])
    else:
        return "Invalid opcode definition in line:" + str(counter)

    if(instr[0] == "nop"):
        rd = "00000"
        ra = "00000"
        rb = "00000"
        rc = "00000"

    else:
        if binaryRegisters(instr[1]) != "Error":
            rd = binaryRegisters(instr[1])
        else:
            print(instr[1])
            return "Invalid rd register definition in line :" + str(counter)

        if binaryRegisters(instr[2].strip()) != "Error":
            ra = binaryRegisters(instr[2].strip())
        else:
            return "Invalid ra register definition in line:" + str(counter)

        print(instr[3])
        if binaryRegisters(instr[3].strip()) != "Error":
            rb = binaryRegisters(instr[3].strip())
            rc = "00000"
        elif (instr[0] == "sll" or instr[0] == "srl" or instr[0] == "sra"):
            if instr[3][:2] == "0x":
                rc = binary_repr(int(instr[3], 10), width=5)
            else:
                rc = binary_repr(int(instr[3], 16), width=5)
            rb = "00000"
        else:
            return "Invalid rb register definition in line:" + str(counter)



        if instr[0] == "mula":
            if binaryRegisters(instr[4].strip()) != "Error":
                rc = binaryRegisters(instr[4].strip())
                print("deagle")
            else:
                return "Invalid rc register definition in line:" + str(counter)

    print(rd + ra + rb + rc + "0000" + opcode )

    return constructHex(rd + ra + rb + rc + "0000" + opcode, mode)


# Handling J Type Instruction
# Takes instr array converts each term to binary
# Starts by checking if its psudo instruction converts it to jtype format
# First takes opcode then checks jump address type: hex, decimal, label
# For label uses labelDict dictionary to find address of the label. Check findLabelLine()
# To add new pseudo instruction: add its conversion algorithm to else case of pseudoCheck(instr[0])
# To add special case Jtype attach new algorithms to required fields
# Default J type list instr[] consists these fields in order: opcode jumpaddress
def Jtype(instr, mode, counter):
    if instrFormat("Jtype", instr):
        return "Invalid J type instruction usage" + counter

    if binaryOpcode(instr[0]) != "Error":
        opcode = binaryOpcode(instr[0])
    else:
        return "Invalid opcode definition"

    if instr[1][:2] == "0x" and int(instr[1][2:], 16) <= 67108863:
        addr = binary_repr(int(instr[1], 16), width=19)
    else:
        try:
            instr[1] = int(instr[1])
            if instr[1] <= 33554431 and instr[1] >= -33554432:
                addr = binary_repr(instr[1], width=19)
            else:
                return "Value is out of reach"
        except ValueError:
            if mode == "2":
                return "In interactive mode enter hex or decimal"
            elif mode == "1":
                if instr[1].strip() in labelDict.keys():
                    #EVALUATE THIS
                    addr = binary_repr(labelDict[instr[1].strip()] + 4, width=32)[13:32]
                    print("address jum:" + addr)
                else:
                    return "Jump location not defined in line:" + counter

    return constructHex("11111" + addr + opcode, mode)


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
    # Additional function for Lw Sw dependencies
    instr = memoryTypeFix(instr, counter)

    if instrFormat("Itype", instr):
        return "Invalid I type instruction usage in Line: " + str(counter)

    if binaryOpcode(instr[0]) != "Error":
        opcode = binaryOpcode(instr[0])
    else:
        return "Invalid opcode definition in Line: " + str(counter)

    if binaryRegisters(instr[1]) != "Error":
        rd = binaryRegisters(instr[1])
    else:
        if ItypeSelect(instr[0]) == 1:
            return "Invalid ra register definition in Line: " + str(counter)
        else:
            return "Invalid rd register definition in Line: " + str(counter)

    print(instr[2])
    if binaryRegisters(instr[2].lstrip()) != "Error":
        ra = binaryRegisters(instr[2].lstrip())
    else:
        if ItypeSelect(instr[0]) == 1:
            return "Invalid rd register definition in Line: " + str(counter)
        else:
            return "Invalid ra register definition in Line: " + str(counter)

    # Checks if branch address is written as hex decimal or a label
    if(instr[0] != "ssld"):
        try:
            instr[3] = instr[3].strip()
            print("demo " + instr[3])
            print(labelDict)
            if instr[3][:2] == "0x" and int(instr[3][2:], 16) <= 65534:
                addr = binary_repr(int(instr[3], 16), width=14)
                print("address branch:" + addr)
            else:
                try:
                    instr[3] = int(instr[3])
                    if instr[3] <= 32767 and instr[3] >= -32768:
                        addr = binary_repr(instr[3], width=14)
                    else:
                        return "Out of reach"
                except:
                    if mode == "2":
                        return "In interactive mode enter hex or decimal"
                    elif mode == "1":
                        print("yes: " + instr[3].strip())
                        #print("guys: " + labelDict['lbl1'])
                        if instr[3].strip() in labelDict.keys():
                            print("its in")
                            instrLocation = counter * 4
                            branchAddr = int(labelDict[instr[3].strip()])
                            branchDistance = branchAddr - instrLocation
                            addr = binary_repr(int(branchAddr+4), width=32)[18:32]
                            #addr = binary_repr(int(branchDistance), width=32)[14:30]
                      #      print("instr loc: " + instrLocation)
                      #      print("branch addr: " + branchAddr)
                      #      print("address branchh:" + addr)
                            print(addr)
                            return constructHex(rd + ra + addr + opcode, mode)
                        else:
                            return "Branch location not defined in line:" + str(counter)
        except ValueError:
            return "I type format is instr reg, reg, addr in line:" + str(counter)
    else:
        addr = "00000000000000"

    return constructHex(rd + ra + addr + opcode, mode)
    #if ItypeSelect(instr[0]) == 1:  # branch instructions
    #    return constructHex(opcode + rt + rs + addr, mode)
    #elif ItypeSelect(instr[0]) == 3 or ItypeSelect(instr[0]) == 2:
    #    return constructHex(opcode + rs + rt + addr, mode)
    #else:
    #    return "There were an internal Error!"

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
        print(splittedInstruction[0])
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
                    results.writelines(str(builder(x, mode, counter)) + "\n")
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
                    print("AAAError occured program terminated")
        else:
            print("Invalid  mode number!!\n", "Try 1 or 2")
