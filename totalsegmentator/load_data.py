from pathlib import Path
import os
import dicom2nifti


def validate_nifti_file(filepath: str) -> str:
    """Validate and return the file path for a NIFTI file."""
    file_path = Path(filepath)
    if file_path.is_file() and (filepath.lower().endswith('.nii') or filepath.lower().endswith('.nii.gz')):
        return str(file_path)
    else:
        raise ValueError("Provided file is not a NIFTI file or does not exist: {}".format(filepath))

def validate_dicom_file(filepath: str) -> str:
    """Validate and return the file path for a NIFTI file or convert DCM folder to NIFTI."""
    file_path = Path(filepath)
    if file_path.is_dir() and any(file_path.glob('*.dcm')):
        nifti_path = convert_dcm_to_nifti(filepath)
        return str(nifti_path)
    else:
        raise ValueError("Provided file is not a DCM folder, or does not exist: {}".format(filepath))
    
def convert_dcm_to_nifti(dcm_folder: str) -> str:
    """Convert DCM folder to a NIFTI file."""
    dcm_files = list(Path(dcm_folder).glob('*.dcm'))
    if not dcm_files:
        raise ValueError("No DCM files found in the provided folder: {}".format(dcm_folder))
    
    # Save NIFTI image
    folder_name = Path(dcm_folder).name
    nifti_path = Path(dcm_folder) / f"{folder_name}.nii.gz"
    dicom2nifti.dicom_series_to_nifti(dcm_folder,nifti_path,reorient_nifti=True)
    
    return nifti_path


def generate_dicom_path(input_path: str) -> str:
    """Generate output path based on the input path."""
    path=input_path.replace(".nii.gz","")
    # os.makedirs(path, exist_ok=True)
    return path


def generate_output_path(input_path: str, output_path: str) -> str:
    """Generate output path based on the input path."""
    base_name = os.path.basename(input_path)
    return os.path.join(output_path, base_name)