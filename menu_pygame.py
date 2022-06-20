import pygame
import main_pygame


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

        self.height = 16 + self.dimension[1] * 24
        self.width = 16 + self.dimension[0] * 24
        self.refx = 160
        self.refy = 100

    def drawme(self, surface):

        rect_fond = pygame.Rect(pygame.Rect(self.refx, self.refy, self.width, self.height))
        pygame.draw.rect(surface, self.color_fond, rect_fond)
        surface.blit(self.image_coin_haut_gauche, (self.refx, self.refy))
        surface.blit(self.image_coin_haut_droit, (self.refx+self.width-8, self.refy))
        surface.blit(self.image_coin_bas_droit, (self.refx + self.width - 8, self.refy+self.height-8))
        surface.blit(self.image_coin_bas_gauche, (self.refx, self.refy + self.height - 8))

        self.image_bar_h = pygame.transform.scale(self.image_bar_h, (self.width-16, 8))
        surface.blit(self.image_bar_h, (self.refx+8, self.refy))

        self.image_bar_b = pygame.transform.scale(self.image_bar_b, (self.width-16, 8))
        surface.blit(self.image_bar_b, (self.refx + 8, self.refy + self.height - 8))

        self.image_bar_g = pygame.transform.scale(self.image_bar_g, (8, self.height-16))
        surface.blit(self.image_bar_g, (self.refx, self.refy + 8))

        self.image_bar_d = pygame.transform.scale(self.image_bar_d, (8, self.height - 16))
        surface.blit(self.image_bar_d, (self.refx+self.width-8, self.refy + 8))

    def gocurseur(self, direction):
        pass


class MenuSelect(Menu):
    """ Menu qui créer une liste vertical avec un curseur de selection"""
    def __init__(self, nom, dimension, dico_choix, font):

        super().__init__(nom, dimension)

        self.image_curseur = pygame.image.load("./images/fleche.png").convert_alpha()
        self.poscursor = [0, 0]

        self.dico_choix = dico_choix

        self.liste_choix = []
        for key in self.dico_choix:
            self.liste_choix.append(key)

        self.font = font

        self.dict_label = {}

        for element in self.liste_choix:
            self.dict_label[element] = self.font.render(element, True, JAUNE)

        self.calcul_dimension()

    def calcul_dimension(self):
        maxw = 0
        i = 0
        for _ in self.liste_choix:
            maxw = len(self.liste_choix[i]) if len(self.liste_choix[i]) > maxw else maxw
            i += 1

        self.width = 16 + maxw * 24
        self.height = 16 + len(self.liste_choix)*24

    def gocurseur(self, direction):
        x, y = self.poscursor

        if direction.key == pygame.K_LEFT:
            x -= 1
        elif direction.key == pygame.K_RIGHT:
            x += 1
        elif direction.key == pygame.K_UP:
            y -= 1
        elif direction.key == pygame.K_DOWN:
            y += 1

        x = 0 if x > self.dimension[0] - 1 else x
        x = self.dimension[0] - 1 if x < 0 else x
        y = 0 if y > self.dimension[1] - 1 else y
        y = self.dimension[1] - 1 if y < 0 else y

        self.poscursor = (x, y)

    def drawme(self, surface):
        super().drawme(surface)

        surface.blit(self.image_curseur, (self.refx+16+(self.poscursor[0]*24), self.refy+(self.poscursor[1]*24)))
        i = 0
        for element in self.liste_choix:
            surface.blit(self.dict_label[element], (self.refx + 48, self.refy + (i * 24)))
            i += 1

    def select_action(self, apj, amechant):
        self.attaquer(apj, amechant)

    def attaquer(self, apj, amechant):
        apj.attaquer_cible(amechant)


class InterfaceCombat:
    """ ensemble de menu qui dessine l'interface de combat"""
    def __init__(self, font, liste_hero):
        self.font = font
        self.liste_hero = liste_hero
        self.color_fond = (30, 5, 5)
        self.partiehaute = Menu('Haute', [20, 12])
        self.dico_action = self.liste_hero[0].dico_action
        self.partiebasse1 = MenuSelect('selecteur', [7, len(self.dico_action)], self.dico_action,
                                       self.font)
        self.partiebasse2 = Menu('global', [13, 5])
        self.piedpage = Menu('pied', [20, 1])
        self.liste_hero = []
        self.liste_npc = []
        self.pos_curseur = [0, 0]
        self.fen_encours = self.partiebasse1

    def drawme(self, surface):

        self.partiehaute.refx = 0
        self.partiehaute.refy = 0
        self.partiehaute.drawme(surface)
        self.partiebasse1.refx = 0
        self.partiebasse1.refy = 302
        self.partiebasse1.drawme(surface)
        self.partiebasse2.refx = 160
        self.partiebasse2.refy = 302
        self.partiebasse2.drawme(surface)
        self.piedpage.refx = 0
        self.piedpage.refy = 437
        self.piedpage.drawme(surface)

    def gocurseur(self, event):

        if event.key in [pygame.K_UP, pygame.K_DOWN]:
            self.fen_encours.gocurseur(event)
        elif event.key in [pygame.K_LEFT, pygame.K_RIGHT]:
            pass

        pass

    def initialisecombat(self, liste_hero, liste_npc):
        self.liste_hero = liste_hero
        self.liste_npc = liste_npc


if __name__ == '__main__':

    pygame.init()
    taille_fenetre = (640, 640)
    screen_surface = pygame.display.set_mode(taille_fenetre)

    hero = main_pygame.Hero('Bob', (1, 1), './images/pj/pj.png')

    font_par_def = pygame.font.SysFont('Comic sans MS', 24)

    menusimple = Menu('simple', [10, 10])
    interface = InterfaceCombat(font_par_def,[hero])

    continuer = True
    mode = ''
    menu_encours = None
    while continuer:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                continuer = False
            elif event.type == pygame.KEYUP:

                if event.key in [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT]:
                    if mode == 'menu':
                        menu_encours.gocurseur(event)

                elif event.key == pygame.K_a:
                    mode = 'menu'
                    menu_encours = menusimple
                    break
                elif event.key == pygame.K_z:
                    mode = 'menu'
                    menu_encours = interface
                    break
                elif event.key == pygame.K_SPACE:
                    mode = ''
                    break

        screen_surface.fill((5, 5, 30))
        if mode == 'menu':
            menu_encours.drawme(screen_surface)

        pygame.display.flip()
        # fin affichage ------------------------

    pygame.quit()
