import struct

def main():
    with open('SAVED.GAM', 'r+b') as save:
        print('Editing Ultima 5 Save File...\n')
        str = int(input('Enter the desired amount of STR: '))
        int_ = int(input('Enter the desired amount of INT: '))
        dex = int(input('Enter the desired amount of DEX: '))
        hp = int(input('Enter the desired amount of HP: '))
        hm = int(input('Enter the desired amount of HM (Max HP): '))
        exp = int(input('Enter the desired amount of EXP: '))
        gold = int(input('Enter the desired amount of GOLD: '))
        key = int(input('Enter the desired amount of keys: '))
        skullkey = int(input('Enter the desired amount of skull keys: '))
        blackbadge = int(input('Enter the desired amount of black badges: '))
        magiccarpet = int(input('Enter the desired amount of magic carpets: '))
        magicaxe = int(input('Enter the desired amount of magic axes: '))
        offset = 2
        for _ in range(16):
            save.seek(offset + 12) # 14
            save.write(struct.pack('B', str))
            save.seek(offset + 13) # 15
            save.write(struct.pack('B', dex))
            save.seek(offset + 14) # 16
            save.write(struct.pack('B', int_))
            save.seek(offset + 16) # 18
            save.write(struct.pack('H', hp))
            save.seek(offset + 18) # 20
            save.write(struct.pack('H', hm))
            save.seek(offset + 20) # 22
            save.write(struct.pack('H', exp))
            offset += 32
        save.seek(516)
        save.write(struct.pack('H', gold))
        save.seek(518)
        save.write(struct.pack('B', key))
        save.seek(523)
        save.write(struct.pack('B', skullkey))
        save.seek(536)
        save.write(struct.pack('B', blackbadge))
        save.seek(522)
        save.write(struct.pack('B', magiccarpet))
        save.seek(576)
        save.write(struct.pack('B', magicaxe))
        save.seek(693)
        save.write(struct.pack('B', 6)) # Make it so all 6 party members appear.
if __name__ == "__main__":
    main()