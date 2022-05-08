import matplotlib.pyplot as plt
import numpy as np
from collections import Counter
from dahuffman import HuffmanCodec as hm



# Permet de construire l'alphabet d'un texte (var texte) et de plot la répartition
def alphabet(texte):
    f = open(texte, 'r').read()
    alphabet_dico = Counter(f)

    compteur = sum(alphabet_dico.values())
    for key, value in alphabet_dico.items():
        value /= compteur
        alphabet_dico[key] = value

    plt.bar(alphabet_dico.keys(), alphabet_dico.values(), color='b')
    plt.title("Fréquence d'apparation des lettres")
    plt.xlabel("Lettre du texte")
    plt.ylabel("Fréquence d'apparition")

    plt.ylim([0, 1])
    plt.yticks(np.arange(0, 1, 0.05))

    plt.show()
    return alphabet_dico


# Calcul de l'entropie d'un alphabet (var alphabet) et l'affiche
def calcul_entropie(alphabet):
    entropie = 0

    for value in alphabet.values():
        entropie -= value * np.log2(value)

    return round(entropie, 2)


def codec_huffman(texte):
    f = open(texte, 'r').read()
    codec = hm.from_data(f)
    dico_codec = hm.get_code_table(codec)
    return dico_codec


# Encode un texte par la méthode Huffman et affiche la table de codage ainsi que le texte encodé
def codage_huffman(texte):
    f = open(texte, 'r').read()
    codec = hm.from_data(f)
    hm.print_code_table(codec)  # Affiche la table de codage
    encoded = codec.encode(f)

    # decodage
    decoded = codec.decode(encoded)
    # print(decoded)

    return encoded


def bytes_to_bits(encoded):  # Convertis un array bytes (encodé) en bits
    x = np.fromstring(encoded, dtype=np.uint8)
    bits = np.array(np.unpackbits(x))

    return bits

def bytes_to_int(encoded):
    int_val = int.from_bytes(encoded, "big")
    return int_val

def bits_to_bytes(encoded):  # Convertis un array bytes (encodé) en bits
    x = np.fromstring(encoded, dtype=np.uint8)
    bits = np.array(np.packbits(x))

    return bits

def calcul_R(alphabet, dico_codec):
    moyenne = 0
    for carac in alphabet:
        for carac2 in dico_codec:
            if carac == carac2:
                tuple_dico = dico_codec[carac2]
                moyenne += tuple_dico[0] * alphabet[carac]


    return round(moyenne, 2)


def calcul_efficiency(entropie, R):
    efficiency = round(entropie / R * 100, 2)

    return round(efficiency, 2)


def reshape_bitsarray(k, tab_bits):

    remhk = tab_bits.size % k

    if remhk > 0:
        nrow = int(tab_bits.size / k + 1)
        bitsjam = k - remhk


    else:
        nrow = int(tab_bits.size // k)
        bitsjam = 0

    if bitsjam > 0:
        tab_bits = np.append(tab_bits, np.zeros(bitsjam).astype(int))
        #print(f"{bitsjam} jam bits added")


    k_words = np.reshape(tab_bits, (nrow, k))
    #print(k_words[0:5:1, ::])

    return k_words, bitsjam, nrow



alphabet = alphabet('The_Adventures_of_Sherlock_Holmes_A_Scandal_In_Bohemia.txt')
 entropie = calcul_entropie(alphabet)
encoded = codage_huffman('The_Adventures_of_Sherlock_Holmes_A_Scandal_In_Bohemia.txt')
tab_bits = bytes_to_bits(encoded)
dico_codec = codec_huffman('The_Adventures_of_Sherlock_Holmes_A_Scandal_In_Bohemia.txt')
R = calcul_R(alphabet, dico_codec)
efficiency = calcul_efficiency(entropie, R)
tab_bits_shaped, nb_bits, nrow = reshape_bitsarray(4, tab_bits)
tab_int = bytes_to_int(encoded)

print(f"Source codé/compressé : {encoded}")
print(f"L'entropie de la source est de {entropie}")
print(f"La moyenne de bits par symbole issue du codage Huffman est de {R}")
print(f"L'efficacité du codage huffman pour cette source est de {efficiency}%")
print(f"bytes encodés en bits : {tab_bits}")
print(f"Bits shaped : \n{tab_bits_shaped[0:5:1, ::]} \n {nb_bits} bits de bourrage ajouté(s)") 

 #np.ravel