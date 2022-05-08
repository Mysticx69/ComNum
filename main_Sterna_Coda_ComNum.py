
"""
Author: Antoine Sterna
        Robin Coda

Title: TP ComNum, mise en place d'une chaine de communication.
        
Subject: Codage/compression d'une source avec analyses statistiques. 
         Codage canal et code correcteur d'erreurs (CCE)  
         Simulation d'un canal binaire symétique (CBS) pour l'introduction des erreurs 

"""

# Librairies
import matplotlib.pyplot as plt
import numpy as np
from collections import Counter
from dahuffman import HuffmanCodec as hm
from pyparsing import col
from pyrsistent import b
import sk_dsp_comm.sigsys as ss
import scipy.signal as signal
import commpy.channelcoding as commpy
import scipy.special as special
import sk_dsp_comm.digitalcom as dc
import sk_dsp_comm.fec_block as block
from numpy import reshape, size
from termcolor import colored
from fractions import Fraction

# Some colors


class bcolors:
    GREEN = '\033[92m'  # GREEN
    YELLOW = '\033[93m'  # YELLOW
    RED = '\033[91m'  # RED
    RESET = '\033[0m'  # RESET COLOR


"#1. Construction de l'alphabet d'une source (On supposera pour la suite que la fréquence relative obtenue est proche de la réalité d'un point de vu statistique)"


def alphabet(texte):

    # Permet de construire l'alphabet d'un texte (var texte) et de plot la fréquence d'apparition de chaque caractère de la source

    f = open(texte, 'r').read()
    # Construction du dictionnaire (Caractère => Fréquence)
    alphabet_dico = Counter(f)

    # Conversion en fréquence
    compteur = sum(alphabet_dico.values())
    for key, value in alphabet_dico.items():
        value /= compteur
        alphabet_dico[key] = value

    # Affichage de la fréquence d'apparition des caractères
    plt.bar(alphabet_dico.keys(), alphabet_dico.values(), color='b')
    plt.title("Fréquence d'apparation des caractères ")
    plt.xlabel("Caractère  du texte")
    plt.ylabel("Fréquence d'apparition")

    plt.ylim([0, 1])
    plt.yticks(np.arange(0, 1, 0.05))

    plt.show()
    return alphabet_dico


"#2. Nous souhaitons maintenant calculer l'entropie de cette source"


def calcul_entropie(alphabet):

    # Calcul l'entropie d'une source et la renvoie arrondie à deux chiffres après la virgule
    entropie = 0

    for value in alphabet.values():
        entropie -= value * np.log2(value)

    return round(entropie, 2)


"""#3. Il est nécessaire de coder et compresser la source avant de la traiter (moduler, transmettre, etc...) => Utilisation du codage Huffman"
L'objectif étant de représenter les symboles de la source avec le plus petit nombre de bits pour chacun"""


def codec_huffman(texte):

    # Retourne simplement le dictionnaire qui est la résultante du codage Huffman d'une source donnée en paramètre => var texte

    f = open(texte, 'r').read()
    codec = hm.from_data(f)
    # Cette méthode affiche le dictionnaire (bits => symbole associé)
    dico_codec = hm.get_code_table(codec)

    return codec, dico_codec


def codage_huffman(texte):

    # Encode un texte par la méthode Huffman et affiche la table de codage ainsi que le texte encodé

    f = open(texte, 'r').read()
    codec = hm.from_data(f)
    hm.print_code_table(codec)  # Affiche la table de codage
    encoded = codec.encode(f)  # Encode la source

    # decodage
    decoded = codec.decode(encoded)
    # print(decoded)

    return encoded


def decodage_huffman(codec, encoded):

    decoded = codec.decode(encoded)

    return decoded


"#4. Calcul de R [bits], la longueur moyenne des mots de codes issus du codage Huffman puis comparaison à l'entropie afin de calculer l'efficacité du code (Entropie/R)"


def calcul_R(alphabet, dico_codec):

    # Calcul de R [bits] et renvoi le résultat arrondi au centièmes

    moyenne = 0

    for carac in alphabet:
        for carac2 in dico_codec:
            if carac == carac2:  # Mise en correspondance de chaque caractère
                tuple_dico = dico_codec[carac2]
                moyenne += tuple_dico[0] * alphabet[carac]

    return round(moyenne, 2)


def calcul_efficiency(entropie, R):

    # Calcul de l'efficacité du code (Comparasion de l'entropie par rapport à la moyenne R) puis la renvoie arrondie au centième

    efficiency = round(entropie / R * 100, 2)

    return round(efficiency, 2)


"#5. Arrangement de la source encodé en bytes (Tableau de bits; matrice de k colonnes + bits de bourrage)"


def bytes_to_bits(tab_bytes):

    # Convertis un array bytes en  array bits

    x = np.frombuffer(tab_bytes, dtype=np.uint8)
    bits = np.array(np.unpackbits(x))

    return bits


def bits_to_bytes(tab_bits):

    # Convertis un array de bits en array bytes
    x = np.frombuffer(tab_bits,dtype=np.uint8)
    bytes_arr = np.array(np.packbits(x))

    return bytes_arr


def reshape_bitsarray(k, tab_bits):

    # Conversion en matrice de k colonnes et ajout éventuel de bits de bourrage
    # Méthode donnée par Monsieur Nikolai LEBEDEV

    remhk = tab_bits.size % k

    if remhk > 0:
        # Nombres de lignes nécessaires pour le tableau de bits en entrée
        nrow = int(tab_bits.size / k + 1)
        # Calcul du nombre de bits de bourrages nécessaires pour remplir la ligne
        bitsjam = k - remhk

    else:
        nrow = int(tab_bits.size // k)
        bitsjam = 0

    if bitsjam > 0:
        # Ajout des bits de bourrages à la fin de la matrice pour la compléter (pour pouvoir présenter la source au canal car utilisation d'un codage en bloc)
        tab_bits = np.append(tab_bits, np.zeros(bitsjam).astype(int))

    k_words = np.reshape(tab_bits, (nrow, k))

    return k_words, bitsjam, nrow


def enlever_bitjam(source, bitsjam):

    if bitsjam != 0:
        source = source[0: -bitsjam]

    return source


"Affichage des différentes méthodes"

source = 'The_Adventures_of_Sherlock_Holmes_A_Scandal_In_Bohemia.txt'

alphabet = alphabet(source)
entropie = calcul_entropie(alphabet)
encoded = codage_huffman(source)
tab_bits = bytes_to_bits(encoded)
codec, dico_codec = codec_huffman(source)
R = calcul_R(alphabet, dico_codec)
efficiency = calcul_efficiency(entropie, R)


print(
    f"{bcolors.GREEN}Source codé/compressé => Affichage des 20 premiers caractères seulement{bcolors.RESET} \n: {encoded[0:20:1]}")
print(
    f"{bcolors.GREEN}L'entropie de la source est de {bcolors.RED}{entropie}[bits]{bcolors.RESET}")
print(
    f"{bcolors.GREEN}La moyenne de bits par symbole issue du codage Huffman est de {bcolors.RED}{R}[bits]{bcolors.RESET}")
print(f"{bcolors.GREEN}L'efficacité du codage huffman pour cette source est de {bcolors.RED}{efficiency}%{bcolors.RESET}")
print(f'-----Reformation de la source afin de pouvoir la présenter à l\'entrée du canal-----')

print(f"{bcolors.GREEN}Tableau de Bytes (encodage de la source par code de Huffman) transformé en tableau de bits{bcolors.RESET} : {tab_bits}")

"#6. Etape suivante => Code Correcteur D'erreurs (CCE) => Codage canal cyclique5"

print("-" * 20 + "Compression terminée, étape suivante : codage canal" + "-" * 20)
print("-" * 20 + "Génération d'un code cyclique" + "-" * 20)


"""Choix de n et de k"""

n = int(
    input(f"{bcolors.YELLOW}Choix de n (Default = 7) : {bcolors.RESET}") or "7")
k = int(
    input(f"{bcolors.YELLOW}Choix de k (Default = 4) : {bcolors.RESET}") or "4")

parite = n - k
taux_codage = Fraction(k, n)
taux_codage_float = round(k/n, 2)

print(
    f"\nLe taux de codage est de {bcolors.RED}{taux_codage}{bcolors.RESET} soit {bcolors.RED}{taux_codage_float}{bcolors.RESET} \n")
"""Choix du polynome générateur et création de la structure"""
print(
    f"La source sera encodée par bloc de {bcolors.RED}{k}{bcolors.RESET} bits auxquels on ajoutera {bcolors.RED}{parite}{bcolors.RESET} bits de parité pour former une matrice finale de {bcolors.RED}{n}{bcolors.RESET} colonnes qui sera présentée à l'entrée du CBS \n ")
genpoly = commpy.cyclic_code_genpoly(n, k)
print(
    f'Génération des polynômes pour (n,k) : ({bcolors.RED}{n}{bcolors.RESET},{bcolors.RED}{k}{bcolors.RESET}) => {genpoly}')

genpoly_choix = genpoly[0]
print(
    f'Choix d\'un des polynômes du code ({n},{k}): {bcolors.RED}{genpoly_choix}{bcolors.RESET}')

bin = format(genpoly_choix, 'b')
print(f'code {genpoly_choix} converti en bits : {bin}')

print("-" * 10 +
      f"\nCréation de la structure du code'{bcolors.RED}{bin}{bcolors.RESET}'" + "-" * 10)

cb = block.FECCyclic(bin)  # Structure

# Ajout des éventuels bits de bourage et création de la matrice qui sera l'entrée du codeur
tab_bits_shaped, nb_bits, nrow = reshape_bitsarray(k, tab_bits)
# Reshape car la fonction d'encodage prend une entrée spécifique (int)
x = np.reshape(tab_bits_shaped, size(tab_bits_shaped)).astype(int)
codewords = cb.cyclic_encoder(x)  # Encodage => Création des mots de codes


# Reshape pour obtenir la matrice des n mots de codes (k | n-k)
n_words = np.reshape(codewords, (nrow, n))
print(
    f"\n Les mots de codes (source + parité)  codage cyclique => Matrice N (k | n-k) en entrée du CBS : \n {n_words[0:20:1]} \n {bcolors.RED}{nb_bits}{bcolors.RESET} {bcolors.GREEN}bits de bourrage ajouté(s){bcolors.RESET}")

"Simulation du CBS en introduisant une erreur aléatoire dans chaque mot de code de la matrice N"

print("-"*10 + "Ajout d'un bit d'erreur aléatoire par mot de code de la matrice N (Simulation du CBS) :" + "-"*10)

for i in range(nrow):

    error_pos = i % 6
    n_words[i, error_pos] = (n_words[i, error_pos] + 1) % 2


print(
    f"{bcolors.GREEN}Sortie du CBS (erreurs introduites) :{bcolors.RESET} \n {n_words[0:20:1]}")

"#7. Une fois la simulation faite en introduisant des erreurs aléatoires, nous pouvons décoder"

print(f"{bcolors.GREEN}Etape suivante => Décodage canal{bcolors.RESET}")

# Même format pour le décodage (tableau de int)
y = np.reshape(n_words, size(n_words)).astype(int)
decoded_words = cb.cyclic_decoder(y)  # Décodeur / Correcteur

# Affichage du résultat (la source)
nwords_decoded = np.reshape(decoded_words, (nrow, k))
print(f"Matrice décodée et arrangée en k colonne :  \n{nwords_decoded[0:20:1]}")

"Décodage et correction des erreurs terminées => Nous pouvons présenter la source décodé à l'entrée du décodage Huffman pour retrouver notre source décodée et décompressée sans oublier d'enlever les bits de bourrage"

source_reshape = np.reshape(nwords_decoded, size(nwords_decoded))


source_init = enlever_bitjam(source_reshape, nb_bits) #On enlève les bits de bourrage préalablement ajouté à l'entrée du codeur
print(
    f"{nb_bits} bits de bourrage enlevé(s) \nSource sans bits de bourrage (mais encore codée/compressée) : \n{source_init}  ")

"Notre source est maintenant décodé et les bits de bourage éventuels ont été enlevés, on peut passer au décodage huffman "

print(f"{bcolors.GREEN} Etape suivante : Décodage Huffman {bcolors.RESET}")

to_huffman = bits_to_bytes(source_init) # Transformation en bytes pour la décompression

source_decode = decodage_huffman(codec, encoded)

# print(source_decode) Permet d'afficher le livre initial à la fin de toute la chaine de transmission ! Sans erreur