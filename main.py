# Demo: Quantum Satellite Placement
#
# Copyright (c) 2021-2024, Dynex Developers
# 
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without modification, are
# permitted provided that the following conditions are met:
# 
# 1. Redistributions of source code must retain the above copyright notice, this list of
#    conditions and the following disclaimer.
# 
# 2. Redistributions in binary form must reproduce the above copyright notice, this list
#    of conditions and the following disclaimer in the documentation and/or other
#    materials provided with the distribution.
# 
# 3. Neither the name of the copyright holder nor the names of its contributors may be
#    used to endorse or promote products derived from this software without specific
#    prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL
# THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
# STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF
# THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
import itertools
import json
import math
import sys
import matplotlib.pyplot as plt
import dimod
import dynex
import matplotlib.pyplot as plt
from matplotlib.offsetbox import OffsetImage, AnnotationBbox

# Test Dynex account setup:
dynex.test()

# Support functions

def calculate_score(constellation, data):
    """ Function to calculate constellation score."""

    score = 1
    for v in constellation:
        score *= (1 - data['coverage'][str(v)])
    score = 1 - score
    return score

def build_bqm(data, constellation_size):
    """ Build the bqm for the problem."""

    # don't consider constellations with average score less than score_threshold
    score_threshold = .4

    bqm = dimod.BinaryQuadraticModel.empty(dimod.BINARY)

    # first we want to favor combinations with a high score
    for constellation in itertools.combinations(range(data['num_satellites']), constellation_size):
        # the score is the probability of at least one satellite in the constelation having line of sight over the target at any one time.
        score = calculate_score(constellation, data)

        # to make it smaller, throw out the combinations with a score below
        # a set threshold
        if score < score_threshold:
            continue

        # we subtract the score because we want to minimize the energy
        bqm.add_variable(frozenset(constellation), -score)

    # next we want to penalize pairs that share a satellite. We choose 2 because
    # because we don't want it to be advantageous to pick both in the case that
    # they both have 100% coverage
    for c0, c1 in itertools.combinations(bqm.variables, 2):
        if c0.isdisjoint(c1):
            continue
        bqm.add_interaction(c0, c1, 2)

    # finally we wish to choose num_constellations variables. We pick strength of 1
    # because we don't want it to be advantageous to violate the constraint by
    # picking more variables
    bqm.update(dimod.generators.combinations(bqm.variables, data['num_constellations'], strength=1))

    return bqm

def getImage(path, zoom=1):
    return OffsetImage(plt.imread(path), zoom=zoom)

def viz(constellations, data):
    """ Visualize the solution"""
    
    angle = 2*math.pi / data["num_satellites"]
    plt.figure(figsize=(10,6))
    img = plt.imread("satellite-data/earth.jpg")
    
    fig = plt.figure()
    fig.patch.set_facecolor('xkcd:black')
    
    plt.title('Optimal Satellite Constellations\n'+str(data['num_satellites'])+' satellites, '+str(data['num_constellations'])+' targets to observe', color='white')
    plt.imshow(img, zorder=0, extent=[-1.5, 1.5, -1, 1])
    
    s = 0
    for c in constellations:
        x = []
        y = []
        label = []
        for satellite in c:
            coverage = 1 - data["coverage"][str(satellite)]
            label.append(satellite)
            x.append(coverage*math.cos(s*angle))
            y.append(coverage*math.sin(s*angle)+0.2)
            s += 1
    
        x.append(x[0])
        y.append(y[0])
        label.append(label[0])
        plt.plot(x, y, zorder=1, marker = 'o', markersize=10, color='white')
    plt.tight_layout()
    plt.axis('off')
    plt.savefig('result.png')

# load satellite data:
with open('satellite-data/mini.json', 'r') as fp:
    data = json.load(fp)
print('Number of satellites:',data['num_satellites']);
print('Number of targets on earth to observe:',data['num_constellations']);

# each of the x satellites (labelled 0..n-1) has a coverage score. This could be
# calculated as the percentage of time that the Earth region is in range of the
# satellite

constellation_size = data['num_satellites'] // data['num_constellations']
bqm = build_bqm(data, constellation_size)

# Sample on Dynex Testnet
sampleset = dynex.sample(bqm, mainnet=False, num_reads=10000, annealing_time = 1000, description='Satellite Positioning');
print(sampleset)

# Generate result:
constellations = [constellation
                for constellation, chosen in sampleset.first.sample.items()
                if chosen]
tot = 0
for constellation in constellations:
    score = calculate_score(constellation, data)
    print("Constellation: " + str(constellation) + ", Score: " + str(score))
    tot += score
print("Total Score: " + str(tot))
print("Normalized Score (tot / # constellations): " + str((tot / data['num_constellations'])))

viz(constellations, data)
