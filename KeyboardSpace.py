import pygame
import pygame.midi as md
from matplotlib import cm
import numpy as np
from scipy.spatial import distance
import threading

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

points = np.random.random((100, 2)) # 100 points.
point_notes = np.asarray([q%12 for q in range(100)])

def sim():

    # This matrix will be based on the note relationships.
    # The note relationships will also be color coded.
    #multmat = (np.random.random((N,N))*0.2 + 0.8)
    while True:

        N = 100
        #distances = distance.cdist(points, points, metric='chebyshev')
        #distances = distance.cdist(points, points, metric='cityblock')
        distances = distance.cdist(points, points, metric='euclidean')

        x_tiled = np.tile(points[:, 0], (N, 1)).ravel()
        x_repeated = np.repeat(points[:, 0], N).ravel()

        y_tiled = np.tile(points[:, 1], (N, 1)).ravel()
        y_repeated = np.repeat(points[:, 1], N).ravel()

        x_differences = (np.asarray(x_tiled > x_repeated).astype('int')-0.5)*2
        y_differences = (np.asarray(y_tiled > y_repeated).astype('int')-0.5)*2

        # Make the multmat using the transmat...
        multmat = np.zeros((100,100))
        for x in range(100):
            for y in range(100):
                multmat[x][y] = 1 + transmat[point_notes[x]][point_notes[y]]

        distances *= multmat # Change the idea of distance based on the relationship.

        C_distances = np.zeros(distances.shape)
        C_distances[distances > 4.0] = 1
        C_distances[distances < 3.5] = -1

        x_motion = C_distances.ravel() * x_differences * 0.001
        y_motion = C_distances.ravel() * y_differences * 0.001

        x_motion = np.sum(np.reshape(x_motion, (N,N)), axis=1) # 0 was interesting anyway.
        y_motion = np.sum(np.reshape(y_motion, (N,N)), axis=1) # 0 was interesting anyway.

        points[:,0] += x_motion + (np.random.random(x_motion.shape)-0.5)*0.01
        points[:,1] += y_motion + (np.random.random(y_motion.shape)-0.5)*0.01

        points[:, 0] -= np.median(points[:, 0])
        points[:, 1] -= np.median(points[:, 1])

        #print(trial, x_motion[0])

threading.Thread(target=sim).start()

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

    lights = [False for _ in range(12)]
    for n in range(len(notes)):
        if notes[n]: lights[n%12] = True

    for pc in range(len(points)):
        p = points[pc]
        col = colors[pc%12] if lights[pc%12] else (60, 60, 60)
        pygame.draw.rect(screen, col, (250+ int(20*p[0]), 250 + int(20*p[1]), 4, 4), 0)

    transmat /= 1.05
    pygame.display.flip()
    p_clock.tick(60)