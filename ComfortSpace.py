import numpy as np
from scipy.spatial import distance
import threading
import pygame
from matplotlib import cm

def sim():

    # This matrix will be based on the note relationships.
    # The note relationships will also be color coded.
    #multmat = (np.random.random((N,N))*0.2 + 0.8)
    multmat = np.zeros((N,N))
    for x in range(N):
        for y in range(N):
            multmat[x][y] = note_matrix[notes[x]][notes[y]]

    while True:

        #distances = distance.cdist(points, points, metric='chebyshev')
        #distances = distance.cdist(points, points, metric='cityblock')
        distances = distance.cdist(points, points, metric='euclidean')

        x_tiled = np.tile(points[:, 0], (N, 1)).ravel()
        x_repeated = np.repeat(points[:, 0], N).ravel()

        y_tiled = np.tile(points[:, 1], (N, 1)).ravel()
        y_repeated = np.repeat(points[:, 1], N).ravel()

        x_differences = (np.asarray(x_tiled > x_repeated).astype('int')-0.5)*2
        y_differences = (np.asarray(y_tiled > y_repeated).astype('int')-0.5)*2

        distances *= multmat # Change the idea of distance based on the relationship.
        C_distances = np.zeros(distances.shape)
        C_distances[distances > 4.0] = 1
        C_distances[distances < 3.5] = -1

        x_motion = C_distances.ravel() * x_differences * 0.0001
        y_motion = C_distances.ravel() * y_differences * 0.0001

        x_motion = np.sum(np.reshape(x_motion, (N,N)), axis=1) # 0 was interesting anyway.
        y_motion = np.sum(np.reshape(y_motion, (N,N)), axis=1) # 0 was interesting anyway.

        points[:,0] += x_motion + (np.random.random(x_motion.shape)-0.5)*0.1
        points[:,1] += y_motion + (np.random.random(y_motion.shape)-0.5)*0.1

        points[:, 0] -= np.median(points[:, 0])
        points[:, 1] -= np.median(points[:, 1])

        #print(trial, x_motion[0])

N = 300
NOTES = 8

# TODO: Fill this in!
# It could be cool to have it change dynamically as you play.
# Then you'd see how different people's music spaces looked.
# Bigger values mean they should be further apart.
note_matrix = \
    [
        #   C   D   E   F   G   A   B   C
        [    1,  2,   0.5,   1,   0.5,   1,   0.5,   1.0   ], # C
        [    0,  1,   2,     1,   0.5,   0.5, 1,     0.5   ], # D
        [    0,  0,   1,     3,   0.5,   0.5, 0.5,     0.5   ], # E
        [    0,  0,   0,     1,   1,   0.5, 3,     0.5   ], # F
        [    0,  0,   0,     0,   1,   1, 0.5,     0.5   ], # G
        [    0,  0,   0,     0,   0,   1,  2,     1   ], # A
        [    0,  0,   0,     0,   0,   0, 1,     3   ], # B
        [    0,  0,   0,     0,   0,   0, 0,     1   ], # C
    ]


# Now make it symmetric.
for x in range(NOTES):
    for y in range(x, NOTES):
        note_matrix[y][x] = note_matrix[x][y]

print(note_matrix)

#note_matrix = np.ones((NOTES, NOTES))

points = np.random.random((N, 2))
#notes = (np.random.random(N)*(NOTES-1)).astype('int') # Each point has a note.
notes = np.asarray([q%NOTES for q in range(N)])
colormap = cm.get_cmap('rainbow', NOTES)
colors = [(255 * np.asarray(colormap(note)[:-1])).astype('int') for note in notes]

screen = pygame.display.set_mode((500, 500))
p_clock = pygame.time.Clock()

import time
time.sleep(5)

threading.Thread(target=sim).start()

scale = 20
while True:
    pygame.draw.rect(screen, (0,0,0), (0,0,500,500))

    for pc in range(len(points)):
        p = points[pc]
        pygame.draw.rect(screen, colors[pc], (250+ int(scale*p[0]), 250 + int(scale*p[1]), 4, 4), 0)

    pygame.display.flip()
    p_clock.tick(30)