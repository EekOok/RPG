import pygame
import Tools
import mechanics
import menu_pygame

import random

# ------------------------------------------------------------------
# pour calcul des trajectoire NPC
# ------------------------------------------------------------------

from pathfinding.core.diagonal_movement import DiagonalMovement
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder

# ---------------------------------------------------------------------
# Constantes
# ---------------------------------------------------------------------

BLANC = (255, 255, 255)
NOIR = (0, 0, 0)
BLEU_NUIT = (5, 5, 30)
ROUGE = (255, 0, 0)
VERT = (0, 255, 0)
BLEU = (0, 0, 255)
JAUNE = (255, 216, 0)
ORANGE = (255, 106, 0)


# ---------------------------------------------------------------------


class Personnage:
    """ Class impactants la representation du personnage dans pygame et son déplacement"""
    def __init__(self, nom, position, image):
        self.nom = nom
        self.position_map = position
        self.image = pygame.image.load(image).convert_alpha()

    def godirection(self, direction, unemap):
        x = self.position_map[0]
        y = self.position_map[1]
        if x > 0 and direction == pygame.K_LEFT:
            x -= 1
        elif x < 24 and direction == pygame.K_RIGHT:
            x += 1
        elif y > 0 and direction == pygame.K_UP:
            y -= 1
        elif y < 24 and direction == pygame.K_DOWN:
            y += 1
        if unemap.get_tile([x, y]) == 0:
            self.position_map = [x, y]

    def drawme(self, surface, ref_map=(0, 0)):

        surface.blit(self.image, ((self.position_map[0] - ref_map[0]) * 32, (self.position_map[1] - ref_map[1]) * 32))


class Map:
    """Gestion de la carte, chargement du fichier json, création du tableau, dessin du tableau """
    def __init__(self, fichiermap, ref_init, sol, mur):
        self.dict_map = Tools.readthedict(fichiermap)
        self.ref_init = ref_init
        self.ref_global = self.ref_init
        self.sol = pygame.image.load(sol).convert_alpha()
        self.mur = pygame.image.load(mur).convert_alpha()
        self.list_map = []
        for element in self.dict_map['map_move']:
            self.list_map.append(self.dict_map['map_move'][element])
        self.grid = Grid(matrix=self.list_map, inverse=True)

    def map_plus_item(self, item_chercheur):
        self.list_map = []
        for element in self.dict_map['map_move']:
            self.list_map.append(self.dict_map['map_move'][element])

        for item in Mechant.liste_mechant:
            if item != item_chercheur:
                self.list_map[item.position_map[1]][item.position_map[0]] = 1
        for pj in Hero.liste_hero:
            if pj != item_chercheur:
                self.list_map[pj.position_map[1]][pj.position_map[0]] = 1

    def get_tile(self, position):
        return self.list_map[position[1]][position[0]]

    def calcul_ref_global(self, pj):
        x_global = self.ref_global[0]
        y_global = self.ref_global[1]

        if pj.position_map[0] < 5:
            x_global = 0
        elif pj.position_map[0] > 19:
            x_global = 5
        else:
            if pj.position_map[0] - self.ref_global[0] < 5:
                x_global = pj.position_map[0] - 5
            elif pj.position_map[0] - self.ref_global[0] > 14:
                x_global = pj.position_map[0] - 14
        if pj.position_map[1] < 5:
            y_global = 0
        elif pj.position_map[1] > 19:
            y_global = 5
        else:
            if pj.position_map[1] - self.ref_global[1] < 5:
                y_global = pj.position_map[1] - 5
            elif pj.position_map[1] - self.ref_global[1] > 14:
                y_global = pj.position_map[1] - 14
        self.ref_global = (x_global, y_global)

    def drawme(self, surface, pj):
        self.calcul_ref_global(pj)
        y = 0
        for element in self.dict_map["map_image"]:
            if int(element) < self.ref_global[1]:
                pass
            elif int(element) > self.ref_global[1] + 19:
                pass
            else:
                posx = 0
                x = 0
                for _ in self.dict_map["map_image"][element]:
                    if posx < self.ref_global[0]:
                        pass
                    elif posx > self.ref_global[0] + 19:
                        pass
                    else:
                        if self.dict_map["map_image"][element][posx] == 1:
                            surface.blit(self.mur, (x * 32, y * 32))
                        else:
                            surface.blit(self.sol, (x * 32, y * 32))
                        x += 1
                    posx += 1
                y += 1


# ---------------------------------------------------------------------


class Hero(Personnage, mechanics.Joueur):
    """Fusion de la class Personnage et mechanics.Joueur,
    Gestion de la liste_hero"""

    liste_hero = []
    Next_id = 0

    def __init__(self, nom, position, image, force=5, dexterite=4, constitution=3, intelligence=2,
                 sagesse=1, charisme=0):
        Personnage.__init__(self, nom, position, image)
        mechanics.Joueur.__init__(self, nom, force, dexterite, constitution, intelligence, sagesse, charisme)
        self.id = Hero.Next_id
        Hero.Next_id += 1
        Hero.liste_hero.append(self)


class Mechant(Personnage, mechanics.Pnj):
    """Fusion de la class Personnage et mechanics.Pnj,
    Gestion de la liste_mechant"""

    liste_mechant = []
    next_id = 0

    def __init__(self, nom, position, image, speed=2, ia=('FieldKeeper',), perception=2, mere=None):
        Personnage.__init__(self, nom, position, image)
        mechanics.Pnj.__init__(self, nom, perception)
        self.id = Mechant.next_id
        Mechant.next_id += 1
        Mechant.liste_mechant.append(self)

        self.ia = ia
        self.perception = perception
        self.position_origine = position
        self.speed = speed
        self.nbpas = 0
        self.trouve = False
        self.mere = mere
        self.filles = []
        self.gestation = 0
        self.filles2kill = []

    def seek_direction(self, amap, pj):
        """selection du 'moteur de recherche' en fonction de l'IA"""
        self.nbpas += 1
        if 'FieldKeeper' in self.ia:
            self.field_keeper(amap, pj)
        elif 'Hunter' in self.ia:
            self.hunter(amap, pj)
        elif self.ia == 'Gardian':
            pass
        if 'Mother' in self.ia:
            self.mother(amap)
        if 'Oeuf' in self.ia:
            self.oeuf(amap)

    def field_keeper(self, amap, pj):
        """le pnj va poursuivre et, s'il perd le pj de vue, retourne a son point de départ"""
        if (self.nbpas % self.speed) == 0:
            amap.grid.cleanup()
            start = amap.grid.node(self.position_map[0], self.position_map[1])
            end = amap.grid.node(pj.position_map[0], pj.position_map[1])

            finder = AStarFinder(diagonal_movement=DiagonalMovement.never)
            path, runs = finder.find_path(start, end, amap.grid)
            if 1 < len(path) < 6 + self.perception:
                if self.cherche_pj(pj):
                    self.trouve = True
            else:
                self.trouve = False
            if 1 < len(path) < 6 + self.perception and self.trouve:
                x_origine = path[0][0]
                y_origine = path[0][1]
                x_destin = path[1][0]
                y_destin = path[1][1]
                if x_destin > x_origine:
                    direction = pygame.K_RIGHT
                elif x_destin < x_origine:
                    direction = pygame.K_LEFT
                elif y_destin > y_origine:
                    direction = pygame.K_DOWN
                elif y_destin < y_origine:
                    direction = pygame.K_UP
                else:
                    direction = 0
                self.godirection(direction, amap)

            else:
                amap.grid.cleanup()
                start = amap.grid.node(self.position_map[0], self.position_map[1])
                end = amap.grid.node(self.position_origine[0], self.position_origine[1])

                finder = AStarFinder(diagonal_movement=DiagonalMovement.never)
                path, runs = finder.find_path(start, end, amap.grid)
                if 1 < len(path):
                    x_origine = path[0][0]
                    y_origine = path[0][1]
                    x_destin = path[1][0]
                    y_destin = path[1][1]

                    if x_destin > x_origine:
                        direction = pygame.K_RIGHT
                    elif x_destin < x_origine:
                        direction = pygame.K_LEFT
                    elif y_destin > y_origine:
                        direction = pygame.K_DOWN
                    elif y_destin < y_origine:
                        direction = pygame.K_UP
                    else:
                        direction = 0
                    self.godirection(direction, amap)

    def hunter(self, amap, pj):
        """Le Pnj Va poursuivre le pj et s'arreter s'il le perd de vue"""
        if self.nbpas % self.speed == 0:
            amap.grid.cleanup()
            start = amap.grid.node(self.position_map[0], self.position_map[1])
            end = amap.grid.node(pj.position_map[0], pj.position_map[1])

            finder = AStarFinder(diagonal_movement=DiagonalMovement.never)
            path, runs = finder.find_path(start, end, amap.grid)
            if 1 < len(path) < 10 + self.perception:
                if self.cherche_pj(pj):
                    self.trouve = True
            else:
                self.trouve = False
            if 1 < len(path) < 10 + self.perception and self.trouve:
                x_origine = path[0][0]
                y_origine = path[0][1]
                x_destin = path[1][0]
                y_destin = path[1][1]
                if x_destin > x_origine:
                    direction = pygame.K_RIGHT
                elif x_destin < x_origine:
                    direction = pygame.K_LEFT
                elif y_destin > y_origine:
                    direction = pygame.K_DOWN
                elif y_destin < y_origine:
                    direction = pygame.K_UP
                else:
                    direction = 0
                self.godirection(direction, amap)

    def mother(self, amap):
        """Tous les x pas va générer un Oeuf"""
        if self.nbpas % 10 == 0 and not self.trouve:
            choix_possible = []
            nord = (self.position_map[0], self.position_map[1] - 1)
            sud = (self.position_map[0], self.position_map[1] + 1)
            est = (self.position_map[0] + 1, self.position_map[1])
            ouest = (self.position_map[0] - 1, self.position_map[1])
            for direction in [nord, sud, est, ouest]:
                if amap.get_tile(direction) == 0:
                    choix_possible.append(direction)
            random.shuffle(choix_possible)
            if len(choix_possible) > 0 and len(self.filles) < 3:
                self.filles.append(Mechant('Oeuf', choix_possible[0], 'spideregg.png', ia=('Gardian', 'Oeuf'),
                                           mere=self))

    def oeuf(self, amap):
        """Attend un certain de nombre de pas avant d'éclore"""
        self.gestation += 1
        if self.gestation >= 10:
            self.mere.filles2kill.append(self)
            self.mere.filles.append(Mechant('spider', self.position_map, 'spider.png', ia=('Hunter',), mere=self.mere))
            Mechant.liste_mechant.remove(self)
            self.mere.filles.remove(self)

    def kill_oeuf(self, aoeuf):
        pass


# ---------------------------------------------------------------------

if __name__ == '__main__':
    pygame.init()

    taille_fenetre = (640, 640)
    screen_surface = pygame.display.set_mode(taille_fenetre)

    font_par_def = pygame.font.SysFont('Comic sans MS', 24)

    monmenu = menu_pygame.MenuSelect('First Menu', [1, 4], ['Sauvegarder', 'Personnage', 'Inventaire', 'Quitter(x)'],
                                     font_par_def)

    mamap = Map('./Map/map0.json', [0, 0], "sol.png", "mur.png")

    for npc in mamap.dict_map["npc"]:
        pos = mamap.dict_map["npc"][npc]["pos"]
        datas = mamap.dict_map["npc"][npc]["datas"]
        info = Tools.readthedict(datas[0])
        source = datas[0]
        ref = datas[1]
        infonpc = Tools.readthedict(source)[ref]
        Mechant(npc, pos, infonpc["image"], ia=infonpc["ia"], mere=infonpc["fille"])

    monhero = Hero('Bob', (1, 1), './images/pj/pj.png')

    interface_combat = menu_pygame.InterfaceCombat('fight', [monhero, ])

    continuer = True
    mode = 'On Map'
    menu_encours = None
    while continuer:

        already_move = False
        # -------------------------------------------------------
        # Gestion Evenement -------------------------------------
        # -------------------------------------------------------

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                continuer = False

            elif event.type == pygame.KEYUP:
                if mode == 'On Map' and not already_move:
                    if event.key in [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT]:
                        monhero.godirection(event.key, mamap)
                        already_move = True
                        break
                    elif event.key == pygame.K_m:
                        mode = 'Menu'
                        menu_encours = monmenu
                        break

                elif mode == 'Menu':
                    if event.key == pygame.K_x:
                        mode = 'On Map'
                        break
                    elif event.key in [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT]:
                        monmenu.gocurseur(event.key)
                        break
                    elif event.key == pygame.K_RETURN:
                        if monmenu.poscursor == (0, 3):
                            mode = 'On Map'

                elif mode == 'Battle':
                    if event.key in [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_RETURN]:
                        interface_combat.gocurseur(event.key)

        # -------------------------------------------------------
        # moteur ------------------------------------------------
        # -------------------------------------------------------

        if mode == 'On Map' and already_move:
            for npc in Mechant.liste_mechant:
                mamap.map_plus_item(npc)
                npc.seek_direction(mamap, monhero)

        # -------------------------------------------------------
        # Gestion Evenement -------------------------------------
        # -------------------------------------------------------

        # fin moteur ---------------------------

        # affichage ----------------------------

        screen_surface.fill(BLEU_NUIT)
        # screen_surface.blit(text_surface, text_rect)
        mamap.drawme(screen_surface, monhero)

        for enemi in Mechant.liste_mechant:
            enemi.drawme(screen_surface, mamap.ref_global)

        monhero.drawme(screen_surface, mamap.ref_global)

        if mode == 'Menu':
            monmenu.drawme(screen_surface)

        pygame.display.flip()
        # fin affichage ------------------------

    pygame.quit()
