import streamlit as st      #for making the web-app (GUI)
import os                   #for getting the path of the output file
from pyparsing import * #for parsing the input file. It contains all the Suppress functions used later on.
from pyparsing import Word, alphas, nums, oneOf, Optional, Combine      #for interpretation of instructions of the input file as strings
from bitstring import BitArray     #for decimal to binary conversion of negative integers

page_bg_img = '''
<style>
body {
background-image: url("https://media.istockphoto.com/vectors/abstract-background-of-connecting-lines-and-dots-vector-id1030847248?k=20&m=1030847248&s=612x612&w=0&h=JHB_AmFXFHBblm9n_EgL9eq2CjERggrnyxSv2H29n7A=");
background-size: cover;
}
</style>
'''

st.markdown(page_bg_img, unsafe_allow_html=True)

st.header("ES215 End Semester Project")
st.subheader("MIPS-32 Assembler-Disassembler")
input_msg = "Please enter the path of the input file containing the assembly code in .txt format."
in_box = st.text_input(input_msg, "")
in_box_addr = st.text_input("Enter the initial address in hexadecimal", "")

#Defining the assembly instructions accepted by our assembler
#The data card containing all the valid instructions has been mentioned in the project report
instructions = {}  #we will store the instructions in a python dictionary
#format of the instructions : type = (R/I/J), opcode, reg operands, immediate value, shamt, funct code
#num_operands is a number/integer assigned to each of the possible format of the regs used by MIPS 32 architecture

#num_operands = 0: reg used in I-type instruction - rt, imm(rs)
#num_operands = 1: rs, rt, imm
#num_operands = 2: rs
#num_operands = 3: three reg are used - (rs, rt, rd)
#num_operands = 4 : reg used in I-type iinstruction - rt, imm
#num_operands = 5 :  rs, rt, address

#defining the valid operations :
instructions['add']  = {'format': 'R', 'opcode': '0', 'num_operands': 3, 'shamt': 0,  'funct': '20'}
instructions['sub']  = {'format': 'R', 'opcode': '0', 'num_operands': 3, 'shamt': 0, 'funct': '22'}
instructions['addi'] = {'format': 'I', 'opcode': '8', 'num_operands': 1}
instructions['lw']   = {'format': 'I', 'opcode': '23', 'num_operands': 0}
instructions['sw']   = {'format': 'I', 'opcode': '2b', 'num_operands': 0}
instructions['lh']   = {'format': 'I', 'opcode': '21', 'num_operands': 0}
instructions['lhu']  = {'format': 'I', 'opcode': '25', 'num_operands': 0}
instructions['sh']  =  {'format': 'I', 'opcode': '29', 'num_operands': 0}
instructions['lb']  =  {'format': 'I', 'opcode': '20', 'num_operands': 0}
instructions['lbu']  =  {'format': 'I', 'opcode': '24', 'num_operands': 0}
instructions['sb']  =  {'format': 'I', 'opcode': '28', 'num_operands': 0}
instructions['ll']  = {'format': 'I', 'opcode': '30', 'num_operands': 1}
instructions['sc']  =  {'format': 'I', 'opcode': '38', 'num_operands': 0}
instructions['lui'] =   {'format': 'I', 'opcode': 'f', 'num_operands': 4}
instructions['and']   =   {'format': 'R', 'opcode': '0', 'num_operands': 3, 'funct': '24'}
instructions['or']   =   {'format': 'R', 'opcode': '0', 'num_operands': 3, 'funct': '25'}
instructions['nor']   =   {'format': 'R', 'opcode': '0', 'num_operands': 3, 'funct': '27'}
instructions['andi']  =   {'format': 'I', 'opcode': 'c', 'num_operands': 1}
instructions['ori']  =   {'format': 'I', 'opcode': 'd', 'num_operands': 1}
instructions['sll']   =   {'format': 'R', 'opcode': '0', 'num_operands': 1, 'funct': '00'}
instructions['srl']   =   {'format': 'R', 'opcode': '0', 'num_operands': 1, 'funct': '02'}
instructions['beq']   =   {'format': 'I', 'opcode': '4', 'num_operands': 5 }
instructions['bne']   =   {'format': 'I', 'opcode': '5', 'num_operands': 5 }
instructions['slt']   =   {'format': 'R', 'opcode': '0', 'num_operands': 3, 'funct': '2a'}
instructions['sltu']   =   {'format': 'R', 'opcode': '0', 'num_operands': 3, 'funct': '2b'}
instructions['slti']  =   {'format': 'I', 'opcode': 'a', 'num_operands': 1}
instructions['sltiu'] = {'format': 'I', 'opcode': 'b', 'num_operands': 1}
instructions['j']     =   {'format': 'J', 'opcode': '2'}
instructions['jal']   =   {'format': 'J', 'opcode': '3'}
instructions['jr']    =   {'format': 'R', 'opcode': '0', 'num_operands': 2, 'funct': '08'}

all_instructions = list(instructions.keys())  #making a list of the mnemonic codes of all the instructions in the data card

#organizing instructions of distinct types in distinct lists :

R1 = []    #R-type, num_operands = 1
R2 = []    #R-type, num_operands = 2
R3 = []    #R-type, num_operands = 3
I0 = []    #I-type, num_operands = 0
I1 = []    #I-type, num_operands = 1
I4 = []    #I-type, num_operands = 4
I5 = []    #I-type, num_operands = 5
J = []     #J-type

for ins in all_instructions:    #ins = mnemonic of the instruction
    current_ins = instructions[ins]  #all the info about the instruction stored in the 'instructions' dict
    if current_ins['format'] == 'R':
        if current_ins['num_operands'] == 1:
            R1.append(ins)
        if current_ins['num_operands'] == 2:
            R2.append(ins)
        if current_ins['num_operands'] == 3:
            R3.append(ins)

    if current_ins['format'] == 'I':
        if current_ins['num_operands'] == 0:
            I0.append(ins)
        if current_ins['num_operands'] == 1:
            I1.append(ins)
        if current_ins['num_operands'] == 4:
            I4.append(ins)
        if current_ins['num_operands'] == 5:
            I5.append(ins)

    if current_ins['format'] == 'J':
        J.append(ins)

#dictionary specifying the number of each of 32 registers in MIPS architecture
#This has also been done according to the data card provided by the professor in the lecture slides. (data card is also in the report)
regs = {}
regs['$zero'] = 0
regs['$at'] = 1
regs['$v0'] = 2
regs['$v1'] = 3
for i in range(4, 8):        # for $a0-$a3 registers
    regs['$a%d' %(i-4)] = i
for i in range(8, 16):       # for $t0-$t7 registers
    regs['$t%d' %(i-8)] = i
for i in range(16, 24):      # for $s0-$s7 registers
    regs['$s%d' %(i-16)] = i
for i in range(24, 26):      # for $t8-$t9 registers
    regs['$t%d' %(i-16)] = i
for i in range(26, 28):      # for $k0-$k1 registers
    regs['$k%d' %(i-26)] = i
regs['$gp']=28
regs['$sp']=29
regs['$fp']=30
regs['$ra']=31
#creating the registers holding immediate values
for i in range(0,31):
    regs['$%d'%i]=i


all_regs = list(regs.keys())

#rules for parsing the input file
#for each input line we know the input is of the type :
line_format = Combine(Optional(Word(alphas)) + Optional(Word(nums)))    #this will be used for translating the load, store and branch instructions.
label_format_j = Word(alphas)
imm_format_j = Word(nums)
remove_comma = Suppress(',')  #we are ignoring the commas in the instructions of the assembly code
identify_reg = oneOf(all_regs)    #identify_reg will contain the valid regs mentioned in the input file
num = Combine(Optional('-') + Word(nums))    #for parsing the "-x" string as negative integer -x. If the number is positive then also it will be stored as num var because '-' is optional.
label_add = label_format_j.setResultsName('label_add')
imm_add = imm_format_j.setResultsName('imm_add')
address_for_branch = line_format.setResultsName("address_for_branch") + Suppress(":")     #if the branch of a loop is in the form of a label, eg. For: (assembly code)
rs = identify_reg.setResultsName('rs')    #from now any valid input reg from the all_regs array will be denoted as rs
rt = identify_reg.setResultsName('rt')    #from now any valid input reg from the all_regs array will be denoted as rs
rd = identify_reg.setResultsName('rd')    #from now any valid input reg from the all_regs array will be denoted as rs
imm = num.setResultsName('imm')           #any input string containg numbers will be taken as imm
addr = line_format.setResultsName("address")     #any input string parsed according to the line_format will be denoted as address

R_format =  (oneOf(R1).setResultsName('instruction') + White() + rd + remove_comma + rt + remove_comma + num.setResultsName('shamt')) ^\
            (oneOf(R2).setResultsName('instruction') + White() + rs)^\
            (oneOf(R3).setResultsName('instruction') + White() + rd + remove_comma + rs + remove_comma + rt)
                #This contains the possible instruction formats of R-type instructions. Any input valid ins of the above options will be denoted as R_format

I_format = (oneOf(I0).setResultsName('instruction') + White() + rt + remove_comma + imm+  Suppress('(') + rs + Suppress(')')) ^\
            (oneOf(I1).setResultsName('instruction') + White() + rt + remove_comma + rs + remove_comma + imm) ^\
           (oneOf(I4).setResultsName('instruction') + White() + rt + remove_comma + imm) ^\
           (oneOf(I5).setResultsName('instruction') + White() + rs + remove_comma + rt + remove_comma + addr)
#This contains the possible instruction formats of I-type instructions. Any input valid ins of the above options will be denoted as I_format

J_format = (oneOf(J).setResultsName('instruction') + White() + imm_add ) ^\
           (oneOf(J).setResultsName('instruction') + White() + label_add)
# This contains the possible instruction formats of J-type instructions. Any input valid ins of the above options will be denoted as J_format
line_end = OneOrMore(LineEnd())

instruction =   ((address_for_branch) + (R_format ^ I_format ^ J_format)) ^\
                (address_for_branch) ^ (R_format ^ I_format ^ J_format) ^ line_end.setResultsName('line_end')
            #Possible format of any input line in the assembly code


input_code = open(in_box, 'r')
Pointer_for_labels_of_loops = {}       #eg. For: bne reg, reg, end  => Pointer_for_labels_of_loops[For] = line address of this instruction
Mem = []                                #contains all the instructions of the input file
addr_line = int(in_box_addr, 16)        #the initial line address in decimal

for line in input_code:
    inst = instruction.parseString(line)    #Parsing each input line(a string)  according to the instruction format defined above
    if len(inst)==0:
        continue
    if inst[0] == '\n':
        continue
    Mem.append(inst)                #if the line is not empty, append the instruction to memory
    if inst.address_for_branch != '':      #if there is some initial label of the instruction (eg For: ...)
        if inst.instruction != '':
            Pointer_for_labels_of_loops [inst.address_for_branch] = addr_line         # adding the address_for_branch in Pointer_for_labels_of_loops
        else:
            Pointer_for_labels_of_loops [inst.address_for_branch] = addr_line
            continue
    addr_line += 4              #as address of instructions in memory differ by 4

def hex_to_bin(hex_str, num_bits):                       # for converting hexadecimal numbers to binary
    return bin(int(hex_str, 16))[2:].zfill(num_bits)    #returns as a string

def dec_to_bin(dec, num_bits):                           # for converting decimal numbers to binary
    if int(dec) < 0:
        dec = int(dec)
        b = BitArray(int=dec, length=num_bits)
        ans = ''
        for i in b[2:]:
            x = ''
            if int(i) == 0:
                x = '0'
            else:
                x = '1'

            ans = ans + x
        return ans
    else:
        return bin(int(dec))[2:].zfill(num_bits)       #returns as a string

#creating the output file
output_file = open('output_file.txt','w') #opening the output file
inp_dis_file = open('inp_dis_file.txt', 'w')
out_p = []
output_file.write("PC" + "-" + "Instruction in machine code" + '\n' + '\n')
#t = st.text_area("The output of assembler", height= 350)
PC= int(in_box_addr, 16) - 4              # initializing PC
#The translation starts from here
for inst in Mem:            #iterating through instructions in memory
    if inst.instruction == '':
        continue
    curri = instructions[inst.instruction]      #holds all the info of the instruction as provided in the instructions dict
    PC+= 4                          #incrementing PC by 4

    if curri['format'] == 'R':                  #if the instruction type is R
        opcode = curri['opcode']
        funct = curri['funct']
        if inst.shamt != '':
            shamt = inst.shamt
            rs_code = 0
        else:
            shamt = 0
            rs_code = regs[inst.rs]
                     #number of the register in decimal format
        rt_code = regs[inst.rt]
        rd_code = regs[inst.rd]
        inst_mc = hex_to_bin(opcode, 6) + dec_to_bin(rs_code, 5) + dec_to_bin(rt_code, 5) + dec_to_bin(rd_code, 5) + dec_to_bin(shamt, 5) + hex_to_bin(funct, 6)

        out = hex(int(inst_mc, 2))          #converting the 32-bit binary instruction into hexadecimal
        output_file.write(str(PC) + "-" + out + '\n')
        inp_dis_file.write(out + '\n')
        print( out)
        out_p.append(out)

    if curri['format'] == 'I':    #if the instruction type is I
        opcode = curri['opcode']
        rs_code = regs[inst.rs]         #register number in decimal
        rt_code = regs[inst.rt]
        if inst.imm != '':          #if an immediate value like 1/2/-2 etc. is given
            imm = inst.imm
        else:
            address = Pointer_for_labels_of_loops [inst.address]        #if the label of an another instruction is given, eg., bne rs, tr, end
            imm = (address - PC) / 4
        inst_mc = hex_to_bin(opcode, 6) + dec_to_bin(rs_code, 5) + dec_to_bin(rt_code, 5) + dec_to_bin(imm, 16)

        out = hex(int(inst_mc, 2))
        output_file.write(str(PC) + "-"+ out + '\n')
        inp_dis_file.write(out + '\n')
        print(out)
        out_p.append(out)

    if curri['format']  == 'J':
        opcode = curri['opcode']
        if inst.imm_add != '':      #if the address is given in decimal form of how many lines to jump
            imm_var = inst.imm_add
            address =  dec_to_bin(imm_var, 32)
        else:
            address = Pointer_for_labels_of_loops [inst.label_add]      #if the label of another instruction is given, eg., j end
            address = dec_to_bin(address, 32)
        address = address[4:]
        address = int(address, 2)/4
        inst_mc = hex_to_bin(opcode, 6) + dec_to_bin(address, 26)

        out = hex(int(inst_mc, 2))
        output_file.write(str(PC) + "-" + out + '\n')
        inp_dis_file.write(out + '\n')
        print(out)
        out_p.append(out)

output_file.close()
inp_dis_file.close()
file = 'output_file.txt'
path = os.path.abspath(file)
st.subheader("This is the output of the assembler")
try:
    with open(path) as print_file:
        st.text(print_file.read())
except FileNotFoundError:
    st.error('File not found.')

         ###########################  Disassembler ############################

proceed = st.radio("Do you wish to convert the output machine code to the Assembly code using our disassembler?", ("Yes", "No, thanks"))


# Converting Bin to Dec
def bin_to_dec(bin_str, num_bits):
    sign = bin_str[0]
    if sign == '0':
        return int(bin_str, 2)
    elif sign == '1':
        comp = int(bin_str[1:], 2)
        dec = (2 ** (num_bits - 1)) - comp
        return -1 * dec


# Creating Dictionary for opcode and defining R I J types.
opcode = {}
opcode['0'] = {'format': 'R'}
opcode['8'] = {'format': 'I', 'instructions': 'addi', 'num_operands': 1}
opcode['23'] = {'format': 'I', 'instructions': 'lw', 'num_operands': 0}
opcode['2b'] = {'format': 'I', 'instructions': 'sw', 'num_operands': 0}
opcode['21'] = {'format': 'I', 'instructions': 'lh', 'num_operands': 0}
opcode['25'] = {'format': 'I', 'instructions': 'lhu', 'num_operands': 0}
opcode['29'] = {'format': 'I', 'instructions': 'sh', 'num_operands': 0}
opcode['20'] = {'format': 'I', 'instructions': 'lb', 'num_operands': 0}
opcode['24'] = {'format': 'I', 'instructions': 'lbu', 'num_operands': 0}
opcode['28'] = {'format': 'I', 'instructions': 'sb', 'num_operands': 0}
opcode['30'] = {'format': 'I', 'instructions': 'll', 'num_operands': 1}
opcode['38'] = {'format': 'I', 'instructions': 'sc', 'num_operands': 0}
opcode['f'] = {'format': 'I', 'instructions': 'lui', 'num_operands': 4}
opcode['c'] = {'format': 'I', 'instructions': 'andi', 'num_operands': 1}
opcode['d'] = {'format': 'I', 'instructions': 'or', 'num_operands': 1}
opcode['4'] = {'format': 'I', 'instructions': 'beq', 'num_operands': 5}
opcode['5'] = {'format': 'I', 'instructions': 'bne', 'num_operands': 5}
opcode['2'] = {'format': 'J', 'instructions': 'j'}
opcode['3'] = {'format': 'J', 'instructions': 'jal'}
opcode['a'] = {'format': 'I', 'instructions': 'slti', 'num_operands': 1}
opcode['b'] = {'format': 'I', 'instructions': 'sltiu', 'num_operands': 1}

# Creating dictionary for 32 reigster in MIPS architecture
# This has been done according to the data card provided by the professor in the lecture slides.
# Data card is attached in the report
reg_file = {}
reg_file[0] = '$zero'
reg_file[1] = '$at'
reg_file[2] = '$v0'
reg_file[3] = '$v1'
reg_file[4] = '$a0'
reg_file[5] = '$a1'
reg_file[6] = '$a2'
reg_file[7] = '$a3'
reg_file[8] = '$t0'
reg_file[9] = '$t1'
reg_file[10] = '$t2'
reg_file[11] = '$t3'
reg_file[12] = '$t4'
reg_file[13] = '$t5'
reg_file[14] = '$t6'
reg_file[15] = '$t7'
reg_file[16] = '$s0'
reg_file[17] = '$s1'
reg_file[18] = '$s2'
reg_file[19] = '$s3'
reg_file[20] = '$s4'
reg_file[21] = '$s5'
reg_file[22] = '$s6'
reg_file[23] = '$s7'
reg_file[24] = '$t8'
reg_file[25] = '$t9'
reg_file[26] = '$k0'
reg_file[27] = '$k1'
reg_file[28] = '$gp'
reg_file[29] = '$sp'
reg_file[30] = '$fp'
reg_file[31] = '$ra'

# Creatingdictionary for different functions in MIPS architecture
funct_code = {}
funct_code['20'] = {'instructions': 'add', 'num_operands': 3}
funct_code['22'] = {'instructions': 'sub', 'num_operands': 3}
funct_code['24'] = {'instructions': 'and', 'num_operands': 3}
funct_code['25'] = {'instructions': 'or', 'num_operands': 3}
funct_code['27'] = {'instructions': 'nor', 'num_operands': 3}
funct_code['00'] = {'instructions': 'sll', 'num_operands': 1}
funct_code['02'] = {'instructions': 'srl', 'num_operands': 1}
funct_code['2a'] = {'instructions': 'slt', 'num_operands': 3}
funct_code['2b'] = {'instructions': 'sltu', 'num_operands': 3}
funct_code['08'] = {'instructions': 'jr', 'num_operands': 2}


if proceed == "Yes":
    in_box_addr_2 =  in_box_addr
    machinecode_file = out_p  # Reading the input txt file
else:
    input_msg_2 = "If you wish to use the disassembler for some other file, please enter the path of the input file containing the machine code in .txt format."
    in_box_2 = st.text_input(input_msg_2, "")
    in_box_addr_2 = st.text_input("Enter the initial address of the instructions in hexadecimal", "")

initial_address = int(in_box_addr_2, 16)  # Storing the initial address in hexadecimal
PC = initial_address   # Initializing Program Counter
instruction_list = []  # creating list of instructions
addresses_list = []    # Creating a list of addresses
address_table = {}     # Hashtable containing addresses as keys and labels as values

for line in machinecode_file:
    line = line[2:]      # Removing '0x' from LSB
    line = hex_to_bin(line, 32)          # converting the hexadecimal machine code to binary
    opcode_hex = hex(int(line[0:6], 2))  # Converting opcode from binary to hex
    opcode1 = opcode_hex[2:]  # Removing '0x' from LSB
    if opcode1 == '1':
        continue
    data = opcode[opcode1]
    PC += 4

    if data['format'] == 'R':
        rs = reg_file[int(line[6:11], 2)]      # In the machine code bit 6-bit 11 represents the rs register. This rs register is added in the reg_file defined above
        rt = reg_file[int(line[11:16], 2)]     # In the machine code bit 11-bit 16 represents the rt register. This rs register is added in the reg_file defined above
        rd = reg_file[int(line[16:21], 2)]     # In the machine code bit 16-bit 21 represents the rd register. This rs register is added in the reg_file defined above
        shamt = int(line[21:26], 2)            # In the machine code bit 21-bit 26 represents the shift amount. It is assigned a variable 'shamt'
        funct = hex(int(line[26:32], 2))[2:].zfill(2)   # In the machine code bit 21-bit 32 represents the function. It is converted to hexa decimal and stored in 'funct'
        instructions = funct_code[funct]['instructions']   # the 'instruction' corresponding to the funct defined above is assigned a variable 'instructions'
        num_operands = funct_code[funct]['num_operands']   # the 'num_operands' corresponding to the funct defined above is assigned a variable 'num_operands'

        # forming the instruction line in MIPS according to the number of operands | The R type of instructions have num_operands only 1, 2, 3
        # inst is Instruction
        if (num_operands == 3):
            inst = [instructions + ' ' + rd + ', ' + rs + ', ' + rt, None]
        if (num_operands == 1):
            inst = [instructions + ' ' + rd + ', ' + rt + ', ' + str(shamt), None]
        if (num_operands == 2):
            inst = [instructions + ' ' + rs,
                    None]  # list containing instruction (finishied or not) and jumping or branching address if any

    if data['format'] == 'I':
        rs = reg_file[int(line[6:11], 2)]     # In the machine code bit 6-bit 11 represents the rs register. This rs register is added in the reg_file defined above
        rt = reg_file[int(line[11:16], 2)]    # In the machine code bit 11-bit 16 represents the rt register. This rs register is added in the reg_file defined above
        imm = str(bin_to_dec(line[16:], 16))  # In the machine code bits after bit 16 is the binary form of the immediate value, this line converts the binary form back to decimal form in string format
        instructions = data['instructions']   # the 'instruction' corresponding to the funct defined above is assigned a variable 'instructions'
        num_operands = data['num_operands']   # the 'num_operands' corresponding to the funct defined above is assigned a variable 'num_operands'

        # forming the instruction line in MIPS according to the number of operands | The R type of instructions have num_operands only 0, 1, 4, 5
        if (num_operands == 1):
            inst = [instructions + ' ' + rt + ', ' + rs + ', ' + imm, None]
        if (num_operands == 4):
            inst = [instructions + ' ' + rt + ', ' + imm, None]
        if (num_operands == 0):
            inst = [instructions + ' ' + rt + ', ' + imm + '(' + rs + ')', None]
        if (num_operands == 5):                            # when num_operands=5, the format is rs, rt, address in MIPS code, this if condition forms the MIPS code accordingly
            address = PC + int(imm) * 4
            if address not in addresses_list:
                addresses_list.append(address)
            inst = [instructions + ' ' + rs + ', ' + rt + ', ', address]

    if data['format'] == 'J':
        instructions = data['instructions']
        address = int(line[6:], 2) << 2  # shifts address by 2
        address = dec_to_bin(address, 28)  # convert it to binary form
        address = dec_to_bin(PC, 32)[0:4] + address  # concatenate 28 bits of address and the 4 MSBs of PC
        address = int(address, 2)
        if address not in addresses_list:
            addresses_list.append(address)
        inst = [instructions + ' ', address]

    instruction_list.append(inst)    # appending all the instructions in the instruction_list created above

addresses_list.sort()  # sorting list of addresses in ascending order

# formulating the address table
i = 1
for address in addresses_list:
    address_table[address] = 'L%d' % i    # creating labels for each address
    i += 1

assembly_file = open('assembly_file.txt', 'w')  # opening the output file for disassembler

line_num = 0
for inst in instruction_list:
    inst_address = initial_address + line_num
    if address_table.get(inst_address) != None:
        label = address_table.get(inst_address)   # a variable 'label' is assigned to the label corresponding to the inst_address in the address_table
    else:
        label = ''
    if inst[1] == None:                             # for instruction type R and I
        if label == '':
            print(inst[0])
            assembly_file.write(inst[0] + '\n')     # if there is no label, the MIPS code is printed directly
        else:
            print(label + ': ' + inst[0])           # if there is a label, the MIPS code is printed with name of the label first for example, for: ......
            assembly_file.write(label + ': ' + inst[0] + '\n')
    else:                                           # for instruction type J
        if label == '':
            print(inst[0] + address_table[inst[1]])
            assembly_file.write(inst[0] + address_table[inst[1]] + '\n')
        else:
            print(label + ': ' + inst[0] + address_table[inst[1]])
            assembly_file.write(label + ': ' + inst[0] + address_table[inst[1]] + '\n')
    line_num += 4

assembly_file.close()
file = 'assembly_file.txt'
path = os.path.abspath(file)
st.write("This is the output of the disassembler")
try:
    with open(path) as print_file:
        st.text(print_file.read())
except FileNotFoundError:
    st.error('File not found.')