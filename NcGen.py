import numpy as np
import netCDF4 as nc
import os
import XsecConvert as XC





# Converts .xsec files into .npy files, and then creates a .nc 
# for use in corr-k and SOCRATES/ATMO
def NcCreate(fname,mass,homedir,absdir,datadir,xsecfolder,npyfolder,npoints_P=40,npoints_T=20):
    files_all=os.listdir(xsecfolder)
    files=[]
    count=0
    for file_ in files_all:
        fname, ext=os.path.splitext(file_)
        if file_.endswith('.xsec'):
            fnamenpy=fname+'.npy'
            count+=1
            if not os.path.isfile(npyfolder+fnamenpy):
                print(count,'Converting {0} to .npy format.'.format(file_))
                XC.Convert(xsecfolder,file_,mass,savedir=npyfolder)
    # File format is wavenumber (cm-1) and absorption coeff (m^2/kg)        
    print('Getting list of .npy files')
    files_npy=os.listdir(npyfolder)

    temp_list=[]
    pressure_list=[]
    abscoeff_list=[]
    for file_ in files_npy:
        print('Loading ',file_)
        fname,ext=os.path.splitext(file_)
        fname=fname.split('_')
        temp=float(fname[2])
        pressure=float(fname[3])
        temp_list.append(temp)
        pressure_list.append(pressure)
        filenp=np.load(npyfolder+file_)
        nu, absc = filenp[0]*100,filenp[1] # m^{-1}, m^2/kg
        abscoeff_list.append(absc)

    temp_list=np.array(temp_list)
    pressure_list=np.array(pressure_list)
    abscoeff_list=np.array(abscoeff_list)
    idx_P=np.argsort(pressure_list)

    temp_list=temp_list[idx_P]
    pressure_list=pressure_list[idx_P]
    abscoeff_list=abscoeff_list[idx_P]
    temp_ss=[]
    pressure_ss=[]
    abs_ss=[]

    proper_nu_length=len(abscoeff_list[0])
    for pressure in np.unique(pressure_list):
        # List of pressure indices 
        idx=np.where(pressure_list == pressure)
        #print(idx)
        temp_slice=temp_list[idx]
        if (npoints_T - len(temp_slice)) > 1: 
            print('{0:.3e} Bar is missing {1} points, skipping.'.format(pressure,40-len(temp_slice)))
            continue
        elif (npoints_T - len(temp_slice)) ==1:
            print('{0:.3e} Bar is missing {1} point, skipping.'.format(pressure,40-len(temp_slice)))
            continue
        #print('{0:.3e} Bar has all {1} points, adding to the .nc.'.format(pressure,len(temp_slice)))
        abs_slice=abscoeff_list[idx]
    
        idx_t=np.argsort(temp_slice)
        temp_slice=temp_slice[idx_t]
        abs_slice=abs_slice[idx_t]
        #print(pressure,len(temp_slice),len(abs_slice),len(abs_slice[0]))
        for i in range(len(temp_slice)):
            pressure_ss.append(pressure)
            temp_ss.append(temp_slice[i])
            if len(abs_slice[i]) != (proper_nu_length):
                print(pressure,temp_slice[i],len(abs_slice[i]))
            abs_ss.append(abs_slice[i])
    
    pressure_ss=np.array(pressure_ss)
    temp_ss=np.array(temp_ss)
    abs_ss=np.array(abs_ss)
        
        #Okay, so they're all in .npy format for easy access, now what?

    # Let's make a .nc file for them!

    fnc=nc.Dataset(absdir+filename,'w')

    scalar_dim=fnc.createDimension('scalar',1)
    nu_dim=fnc.createDimension('nu',proper_nu_length)
    pt_pair_dim=fnc.createDimension('pt_pair',len(temp_ss))


    nu_var=fnc.createVariable('nu','f8',('nu',))
    kabs=fnc.createVariable('kabs','f4',('pt_pair','nu',))
    t_calc= fnc.createVariable('t_calc','f8',('pt_pair',))
    p_calc= fnc.createVariable('p_calc','f8',('pt_pair',))

    nu_var[:]=nu
    print(nu[1]-nu[0])
    nu_var.step=float(abs(nu[1]-nu[0]))
    #nu_var.step=10.0 # Equivalent to 0.1 in cm-1

    # Number of PT points

    PTnum=npoints_P*npoints_T

    for i in range(0,len(pressure_ss)):
        print(i,PTnum)
        t_calc[i]=temp_ss[i]
        p_calc[i]=pressure_ss[i]*1e5 # Bar to Pa
        #for j in range(1,len(abs_ss[i])):
        #    kabs[i,j]=abs_ss[i][j]
        #print(i,pressure_ss[i])
        kabs[i,:] = abs_ss[i]


    fnc.close()
    print('File written to: {0}'.format(absdir+fname))
    return None


################ End of Functions
################ Beginning of work area

homedir='/home/dc-ridg1/data/Exocross/'
absdir='/home/dc-ridg1/AbsCoeffs/'
datadir='/data/dp015/dc-ridg1/NewSpecies/AbsCoeffs/H2O/'
xsecfolder=homedir+'Results/POKAZATEL_HiRez/'
npyfolder=homedir+'npys/POKAZATEL_HiRez/'
filename='abs_coeff_H2O_POKAZATEL_pt800.nc'
waterMass=18.02*1.6726e-27
NcCreate(filename,waterMass,homedir,absdir,datadir,xsecfolder,npyfolder,npoints_P=40,npoints_T=20)

import shutil
shutil.copy(absdir+fname,datadir+fname)

    
    




