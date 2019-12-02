#v1.0.0:
#   Át kell írni, hogy mindig csak az adott USER_DATA{:03} -at unpackelje,
#   így elkerülve, hogy hozzányúljon a többi save filehoz
#   MÓDOSÍTANI:
#       save_slot_iv -- levenni a '*11'-et a végéről
#       megnézni, hogy létezik-e a fájl
#       sorban: 
#           copy, megnyitja, select a save file, -1, unpackeli azt a for ciklus helyett, sima függvény
#        TESZT


import enum
import collections
import struct
import bs4
import os
import requests

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from shutil import copyfile

MAX_ENTRIES  = 17
BASE_SLOT_OFFSET = 0x02c0
SAVE_FILE_SIZE = 0x4204d0
SAVE_SLOT_SIZE = 0x060030

KEY = b"\x01\x23\x45\x67\x89\xab\xcd\xef\xfe\xdc\xba\x98\x76\x54\x32\x10"

BACKEND = default_backend()

#save_slot_iv = [b'0']

class data_entry_type(enum.Enum):
    integer = enum.auto()
    string = enum.auto()
data_entry = collections.namedtuple("data_entry", "name offset length id type")

all_entries = [
    data_entry("hp_current", 0x74, 4, 0, data_entry_type.integer),
    data_entry("hp", 0x78, 4, 1, data_entry_type.integer),
    data_entry("hp_2", 0x7c, 4, 2, data_entry_type.integer),
    data_entry("stamina", 0x90, 4, 3, data_entry_type.integer),
    data_entry("stamina_2", 0x94, 4, 4, data_entry_type.integer),
    data_entry("stamina_3", 0x98, 4, 5, data_entry_type.integer),
    data_entry("vitality", 0xa0, 4, 6, data_entry_type.integer),
    data_entry("attunement", 0xa8, 4, 7, data_entry_type.integer),
    data_entry("endurance", 0xb0, 4, 8, data_entry_type.integer),
    data_entry("strength", 0xb8, 4, 9, data_entry_type.integer),
    data_entry("dexterity", 0xc0, 4, 10, data_entry_type.integer),
    data_entry("intelligence", 0xc8, 4, 11, data_entry_type.integer),
    data_entry("faith", 0xd0, 4, 12, data_entry_type.integer),
    data_entry("humanity", 0xe0, 4, 13, data_entry_type.integer),
    data_entry("resistance", 0xe8, 4, 14, data_entry_type.integer),
    data_entry("level", 0xf0, 4, 15, data_entry_type.integer),
    data_entry("souls", 0xf4, 4, 16, data_entry_type.integer),
    data_entry("earned", 0xf8, 4, 17, data_entry_type.integer),
    #data_entry("player_name",)
]

def readint(prompt):
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            pass

def print_all_entries(selected_save_file):
    with open("USER_DATA{:03}".format(selected_save_file), "rb") as file:
        for i in range(MAX_ENTRIES):
            file.seek(all_entries[i].offset)
            value = file.read(all_entries[i].length)
            print(all_entries[i].name, ":", struct.unpack("<i", value), "[ID:", all_entries[i].id, "]")



def main():
    filename = "DRAKS0005.sl2"

    #if os.path.isfile('./DRAKS0005.sl2') == False:
       #print(filename, "does not exist! Please copy the file from Users\YOUR_USERNAME\Documents\NBGI\DARK SOULS:REMASTERED\STEAM_ID" );

    #print("Unpacking save file...", filename)

    copyfile("DRAKS0005.sl2", "backup/DRAKS0005.sl2")

    with open(filename, "rb") as file:
        content = file.read()

    selected_save_slot = readint("Please select a save slot: ")
    selected_save_slot = selected_save_slot -1



    #for i in range(11): # ------ Helyette csak az adott save_filet unpackelje, előbb bekérjük a kívánt save_file-t

    slot_data = content[BASE_SLOT_OFFSET + selected_save_slot * SAVE_SLOT_SIZE : BASE_SLOT_OFFSET + ( selected_save_slot + 1 ) * SAVE_SLOT_SIZE]
    IV = slot_data[:16]
    #save_slot_iv[0] = IV
    cipher = Cipher(algorithms.AES(KEY), modes.CBC(IV), backend = BACKEND)
    decryptor = cipher.decryptor()
    user_filename = "USER_DATA{:03}".format(selected_save_slot)
    with open(user_filename, "wb") as file:
        file.write(decryptor.update(slot_data[16:]) + decryptor.finalize())

    #selected_save_slot = readint("Please select a save slot: ")
    #selected_save_slot = selected_save_slot - 1

    print_all_entries(selected_save_slot)
    
    with open("USER_DATA{:03}".format(selected_save_slot), "r+b") as file: #---------- ezt is módosítani!!!
        while True:
            selected_id = readint("Please select an ID to change its value: ")
            if (selected_id >= 0 and selected_id <= MAX_ENTRIES):
                print("Please write the new value of:", all_entries[selected_id].name)
                new_value = readint("New value: ")

                file.seek(all_entries[selected_id].offset)
                file.write(struct.pack("<i", new_value))

                print("Value of", all_entries[selected_id].name, "is overwritten!")
                print("If you want to finish editing, write '-1'")
            elif selected_id == -1:
                break
            else:
                print("Wrong ID! Please enter another one!")

    #for i in range(11): # ---------- Ezt is, hogy csak a "selcted_save_file"-t packelje, a MEGFELELŐ helyre!!!
    with open("USER_DATA{:03}".format(selected_save_slot), "rb") as file:
        current_content = file.read()
        #encryptor_IV = save_slot_iv[0]
        encrypt_cipher = Cipher(algorithms.AES(KEY),modes.CBC(IV), backend = BACKEND)
        encryptor = cipher.encryptor()
        with open(filename, "r+b") as save_file:
            seek_to = BASE_SLOT_OFFSET +  selected_save_slot * SAVE_SLOT_SIZE + 16
            save_file.seek(seek_to)
            save_file.write(encryptor.update(current_content) + encryptor.finalize())

    #for i in range(11):
    os.remove("USER_DATA{:03}".format(selected_save_slot)) #-------- Ezt is, hogy csak az egyetlen USER_DATA{:03} fájlt törölje
if __name__ == "__main__":
    main()