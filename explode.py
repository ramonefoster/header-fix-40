"""
    Created on Jun 24 2024

    Description: Module to fix header of images obtained with ROBO40

    @author: Eder Martioli <martioli@lna.br>

    Laboratório Nacional de Astrofísica - LNA/MCTI

    Adapt for usage with TCS40 by Ramon Gargalhone
    
    """

import os, sys
from optparse import OptionParser

import astropy.io.fits as fits
from astropy.time import Time

from copy import deepcopy
import time

"""
O padrão do arquivo FITS deve ser salvo com os seguintes dados para que consigamos processar pelo GSTT:

- "NAXIS1": integer value of the number of pixels along the fastest changing axis;
- "NAXIS2": integer value of the number of pixels along the next to fastest changing axis;
- "DATE-OBS": ISO 8061 format string representation of the acquisition datetime (UTC);
- "EXPOSURE" or "EXPTIME": floating value of the exposure interval;
- "OBJCTRA": floating value of the nominal center image Right Ascension (decimal hours, J2000);
- "OBJCTDEC" : floating value of the nominal center image Declination (decimal degrees, J2000);
- "XBINNING": integer value of the X axis image binning;
- "YBINNING": integer value of the Y axis image binning;
- "XPIXSZ": floating value of the pixel phisical dimension on X (micron);
- "YPIXSZ": floating value of the pixel phisical dimension on Y (micron);
- "BITPIX": integer value of the bit image depth (typically 16);

"""

def explode_cube(path):                
    try :        
        hdul = fits.open(path)
        hdr = hdul[0].header
        num_axis = int(hdr["NAXIS"])
        if num_axis < 3:
            return
            
        # set obstime
        obstime = Time(hdr['FRAME'], format='isot', scale='utc')
            
        total_exptime = hdr["EXPOSURE"]
        
        nslices = hdr["NAXIS3"]
                
        basename = os.path.basename(path)

        s = basename.split("_")
        
        #################
        #### This line needs to be adjusted depending on how many underscores there is in the file name
        # frame, filter, suffix = s[-4], s[-3], "{}_{}".format(s[-2],s[-1])
        if len(s)==5:
            prefix, filter, frame, suffix = s[0], s[2], s[3], s[4]
        else:
            prefix, filter, frame = s[0], s[2], s[3]
            suffix = ""
        
        frame = frame.replace(".fits", "")
        suffix = suffix.replace(".fits","")
        filter = filter.replace(".fits","")
        obj = hdr['OBJECT'].replace(" ","")
                
        for j in range(nslices) :
            
            # set output frame filename
            # outfile = path.replace(basename,"{}_{:05d}_{}_{}_{:05d}.fits".format(obj, int(frame), filter, suffix, j))
            outfile = path.replace(basename,"{}_{}_{}_{:05d}_{}_{:05d}.fits".format(prefix, obj, filter, int(frame), suffix, j))
            if nslices == 1 :
                outfile = path.replace(basename,"{}_{}_{}_{:05d}_{}.fits".format(prefix, obj, filter, int(frame), suffix))

            # make a deep copy of the main header
            outhdr = deepcopy(hdr)
            
            # calculate exptime
            exptime = (total_exptime / nslices)
            # calculate delta time
            deltat =  exptime / (24*60*60)
            
            # calculate jd of current frame
            jd = obstime.jd + deltat * j
            # set obstime of current frame
            curr_obstime = Time(jd, format='jd', scale='utc')
        
            # update header
            outhdr.set("DATE-OBS", curr_obstime.isot, "Frame acquisition datetime (UTC)")
            outhdr.set("EXPOSURE", exptime, "Frame exposure time (s)")
            outhdr.set("XBINNING", hdr["HBIN"], "X axis image binning")
            outhdr.set("YBINNING", hdr["VBIN"], "Y axis image binning")
            outhdr.set("XPIXSZ", 6.5, "pixel physical dimension on X (micron)")
            outhdr.set("YPIXSZ", 6.5, "pixel physical dimension on Y (micron)")

            print("\tExtracting slice {} of {} : saving frame to file {}".format(j+1,nslices,outfile))
            
            # create primary hdu
            primary_hdu = fits.PrimaryHDU(header=outhdr)
            
            # set data cube into primary extension
            primary_hdu.data = hdul[0].data[j]
                        
            # create hdu list
            hdu_list = fits.HDUList()
            
            hdu_list.append(primary_hdu)
            
            max_retries = 10
            retries = 0
            # write output image file
            while retries < max_retries:
                try:
                    # Try to open the file in read mode
                    hdu_list.writeto(outfile, overwrite=True, output_verify="fix+warn")
                except IOError:
                    # File is still being written, wait and retry
                    retries += 1
                    time.sleep(int(total_exptime)/max_retries)
                

            print("Finished Job", outfile)
            
    except Exception as e:
        print("ERROR: could not fix header of image {} with error: {}".format(path,e))
