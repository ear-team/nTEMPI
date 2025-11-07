## Imports
#external libs
from dependencies import *

#internal acoustic index
from NTempi import *


# Simple tests for different accoustic richnesses ##

#0: no species
s0 = loader('test-audios/RX01_0710_0345.WAV')
assert(NTempi(s0) == 0)

#1: one vocalizing species
s1 = loader('test-audios/RX04_0811_1415.WAV')
assert(NTempi(s1) == 1)

#2: two vocalizing species
s2 = loader('test-audios/RX01_0803_2300.WAV')
assert(NTempi(s2) == 2)

#3: three vocalizing species
#REVOIR
s3 = loader('test-audios/RX01_0718_2300.WAV')
assert(NTempi(s3) == 3)

#4: strictly more than three species
s4 = loader('test-audios/RX01_0714_1400.WAV')
assert(NTempi(s4) == 5)

print('Tests worked as intended!')