## Imports
#external libs
from dependencies import *

#internal files
from params import *
from aux_files.band_separation import identify_bands, isolate
from aux_files.temprums import cp_novs, cp_temprums
from aux_files.tempo_identification import delta_in, fd_all_tempi


##1. Preprocessing

def loader(file, Fc=(6000, 40000)):
    """ Load .wav audio file, select specified spectral bandwidth. """
    s, fs_ = sound.load(file)
    s = sound.select_bandwidth(s, fs_, fcut=Fc, forder=5, fname ='butter', ftype='bandpass')
    return s

def get_baseresponse(fs=Fs0):
    """ Retrieve base response of microphones from an empty file. """
    empty_sig = loader('aux_files/empty_file.WAV')
    empty_sig = sound.trim(empty_sig, fs, 0, 5)
    f_idx, pxx = signal.welch(empty_sig, Fs0, 'hann', N0)
    return f_idx, pxx

def segment(s, tlen=5, Fs=Fs0):
    """ Step (a): divide soundfile into smaller segments of equal length.
        
    Parameters
    ----------
    s: 1d ndarray. Sound waveform.
    tlen: int. Length of produced segments. Must be a whole divider of the initial file length.
    Fs: float. Sampling frequency (Hz).
    
    Returns
    -------
    seg: list of 1d ndarray. Audio segments obtained from the input soundfile.
    """
    seg = []
    for k in range(30//tlen):
        tmin, tmax = k*tlen, (k+1)*tlen
        seg.append(sound.trim(s, Fs, tmin, tmax))
    return seg


##2. NTempi

def NTempi(s, win=win0, bsize=bsize0, t=t0, Fs=Fs0, N=N0, H = H0, gamma=g0, wind=win1, Q=Q0,
           Theta = Theta0, Fs_feature=Fs_feat0, Na=Na0, eps=eps0, delta=delta0, thresh=t1,
           prom_c=prom_c0, disp=display0):
    """Compute NTempi acoustic index, by calling intermediate functions at each step.
    
    Parameters
    ----------
    s: 1d ndarray. Sound waveform.
    
    #spectrum-based band separation:
    win: int. Window length for running mean smoothing.
    bsize: int. Size for the frequency band to be kept.
    t: float. Threshold for peak finding.
    
    #novelty and temprum
    gamma: int. Logarithmic compression parameter.
    wind: int. Window size (2wind+1) in samples used for running mean.
    Q: float. Quantile for discretization threshold. 0<Q<1.
    
    #peak tempo identification
    Fs_feature: float. Novelty common feature rate (Hz).
    Na: int. Window size for Fourier transform of novelty functions.
    eps: float. Error margin for detection of harmonics (BPM).
    delta: float. Error margin for tempo merging (BPM).
    thresh: float. threshold for peak detection.
    prom_c: float. Coefficient for prominence value.
    
    Fs: float. Sampling rate (Hz).
    display: bool. Whether or not to plot intermediary outputs
    
    Returns
    -------
    NbTempi: int. Total number of tempi identified in the audio segment.
    """
 
    # crop file to 30s
    s = sound.trim(s, Fs, 0, 30)
    
    # segment
    seg = segment(s)
    tempi_set = []
    baseresponse = get_baseresponse()
    
    for (i,x) in enumerate(seg):
        
        #1. spectrum-based separation
        band_limits = identify_bands(x, Fs, N, baseresponse, win, bsize, t, disp)
        bands = isolate(x, Fs, band_limits, disp)

        #2. novelty and temprums
        novs, _= cp_novs(bands, gamma, wind, Q, Fs, N, H, disp)
        temprums = cp_temprums(novs, Fs_feature, Na, Theta, disp)

        #3. all found tempi
        tempi = fd_all_tempi(temprums, eps, delta, thresh, prom_c, disp)
        
        #4. add to tempi of all segs
        for y in tempi:
            if not delta_in(tempi_set, y, delta):
                tempi_set.append(y)
        NbTempi = len(tempi_set)

    return NbTempi


if __name__ == "__main__":
    s = loader(sys.argv[1])
    print(NTempi(s))