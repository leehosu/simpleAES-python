import sys

import binascii
from uu import encode

import detectEnglish

# S-Box
sBox = [0x9, 0x4, 0xa, 0xb, 0xd, 0x1, 0x8, 0x5,
        0x6, 0x2, 0x0, 0x3, 0xc, 0xe, 0xf, 0x7]

# Inverse S-Box
sBoxI = [0xa, 0x5, 0x9, 0xb, 0x1, 0x7, 0x8, 0xf,
         0x6, 0x0, 0x2, 0x3, 0xc, 0x4, 0xd, 0xe]

# Round keys
w = [None] * 6

# function which multiplies in GF(2^4)
def mult(p1, p2):
    p = 0
    while p2:
        if p2 & 0b1:
            p ^= p1
        p1 <<= 1
        if p1 & 0b10000:
            p1 ^= 0b11
        p2 >>= 1
    return p & 0b1111


# function used to convert an 8 bit integer into a 4 element vector
def convertVector(n):
    return [n >> 12, (n >> 4) & 0xf, (n >> 8) & 0xf, n & 0xf]


# fuction used to convert a 4 element vector into 8 bit integers
def convertInteger(x):
    return (x[0] << 12) + (x[1] << 4) + (x[2] << 8) + x[3]


# function used to add two keys in GF(2^4) (s-AES)
def addKey(s1, s2):
    return [i ^ j for i, j in zip(s1, s2)]


# simple substitution function
def substitution(sbox, s):
    return [sbox[e] for e in s]


# simple function to shift the current row
def shift(s):
    return [s[0], s[1], s[3], s[2]]


# this function expands the key into subkeys, then creates the other keys
def keyExpansion(key):
    # generates the key rounds
    def sub2Nib(B):# swaps and then subsitutes the key using the above s-box
        return sBox[B >> 4] + (sBox[B & 0x0f] << 4)

    Rcon1, Rcon2 = 0b10000000, 0b00110000
    w[0] = (key & 0xff00) >> 8
    w[1] = key & 0x00ff
    w[2] = w[0] ^ Rcon1 ^ sub2Nib(w[1])
    w[3] = w[2] ^ w[1]
    w[4] = w[2] ^ Rcon2 ^ sub2Nib(w[3])
    w[5] = w[4] ^ w[3]

# The main decryption function, used to decrypt input ciphertext
def decrypt(ctext):
    # function used to mix the columns of the two matrixs by [9, 2, 2, 9]

    def inverseMixColumns(s):
        return [mult(9, s[0]) ^ mult(2, s[2]), mult(9, s[1]) ^ mult(2, s[3]),
                mult(9, s[2]) ^ mult(2, s[0]), mult(9, s[3]) ^ mult(2, s[1])]

    state = convertVector(((w[4] << 8) + w[5]) ^ ctext)
    state = substitution(sBoxI, shift(state))
    state = inverseMixColumns(addKey(convertVector((w[2] << 8) + w[3]), state))
    state = substitution(sBoxI, shift(state))
    return convertInteger(addKey(convertVector((w[0] << 8) + w[1]), state))

def bits16ToString(st):
    output = []
    for x in st:
        if len(x) > 8:
            output.append(chr(int(x[0:len(x)-8], 2)))
            output.append(chr(int(x[len(x)-8:], 2)))
        else:
            output.append(chr(int(x, 2)))
    return ''.join(output)

def bitsTo16bits(encryptedList):
    for x in range(len(encryptedList)):
        if(len(encryptedList[x]) < 16):
            encryptedList[x] = encryptedList[x].zfill(16)
    return encryptedList

# main function
if __name__ == '__main__':
    print('This program encrypts your 16-bit binar y plaintext and key using')
    print('s-AES (simplified advanced encryption standard)')
    print()

    # used to convert to binary
    getBin = lambda x: x >= 0 and str(bin(x))[2:] or "-" + str(bin(x))[3:]

    encryptedList = ['1001001100011001', '1010111100101110', '1110100101000010', '1011111100110011', '1010001100011110', '1101000100101111', '1010101010000110', '101110010010001', '11100101000001', '11110101110001', '1001111010001', '1100010111001001', '1011110010010000', '1000000100100111', '101110010011110', '111011010101010', '100011111100101', '1000101111011010', '1101111100111111', '1111100100011000', '111101101111110', '1011111010010011', '1100001111010101', '1001010010110010', '1100100110111001']
    decryptedList = []

    encryptedList16Bits = bitsTo16bits(encryptedList)

    for cipher in encryptedList16Bits:
        ciphertext = cipher
        key = 0b0100100001001001
        keyExpansion(key)
        plaintext = decrypt(int(ciphertext, 2))
        decryptedList.append(getBin(plaintext))

    print("Key:" + getBin(key))
    print()

    print("Encrypted to 16 bit :")
    print(encryptedList16Bits)

    print("Decrypted :")
    print(decryptedList)
    print("Decrypted Plaintext :", bits16ToString(decryptedList))
    print()

    yes = {'yes', 'y', 'ye', ''}
    no = {'no', 'n'}

    choice = input("S-AES로 해독 하시겠습니까? ").lower()
    if choice in yes:
        for key in range(0b01000000000000000, 0b10000000000000000):
            decryptedList = []
            decryptedPlaintext = []
            print("Key:" + getBin(key))
            for cipher in encryptedList16Bits:
                ciphertext = cipher
                keyExpansion(key)
                plaintext = decrypt(int(cipher, 2))
                decryptedList.append(getBin(plaintext))

            decryptedPlaintext = bits16ToString(decryptedList)
            print(decryptedPlaintext)

            if(detectEnglish.isEnglish(decryptedPlaintext)):
                print("Found Key!")
                print("Key : ", bin(key), "Decrypted Message : ", decryptedPlaintext)
                break
    elif choice in no:
        print("See you")
    else:
        sys.stdout.write("Please respond with 'yes' or 'no' ")