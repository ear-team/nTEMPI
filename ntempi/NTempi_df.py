## Imports
#external libs
from dependencies import *

#internal acoustic index
from NTempi import *

## NTempi index on all audiofiles of a given folder ##

def NTempi_df(fold_src, path_dst=None, verbose=True):
    """ Compute NTempi acoustic index on all files present in 'fold_src' folder,
    saving the result inside a dataframe at 'path_dst'. 
    
    Parameters
    ----------
    fold_src : string. Path to source folder, containing the audio files on which to compute the NTempi index.
    path_dst : string. Path to destination folder, where output dataframe is saved. Default value is set to None, 
    corresponding to the computed indices not being saved into a permanent file somewhere.
    verbose : boolean. Whether or not to print information related to the file being processed.

    Returns
    -------
    df_NTempi : pandas DataFrame. Two columns, corresponding to filenames and their associated NTempi index.
    """

    assert(os.path.isdir(fold_src)) #check that source folder indeed exists.

    p = Path(fold_src)
    filenames = list(p.glob('**/*.WAV')) #list of all filenames.
    Nfiles = len(filenames)

    df_NTempi = pd.DataFrame(columns = ['names', 'NTempi'])
    
    for (i,x) in enumerate(filenames):
        if verbose:
            print('File {}/{}'.format(i+1, Nfiles))

        #load given file
        x = str(x)
        s = loader(x)

        #compute NTempi index
        Nt = NTempi(s)
        new_row = pd.DataFrame({'names': x.replace('\\', '/').split('/')[-1][:-4], 'NTempi': Nt}, index=[0]) #robust for both paths with '\' or with '/'
        df_NTempi = pd.concat([df_NTempi, new_row]).reset_index(drop=True)

    if path_dst != None:
        df_NTempi.to_csv(path_dst+'/df_NTempi.csv', sep=';', index=False)
        if verbose :
            print('Dataframe saved at {}'.format(path_dst))
    return df_NTempi

if __name__ == "__main__":
    NTempi_df(sys.argv[1], sys.argv[2])