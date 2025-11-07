## Default parameters used for the index ##

Fs0 = 96000           #sampling rate of input signal.
N0, H0 = 2048, 512    #N0: length of segment (nperseg). H0 : hop size (noverlap).
tlen0 = 5             #subsegment duration.


##1.
t0 = 5e-11      #threshold for peak finding in spectrum band separation.
win0 = 40       #window size for running mean smoothing of spectrum.
bsize0 = 1500   #size for the frequency band to be kept.

##2.
g0 = 10         #parameter for logarithmic compression step in cp_novelty_spectrum.
win1 = 10         #window size for running mean smoothing of signal.
Q0 = 0.8        #Quantile for discretization threshold used on novelty spectrums.

Fs_feat0 = Fs0/H0      #Feature rate for novelty functions.
k = 1
Na0 = int(Fs_feat0*k)  #Window size for novelty function, corresponding to k seconds.
Theta0 = (100, 6100)  #tempi range, from 100 to 6100 BPM.

##3.
t1 = 0.3         #threshold for temprum peak search.
prom_c0 = 1/3    #prominence coefficient for temprum peak search.

eps0, delta0 = 60, 60  #margins for tempo identification.

display0 = False  #whether or not to display intermediary outputs.