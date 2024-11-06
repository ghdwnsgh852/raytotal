import nibabel as nib
import numpy as np
import os
from totalsegmentator.python_api import totalsegmentator
from scipy.ndimage import rotate
from rt_utils import RTStructBuilder
import SimpleITK as sitk
import pydicom

def merge_labels(mask_path, label_groups,style='nifti'):
    # Load the original NIFTI file
    mask_nii = nib.load(mask_path)
    mask_data = mask_nii.get_fdata()

    # Initialize all labels to 0 first
    new_mask_data = np.zeros_like(mask_data)

    # Apply the label mapping to the mask data
    for old_label, new_label in label_groups.items():
        new_mask_data[mask_data == old_label] = new_label
    
    new_mask_data = new_mask_data.astype(np.int32)

    # Create a new NIFTI file with the modified data
    if style=="dicom":
        new_mask_data = rotate(new_mask_data, 90, axes=(0, 1), reshape=False)
    new_mask_nii = nib.Nifti1Image(new_mask_data, mask_nii.affine)


    # Save the new NIFTI file
    # new_mask_nii.to_filename(mask_path)

    return new_mask_nii


def read_dicom_series(directory):
    """
    Reads a series of DICOM files from a directory and returns a 3D numpy array.
    
    Parameters:
    directory (str): The directory containing the DICOM files.
    
    Returns:
    numpy.ndarray: A 3D numpy array containing the pixel data from the DICOM series.
    """
    # Get list of all DICOM files in the directory
    dicom_files = [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith('.dcm')]
    
    # Read the first file to get the dimensions
    first_dicom = pydicom.dcmread(dicom_files[0])
    pixel_dims = (int(first_dicom.Rows), int(first_dicom.Columns), len(dicom_files))
    
    # Create an empty array to store the pixel data
    pixel_array = np.zeros(pixel_dims, dtype=first_dicom.pixel_array.dtype)
    
    # Read each DICOM file and store the pixel data in the array
    for i, dicom_file in enumerate(dicom_files):
        dicom_data = pydicom.dcmread(dicom_file)
        pixel_array[:, :, i] = dicom_data.pixel_array
    
    return pixel_array



def nifti_to_rtstruct(dicom_path: str, rtstruct_path: str, mask,  label_groups):

    mask = mask.get_fdata()
    rtstruct = RTStructBuilder.create_new(dicom_series_path=dicom_path)


    for i in np.unique(list(label_groups.values())):
        temp_mask = mask == i
        if np.any(temp_mask):
            rtstruct.add_roi(temp_mask)

    print("Saving RTSTRUCT file...")
    rtstruct.save(rtstruct_path)



def save_as_dicom_series(image, output_dir):
    # 기존 DICOM의 메타데이터 유지
    writer = sitk.ImageFileWriter()
    writer.KeepOriginalImageUIDOn()
    
    # 이미지 정보를 사용해 파일 이름 생성
    for i in range(image.GetDepth()):
        slice_i = image[:, :, i]
        output_filename = os.path.join(output_dir, f"slice_{i}.dcm")
        
        # DICOM 파일로 저장
        sitk.WriteImage(slice_i, output_filename)


def segment_image(input_path: str, output_base_path: str,labels, save_numpy=False, use_cpu=False):
    """Segment the image using file path and save in .nii.gz and .npy formats."""
    # Check if the input path is valid
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input path {input_path} does not exist.")
    
    if use_cpu==True:
        totalsegmentator(input_path, output_base_path,ml=True,fast=False,roi_subset=labels,body_seg=False, device="cpu")
    else:
        totalsegmentator(input_path, output_base_path,ml=True,fast=False,roi_subset=labels,body_seg=False)
    
    os.remove(input_path)
    # if save_numpy:
    #     # Load the .nii.gz for conversion to .npy
    #     nii_img = nib.load(output_base_path)
    #     output_base_path=output_base_path.replace(".nii.gz",".npy")
    #     np.save(output_base_path, nii_img.get_fdata())  # Save as numpy array

def segment_image_body(input_path: str, output_base_path: str,labels, save_numpy=False, use_cpu=False):
    """Segment the image using file path and save in .nii.gz and .npy formats."""
    # Check if the input path is valid
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input path {input_path} does not exist.")
    
    if use_cpu==True:
        totalsegmentator(input_path, output_base_path,ml=True,fast=False,task="body",body_seg=True,device="cpu")
    else:
        totalsegmentator(input_path, output_base_path,ml=True,fast=False,task="body",body_seg=True)
    
    if save_numpy:
        # Load the .nii.gz for conversion to .npy
        nii_img = nib.load(output_base_path)
        output_base_path=output_base_path.replace(".nii.gz",".npy")
        np.save(output_base_path, nii_img.get_fdata())  # Save as numpy array