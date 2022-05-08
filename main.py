import matplotlib.pyplot as plt
import numpy as np
from  collections import  Counter
from dahuffman import HuffmanCodec as hm
from bitstring import BitArray

# f = open('phrase.txt','r')
# phrase = f.read()
# print(phrase)
# f.close()

# car = [' ', ',', ':', ';', '.', "'", '-', '!', '?', '"', '*', '/', '(', ')', '0', '1', '2', '3', '4', '5', '6', '7',
#        '8', '9', '@', '$', '[', ']', '#', '&', '%']

car = []


def freq(texte):
    d, compteur = {}, 0
    for c in texte:
        if c not in d:
             d[c] = 1
             compteur += 1
        else:
            d[c] += 1
            compteur += 1

    return d, compteur


texte = ""

# with open('The_Adventures_of_Sherlock_Holmes_A_Scandal_In_Bohemia.txt', encoding='utf8') as phrase:
#     for ligne in phrase:
#         texte += ligne.replace('\n', '')

f = open('The_Adventures_of_Sherlock_Holmes_A_Scandal_In_Bohemia.txt', 'r')
texte = f.read()

d, compteur = freq(texte)

f.close()

L = sorted(d.items(), key=lambda colonne: colonne[1], reverse=True)
for i in L:
    print(f"{i[0]} : {i[1] / compteur}")

# print(type(L), compteur)

dico = dict(L)

print(dico, compteur)



for key, value in dico.items():
    value = value / compteur
    dico[key] = value

print(dico)

plt.bar(list(dico.keys()), dico.values(), color='b')
plt.title("Fréquence d'apparation des lettres")
plt.xlabel("Lettre du texte")
plt.ylabel("Fréquence d'apparition")

plt.ylim([0, 1])
plt.yticks(np.arange(0, 1, 0.025))

plt.show()


entropie = 0
for value in dico.values():
    entropie -= value * np.log2(value)

print(f"L'entropie de la source est de {entropie}")
#
# alphabet = Counter(texte)
# print(alphabet)

# objet = hm.from_data(texte)
# hm.print_code_table(objet)
# print(hm.get_code_table(objet))

f = open('The_Adventures_of_Sherlock_Holmes_A_Scandal_In_Bohemia.txt', 'r').read()
codec = hm.from_data(f)
hm.print_code_table(codec)
dico_codec = hm.get_code_table(codec)
print(dico_codec)
encoded = codec.encode(f)
print(encoded)
# codec.decode(encoded)

x = np.fromstring(encoded, dtype=np.uint8)
bits = np.array(np.unpackbits(x))
print(bits)
# total = 0
# count = 0
# for value in dico_codec.values():
#     total += value[0]
#     count += 1
#
# print(total / count)
moyenne = 0
for carac in dico:
    for carac2 in  dico_codec:
        if carac==carac2:
            tuple_dico = dico_codec[carac2]
            moyenne += tuple_dico[0] * dico[carac]

print(moyenne)

efficiency = entropie / moyenne
print(efficiency)

# if len(bits) % k == 0:
#     nblignes = int(len(bits) / k)
#     bitsreshaped = np.reshape(bits, (nblignes, k))
#     return bitsreshaped
#
# else:
#     nblignes = int(len(bits) / k) + 1
#     reste = len(bits) % k
#     for i in range(reste):
#         np.insert(bits, 0, 0)
#         np.reshape(bits, (nblignes, k))
#         return bits

# bitsreshaped = np.reshape(bits, (nblignes, k))
