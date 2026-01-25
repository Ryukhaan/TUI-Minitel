#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Sequence est un module permettant de gérer les séquences de caractères
pouvant être envoyées à un Minitel.

"""

from unicodedata import normalize
from binascii import unhexlify

# Tables de conversion des caractères spéciaux
UNICODEVERSVIDEOTEX = {
    '£': '1923', '°': '1930', '±': '1931', 
    '←': '192C', '↑': '192D', '→': '192E', '↓': '192F', 
    '¼': '193C', '½': '193D', '¾': '193E', 
    'ç': '194B63', '’': '194B27', 
    'à': '194161', 'á': '194261', 'â': '194361', 'ä': '194861', 
    'è': '194165', 'é': '194265', 'ê': '194365', 'ë': '194865', 
    'ì': '194169', 'í': '194269', 'î': '194369', 'ï': '194869', 
    'ò': '19416F', 'ó': '19426F', 'ô': '19436F', 'ö': '19486F', 
    'ù': '194175', 'ú': '194275', 'û': '194375', 'ü': '194875', 
    'Œ': '196A', 'œ': '197A', 
    'ß': '197B', 'β': '197B'
}

UNICODEVERSAUTRE = {
    '£': '0E230F',
    '°': '0E5B0F', 'ç': '0E5C0F', '’': '27', '`': '60', '§': '0E5D0F',
    'à': '0E400F', 'è': '0E7F0F', 'é': '0E7B0F', 'ù': '0E7C0F'
}

# UNICODEVERSAUTRE = {
#     '£': '0E230F',
#     '°': '0E5B0F', 'ç': '0E5C0F', "'": '27', '`': '60', '§': '0E5D0F',
#     'à': '0E400F', 'â': '0E5E0F', 'ä': '0E7D0F',
#     'è': '0E7F0F', 'é': '0E7B0F', 'ê': '0E5F0F', 'ë': '0E7E0F',
#     'î': '0E5E0F', 'ï': '0E7E0F',
#     'ô': '0E5E0F', 'ö': '0E7D0F',
#     'ù': '0E7C0F', 'û': '0E5E0F', 'ü': '0E7D0F',
# }

# table inverse VIDEOTEX (hex → unicode)
VIDEOTEX_TO_UNICODE = {}

# VIDEOTEX
for char, hexcode in UNICODEVERSVIDEOTEX.items():
    VIDEOTEX_TO_UNICODE[unhexlify(hexcode)] = char

# MIXTE / TELEINFORMATIQUE
for char, hexcode in UNICODEVERSAUTRE.items():
    VIDEOTEX_TO_UNICODE[unhexlify(hexcode)] = char

class Sequence:
    """Une classe représentant une séquence de valeurs

    Une Séquence est une suite de valeurs prêtes à être envoyées à un Minitel.
    Ces valeurs respectent la norme ASCII.
    """
    def __init__(self, valeur = None, standard = 'VIDEOTEX'):
        """Constructeur de Sequence

        :param valeur:
            valeur à ajouter à la construction de l’objet. Si la valeur est à
            None, aucune valeur n’est ajoutée
        :type valeur:
            une chaîne de caractères, un entier, une liste, une séquence ou
            None

        :param standard:
            standard à utiliser pour la conversion unicode vers Minitel. Les
            valeurs possibles sont VIDEOTEX, MIXTE et TELEINFORMATIQUE (la
            casse est importante)
        :type standard:
            une chaîne de caractères
        """
        assert valeur == None or \
                isinstance(valeur, (list, int, str, Sequence))
        assert standard in ['VIDEOTEX', 'MIXTE', 'TELEINFORMATIQUE']

        self.valeurs = []
        self.longueur = 0
        self.standard = standard

        if valeur != None:
            self.ajoute(valeur)
        
    def ajoute(self, valeur):
        """Ajoute une valeur ou une séquence de valeurs

        La valeur soumise est d’abord canonisée par la méthode canonise avant
        d’être ajoutée à la séquence. Cela garantit que la séquence ne contient
        que des entiers représentant des caractères de la norme ASCII.

        :param valeur:
            valeur à ajouter
        :type valeur:
            une chaîne de caractères, un entier, une liste ou une Séquence
        """
        assert isinstance(valeur, (list, int, str, Sequence))

        self.valeurs += self.canonise(valeur)
        self.longueur = len(self.valeurs)

    def canonise(self, valeur):
        """Canonise une séquence de caractères

        Si une liste est soumise, quelle que soit sa profondeur, elle sera
        remise à plat. Une liste peut donc contenir des chaînes de caractères,
        des entiers ou des listes. Cette facilité permet la construction de
        séquences de caractères plus aisée. Cela facilite également la
        comparaison de deux séquences.

        :param valeur:
            valeur à canoniser
        :type valeur:
            une chaîne de caractères, un entier, une liste ou une Séquence

        :returns:
            Une liste de profondeur 1 d’entiers représentant des valeurs à la
            norme ASCII.

        Exemple::
            canonise(['dd', 32, ['dd', 32]]) retournera
            [100, 100, 32, 100, 100, 32]
        """
        assert isinstance(valeur, (list, int, str, Sequence))

        # Si la valeur est juste un entier, on le retient dans une liste
        if isinstance(valeur, int):
            return [valeur]

        # Si la valeur est une Séquence, ses valeurs ont déjà été canonisées
        if isinstance(valeur, Sequence):
            return valeur.valeurs

        # À ce point, le paramètre contient soit une chaîne de caractères, soit
        # une liste. L’une ou l’autre est parcourable par une boucle for ... in
        # Transforme récursivement chaque élément de la liste en entier
        canonise = []
        for element in valeur:
            if isinstance(element, str):
                # Cette boucle traite 2 cas : celui ou liste est une chaîne
                # unicode et celui ou element est une chaîne de caractères
                for caractere in element:
                    for ascii in self.unicode_vers_minitel(caractere):
                        canonise.append(ascii)
            elif isinstance(element, int):
                # Un entier a juste besoin d’être ajouté à la liste finale
                canonise.append(element)
            elif isinstance(element, list):
                # Si l’élément est une liste, on la canonise récursivement
                canonise = canonise + self.canonise(element)

        return canonise

    def unicode_vers_minitel(self, caractere):
        """Convertit un caractère unicode en son équivalent Minitel

        :param caractere:
            caractère à convertir
        :type valeur:
            une chaîne de caractères unicode

        :returns:
            une chaîne de caractères contenant une suite de caractères à
            destination du Minitel.
        """
        assert isinstance(caractere, str) and len(caractere) == 1

        if self.standard == 'VIDEOTEX':
            if caractere in UNICODEVERSVIDEOTEX:
                return unhexlify(UNICODEVERSVIDEOTEX[caractere])
        else: # TELEINFORMATIQUE / MIXTE
            if caractere in UNICODEVERSAUTRE:
                return unhexlify(UNICODEVERSAUTRE[caractere])
            # sinon renvoyer directement le code ASCII brut (compatible 0x20-0x7E)
            return bytes([ord(caractere)])
        # return normalize('NFKD', caractere).encode('ascii', 'replace')
        return bytes([ord(caractere)])

    def egale(self, sequence):
        """Teste l’égalité de 2 séquences

        :param sequence:
            séquence à comparer. Si la séquence n’est pas un objet Sequence,
            elle est d’abord convertie en objet Sequence afin de canoniser ses
            valeurs.
        :type sequence:
            un objet Sequence, une liste, un entier, une chaîne de caractères
            ou une chaîne unicode

        :returns:
            True si les 2 séquences sont égales, False sinon
        """
        assert isinstance(sequence, (Sequence, list, int, str))

        # Si la séquence à comparer n’est pas de la classe Sequence, alors
        # on la convertit
        if not isinstance(sequence, Sequence):
            sequence = Sequence(sequence)

        return self.valeurs == sequence.valeurs

    def decode(self) -> str:
        """
        Décode des octets reçus du Minitel en Unicode Python, selon le mode
        : VIDEOTEX ou TELEINFORMATIQUE.
        """
        i = 0
        output = ""
        data = bytes(self.valeurs)

        while i < len(data):
            matched = False

            # Mode VIDEOTEX : tenter de correspondre à une séquence spéciale VIDEOTEX
            if self.standard == 'VIDEOTEX':
                for seq, unicode_char in VIDEOTEX_TO_UNICODE.items():
                    if data[i:i+len(seq)] == seq:
                        output += unicode_char
                        i += len(seq)
                        matched = True
                        break

                if matched:
                    continue

            # Mode TELEINFORMATIQUE : les caractères sont directement ASCII imprimables
            if self.standard == 'TELEINFORMATIQUE':
                # Ignorer ESC (0x1B) ou autres codes de contrôle connus
                if data[i] in (0x00, 0x1B, 0x0D, 0x0A):
                    i += 1
                    continue

                # Pour les octets imprimables ASCII standard
                if 32 <= data[i] <= 126:
                    output += chr(data[i])
                else:
                    # Pour tout autre octet non imprimable, ignorer
                    pass
                i += 1
            else:
                # Mode VIDEOTEX standard : ASCII direct si pas de correspondance VIDEOTEX
                if 32 <= data[i] <= 126:
                    output += chr(data[i])
                i += 1

        return output