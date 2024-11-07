from load_data import validate_nifti_file, validate_dicom_file,generate_output_path,generate_dicom_path
from segmentation import segment_image,merge_labels,nifti_to_rtstruct
import time
import os
import numpy as np
import argparse
import torch
print("CUDA available:", torch.cuda.is_available())

def inference(img_path, mask_path, save_numpy=False,use_cpu=False,style='dicom'):


    # Define the organ labels for the segmentation
    labels=["spleen","kidney_right","kidney_left","liver","stomach","pancreas",'prostate',
            "lung_upper_lobe_left","lung_upper_lobe_right",
            "lung_lower_lobe_left","lung_lower_lobe_right","lung_middle_lobe_right",
            "vertebrae_S1","vertebrae_L5","vertebrae_L4","vertebrae_L3","vertebrae_L2",
            "vertebrae_L1","vertebrae_T12","vertebrae_T11","vertebrae_T10","vertebrae_T9",
            "vertebrae_T8","vertebrae_T7","vertebrae_T6","vertebrae_T5","vertebrae_T4",
            "vertebrae_T3","vertebrae_T2","vertebrae_T1",
            "vertebrae_C7","vertebrae_C6","vertebrae_C5","vertebrae_C4","vertebrae_C3",
            "vertebrae_C2","vertebrae_C1"]
    
    label_groups = {
        1: 1, 
        2: 2,
        3: 3, 
        5: 4, 
        6: 5,
        7: 6,
        10:10,
        11:10,
        12:11,
        13:13,
        14:11,
        }
    for i in range(26, 51):
        label_groups[i] = 19

    # Start timer
    start_time = time.time()
    if style=="nifti":
        # Loop through all images in the input directory
        nifti_file_path = img_path
        valid_nifti_path = validate_nifti_file(nifti_file_path) # Validate the NIFTI file
        output_path_nifti = generate_output_path(valid_nifti_path,mask_path) # Generate output path            
        segment_image(valid_nifti_path, output_path_nifti,labels, save_numpy=save_numpy,use_cpu=use_cpu) # Segment the image
        merge_labels(output_path_nifti, label_groups)


        # # 여기에 nifti 파일 이 있고 dicom으로 바꿔줘야 함
        # nifti_to_rtstruct(output_path_nifti, output_path_nifti+'.dcm', mask, label_groups) # Convert NIFTI to RTSTRUCT
        # os.rmdir(output_path_nifti) # Remove the DICOM folder

    
    elif style=="dicom":
       
        dicom_file_path = img_path
        valid_dicom_path = validate_dicom_file(dicom_file_path) # Validate the DICOM file
        
        output_path_nifti = generate_output_path(valid_dicom_path,mask_path) # Generate output path
        print('output_path_nifti',output_path_nifti)
        segment_image(valid_dicom_path, output_path_nifti,labels, save_numpy=save_numpy,use_cpu=use_cpu) # Segment the image
        mask=merge_labels(output_path_nifti, label_groups, style=style)


        output_path = generate_dicom_path(output_path_nifti)
        # 여기에 nifti 파일 이 있고 dicom으로 바꿔줘야 함
        os.remove(output_path_nifti)

        result_path = output_path+'.dcm'
        nifti_to_rtstruct(dicom_file_path, result_path, mask, label_groups) # Convert NIFTI to RTSTRUCT


    else:
        print("Please enter a valid style either dicom or nifti")
        ValueError("Please enter a valid style either dicom or nifti")


    # End timer and print elapsed time
    elapsed_time = time.time() - start_time
    print(f"Total processing time: {elapsed_time:.2f} seconds")
    return result_path

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--img_path", type=str, required=True, help="Path to the input images")
    parser.add_argument("--mask_path", type=str, required=True, help="Path to the output segmentation masks")
    parser.add_argument("--save", type=bool, default=False, help="Set to True to save numpy files, False only nifti files.")
    parser.add_argument("--use_cpu", type=bool, default=True, help="Set to True to use CPU.")
    parser.add_argument("--style", type=str, default='dicom', help="Set dicom or nifti.")
    args = parser.parse_args()
    inference(args.img_path, args.mask_path, args.save, args.use_cpu,args.style)