## II - Band-specific temprum ##
from dependencies import *


##1. Running mean

def cp_running_mean(x, wind):
    """ Compute running mean of signal x.

    Parameters
    ----------
    x: 1d ndarray. Sound waveform.
    wind: int. Window size (2wind+1) in samples used for running mean.

    Returns
    -------
        running-mean: ndarray. Smoothed signal.
    """
    N = len(x)
    x_rm = np.zeros(N)
    for k in range(N):
        a = max(k - wind, 0)
        b = min(k + wind + 1, N)
        x_rm[k] = np.sum(x[a:b])/(2*wind+1)
    return x_rm


##2. Novelty curves

def cp_novelty_spectrum(x, gamma, wind, Fs, N, H, norm=True):
    """ Compute spectral-based novelty function.

    Parameters
    ----------
    x: 1d ndarray. Sound waveform.
    gamma: int. Logarithmic compression parameter.
    wind: int. Parameter for window size in running mean.
    Fs: float. Sampling rate (Hz).
    N: int. Window size for Fourier transform.
    H: int. Hop size for Fourier transform.
    norm: bool. Whether to apply max norm or not.
    
    Returns
    -------
        novelty_spectrum: ndarray. Energy-based novelty function.
    """
    Sxx = librosa.stft(x, n_fft=N, hop_length=H, win_length=N, window='hann')
    Fs_feature = Fs/H
    Y = np.log(1 + gamma*np.abs(Sxx))
    Y_diff = np.diff(Y)
    Y_diff[Y_diff < 0] = 0
    novelty_spectrum = np.sum(Y_diff, axis=0)
    novelty_spectrum = np.concatenate((novelty_spectrum, np.array([0.0])))
    if wind > 0:
        running_mean = cp_running_mean(novelty_spectrum, wind)
        novelty_spectrum = novelty_spectrum - running_mean
        novelty_spectrum[novelty_spectrum < 0] = 0.0
    if norm:
        max_value = max(novelty_spectrum)
        if max_value > 0:
            novelty_spectrum = novelty_spectrum / max_value
    return novelty_spectrum


def discretize(x, t=None):
    """ Discretize input array x using threshold t. """
    
    xd = np.zeros_like(x)

    if t is None:
        t = np.min(x) - 1
    for i in range(1, x.shape[0] - 1):
        if x[i] >= t:
            xd[i] = x[i]
    return xd

def cp_novs(bands, gamma, wind, Q, Fs, N, H, display):
    """ Compute spectral-based novelty functions for all selected frequency bands. 
    
    Parameters
    ----------
    bands: list of 1d ndarray. Waveforms of isolated frequency bands.
    gamma: int. Logarithmic compression parameter.
    wind: int. Parameter for window size in running mean.
    Q: float. Quantile for discretization threshold. 0<Q<1.
    Fs: float. Sampling rate (Hz).
    N: int. Window size for Fourier transform.
    H: int. Hop size for Fourier transform.
    display: bool. Whether or not to plot intermediary outputs.
    
    Returns
    -------
        novs: list of 1d np.ndarray. Energy-based novelty functions for selected bands.
        Fs_feature: float. Novelty feature rate (Hz).
    """

    novs = []
    Fs_feature = Fs/H

    for (i, x) in enumerate(bands):
        nov = cp_novelty_spectrum(x, gamma, wind, Fs, N, H, norm=True)
        t = np.quantile(nov, Q)
        nov_d = discretize(nov, t)
        novs.append(nov_d)
        
        if display:
            ind = np.arange(nov.shape[0])/Fs_feature
            fig, ax, line = plt.plot(ind, nov, title= 'Spectral-based novelty function for band {}'.format(i),
                                     figsize = (10, 5))
            fig, ax, line = plt.plot(ind, nov_d, title= 'Spectral-based novelty function for band {}'.format(i),
                                     figsize = (10, 5))
    return novs, Fs/H


##3. Temprums

def normalize(f):
    """ Applies norm2-normalization to an input ndarray f. """
    y = np.sqrt(np.sum(np.square(f)))
    return np.array([x/y for x in f])


def cp_temprum(nov_d, Fs_feature, Na, Theta, display):
    """ Compute temprum, ie power spectral density of novelty function.
    
    Parameters
    ----------
    nov_d: 1d ndarray. Discretized novelty function.
    Fs_feature: float. Novelty feature rate (Hz).
    Na: int. Window size for Fourier transform of novelty function.
    Theta: tuple (int, int). Boundaries for the tempo range considered.
    display: bool. Whether or not to plot intermediary outputs.

    Returns
    -------
    temp_bpm: 1d ndarray. Array of sample tempi (BPM).
    pxx: 1d ndarray. Array of temprum values.
    """
    temp_idx, pxx = signal.welch(nov_d, Fs_feature, 'hann', Na)
    
    pxx = normalize(pxx)
    temp_bpm = temp_idx*60
    
    pxx = pxx[np.where((temp_bpm>=Theta[0]) & (temp_bpm<=Theta[1]))]
    temp_bpm = temp_bpm[np.where((temp_bpm>=Theta[0]) & (temp_bpm<=Theta[1]))]
    
    if display:
        util.plot_spectrum(pxx, temp_bpm)
    return temp_bpm, pxx


def cp_temprums(novs, Fs_feature, Na, Theta, display):
    """ Compute temprums, ie power spectral density, for a list of novelty functions.
    
    Parameters
    ----------
    novs: lit of 1d np.ndarray. Array of novelty functions.
    Fs_feature: float. Novelty common feature rate (Hz).
    Na: int. Window size for Fourier transform of novelty functions.
    Theta: tuple (int, int). Boundaries for the tempo range considered.
    display: bool. Whether or not to plot intermediary outputs.

    Returns
    -------
    temprums: list of tuples (1d ndarray, 1d ndarray). Array of sample tempi (BPM) and temprum values.
    """
    temprums = []
    
    for x in novs:
        f_temp, pxx = cp_temprum(x, Fs_feature, Na, Theta, display)
        temprums.append((f_temp, pxx))
    return temprums