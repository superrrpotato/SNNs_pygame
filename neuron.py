import os, sys
import numpy as np
import pygame
import pygame.gfxdraw
from pygame.locals import *
from matplotlib import cm
cividis = cm.get_cmap('cividis', 12)

if not pygame.font: print('Warning, fonts disabled')
if not pygame.mixer: print('Warning, sound disabled')

class Neuron(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        ATOM_IMG = pygame.Surface((40, 40), pygame.SRCALPHA)
        self.b = b = np.array([47, 82, 143])
        self.b_fill = b_fill = np.array([218, 227, 243])
        self.o = o = np.array([237,125,49])
        self.o_fill = o_fill = np.array([255,217,102])
        self.u = 0.
        self.s = 0.
        self.a = 0.
        self.threshold = 1.
        self.tau_u = 50.
        self.tau_s = 30.
        self.refractory = 1.
        self.decay_u = 1. - 1 / self.tau_u
        self.decay_s = 1. - 1 / self.tau_s
        self.index = None
        pygame.gfxdraw.aacircle(ATOM_IMG, 20, 20, 19, b)
        pygame.gfxdraw.aacircle(ATOM_IMG, 20, 20, 18, b)
        pygame.gfxdraw.aacircle(ATOM_IMG, 20, 20, 17, b)
        pygame.gfxdraw.aacircle(ATOM_IMG, 20, 20, 16, b)
        pygame.gfxdraw.aacircle(ATOM_IMG, 20, 20, 15, b)
        pygame.gfxdraw.filled_circle(ATOM_IMG, 20, 20, 14, b_fill)
        self.image = ATOM_IMG
        self.rect = self.image.get_rect(center=(150, 200))
        self.fix_loc = False
        self.pos = None
        self.mouseon = False
    def update(self, a_all):
        if self.fix_loc == True and self.pos == None:
            self.pos = pygame.mouse.get_pos()
        if self.fix_loc == True:
            pos = self.pos
        else:
            pos = pygame.mouse.get_pos()
        self.rect.center = pos
        if self.mouseon:
            self.rect.move_ip(2, 2)

        if self.index != None:
            a_in = a_all[self.index]
            self.u = self.u * self.decay_u + a_in
            self.s = float(self.u >= self.threshold)
            self.u *= (1-self.s)
            # self.u -= self.s * self.refractory
            self.a = self.a * self.decay_s + 1 / self.tau_s * self.s

        ATOM_IMG = pygame.Surface((40, 40), pygame.SRCALPHA)
        b_u = np.clip((self.b+self.u*(self.o-self.b)).astype(int),0,255)
        b_fill_u = np.clip((self.b_fill+self.u*(self.o_fill-self.b_fill)).astype(int),0,255)
        if self.s == 1:
            b_u = self.o
            b_fill_u = self.o_fill
        pygame.gfxdraw.aacircle(ATOM_IMG, 20, 20, 19, b_u)
        pygame.gfxdraw.aacircle(ATOM_IMG, 20, 20, 18, b_u)
        pygame.gfxdraw.aacircle(ATOM_IMG, 20, 20, 17, b_u)
        pygame.gfxdraw.aacircle(ATOM_IMG, 20, 20, 16, b_u)
        pygame.gfxdraw.aacircle(ATOM_IMG, 20, 20, 15, b_u)
        pygame.gfxdraw.filled_circle(ATOM_IMG, 20, 20, 14, b_fill_u)
        self.image = ATOM_IMG
        #self.rect = self.image.get_rect(center=(150, 200))
    def place_neuron(self):
        self.fix_loc = True
    def mouse_on(self):
        self.mouseon = True
    def mouse_leave(self):
        self.mouseon = False
def main():
    pygame.init()
    screen = pygame.display.set_mode((1000, 1000))
    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill((250, 250, 250))
    screen.blit(background, (0, 0))
    font = pygame.font.SysFont('CourierNew', 20)
    pygame.display.flip()
    w = np.array([[0.]])
    a_all = np.array([0.])
    neuron = Neuron()
    neuron_list = []
    neuron_list += [neuron]
    link_list = []
    link_sign_list = []
    allsprites = pygame.sprite.RenderPlain(neuron_list)
    going = True
    moving_link = False
    clock = pygame.time.Clock()
    state = 'place'
    start = None
    end = None
    adj_matrix_length = 100
    loc_shift_adj = 10
    count = 0
    while going:
        count += 1
        background.fill((250, 250, 250))
        clock.tick(100)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                going = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                going = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                if state != 'place':
                    if state in ['link', 'd_link'] and start != None:
                        link_list = link_list[:-1]
                        link_sign_list = link_sign_list[:-1]
                    state = 'place'
                    neuron = Neuron()
                    neuron_list += [neuron]
                    allsprites = pygame.sprite.RenderPlain(neuron_list)
                else:
                    pass
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_l:
                if state != 'link':
                    if state == 'place':
                        neuron_list = neuron_list[:-1]
                    state = 'link'
                    allsprites = pygame.sprite.RenderPlain(neuron_list)
                else:
                    pass
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_d:
                if state != 'd_link':
                    if state == 'place':
                        neuron_list = neuron_list[:-1]
                    state = 'd_link'
                    allsprites = pygame.sprite.RenderPlain(neuron_list)
                else:
                    pass
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_f:
                if state != 'fire':
                    if state == 'place':
                        neuron_list = neuron_list[:-1]
                    state = 'fire'
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if state == 'place':
                    neuron.place_neuron()
                    neuron.index = len(neuron_list)-1
                    neuron = Neuron()
                    neuron_list += [neuron]
                    if len(neuron_list) != 2:
                        w = np.r_[w, [[0.]*w.shape[0]]]
                        w = np.c_[w, np.array([[0.]*w.shape[0]]).T]
                        a_all = np.hstack((a_all,np.array([0.])))
                    allsprites = pygame.sprite.RenderPlain(neuron_list)
                elif state == 'link' or state == 'd_link':
                    for index, n in enumerate(neuron_list):
                        if n.rect.collidepoint(pygame.mouse.get_pos()):
                            if start == None:
                                start = n.pos #pygame.mouse.get_pos()
                                start_index = index
                            else:
                                end = n.pos #pygame.mouse.get_pos()
                                end_index = index
                                if moving_link == True:
                                    link_list = link_list[:-1]
                                    link_sign_list = link_sign_list[:-1]
                                link_list += [[start,end]]
                                start = None
                                if state == 'link':
                                    w[start_index, end_index] += 0.2
                                else:
                                    w[start_index, end_index] -= 0.2
                                if w[start_index, end_index] > 0:
                                    link_sign_list += [1]
                                elif w[start_index, end_index] == 0:
                                    link_sign_list += [0]
                                else:
                                    link_sign_list += [-1]
                                moving_link = False
                elif state == 'fire':
                    for index, n in enumerate(neuron_list):
                        if n.rect.collidepoint(pygame.mouse.get_pos()):
                            n.u += 0.5*n.threshold
            elif event.type == pygame.MOUSEBUTTONUP:
                pass
            elif event.type == MOUSEMOTION:
                if state == 'link' or state == 'd_link':
                    x,y = event.pos

                    if start == None:
                        pass
                    else:
                        end = [x, y]
                        if moving_link == True:
                            link_list = link_list[:-1]
                            link_sign_list = link_sign_list[:-1]
                        link_list += [[start,end]]
                        if state == 'link':
                            link_sign_list += [1]
                        else:
                            link_sign_list += [-1]
                        moving_link = True
                    for n in neuron_list:
                        if n.rect.collidepoint(x,y):
                            n.mouse_on()
                        else:
                            n.mouse_leave()
                    # add link motion here
        bin_size = 0.001+adj_matrix_length/w.shape[0]
        pygame.draw.rect(background,[100,100,100],(loc_shift_adj,loc_shift_adj,adj_matrix_length,adj_matrix_length),width=3)
        for index_x, x_adj in enumerate(np.arange(0,adj_matrix_length,bin_size)):
            for index_y, y_adj in enumerate(np.arange(0,adj_matrix_length,bin_size)):
                pygame.draw.rect(background,(np.array(cividis((w[index_x,index_y]-np.min(w))/(np.max(w)-np.min(w)))[:3])*255).astype(int).tolist(), # [255*(1-w[index_x,index_y]/(np.max(w)+0.0001))]*3,\
                        (x_adj+loc_shift_adj, y_adj+loc_shift_adj, bin_size, bin_size))
        for index, links in enumerate(link_list):
            start_loc, end_loc = links
            if start_loc == end_loc:
                if link_sign_list[index] > 0: 
                    pygame.draw.circle(background, [255, 192,0], [start_loc[0]+20,start_loc[1]+20], 20, width=2)
                elif link_sign_list[index] < 0:
                    pygame.draw.circle(background, [68,114,196], [start_loc[0]+20,start_loc[1]+20], 20, width=2)
                else:
                    pygame.draw.circle(background, [255,255,255], [start_loc[0]+20,start_loc[1]+20], 20, width=2)
            else:
                if link_sign_list[index] > 0:
                    pygame.draw.line(background,[255, 192,0],start_loc, end_loc, width=2)
                elif link_sign_list[index] < 0:
                    pygame.draw.line(background,[68,114,196],start_loc, end_loc, width=2)
                else:
                    pygame.draw.line(background,[255,255,255],start_loc, end_loc, width=2)
        for index, n in enumerate(neuron_list):
            if index < len(a_all):
                a_all[index] = n.a
        a_all = a_all.dot(w)
        allsprites.update(a_all)
        screen.blit(background, (0, 0))
        f_screen = font.render('p: place neuron mode ', False, (0, 0, 0))
        f_screen.set_colorkey((250,250,250))
        screen.blit(f_screen, (10, 120))
        f_screen = font.render('l: link neurons mode', False, (0, 0, 0))
        f_screen.set_colorkey((250,250,250))
        screen.blit(f_screen, (10, 135))
        f_screen = font.render('f: firing mode (click to fire)', False, (0, 0, 0))
        f_screen.set_colorkey((250,250,250))
        screen.blit(f_screen, (10, 150))
        f_screen = font.render('synaptic currents:'+str(np.round(a_all,3)), False, (0, 0, 0))
        f_screen.set_colorkey((250,250,250))
        screen.blit(f_screen, (10, 165))
        str(a_all)
        
        allsprites.draw(screen)
        pygame.display.flip()
    pygame.quit()
if __name__ == "__main__":
    main()
