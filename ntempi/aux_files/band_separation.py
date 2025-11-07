## I - Spectrum-based band-separation ##
from dependencies import *


##1. Find spectrum peaks, identify bands.

def identify_bands(s, Fs, N, baseresponse, win, bsize, t, display):
    """ Step (b): find peaks on spectrum, using a combinaison of prominence and absolute threshold,
    and identify bands around them.
    
    Parameters
    ----------
    s: 1d ndarray. Sound waveform.
    Fs: float. Sampling rate (Hz).
    N: int. Segment length for Fourier transform.
    baseresponse: tuple (ndarray, ndarray). Base response of microphones.
    win: int. Window size for running mean smoothing.
    bsize: int. Size for the frequency band to be kept.
    t: float. threshold for peak finding
    display: bool. Whether or not to plot intermediary outputs.
    
    Returns
    -------
    band_limits: list of tuples (float, float). Frequency band boundaries.
    """
    f_idx, pxx = signal.welch(s, Fs, 'hann', N)
    
    #remove base response, ensure spectrum remains nonnegative
    f_idx_b0, pxx_b0 = baseresponse
    pxx = np.maximum(pxx-pxx_b0, 0)
    #smooth spectrum
    pxx_r = util.running_mean(pxx, win)
    
    #find peaks with prominence
    peaks = signal.find_peaks(pxx_r, prominence=np.median(pxx_r))[0]
    #keep only peaks greater than threshold t
    peaks = [x for x in peaks if (pxx_r[x]>=t)]
    
    psize = int(bsize/(f_idx[1] - f_idx[0]) + 1)
    band_limits = []
    for x in peaks:
        #add frequency band boundaries
        freqs = (f_idx[x-psize], f_idx[x+psize])
        band_limits.append(freqs)
        
    if display:
        plt.plot([f_idx[x] for x in peaks], [pxx_r[x] for x in peaks], 'x', color='red', label='peaks')
        plt.plot(f_idx, pxx_r, '-', color = 'blue', label='smoothed spectrum')
        plt.axhline(y = t, color = 'green', linestyle = '--', label='threshold')
        plt.legend(loc='upper right')
        for (i,x) in enumerate(band_limits):
            plt.vlines(x[0], ymin = 0, ymax = max(pxx)/2, colors = 'purple')
            plt.vlines(x[1], ymin = 0, ymax = max(pxx)/2, colors = 'purple')
            print('band {}: ({}, {})'.format(i, int(x[0]), int(x[1])))
        plt.show()

    return band_limits


##2. Isolate spectral bands

def isolate(s, Fs, band_limits, display):
    """ Isolate spectral bands, using boundaries obtained with the identify_band function.
    
    Parameters
    ----------
    s: 1d ndarray. Sound waveform.
    Fs: float. Sampling rate (Hz).
    band_limits: list of tuples (float, float). Frequency band boundaries.
    display: bool. Whether or not to plot intermediary outputs.
    
    Returns
    -------
    bands: list of 1d ndarray. Waveforms of isolated frequency bands.
    """
    bands = []

    for freqs in band_limits:
        #isolate associated band
        sc = sound.select_bandwidth(s, Fs, fcut=freqs, forder=5, fname ='butter', ftype='bandpass')
        bands.append(sc)
    
    if display:
        fig_kwargs = {'vmin':-90, 'figsize':(10,24),  'title':'Power spectrogram density (PSD)',
                      'xlabel':'Time [sec]', 'ylabel':'Frequency [Hz]', 'interpolation':'none'}
        for x in bands:
            Sxx_power, tn, fn, ext = sound.spectrogram(x, Fs, nperseg=2048)
            Sxx_dB = util.power2dB(Sxx_power) #convert into dB

            fig_kwargs['vmax'] = Sxx_dB.max()
            fig_kwargs['extent'] = ext
            fig, ax = util.plot2d(Sxx_dB, **fig_kwargs)  
        
    return bands