from multiprocessing import Pool
import numpy as np
import mcubes
import nibabel
from skimage.transform import resize
import copy
import os
from os.path import join

SAVE_OBJ_FOLD = r'G:\front_web\cudes\B-obj'
SAVE_NII_FOLD = r'G:\front_web\cudes\A-nii'
SAVE_GLTF_FOLD = r'G:\front_web\cudes\C-module'
DATASET_FOLD = r'D:\juputer\CECT\ground_truth\clear'

def resize_segmentation(segmentation, new_shape, order=3, cval=0):
    '''
    Resizes a segmentation map. Supports all orders (see skimage documentation). Will transform segmentation map to one
    hot encoding which is resized and transformed back to a segmentation map.
    This prevents interpolation artifacts ([0, 0, 2] -> [0, 1, 2])
    :param segmentation:
    :param new_shape:
    :param order:
    :return:
    '''
    tpe = segmentation.dtype
    unique_labels = np.unique(segmentation)
    assert len(segmentation.shape) == len(new_shape), "new shape must have same dimensionality as segmentation"
    reshaped = np.zeros(new_shape, dtype=segmentation.dtype)
    for i, c in enumerate(unique_labels):
        mask = segmentation == c
        reshaped_multihot = resize(mask.astype(float), new_shape, order, mode="edge", clip=True, anti_aliasing=False)
        reshaped[reshaped_multihot >= 0.5] = c
    return reshaped

def read_file_and_resize(file_path):
    if not file_path.endswith('.nii.gz'):
        file_path = file_path+'.nii.gz'
    file = nibabel.load(file_path)
    img = file.get_fdata()
    spacing = np.array(file.header.get_zooms())
    position_array = np.where(img)
    start = np.array(position_array).min(1)
    end = np.array(position_array).max(1)
    # print('file have been read.')
    cube = img[start[0]:end[0]+2,start[1]:end[1]+2,start[2]:end[2]+2]
    shape = np.array(cube.shape)
    new_shape = np.around(spacing/spacing.min()*shape).astype(int)
    # print('resize the spacing into the same....there need some time')
    new_array = resize_segmentation(cube,new_shape)
    # print('resize done, waiting reconstruction')
    return new_array

def get_multi_class_reconstruction(file_path,save_path,zxy_position=[2,1,0],parts=None):
    new_array = read_file_and_resize(file_path)
    z,x,y = zxy_position
    array = np.transpose(new_array,[y,z,x])

    if not os.path.exists(save_path):
        os.mkdir(save_path)

    if parts==None:
        parts = ['back','pelvis','aorta','right_common_iliac_artery','left_common_iliac_artery','right_external_iliac_artery','right_internal_iliac_artery','left_external_iliac_artery','left_internal_iliac_artery']
    for index in range(1,len(parts)):
        test = copy.deepcopy(array)
        test[test!=index]=0
        test[test==index]=1
        not_zero = np.where(test)
        start = np.array(not_zero).min(1)
        end = np.array(not_zero).max(1)
        part = test[start[0]:end[0]+2,start[1]:end[1]+2,start[2]:end[2]+2]
        part = mcubes.smooth(part,'constrained')
        test[start[0]:end[0]+2,start[1]:end[1]+2,start[2]:end[2]+2] = part
        vertices, triangles = mcubes.marching_cubes(test, 0)
        mcubes.export_obj(vertices, triangles, os.path.join(save_path,parts[index]+'.obj'))
        print(parts[index]+' have done')


def text(patient):
    print('Process %s is running as patient(%s).' % (os.getpid(),patient))
    os.makedirs(join(SAVE_GLTF_FOLD,patient.split('.')[0]))
    get_multi_class_reconstruction(join(SAVE_NII_FOLD,patient),join(SAVE_OBJ_FOLD,patient.split('.')[0]))
    return None

if __name__ == '__main__':
    pool = Pool(3) 
    patient_list = os.listdir(SAVE_NII_FOLD)
    for i in patient_list:
        result = pool.apply_async(text,args=(i,))
    pool.close()
    pool.join()

