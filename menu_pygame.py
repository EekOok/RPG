import pygame

import PIL.Image

# pour test uniquement
import Tools
import mechanics
import game

BLANC = (255, 255, 255)
NOIR = (0, 0, 0)
BLEU_NUIT = (5, 5, 30)
ROUGE = (255, 0, 0)
VERT = (0, 255, 0)
BLEU = (0, 0, 255)
JAUNE = (255, 216, 0)
ORANGE = (255, 106, 0)


class Menu:
    """ Class de base qui dessine le cadre des menus"""
    def __init__(self, nom, dimension):
        self.nom = nom
        self.color_fond = (30, 5, 5)

        self.image_bar_b = pygame.image.load("images/menu/bar_b.png").convert_alpha()
        self.image_bar_d = pygame.image.load("images/menu/bar_d.png").convert_alpha()
        self.image_bar_h = pygame.image.load("images/menu/bar_h.png").convert_alpha()
        self.image_bar_g = pygame.image.load("images/menu/bar_g.png").convert_alpha()

        self.image_coin_bas_droit = pygame.image.load("images/menu/coin_bas_droit.png").convert_alpha()
        self.image_coin_bas_gauche = pygame.image.load("images/menu/coin_bas_gauche.png").convert_alpha()
        self.image_coin_haut_droit = pygame.image.load("images/menu/coin_haut_droit.png").convert_alpha()
        self.image_coin_haut_gauche = pygame.image.load("images/menu/coin_haut_gauche.png").convert_alpha()

        self.dimension = dimension

        self.refx = self.dimension[0]
        self.refy = self.dimension[1]
        self.width = self.dimension[2]
        self.height = self.dimension[3]

    def drawme(self, surface):

        rect_fond = pygame.Rect(pygame.Rect(self.refx, self.refy, self.width, self.height))
        pygame.draw.rect(surface, self.color_fond, rect_fond)
        surface.blit(self.image_coin_haut_gauche, (self.refx, self.refy))
        surface.blit(self.image_coin_haut_droit, (self.refx+self.width-8, self.refy))
        surface.blit(self.image_coin_bas_droit, (self.refx + self.width - 8, self.refy+self.height-8))
        surface.blit(self.image_coin_bas_gauche, (self.refx, self.refy + self.height - 8))

        self.image_bar_h = pygame.transform.scale(self.image_bar_h, (max(self.width-16, 0), 8))
        surface.blit(self.image_bar_h, (self.refx+8, self.refy))

        self.image_bar_b = pygame.transform.scale(self.image_bar_b, (max(self.width-16, 0), 8))
        surface.blit(self.image_bar_b, (self.refx + 8, self.refy + self.height - 8))

        self.image_bar_g = pygame.transform.scale(self.image_bar_g, (8, max(self.height-16, 0)))
        surface.blit(self.image_bar_g, (self.refx, self.refy + 8))

        self.image_bar_d = pygame.transform.scale(self.image_bar_d, (8, max(self.height - 16, 0)))
        surface.blit(self.image_bar_d, (self.refx+self.width-8, self.refy + 8))

    def gocurseur(self, direction):
        pass


class MenuMsg(Menu):
    def __init__(self, nom, dimension, msg, font):
        super().__init__(nom, dimension)
        self.font = font
        self.label = self.font.render(msg, True, JAUNE)

    def drawme(self, surface):
        super().drawme(surface)
        surface.blit(self.label, (self.refx+8, self.refy+160))


class MenuSelect(Menu):
    """ Menu qui créer une liste verticale avec un curseur de selection"""
    def __init__(self, nom, dimension, dico_choix, font, focus=True):
        super().__init__(nom, dimension)

        self.image_curseur = pygame.image.load("./images/menu/fleche.png").convert_alpha()
        self.poscursor = 0
        self.focus = focus

        self.dico_choix = dico_choix

        self.liste_choix = []
        for key in self.dico_choix:
            self.liste_choix.append(key)

        self.font = font

        self.dict_label = {}

        for element in self.liste_choix:
            self.dict_label[element] = self.font.render(element, True, JAUNE)

    def gocurseur(self, direction):
        y = self.poscursor

        if direction.key == pygame.K_UP:
            y -= 1
        elif direction.key == pygame.K_DOWN:
            y += 1

        y = 0 if y > len(self.liste_choix) - 1 else y
        y = len(self.liste_choix) - 1 if y < 0 else y

        self.poscursor = y

    def drawme(self, surface):
        super().drawme(surface)
        i = 0
        for element in self.liste_choix:
            surface.blit(self.dict_label[element], (self.refx + 40, self.refy + (i * 24)))
            i += 1
        if self.focus:
            surface.blit(self.image_curseur,
                         (self.refx + 8, self.refy + (self.poscursor * 24)))


class InterfaceCombat:
    """ ensemble de menu qui dessine l'interface de combat"""
    def __init__(self, font, liste_hero, liste_pnj):
        self.font = font
        self.liste_hero = liste_hero
        self.liste_pnj = liste_pnj
        self.action_faites = False
        self.touspnjmorts = False
        self.color_fond = (30, 5, 5)
        self.partiehaute = Menu('Haute', [0, 0, 640, 320])
        self.dico_action = self.liste_hero[0].dico_action
        self.dico_pnj = {}
        self.liste_jaugepj=[]
        self.liste_jaugepnj = []
        for pj in liste_hero:
            self.liste_jaugepj.append(Jauge(ROUGE,pj.point_de_vie_max,(8,8,10,64)))
            pj.direction = 'right'
            pj.refreshdirection()
        for pnj in liste_pnj:
            self.liste_jaugepnj.append(Jauge(ROUGE,pnj.point_de_vie_max,(640-8-10,8,10,64)))
            pnj.direction = 'left'
            pnj.refreshdirection()
            self.dico_pnj[pnj.nom] = pnj

        self.partiebasse1 = MenuSelect('selecteur', [0, self.partiehaute.refy+self.partiehaute.height, 150, 150],
                                       self.dico_action, self.font)

        self.pnjselecteur = MenuSelect('selecteur_pnj', [self.partiebasse1.refx+self.partiebasse1.width,
                                       self.partiebasse1.refy, 150, 120], self.dico_pnj, self.font)
        self.pnjselecteur.focus = False
        self.partiebasse2 = Menu('global', [self.partiebasse1.refx+self.partiebasse1.width,
                                            self.partiebasse1.refy, 490, self.partiebasse1.height])
        self.piedpage = Menu('pied', [0, self.partiebasse1.refy+self.partiebasse1.height, 640, 120])
        self.pos_curseur = [0, 0]
        self.fen_encours = self.partiebasse1
        self.liste_evenement_combat = []

    def drawme(self, surface):
        self.partiehaute.drawme(surface)
        for jauge in self.liste_jaugepj:
            jauge.drawme(surface,self.liste_hero[0].point_de_vie)
        for jauge in self.liste_jaugepnj:
            jauge.drawme(surface, self.liste_pnj[0].point_de_vie)
        self.liste_hero[0].index_image=0
        picture = pygame.transform.scale(self.liste_hero[0].image, (64, 64))
        surface.blit(picture, (18, 8))
        picture = pygame.transform.scale(self.liste_pnj[0].image, (64, 64))
        surface.blit(picture, (640-64-18, 8))

        self.partiebasse1.drawme(surface)
        self.partiebasse2.drawme(surface)
        if self.partiebasse1.poscursor == 0 and self.pnjselecteur.focus:
            self.pnjselecteur.drawme(surface)
        self.piedpage.drawme(surface)
        if len(self.liste_evenement_combat) > 0:
            surface.blit(self.liste_evenement_combat[-1].msg, (self.piedpage.refx + 8, self.piedpage.refy + 8))
        if len(self.liste_evenement_combat) > 1:
            surface.blit(self.liste_evenement_combat[-2].msg, (self.piedpage.refx + 8, self.piedpage.refy + 8 + 24))
        if len(self.liste_evenement_combat) > 2:
            surface.blit(self.liste_evenement_combat[-3].msg, (self.piedpage.refx + 8, self.piedpage.refy + 8 + 48))
        if len(self.liste_evenement_combat) > 4:
            surface.blit(self.liste_evenement_combat[-4].msg, (self.piedpage.refx + 8, self.piedpage.refy + 8 + 72))

    def gocurseur(self, event):
        if event.key in [pygame.K_UP, pygame.K_DOWN]:
            self.fen_encours.gocurseur(event)
        elif event.key in [pygame.K_RETURN, pygame.K_RIGHT]:
            if self.fen_encours == self.partiebasse1 and self.partiebasse1.poscursor == 0:
                self.partiebasse1.focus = False
                self.pnjselecteur.focus = True
                self.fen_encours = self.pnjselecteur
            elif self.fen_encours == self.pnjselecteur:
                self.action_faites = True
                uneEvent = AffichFightEvenement(self.liste_hero[0].attaquer_cible(self.liste_pnj[self.pnjselecteur.poscursor]),self.font)
                self.liste_evenement_combat.append(uneEvent)

        elif event.key in [pygame.K_ESCAPE, pygame.K_LEFT]:
            if self.fen_encours == self.pnjselecteur:
                self.pnjselecteur.focus = False
                self.partiebasse1.focus = True
                self.fen_encours = self.partiebasse1

    def initialisecombat(self, liste_hero, liste_npc):
        self.liste_hero = liste_hero
        self.liste_npc = liste_npc

    def actionpnj(self):
        if self.action_faites:
            self.action_faites = False
            self.touspnjmorts = True
            for pnj in self.liste_pnj:
                if pnj.etat != 'mort':
                    self.touspnjmorts = False
                    uneEvent = AffichFightEvenement(pnj.attaquer_cible(self.liste_hero[0]), self.font)
                    self.liste_evenement_combat.append(uneEvent)
                else:
                    uneEvent = AffichFightEvenement([mechanics.FightEvent.PNJ_DEAD, pnj.nom], self.font)
                    self.liste_evenement_combat.append(uneEvent)


class AffichFightEvenement:
    def __init__(self, monevenement, font):
        self.font = font
        self.code = monevenement[0]
        self.msg = self.font.render(f"unknown{self.code}", True, JAUNE)

        if self.code == mechanics.FightEvent.PJ_ATTACK_FAILED:
            self.nom_executeur = monevenement[1]
            self.nom_cible = monevenement[2]
            self.jet_attaque = monevenement[3]
            self.msg = self.font.render(f"{self.nom_executeur} n'arrive pas à toucher {self.nom_cible}!{self.jet_attaque}", True, JAUNE)
        elif self.code == mechanics.FightEvent.PJ_ATTACK_SUCCESS:
            self.nom_executeur = monevenement[1]
            self.nom_cible = monevenement[2]
            self.jet_attaque = monevenement[3]
            self.jet_defense = monevenement[4]
            self.jet_degat = monevenement[5]+monevenement[6]
            self.pdv_restant = monevenement[7]
            self.pdv_etat = monevenement[8]
            self.msg = self.font.render(f"{self.nom_executeur} arrive à toucher {self.nom_cible} et lui fait {self.jet_degat} dégat(s)", True, JAUNE)
        elif self.code == mechanics.FightEvent.PNJ_DEAD:
            self.nom_cible = monevenement[1]
            self.msg = self.font.render(
                f"{self.nom_cible} est mort", True,
                JAUNE)

    def __str__(self):
        return str(self.code)


class Jauge:
    def __init__(self, color, valeurmax=10, position=(0, 0, 0, 0)):
        self.color = color
        self.vmax = valeurmax
        self.refx = position[0]
        self.refy = position[1]
        self.width = position[2]
        self.height = position[3]

    def drawme(self, surface, vactu):
        remplissage = int((64 * vactu) / self.vmax)
        vide = 64 - remplissage
        pygame.draw.rect(surface, self.color, pygame.Rect(self.refx, self.refy, 10, 64), 2)
        pygame.draw.rect(surface, self.color, pygame.Rect(self.refx, self.refy+vide, 10, remplissage))


class Creaperso:
    def __init__(self, font):
        self.font = font

        self.cadre_couleur = Menu('couleur', (0, 0, 320, 200))
        self.label_couleur = self.font.render('Couleur', True, JAUNE)
        self.label_chev = self.font.render('< Cheveux  >', True, JAUNE)
        self.label_yeux = self.font.render('<   Yeux   >', True, JAUNE)
        self.label_peau = self.font.render('<   Peau   >', True, JAUNE)
        self.label_chemise = self.font.render('< Chemise  >', True, JAUNE)
        self.label_pantalon = self.font.render('< Pantalon >', True, JAUNE)

        self.ligne_selector = 0
        self.cadre_selector = 0
        self.liste_coul = ["rouge", "rouge sombre", "bleu", "bleu sombre", "vert", "vert sombre", "black", "rose"]
        self.index = [1, 4, 7, 6, 5]
        self.sprite_sheet = None
        self.modifcoul = True  # pour optimiser l'accès au fichier img

        self.cadre_carac = Menu('carac', (320, 0, 320, 200))
        self.label_carac = self.font.render('Caractéristiques', True, JAUNE)

        self.car_force = ModificateurCarac('Force',self.font)
        self.car_dexterite = ModificateurCarac('Dextérité', self.font)
        self.car_constitution = ModificateurCarac('Constitution', self.font)
        self.car_intelligence = ModificateurCarac('Intelligence', self.font)
        self.car_sagesse = ModificateurCarac('Sagesse', self.font)
        self.car_charisme = ModificateurCarac('Charisme', self.font)

        self.liste_carac = [self.car_force, self.car_dexterite, self.car_constitution,
                        self.car_intelligence, self.car_sagesse, self.car_charisme]

        self.carindex = [0, 0, 0, 0, 0, 0]

        self.point_car_restante = 15

        self.cadre_atout = Menu('atout', (0, 200, 640, 440))
        self.cadre_at1 = Menu('at1', (0, 200, 320, 120))

        self.dict_atout = Tools.readthedict(f"./rules/atout.json")

        self.firstatout = ChoixDoubleEntree(self.dict_atout, self.font)

    def getcoulliterral(self):
        listecoullit = []
        for valeur in self.index:
            listecoullit.append(self.liste_coul[valeur])
        return listecoullit

    def gocurseur(self, direction):
        y = self.ligne_selector
        x = self.cadre_selector
        if direction.key == pygame.K_UP:
            y -= 1
            self.danscategorie = False
        elif direction.key == pygame.K_DOWN:
            y += 1
            self.danscategorie = False

        if y > 4 and x == 0:
            y = 0
            x = 1
        elif y < 0 and x == 0:
            y = 0
            x = 2

        elif y < 0 and x == 1:
            y = 4
            x = 0
        elif y > 5 and x == 1:
            y = 0
            x = 2

        elif y < 0 and x == 2:
            y = 5
            x = 1
        elif y > 0 and x == 2:
            y = 0
            x = 0

        self.ligne_selector = y
        self.cadre_selector = x

        if self.cadre_selector == 0:
            couselector = self.index[y]
            if direction.key == pygame.K_RIGHT:
                self.modifcoul = True
                couselector += 1
            elif direction.key == pygame.K_LEFT:
                self.modifcoul = True
                couselector -= 1
            couselector = 0 if couselector > len(self.liste_coul)-1 else couselector
            couselector = len(self.liste_coul)-1 if couselector < 0 else couselector
            self.index[y] = couselector

        elif self.cadre_selector == 1:
            self.liste_carac[self.ligne_selector].eventreaction(direction)

        elif self.cadre_selector == 2:
            categorieselector = self.indexfirstcategorie
            atoutselector = self.indexfirstatout
            if not self.danscategorie:
                modif = False
                if direction.key == pygame.K_RIGHT:
                    categorieselector -= 1
                    modif = True
                elif direction.key == pygame.K_LEFT:
                    categorieselector += 1
                    modif = True
                elif direction.key == pygame.K_RETURN:
                    self.danscategorie = True

                categorieselector = 0 if categorieselector > len(self.liste_categorie) - 1 else categorieselector
                categorieselector = len(self.liste_categorie) - 1 if categorieselector < 0 else categorieselector

                self.indexfirstcategorie = categorieselector
                self.firstcategorie = self.liste_categorie[self.indexfirstcategorie]
                self.label_firstcategorie = self.font.render('< ' + str(self.firstcategorie) + ' >', True, JAUNE)

                if modif:
                    self.liste_atout=[]
                    for atout in self.dict_atout[self.firstcategorie]:
                        self.liste_atout.append(atout)
                    self.firstatout = self.liste_atout[0]

            elif self.danscategorie:
                if direction.key == pygame.K_RIGHT:
                    atoutselector -= 1
                elif direction.key == pygame.K_LEFT:
                    atoutselector += 1
                elif direction.key == pygame.K_RETURN:
                    self.danscategorie = False
                atoutselector = 0 if atoutselector > len(self.liste_atout) - 1 else atoutselector
                atoutselector = len(self.liste_atout) - 1 if atoutselector < 0 else atoutselector

                self.indexfirstatout = atoutselector
                self.firstatout = self.liste_atout[self.indexfirstatout]
                self.label_firstatout = self.font.render('< ' + str(self.firstatout) + ' >', True, JAUNE)

    def update_image(self, img2modify):
        index = self.getcoulliterral()
        color_cheveux = index[0]
        color_oeuil = index[1]
        color_peau = index[2]
        color_chemise = index[3]
        color_pantalon = index[4]

        (largeur, hauteur) = img2modify.size
        px = img2modify.load()
        for x in range(largeur):
            for y in range(hauteur):
                coul = px[x, y]
                # Chemise ------------------------------
                if coul == (54, 56, 74):
                    img2modify.putpixel((x, y), self.retournecouleurset(color_chemise, 'sombre'))
                elif coul == (26, 36, 43):
                    img2modify.putpixel((x, y), self.retournecouleurset(color_chemise, 'tres sombre'))
                elif coul == (41, 48, 59):
                    img2modify.putpixel((x, y), self.retournecouleurset(color_chemise, 'clair'))
                elif coul == (79, 82, 107):
                    img2modify.putpixel((x, y), self.retournecouleurset(color_chemise, 'tres clair'))
                # Oeuil
                elif coul == (107, 23, 23):
                    img2modify.putpixel((x, y), self.retournecouleurset(color_oeuil, 'clair'))
                elif coul == (163, 51, 51):
                    img2modify.putpixel((x, y), self.retournecouleurset(color_oeuil, 'tres clair'))
                # Cheveux
                elif coul == (38, 41, 38):
                    img2modify.putpixel((x, y), self.retournecouleurset(color_cheveux, 'tres sombre'))
                elif coul == (59, 56, 56):
                    img2modify.putpixel((x, y), self.retournecouleurset(color_cheveux, 'sombre'))
                elif coul == (84, 89, 89):
                    img2modify.putpixel((x, y), self.retournecouleurset(color_cheveux, 'medium'))
                elif coul == (133, 138, 140):
                    img2modify.putpixel((x, y), self.retournecouleurset(color_cheveux, 'clair'))
                elif coul == (176, 184, 186):
                    img2modify.putpixel((x, y), self.retournecouleurset(color_cheveux, 'tres clair'))
                # pantalon
                elif coul == (31, 48, 105):
                    img2modify.putpixel((x, y), self.retournecouleurset(color_pantalon, 'tres sombre'))
                elif coul == (71, 102, 143):
                    img2modify.putpixel((x, y), self.retournecouleurset(color_pantalon, 'sombre'))
                elif coul == (130, 173, 212):
                    img2modify.putpixel((x, y), self.retournecouleurset(color_pantalon, 'clair'))
                #peau
                elif coul == (135, 88, 68):
                    img2modify.putpixel((x, y), self.retournecouleurset(color_peau, 'tres sombre'))
                elif coul == (196, 159, 165):
                    img2modify.putpixel((x, y), self.retournecouleurset(color_peau, 'sombre'))
                elif coul == (212, 153, 122):
                    img2modify.putpixel((x, y), self.retournecouleurset(color_peau, 'medium'))
                elif coul == (255, 207, 176):
                    img2modify.putpixel((x, y), self.retournecouleurset(color_peau, 'clair'))
                elif coul == (255, 232, 204):
                    img2modify.putpixel((x, y), self.retournecouleurset(color_peau, 'tres clair'))

        img2modify.save('.\current\pj_type.png')

    def retournecouleurset(self, selection, teinte):
        colorset = {
            "rouge": {
                "tres clair": (255, 0, 0),
                "clair": (202, 0, 0),
                "medium": (121, 0, 0),
                "sombre": (160, 0, 0),
                "tres sombre": (128, 0, 0)},
            "rouge sombre": {
                "tres clair": (191, 0, 0),
                "clair": (138, 0, 0),
                "medium": (117, 0, 0),
                "sombre": (96, 0, 0),
                "tres sombre": (64, 0, 0)},
            "bleu": {
                "tres clair": (0, 0, 255),
                "clair": (0, 0, 202),
                "medium": (0, 0, 121),
                "sombre": (0, 0, 160),
                "tres sombre": (0, 0, 128)},
            "bleu sombre": {
                "tres clair": (0, 0, 191),
                "clair": (0, 0, 138),
                "medium": (0, 0, 117),
                "sombre": (0, 0, 96),
                "tres sombre": (0, 0, 64)},
            "vert": {
                "tres clair": (0, 255, 0),
                "clair": (0, 202, 0),
                "medium": (0, 121, 0),
                "sombre": (0, 160, 0),
                "tres sombre": (0, 128, 0)},
            "vert sombre": {
                "tres clair": (0, 191, 0),
                "clair": (0, 138, 0),
                "medium": (0, 117, 0),
                "sombre": (0, 96, 0),
                "tres sombre": (0, 64, 0)},
            "black": {
                "tres clair": (96, 96, 96),
                "clair": (64, 64, 64),
                "medium": (48, 48, 48),
                "sombre": (32, 32, 32),
                "tres sombre": (1, 1, 1)},

            "rose": {
                "tres clair": (255, 232, 204),
                "clair": (255, 207, 176),
                "medium": (212, 153, 122),
                "sombre": (196, 159, 165),
                "tres sombre": (135, 88, 68)},
        }
        return colorset[selection][teinte]

    def drawme(self, surface):

        self.cadre_couleur.drawme(surface)
        surface.blit(self.label_couleur, (100, 8))
        surface.blit(self.label_chev, (8, 8 + 24))
        surface.blit(self.label_yeux, (8, 8 + 48))
        surface.blit(self.label_peau, (8, 8 + 72))
        surface.blit(self.label_chemise, (8, 8 + 96))
        surface.blit(self.label_pantalon, (8, 8 + 120))

        if self.modifcoul:
            imgsource = './images/pj/pj_type.png'
            img2modify = PIL.Image.open(imgsource).convert('RGB')
            self.update_image(img2modify)
            self.sprite_sheet = pygame.image.load('.\current\pj_type.png').convert_alpha()
            self.modifcoul = False

        image = self.sprite_sheet.subsurface((32, 0, 32, 32))
        image = pygame.transform.scale(image, (128, 128))
        surface.blit(image, (150, 8+30))

        self.cadre_carac.drawme(surface)
        surface.blit(self.label_carac, (8 + 320 + 75, 8))

        x, y = 8 + 320, 8 + 24
        i = 0
        for carac in self.liste_carac:
            if self.cadre_selector == 1 and self.ligne_selector == i:
                ligne = True
            else:
                ligne = False
            carac.drawme(surface, (x,y), ligne)
            y += 24

        self.cadre_atout.drawme(surface)
        self.cadre_at1.drawme(surface)

        if self.cadre_selector == 0:
            pygame.draw.line(surface, JAUNE, (8, 8 + (2 + self.ligne_selector) * 24),
                             (100, 8 + (2 + self.ligne_selector) * 24), 2)
        theligne = True if self.cadre_selector == 2 else False
        self.firstatout.drawme(surface, (8, 8+200), theligne)

    def recup_pj(self):
        self.carindex=[]

        for carac in self.liste_carac:
            self.carindex.append(carac.total)

        return {'nom': 'Bob',
                     'source_img': '.\current\pj_type.png',
                     'caracs': self.carindex}


class ChoixDoubleEntree:
    def __init__(self, dictionnaire, font):
        self.dictionnaire = dictionnaire

        self.font = font

        self.list_choix_1 = ['choisir']
        for choix in self.dictionnaire:
            self.list_choix_1.append(choix)
        self.longueur_choix_1 = len(self.list_choix_1)
        self.index_liste_1 = 0

        self.list_choix_2 = ['choisir']
        self.longueur_choix_2 = len(self.list_choix_2)
        self.index_liste_2 = 0

        self.contenu = 'Merci de choisir un atout'
        self.indexselector = 0

    def refresh_list2(self):
        self.list_choix_2 = ['choisir']
        if self.index_liste_1 != 0:
            for choix in self.dictionnaire[self.list_choix_1[self.index_liste_1]]:
                self.list_choix_2.append(choix)
        self.longueur_choix_2 = len(self.list_choix_2)
        self.index_liste_2 = 0

    def eventreaction(self, event):
        modifliste2 = False
        if event.key == pygame.K_RETURN:
            self.indexselector += 1
            if self.indexselector > 1:
                self.indexselector = 0

        elif self.indexselector == 0:
            if event.key == pygame.K_LEFT:
                self.index_liste_1 -= 1
                if self.index_liste_1 < 1:
                    self.index_liste_1 = self.longueur_choix_1 - 1
                modifliste2 = True
            elif event.key == pygame.K_RIGHT:
                self.index_liste_1 += 1

                if self.index_liste_1 > self.longueur_choix_1 - 1:
                    self.index_liste_1 = 1
                modifliste2 = True

            if modifliste2:
                self.refresh_list2()

        elif self.indexselector == 1:
            if event.key == pygame.K_LEFT:
                self.index_liste_2 -= 1
                if self.index_liste_2 < 0:
                    self.index_liste_2 = self.longueur_choix_2 - 1
            elif event.key == pygame.K_RIGHT:
                self.index_liste_2 += 1
                if self.index_liste_2 > self.longueur_choix_2 - 1:
                    self.index_liste_2 = 0

    def drawme(self, surface, position, ligne):
        x, y = position
        text = '< ' + self.list_choix_1[self.index_liste_1] + ' >'
        val1 = self.font.render(text, True, JAUNE)
        surface.blit(val1, (x, y))

        x2 = x + val1.get_width() + 10

        text = '< ' + self.list_choix_2[self.index_liste_2] + ' >'
        val2 = self.font.render(text, True, JAUNE)
        surface.blit(val2, (x2, y))

        if ligne:
            y2 = y+30
            if self.indexselector == 0:
                pygame.draw.line(surface, JAUNE, (x, y2), (x2 - 10, y2), 2)
            else:
                pygame.draw.line(surface, JAUNE, (x2, y2), (x2 + val2.get_width(), y2), 2)

    def __str__(self):
        if self.index_liste_1 == 0:

            return 'choisir choisir Merci de choisir un atout'
        else:
            if self.index_liste_2 == 0:
                return self.list_choix_1[self.index_liste_1] + ' ' + 'choisir' + ' ' + 'Merci de choisir un atout'
            else:
                return self.list_choix_1[self.index_liste_1] + ' ' + self.list_choix_2[self.index_liste_2] + ' ' + \
                       self.dictionnaire[self.list_choix_1[self.index_liste_1]][self.list_choix_2[self.index_liste_2]]


class ModificateurCarac:
    def __init__(self, nom, font, pointinvestit=0, modificateur=0, base=0):
        self.nom = nom
        self.font = font

        self._pointinvestit = pointinvestit
        self._modificateur = modificateur
        self._base = base

        self._total = self._base + self._modificateur + self._pointinvestit

    def eventreaction(self, event):

        if event.key == pygame.K_RIGHT:
            self._pointinvestit += 1
        elif event.key == pygame.K_LEFT:
            self._pointinvestit -= 1

        self._pointinvestit = 0 if self._pointinvestit < 0 else self._pointinvestit
        self._pointinvestit = 5 if self._pointinvestit > 5 else self._pointinvestit
        self.actustat()

    def actustat(self):
        self._total = self._base + self._modificateur+self._pointinvestit


    @property
    def base(self):
        return self._base

    @base.setter
    def base(self, newval):
        self._base = newval
        self.actustat()

    @property
    def modificateur(self):
        return self._modificateur

    @modificateur.setter
    def modificateur(self, newval):
        self._modificateur = newval
        self.actustat()

    @property
    def total(self):
        return self._total

    def drawme(self, surface, position, ligne):

        x,y = position
        text = '< '+self.nom + ' > : '+ str(self._base) + ' + '+str(self._modificateur)+' + ' +str(self._pointinvestit)+\
               ' = '+ str(self._total)

        thetext = self.font.render(text, True, JAUNE)
        surface.blit(thetext, position)

        if ligne:
            x2 = x + thetext.get_width()
            y2 = y + 30
            pygame.draw.line(surface, JAUNE, (x, y2), (x2, y2), 2)


if __name__ == '__main__':
    pygame.init()
    taille_fenetre = (640, 640)
    screen_surface = pygame.display.set_mode(taille_fenetre)

    hero = game.Hero('Bob', [1, 1], './images/pj/pj.png')
    meuchant = game.Mechant('Vil1', [3, 3], './images/pnj/spider.png')

    font_par_def = pygame.font.SysFont('Comic sans MS', 20)

    menusimple = Menu('simple', [100, 100, 250, 200])
    interface = InterfaceCombat(font_par_def, [hero], [meuchant])

    continuer = True
    mode = ''
    menu_encours = None
    while continuer:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                continuer = False
            elif event.type == pygame.KEYUP:

                if event.key == pygame.K_z:
                    mode = 'menu'
                    menu_encours = interface
                    break
                elif event.key == pygame.K_SPACE:
                    mode = ''
                    break
                else:
                    if mode == 'menu':
                        menu_encours.gocurseur(event)

        screen_surface.fill((5, 5, 30))
        if mode == 'menu':
            menu_encours.drawme(screen_surface)

        pygame.display.flip()
        # fin affichage ------------------------

    pygame.quit()
