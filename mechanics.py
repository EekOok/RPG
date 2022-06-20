"""Module de Gestion des interactions de PJ et PNJ"""

import random

# ---------------------------------------------------
# Fonction générique
# ---------------------------------------------------

def d20(nb=1):
    """gestion d'un lancer de dé à 20 faces"""
    return random.randint(1, 20)


def d6(nb=1):
    """gestion d'un lancer de dé à 6 faces"""
    return random.randint(1, 6)

# ---------------------------------------------------
# Class liées au PJ/Pnj
# ---------------------------------------------------

class Vivant:
    """Gestion des capacités passives des êtres vivants """
    def recevoir_attaque(self, valeur_attaque):
        jet = d20()
        resultat = valeur_attaque > (self.defense + jet)
        if resultat:
            print(f"{self.nom}: Je suis touché! : Défense{self.defense+jet}")
        else:
            print(f"{self.nom}: tu m'as raté, niak niak : Défense{self.defense + jet}")

        return resultat, self.defense+jet

    def recevoir_sort(self, valeur_sort):
        jet = d20()
        resultat = valeur_sort > (self.sauvegarde + jet)
        if resultat:
            print(f"{self.nom}: Je ne peux resister a ce sort! : sauvegarde{self.sauvegarde +jet}")
        else:
            print(f"{self.nom}: Je resiste a ce sort , niak niak : Défense{self.sauvegarde + jet}")

        return resultat, self.sauvegarde+jet

    def recevoir_degat(self, valeur_degat):
        self.point_de_vie -= valeur_degat
        self.point_de_vie = max(0, self.point_de_vie)
        print(f'{self.nom}arg je souffre. pdv restant = {self.point_de_vie}')
        self.calcul_etat()

    def calcul_etat(self):
        ancien_etat = self.etat
        if self.point_de_vie == 0:
            self.etat = 'mort'
        elif self.point_de_vie < self.point_de_vie_max // 2:
            self.etat = 'mal en point'
        elif self.point_de_vie < self.point_de_vie_max:
            self.etat = 'blessé'
        elif self.point_de_vie == self.point_de_vie_max:
            self.etat = 'Vivant'

        if self.etat != ancien_etat:
            print(f"{self.nom}: Je suis {self.etat}")


class Magicien:
    """Gestion des capacités des magiciens"""
    def se_soigner(self):
        jet = d20()
        if jet+self.magie > 15 and self.recup_pdv_max > 0:
            self.point_de_vie += d6() + 2
            self.point_de_vie = min(self.point_de_vie_max, self.point_de_vie)
            print(f'{self.nom}: Shazammmm !:{self.point_de_vie}')
        else:
            print(f'{self.nom}: marche pas !')

    def magicaliser_cible(self, cible):
        jet = d20()
        valeur_sort = jet + self.attaque

        print(f"{self.nom}: Par le tourbillon de wazaaaaa.")
        cible_touche, valeur_def = cible.recevoir_sort(valeur_sort)

        if cible_touche:
            print(f"{self.nom}: Tu ne peux resister à mon pouvoir!!Sort={valeur_sort}")
            self.faire_degat_cible(cible)
        else:
            print(f"{self.nom}: Je t'aurais la prochaine fois !!Sort={valeur_sort}")


class Combattant:
    """Gestion des capacités des combattants"""
    def attaquer_cible(self, cible):
        jet = d20()
        valeur_attaque = jet + self.attaque
        liste_juron = ['de Malheur', 'de mes deux...', 'de pacotille']
        random.shuffle(liste_juron)

        print(f"{self.nom}: Je t'attaque {cible.nom} {liste_juron[0]}")
        cible_touche, valeur_def = cible.recevoir_attaque(valeur_attaque)

        if cible_touche:
            print(f"{self.nom}: oui je t'ai touché, youpi!Attaque={valeur_attaque}")
            self.faire_degat_cible(cible)
        else:
            print(f"{self.nom}: tu perd rien pour attendre!Attaque={valeur_attaque}")

    def faire_degat_cible(self, cible):
        jet = d6()
        print(f"{self.nom}: dégat = {jet+self.degat}")
        cible.recevoir_degat(jet+self.degat)

# ---------------------------------------------------
# Fusion de class
# ---------------------------------------------------

class Joueur(Vivant, Combattant, Magicien):
    """ Fusion des class Vivant / Combattant / Magicien"""
    def __init__(self, nom, force, dexterite, constitution, intelligence, sagesse, charisme):
        self.nom = nom
        self.etat = 'Vivant'
        self.degat = force
        self.point_de_vie, self.point_de_vie_max = 10 + constitution, 10 + constitution
        self.recup_pdv, self.recup_pdv_max = 1 + constitution, 1 + constitution
        self.energie, self. energie_max = 10 + sagesse, 10 + sagesse
        self.recup_energie, self.recup_energie_max = 1+sagesse, 1+sagesse
        self.attaque = force + intelligence
        self.defense = dexterite + charisme
        self.sauvegarde = constitution + sagesse
        self.init = dexterite + charisme
        self.magie = intelligence + sagesse
        self.Cdiscretion = dexterite + sagesse

        self.dico_action = {'Attaquer': [], 'Défense': [], 'Magie': {'Soigner': []}, 'Objet': []}

    def __str__(self):
        return f"Nom: {self.nom} \n \
PDV/PDVmax : {self.point_de_vie}/{self.point_de_vie_max} \n \
ENE/ENEmax : {self.energie}/{self.energie_max} \n \
Recup PDV/ENE: {self.recup_pdv_max}/ {self.recup_energie_max} \n \
Attaque/Defense/Sauvegarde: {self.attaque}/{self.defense}/{self.sauvegarde} \n \
Init/ Magie: {self.init}/{self.magie}"

    def discretion(self, test):
        return test > d20() + self.Cdiscretion


class Pnj(Vivant, Combattant):
    """ Fusion des class Vivant et combattant pour créer un Pnj minimum"""
    def __init__(self, nom, perception):
        self.nom = nom
        self.etat = 'Vivant'
        self.degat = 2
        self.point_de_vie, self.point_de_vie_max, self.recup_pdv, self.recup_pdv_max = 10, 10, 1, 1
        self.energie, self. energie_max, self.recup_energie, self.recup_energie_max = 10, 10, 1, 1
        self.attaque,  self.defense, self.sauvegarde = 5, 5, 5
        self.init, self.magie = 5, 5
        self.perception = perception

    def cherche_pj(self, pj):
        jet = d20()
        return pj.discretion(jet+self.perception)

# ---------------------------------------------------

if __name__ == '__main__':
    Hero = Joueur('Toto', 5, 4, 3, 2, 1, 0)
    Gob1 = Pnj('Méchant gobelin', 2)
    while 'mort' not in [Hero.etat, Gob1.etat]:
        print(Hero)
        if Hero.etat != 'mort':
            reponse = str(input('Que voulez-vous faire ? A ttaquer, M agie, S oigner ?'))
            if reponse == 'S':
                Hero.se_soigner()
            elif reponse == 'M':
                Hero.magicaliser_cible(Gob1)
            else:
                Hero.attaquer_cible(Gob1)

        if Gob1.etat != 'mort':
            Gob1.attaquer_cible(Hero)
