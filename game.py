import pygame
import Tools

import menu_pygame
import mechanics

import random


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


def estcecotecote(item1, item2):
    cote = False
    if ((-2 < item1.position_map[0] - item2.position_map[0] < 2) and (
            item1.position_map[1] == item2.position_map[1])) or \
            ((-2 < item1.position_map[1] - item2.position_map[1] < 2) and (
                    item1.position_map[0] == item2.position_map[0])):
        cote = True
    return cote


class Personnage:
    """ Class impactants la representation du personnage dans pygame et son déplacement"""

    def __init__(self, nom, position, image):
        self.nom = nom
        self.position_map = position
        self.sprite_sheet = pygame.image.load(image).convert_alpha()
        self.image = self.sprite_sheet.subsurface((0, 0, 32, 32))
        self.direction = 'down'
        self.enmouvement = False
        self.position_reel = [self.position_map[0]*32, self.position_map[1]*32]
        self.nbpas = 0

    def godirection(self, direction, unemap):
        if not self.enmouvement and direction is not None:

            x = self.position_map[0]
            y = self.position_map[1]
            if x > 0 and direction == pygame.K_LEFT:
                x -= 1
                self.direction = 'left'
            elif x < 24 and direction == pygame.K_RIGHT:
                x += 1
                self.direction = 'right'
            elif y > 0 and direction == pygame.K_UP:
                y -= 1
                self.direction = 'up'
            elif y < 24 and direction == pygame.K_DOWN:
                y += 1
                self.direction = 'down'

            self.refreshdirection()

            if unemap.get_tile([x, y]) == 0:
                self.position_map = [x, y]
            self.enmouvement = True

        else:
            if (self.direction == 'left') and self.position_reel[0] >= self.position_map[0]*32:
                self.position_reel[0] -= 2
                if self.position_reel[0] <= self.position_map[0]*32:
                    self.position_reel[0] = self.position_map[0]*32
                    self.enmouvement = False
            elif (self.direction == 'right') and self.position_reel[0] <= self.position_map[0]*32:
                self.position_reel[0] += 2
                if self.position_reel[0] >= self.position_map[0]*32:
                    self.position_reel[0] = self.position_map[0]*32
                    self.enmouvement = False
            elif (self.direction == 'up') and self.position_reel[1] >= self.position_map[1]*32:
                self.position_reel[1] -= 2
                if self.position_reel[1] <= self.position_map[1]*32:
                    self.position_reel[1] = self.position_map[1]*32
                    self.enmouvement = False
            elif (self.direction == 'down') and self.position_reel[1] <= self.position_map[1]*32:
                self.position_reel[1] += 2
                if self.position_reel[1] >= self.position_map[1]*32:
                    self.position_reel[1] = self.position_map[1]*32
                    self.enmouvement = False

    def drawme(self, surface, ref_map=[0, 0]):
        # surface.blit(self.image, ((self.position_map[0] - ref_map[0]) * 32, (self.position_map[1] - ref_map[1]) * 32))
        surface.blit(self.image, ((self.position_reel[0] - ref_map[0] * 32), (self.position_reel[1] - ref_map[1] * 32)))

    def refreshdirection(self):
        if self.direction == 'down':
            self.image = self.sprite_sheet.subsurface((0, 0, 32, 32))
        elif self.direction == 'up':
            self.image = self.sprite_sheet.subsurface((0, 3*32, 32, 32))
        elif self.direction == 'left':
            self.image = self.sprite_sheet.subsurface((0, 32, 32, 32))
        elif self.direction == 'right':
            self.image = self.sprite_sheet.subsurface((0, 2*32, 32, 32))


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

        self.index_image = 0
        self.liste_godown = []
        self.liste_godown.append(self.sprite_sheet.subsurface((0, 0, 32, 32)))
        self.liste_godown.append(self.sprite_sheet.subsurface((32, 0, 32, 32)))
        self.liste_godown.append(self.sprite_sheet.subsurface((64, 0, 32, 32)))

        self.liste_goright = []
        self.liste_goright.append(self.sprite_sheet.subsurface((0, 64, 32, 32)))
        self.liste_goright.append(self.sprite_sheet.subsurface((32, 64, 32, 32)))
        self.liste_goright.append(self.sprite_sheet.subsurface((64, 64, 32, 32)))

        self.liste_goleft = []
        self.liste_goleft.append(self.sprite_sheet.subsurface((0, 32, 32, 32)))
        self.liste_goleft.append(self.sprite_sheet.subsurface((32, 32, 32, 32)))
        self.liste_goleft.append(self.sprite_sheet.subsurface((64, 32, 32, 32)))

        self.liste_goup = []
        self.liste_goup.append(self.sprite_sheet.subsurface((0, 96, 32, 32)))
        self.liste_goup.append(self.sprite_sheet.subsurface((32, 96, 32, 32)))
        self.liste_goup.append(self.sprite_sheet.subsurface((64, 96, 32, 32)))

    def drawme(self, surface, ref_map=[0, 0]):
        if self.direction == 'down':
            self.image = self.liste_godown[self.index_image]
        elif self.direction == 'up':
            self.image = self.liste_goup[self.index_image]
        elif self.direction == 'left':
            self.image = self.liste_goleft[self.index_image]
        elif self.direction == 'right':
            self.image = self.liste_goright[self.index_image]
        if self.enmouvement:
            self.index_image += 1
            if self.index_image >= 3:
                self.index_image = 0

        super().drawme(surface, ref_map)


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
        """le pnj va poursuivre et, s'il perd le pj de vue, retourne à son point de départ"""
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
                self.filles.append(
                    Mechant('Oeuf', choix_possible[0], './images/pnj/spideregg.png', ia=('Gardian', 'Oeuf'),
                            mere=self))

    def oeuf(self, amap):
        """Attend un certain de nombre de pas avant d'éclore"""
        self.gestation += 1
        print(self.gestation)
        if self.gestation >= 10:
            self.mere.filles2kill.append(self)
            self.mere.filles.append(
                Mechant('spider', self.position_map, './images/pnj/spider.png', ia=('Hunter',), mere=self.mere))
            Mechant.liste_mechant.remove(self)
            self.mere.filles.remove(self)

    def kill_oeuf(self, aoeuf):
        pass


class Map:
    """Gestion de la carte, chargement du fichier json, création du tableau, dessin du tableau """

    def __init__(self, fichiermap, ref_init):
        self.fichier = fichiermap
        self.dict_map = Tools.readthedict(fichiermap)
        self.ref_init = ref_init
        self.ref_global = self.ref_init
        self.source_image = self.dict_map['source_image']
        image_sheet = pygame.image.load(self.source_image)
        self.liste_tile = {}
        for key in self.dict_map['detail_image']:
            dim = self.dict_map['detail_image'][key]
            self.liste_tile[key] = image_sheet.subsurface(dim)

        self.list_map = []
        self.dict_map = Tools.readthedict(fichiermap)
        for element in self.dict_map['map_move']:
            self.list_map.append(self.dict_map['map_move'][element].copy())
        self.grid = Grid(matrix=self.list_map, inverse=True)

    def map_plus_item(self):
        self.list_map = []
        for element in self.dict_map['map_move']:
            self.list_map.append(self.dict_map['map_move'][element].copy())
        for porte in SpritePorte.liste_porte:
            if porte.status == 'closed':
                self.list_map[porte.position_map[1]][porte.position_map[0]] = 1
        for mechant in Mechant.liste_mechant:
            self.list_map[mechant.position_map[1]][mechant.position_map[0]] = 1

        for pj in Hero.liste_hero:
            self.list_map[pj.position_map[1]][pj.position_map[0]] = 1

    def get_tile(self, position):
        self.map_plus_item()
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
                        tile = str(self.dict_map["map_image"][element][posx])
                        surface.blit(self.liste_tile[tile], (x * 32, y * 32))

                        x += 1
                    posx += 1
                y += 1

    def __str__(self):
        rep = ''
        for ligne in self.list_map:
            rep += f" {ligne}"


class SpritePorte(mechanics.Porte):
    liste_porte = []

    def __init__(self, nom, id, position, image, orientation='nord', status='closed',
                 crochetable=False, dif_crochetage=99):
        super().__init__(nom, id, status, crochetable, dif_crochetage)
        SpritePorte.liste_porte.append(self)
        self.position_map = position
        self.sprite_sheet = pygame.image.load(image).convert_alpha()
        if orientation == 'est':
            self.imageclosed = self.sprite_sheet.subsurface((0, 32, 32, 32))
        elif orientation == 'ouest':
            self.imageclosed = self.sprite_sheet.subsurface((32, 32, 32, 32))
        elif orientation == 'sud':
            self.imageclosed = self.sprite_sheet.subsurface((32, 0, 32, 32))
        else:
            self.imageclosed = self.sprite_sheet.subsurface((0, 0, 32, 32))
        self.imageopen = self.sprite_sheet.subsurface((64, 0, 32, 32))

    def drawme(self, surface, ref_map=[0, 0]):
        image = self.imageclosed if self.status == 'closed' else self.imageopen
        surface.blit(image, ((self.position_map[0] - ref_map[0]) * 32, (self.position_map[1] - ref_map[1]) * 32))


# ---------------------------------------------------------------------


class Game:
    def __init__(self, screen, lehero, lamap):

        self.screen_surface = screen
        self.monhero = lehero
        self.mamap = lamap

        self.font_par_def = pygame.font.SysFont('Comic sans MS', 20)
        self.interface_combat = None
        self.fenetre_win = menu_pygame.Menu('Win', (0, 160, 640, 320))
        self.memo_event = None
        self.pas = True
        self.ordre = False
        self.eventaction = None

        for npc in self.mamap.dict_map["npc"]:
            pos = self.mamap.dict_map["npc"][npc]["pos"]
            datas = self.mamap.dict_map["npc"][npc]["datas"]
            source = datas[0]
            ref = datas[1]
            infonpc = Tools.readthedict(source)[ref]
            Mechant(npc, pos, infonpc["image"], ia=infonpc["ia"], mere=infonpc["fille"])

        for item in self.mamap.dict_map["item"]:
            if item == "porte":
                for porte in self.mamap.dict_map["item"]["porte"]:
                    theporte = self.mamap.dict_map["item"]["porte"][porte]
                    SpritePorte(porte, theporte['id'], theporte['position'], theporte['image'], theporte['orientation'])

        self.mode = 'On Map'
        self.menu_encours = None
        self.already_move = False
        self.running = True

    def handling_events(self):

        # -------------------------------------------------------
        # Gestion Evenement -------------------------------------
        # -------------------------------------------------------

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYUP:
                if self.mode == 'On Map':
                    if event.key in [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_SPACE] and\
                            not self.ordre:
                        self.ordre = True
                        self.eventaction = event

                elif self.mode == 'Battle':
                    if event.key in [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_RETURN,
                                     pygame.K_ESCAPE]:
                        self.interface_combat.gocurseur(event)
                elif self.mode == 'Winner msg':
                    if event.key in [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_RETURN,
                                     pygame.K_ESCAPE]:
                        self.mode = 'On Map'

    def update(self):
        # -------------------------------------------------------
        # moteur ------------------------------------------------
        # -------------------------------------------------------

        if self.mode == 'On Map':
            if self.ordre:
                self.memo_event = self.eventaction
                self.pas = True
            if self.memo_event is not None:
                key = self.memo_event.key
            else:
                key = None

            self.monhero.godirection(key, self.mamap)
            if not self.monhero.enmouvement:
                self.memo_event = None
                self.pas = False

            for npc in Mechant.liste_mechant:
                if self.ordre:
                    npc.seek_direction(self.mamap, self.monhero)
                else:
                    npc.godirection(None, self.mamap)

                if estcecotecote(self.monhero, npc) and not npc.enmouvement:
                    self.mode = 'Battle'
                    self.interface_combat = menu_pygame.InterfaceCombat(self.font_par_def, [self.monhero], [npc])
            self.ordre = False

            # si toujours on map apres déplacement
            if self.mode == 'On Map':
                for porte in SpritePorte.liste_porte:
                    if estcecotecote(self.monhero, porte) and porte.condition_map and\
                            self.eventaction.key == pygame.K_SPACE:
                        porte.condition_pj = True
                    else:
                        porte.condition_pj = False

                    if estcecotecote(self.monhero, porte):
                        porte.condition_map = True
                    else:
                        porte.condition_map = False

                    porte.interact(self.monhero, self.mamap)

        elif self.mode == 'Battle':
            self.interface_combat.actionpnj()
            if self.interface_combat.touspnjmorts:
                for pnj in self.interface_combat.liste_pnj:
                    try:
                        Mechant.liste_mechant.remove(pnj)
                    except Exception as mes:
                        print(f'méchant perdu dans les limbes {mes}')

                self.mode = 'Winner msg'

        # fin moteur ---------------------------

    def display(self):
        # affichage -------------------------------------------------

        self.screen_surface.fill(BLEU_NUIT)
        # screen_surface.blit(text_surface, text_rect)
        self.mamap.drawme(self.screen_surface, self.monhero)

        for porte in SpritePorte.liste_porte:
            porte.drawme(self.screen_surface, self.mamap.ref_global)

        for enemi in Mechant.liste_mechant:
            enemi.drawme(self.screen_surface, self.mamap.ref_global)

        self.monhero.drawme(self.screen_surface, self.mamap.ref_global)

        if self.mode == 'Battle':
            self.interface_combat.drawme(self.screen_surface)

        elif self.mode == 'Winner msg':
            menu_pygame.MenuMsg('win', (0, 160, 640, 320), 'Gagné ! bientôt des pex !',
                                self.font_par_def).drawme(self.screen_surface)

        pygame.display.flip()
        # fin affichage ------------------------

    def run(self):
        while self.running:
            pygame.time.delay(15)
            self.handling_events()
            self.update()
            self.display()


class EtapeCreaPerso:
    def __init__(self, screen):
        self.screen_surface = screen
        self.font_par_def = pygame.font.SysFont('Comic sans MS', 20)
        self.running = True
        self.result = False

        self.perso = None

        self.cadre = menu_pygame.Creaperso(self.font_par_def)

    def handling_events(self):
        # -------------------------------------------------------
        # Gestion Evenement -------------------------------------
        # -------------------------------------------------------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYUP:
                if event.key in [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_RETURN]:
                    self.cadre.gocurseur(event)

    def update(self):
        pass
        # -------------------------------------------------------
        # moteur ------------------------------------------------
        # -------------------------------------------------------
        # fin moteur ---------------------------

    def display(self):
        # affichage ----------------------------

        self.screen_surface.fill(BLEU_NUIT)
        self.cadre.drawme(self.screen_surface)

        pygame.display.flip()
        # fin affichage ------------------------

    def run(self):
        while self.running:
            self.handling_events()
            self.update()
            self.display()
        stat = self.cadre.recup_pj()
        hero = Hero(stat['nom'], [1, 1], stat['source_img'], force=stat['caracs'][0], dexterite=stat['caracs'][1],
                    constitution=stat['caracs'][2], intelligence=stat['caracs'][3], sagesse=stat['caracs'][4],
                    charisme=stat['caracs'][5])
        return self.result, hero


if __name__ == "__main__":
    pygame.init()

    taille_fenetre = (640, 640)
    screen_surface = pygame.display.set_mode(taille_fenetre)

    etape1 = EtapeCreaPerso(screen_surface)
    result, perso = etape1.run()

    premieremap = Map('./Map/map0.json', [0, 0])

    dongeon = Game(screen_surface, perso, premieremap)
    dongeon.run()

    pygame.quit()
