#
# Auteurs : COTTO Erwan
# Date de création : 14 mars 2022
# Version : version minimale à rendre
# Nom du fichier : projet_space_invaders_COTTO_Erwan
# Professeur de TP : PLANTEC Alain
#
# -----------------------------------------------------------------------------
#
# jeu de type "SPACE INVADERS" :
# - flèche directionnelle droite : permet de déplacer le défenseur à droite
# - flèche directionnelle gauche : permet de déplacer le défenseur à gauche
# - touche espace : permet de tirer une balle
# - un maximum de 8 balles peuvent être présentes en même temps à l'écran
# - lorsqu'une balle entre en contact avec un alien, les deux sont effacés
# - lorsque le défenseur sort de l'écran à gauche, il ressort à droite
# - lorsque le défenseur sort de l'écran à droite, il ressort à gauche
# - la partie s'arrête lorsque tout les aliens ont été effacés ( condition de victoire ) ou que l'alien situé le plus en bas descend sous le défenseur ( condition de défaite )
#
# -----------------------------------------------------------------------------
#
# bug(s) :
#
# -----------------------------------------------------------------------------

try:  # import as appropriate for 2.x vs. 3.x
    import tkinter as tk
    import tkinter.messagebox as tkMessageBox
except:
    import Tkinter as tk
    import tkMessageBox

# classe faisant appel aux fonctions gérant le programme
class SpaceInvaders(object):

    # définition du canvas
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Space Invaders")
        self.frame = tk.Frame(self.root)
        self.frame.pack(side="top", fill="both")
        self.game = Game(self.frame)

    # appel des fonctions de jeu et liaison avec le clavier si nécessaire
    def play(self):
        self.game.start_animation()
        self.root.bind("<Key>", self.game.defender.move_in )
        self.root.bind("<Key>", self.game.defender.fire, add = "+" )
        self.root.mainloop()

# classe définissant l'état du jeu
class Game(object):

    # fonction mettant en place les éléments du jeu
    def __init__(self, frame):
        self.frame = frame
        self.fleet = Fleet()
        self.defender = Defender()
        self.jeu = True     # True = jeu en cours | False = jeu terminé
        self.win = False    # True = partie gagné | False = partie perdue
        self.height = 800
        self.width = 1400 
        self.canvas = tk.Canvas(self.frame, width = self.width, height = self.height, bg = 'black')
        self.defender.install_in(self.canvas)
        self.fleet.install_in(self.canvas)
        self.canvas.pack()

    # appel des fonctions d'affichages à un temps x des objets   
    def animation(self):
        if self.jeu :
            self.game_over() # test de fin de partie
            self.touche_alien()
            self.canvas.after(10, self.move_alien_s_fleet() )
            self.canvas.after(10, self.move_bullets() )
            self.canvas.after(10, self.animation )

    # permet de débuter le jeu    
    def start_animation(self):
        self.canvas.after(10, self.animation)

    # gère le déplacement des balles    
    def move_bullets(self):
        for i in self.defender.fired_bullets :
            if i.hauteur <= 0 or i.etat == 0 :   # si la balle est sortie de l'écran ou invisible
                self.defender.fired_bullets = self.defender.fired_bullets[1:]
                self.defender.recharge()
            else :
                i.move_in(self.canvas)

    # gère le déplacement des aliens    
    def move_alien_s_fleet(self):
        if self.jeu :
            self.fleet.move_alien()

    # si un alien rencontre une balle
    def touche_alien (self) :
        for m in self.fleet.aliens :
            for i in self.defender.fired_bullets :
                if m.etat == 1 and i.etat == 1 : # si l'alien et la balle sont visibles
                    x1, y1, x2, y2 = self.canvas.bbox(m.alien_id)
                    if len(m.canvas.find_overlapping(x1, y1, x2, y2)) > 1 : # si un objet entre en contact avec l'alien
                        i.etat = 0
                        m.etat = 0
                        i.destroy() # rend la balle invisible
                        m.destroy() # rend l'alien invisible

    # fonction gérant la fin de partie
    def game_over(self) :
        test = True
        if self.jeu :
            if self.fleet.aliens[-1].get_y() >= self.defender.y : # si l'alien le plus bas passe sous le défenseur
                self.jeu = False
                self.fin_partie()
        if self.jeu :
            for m in self.fleet.aliens : # teste si dans il y a au moins un alien affiché
                if m.etat == 1 :
                    test = False
            if test : # si aucun alien n'est affiché
                self.jeu = False
                self.win = True
                self.fin_partie()
            
    # affichage de fin de partie
    def fin_partie (self) :
        self.fleet.effacer() # efface les aliens
        self.defender.effacer() # efface le défenseur
        if self.win : # si partie gagnée
            self.message_fin = self.canvas.create_text(self.width/2, self.height/2, fill = 'green', text = 'Win', font =('Times','98') )
        else : # si partie perdue
            self.message_fin = self.canvas.create_text(self.width/2, self.height/2, fill = 'green', text = 'Game Over', font =('Times','98') )

# classe de gestion du défenseur
class Defender(object):

    # définition de son état initial
    def __init__(self):
        self.width = 20
        self.height = 20
        self.move_delta = 20
        self.tire = True # True = droit de tirer | False = interdiction de tirer
        self.max_fired_bullets = 8
        self.fired_bullets = []
        self.balles = 0 # nombre de balles tirées

    # mise en place ( affichage ) du défenseur    
    def install_in(self, canvas):
        w, x, y = 50, int(canvas.cget("width"))/2, 700
        self.canvas = canvas
        self.y = y
        self.rect_id = self.canvas.create_rectangle(x, y, x + w, y + w/2, fill = 'green', width = 0 )

    # gestion du déplacement du défenseur    
    def move_in(self, event):
        max_w = int(self.canvas.cget("width"))
        if event.keysym == 'Left':  # si flèche gauche touchée, calcule le déplacement à gauche
            x1, y1, x2, y2 = self.canvas.bbox(self.rect_id)
            self.move_delta = -20
            if x2 + self.move_delta < 0 : # si il devrait sortir de l'écran, récalcule le déplacement pour le mettre tout à droite
                self.move_delta = max_w
            self.canvas.move(self.rect_id, self.move_delta, 0) # déplacement
        elif event.keysym == 'Right': # si flèche droite touchée, calcule le déplacement à droite
            x1, y1, x2, y2 = self.canvas.bbox(self.rect_id)
            self.move_delta = 20
            if x1 + self.move_delta > max_w : # si il devrait sortir de l'écran, récalcule le déplacement pour le mettre tout à gauche
                self.move_delta = -1 * max_w
            self.canvas.move(self.rect_id, self.move_delta, 0) # déplacement

    # gestion du tir              
    def fire(self, event):
        if self.tire : # s'il a le droit de tirer
            x1, y1, x2, y2 = self.canvas.bbox(self.rect_id)
            if event.keysym == 'space' and self.max_fired_bullets >  self.balles : # s'il y a moins de 8 balles et que la touche espace est pressée
                self.balles += 1
                self.fired_bullets.append(Bullet((x2 - x1)/2 + x1))
                self.fired_bullets[-1].install_in(self.canvas)

    # fonction de rechargement d'une balle
    def recharge (self) :
        self.balles -= 1

    # efface les balles et le défenseur
    def effacer (self) :
        for m in self.fired_bullets :
            m.destroy()
        self.fired_bullets = []
        self.canvas.delete(self.rect_id)
        self.tire = False

# classe d'une balle
class Bullet(object):


    # initialisation d'une balle
    def __init__(self, shooter):
        self.radius = 5
        self.color = "red"
        self.speed = 8
        self.shooter = shooter
        self.hauteur = 700
        self.etat = 1 # 1 : visible | 0 : invisible

    # positionne et affiche la balle
    def install_in(self, canvas):
        x, y = self.shooter, 700
        self.canvas = canvas
        self.bullet_id = self.canvas.create_oval(x, y, x + self.radius, y + self.radius, fill = self.color, width = 0 )

    # défini le déplacement de la balle
    def move_in(self, canvas):
        if self.etat == 1 :
            self.hauteur -= self.speed
            self.canvas.move(self.bullet_id, 0, -1 * self.speed)

    # efface la balle
    def destroy (self) :
        self.canvas.delete(self.bullet_id)

    def __str__ (self) :
        return str(self.id)

# classe de gestion du groupe d'alien        
class Fleet (object) :

    # initialise la classe
    def __init__ (self) :
        self.aliens = []
        self.nb_aliens = 20
        self.speed = 2

    # affiche tout les aliens    
    def install_in (self, canvas) :
        self.canvas = canvas
        x = 400
        y = 50
        for i in range (0, self.nb_aliens) :
            self.aliens.append(Alien(x, y))
            if x == 1200 : # si arrivé en bout de ligne
                x = 400
                y += 75
            else :
                x += 200
            self.aliens[-1].install_in(self.canvas)

    # défini le déplacement des aliens
    def move_alien(self) :
        if self.aliens[0].direction == 1 : # s'ils vont à gauche
            for m in self.aliens :
                m.move_x(5)
        else : # s'ils vont à droite
            for m in self.aliens :
                m.move_x(-5)
        if self.aliens[0].get_x() == 0 : # si le premier alien arrive tout à gauche, change la direction
            for m in self.aliens :
                m.direction = 1
                m.move_y(50)
        elif self.aliens[-1].get_x() == 1400 : # si le dernier alien arrive tout à droite, change la direction
            for m in self.aliens :
                m.direction = 2
                m.move_y(50)

    # vide la liste d'aliens
    def effacer(self) :
        self.aliens = []

# classe de gestion d'un alien            
class Alien (object) :
    
    a_id = 0
    
    def __init__ (self, x, y) :
        self.x = x
        self.y = y
        self.etat = 1 # 1 : visible | 0 : invisible
        self.img = tk.PhotoImage(file = "alien.gif")
        self.direction = 2 # 1 : droite | 2 : gauche
        Alien.a_id += 1 # donne un identifiant à l'alien

    # affiche l'alien    
    def install_in (self, canvas) :
        self.canvas = canvas
        if self.etat == 1 :
            self.alien_id = self.canvas.create_image(self.x, self.y, image = self.img, anchor = 's')

    # renvoi sa position x
    def get_x (self) :
        return self.x

    # renvoi sa position y
    def get_y (self) :
        return self.y

    # le déplace à l'horizontale
    def move_x (self, mouvement) :
        self.x += mouvement
        self.canvas.move(self.alien_id, mouvement, 0)

    # le déplace à la verticale
    def move_y (self, mouvement) :
        self.y += mouvement
        self.canvas.move(self.alien_id, 0, mouvement)

    # efface l'alien
    def destroy (self) :
        self.canvas.delete(self.alien_id)        
        
# programme      
SpaceInvaders().play()
