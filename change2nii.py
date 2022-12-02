import numpy as np
import os
from os.path import join
import SimpleITK as sitk

SAVE_OBJ_FOLD = r'G:\front_web\cudes\B-obj'
SAVE_NII_FOLD = r'G:\front_web\cudes\A-nii'
DATASET_FOLD = r'D:\juputer\CECT\ground_truth\clear'

def dcm2nii_sitk(path_read, path_save,file_name):
    reader = sitk.ImageSeriesReader()
    seriesIDs = reader.GetGDCMSeriesIDs(path_read)

    N = len(seriesIDs)
    lens = np.zeros([N])
    for i in range(N):
        dicom_names = reader.GetGDCMSeriesFileNames(path_read, seriesIDs[i])
        lens[i] = len(dicom_names)
    N_MAX = np.argmax(lens)
    dicom_names = reader.GetGDCMSeriesFileNames(path_read, seriesIDs[N_MAX])

    reader.SetFileNames(dicom_names)
    image = reader.Execute()
    if not os.path.exists(path_save):
        os.mkdir(path_save)
    sitk.WriteImage(image, join(path_save,file_name+'.nii.gz'))

def main():
    patients = os.listdir(DATASET_FOLD)
    for patient in patients:
        try:
            dcm2nii_sitk(join(DATASET_FOLD,patient,'pelvis_artery'),SAVE_NII_FOLD,patient)
            print(patient+' done')
        except:
            continue

if __name__ == '__main__':
    main()
    