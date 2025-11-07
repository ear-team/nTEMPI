## III - Tempo identification ##
from dependencies import *


##0. Aux functions

def fd_peaks(pxx, thresh, prom):
    """ Finds peaks in temprum 'pxx', using both prominence 'prom' and threshold 'thresh' input parameters. """
    return [i for i in signal.find_peaks(pxx, prom)[0] if pxx[i]>=thresh]

def is_harm(x, tempo, eps):
    """ Determines whether a given tempo value x is an harmonic of a base tempo, allowing an eps error margin. """
    return (abs(x-tempo)>eps) and ((x%tempo<=eps*(x//tempo)) or ((x%tempo-tempo)>=-eps*((x//tempo)+1)))

def is_any_harm(x, tempi, eps):
    """ Determines whether a tempo value x is an harmonic of any elements in a tempo list,
    allowing an eps error margin. """
    for y in tempi:
        if y!=x and is_harm(x, y, eps):
            return True
    return False

def delta_in(l, x, delta):
    """ Tests if a float x belongs to a list l, allowing a delta error margin. """
    for y in l:
        if (x<=y+delta) and (x>=y-delta):
            return True
    return False


##1. Find tempi

def find_tempi(temprum, eps, thresh, prom_c, display):
    """ Finds all peak tempi of a temprum, excluding harmonics.
    
    Parameters
    ----------
    temprum: tuple (ndarray, ndarray). Array of sample tempi (BPM) and temprum values.
    eps: float. Error margin for detection of harmonics (BPM).
    thresh: float. threshold for peak detection.
    prom_c: float. Coefficient for prominence value.
    display: bool. Whether or not to plot intermediary outputs.

    Returns
    -------
    tempi: list of float. Peak tempi of the novelty function.
    """
    tempi = []

    temp_bpm, pxx = temprum[0], temprum[1]
    prom1 = prom_c*np.max(pxx)
    peaks = fd_peaks(pxx, thresh, prom= prom1)

    for y in peaks:
        ytemp = int(temp_bpm[y])
        if not is_any_harm(ytemp, tempi, eps):
            tempi.append(ytemp)
            
    if display:
        print('tempi: {}'.format(tempi))
        plt.plot(temp_bpm[peaks], [pxx[x] for x in peaks], 'x', color='purple', label='peaks')
        plt.plot(temp_bpm, pxx, 'orange', label='temprum')
        plt.axhline(y = thresh, color = 'blue', linestyle = '--', label='threshold')
        plt.legend(loc='upper right')
        plt.show()

    return tempi


def fd_all_tempi(temprums, eps, delta, thresh, prom_c, display):
    """Find all peak tempi of a list of temprums.
    
    Parameters
    ----------
    temprum: tuple (ndarray, ndarray). Array of sample tempi (BPM) and temprum values.
    eps: float. Error margin for detection of harmonics (BPM).
    delta: float. Error margin for tempo merging (BPM).
    thresh: float. threshold for peak detection.
    prom_c: float. Coefficient for prominence value.
    display: bool. Whether or not to plot intermediary outputs
    
    Returns
    -------
    tempi: list of float. Peak tempi for all the novelty functions.
    """

    tempi=[]
    for temprum in temprums:
        tem = find_tempi(temprum, eps, thresh, prom_c, display)
        for x in tem:
            if not delta_in(tempi, x, delta):
                tempi.append(x)
    return tempi