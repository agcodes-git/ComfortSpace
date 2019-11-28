import pygame
import pygame.midi as md
from matplotlib import cm
import numpy as np

alt_colormap = cm.get_cmap('viridis', 100)
colormap = cm.get_cmap('rainbow', 12)
colors = [np.asarray(255 * np.asarray(colormap(c)[:-1])).astype('int') for c in range(12)]

pygame.midi.init()
screen = pygame.display.set_mode((800, 800))
i = pygame.midi.Input(1)
p_clock = pygame.time.Clock()
player = pygame.midi.Output(0)
player.set_instrument(87) # 45

notes = [False for n in range(128)]
transmat = np.zeros((12, 12)).astype('float')

while True:
    pygame.draw.rect(screen, (0,0,0), (0,0,800,800))

    if i.poll():
        midi_events = i.read(10)
        midi_evs = pygame.midi.midis2events(midi_events, i.device_id)

        for e in midi_evs:
            if e.data2 > 0:
                player.note_on(e.data1, 127)
                notes[e.data1] = True
            if e.data2 <= 0:
                player.note_off(e.data1, 127)
                notes[e.data1] = False

    for n, note in enumerate(notes):
        pygame.draw.rect(screen, colors[n%12] if note else (30,30,30), (n*8, 0, 6,50), 0)


    # There's a lot of different ways to model the transition matrix, but it all comes down to what looks cool.
    # Now draw the transition matrix!
    for n, note_1 in enumerate(notes):
        for m, note_2 in enumerate(notes):
            if note_1 and note_2:
             #transmat[n%12][m%12] = (transmat[n%12][m%12] + 0.1) * 1.01
                #transmat[n%12][m%12] = min(1, transmat[n%12][m%12] + 0.04)
                transmat[n%12][m%12] += 1# min(1, transmat[n%12][m%12] + 0.04)

    max_t = np.max(transmat) + 0.1
    block = 10
    for x in range(12):
        for y in range(12):
            color = alt_colormap(float(transmat[x%12][y%12]/max_t))
            color = (np.asarray(color[:-1])*255).astype('int')
            pygame.draw.rect(screen, color, (60 + x*block, 60 + y*block, block-1, block-1), 0)

    transmat /= 1.05
    pygame.display.flip()
    p_clock.tick(60)