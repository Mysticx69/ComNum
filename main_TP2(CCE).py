from time import sleep

import sk_dsp_comm.sigsys as ss
import scipy.signal as signal
import commpy.channelcoding as commpy
#from IPython.display import Audio, display
import scipy.special as special
import sk_dsp_comm.digitalcom as dc
import sk_dsp_comm.fec_block as block
#from IPython.display import Image, SVG
from numpy import reshape, size

from main_final_TP1 import *


print(f"Source codé : {encoded}")
print(f"L'entropie de la source est de {entropie}")
print(f"La moyenne de bits par symbole issue du codage Huffman est de {R}")
print(f"L'efficacité du codage huffman pour cette source est de {efficiency}%")
print(f"bytes encodés en bits : {tab_bits}")
print(f"Bits shaped : \n{tab_bits_shaped[0:5:1, ::]} \n {nb_bits} bits de bourrage ajouté(s)")



print("-" * 20 + "Compression terminée, étape suivante : codage canal")
print("-" * 20 + "Génération d'un code cyclique")
"""Choix de n et de k"""
n = int(input("Choix de n :"))
k = int(input("Choix de k : "))

genpoly = commpy.cyclic_code_genpoly(n, k)
print(f'Génération des polynômes pour (n,k) : ({n},{k}) => {genpoly}')
genpoly_choix = genpoly[0]
print(f'Choix d\'un des polynômes du code ({n},{k}): {genpoly_choix}')
bin = format(genpoly_choix, 'b')
print(f'code {genpoly_choix} converti en bits : {bin}')
print("-" * 10 + f"Création de la structure du code'{bin}'" + "-" * 10)
cb = block.FECCyclic(bin)
x = reshape(tab_bits,size(tab_bits)).astype(int)
codewords = cb.cyclic_encoder(x)
reshaped, nb_bitjam, nrow = reshape_bitsarray(n, codewords)
print(f"Bits shaped (encoded) : \n{reshaped[0:10:1, ::]} ")
print("-"*10 +"Ajout d'un bit d'erreur aléatoire" + "-"*10)

for i in range(nrow):
    error_pos = i % 6
    reshaped[i, error_pos] = (reshaped[i, error_pos] + 1) % 2

#reshape(reshaped,size(reshaped))
print(reshaped[0:10:1, ::])

print("-"*10 +"Décodage Canal" + "-"*10)
decoded_blocks = cb.cyclic_decoder(codewords)
reshaped_decoded, nb_bitjam, nrow = reshape_bitsarray(7,decoded_blocks)
print(f"Bits shaped (decoded) : \n{reshaped_decoded[0:10:1, ::]} ")


