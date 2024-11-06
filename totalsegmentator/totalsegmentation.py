from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse
import zipfile
import os 
import sys
from inference import inference
import shutil
from glob import glob


# FastAPI 인스턴스 생성
app = FastAPI()



# POST 요청으로 하나의 ZIP 파일을 업로드하고 처리
@app.post("/process-dicom/")
async def process_dicom(file: UploadFile = File(...)):
    save_directory = "./uploaded_files"
    result_directory = "./results"  
    result_directory = os.path.join(result_directory, file.filename.replace(".zip", ""))

    save_dirs = os.path.join(save_directory, file.filename.replace(".zip", ""))
    os.makedirs(save_dirs, exist_ok=True)
    file_path = os.path.join(save_dirs, file.filename)
    print(file.filename)

    # 파일을 지정된 경로에 저장
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # ZIP 파일을 추출
    with zipfile.ZipFile(file_path, "r") as zip_file:
        zip_file.extractall(save_dirs)
    os.remove(file_path)  # 원본 ZIP 파일은 삭제
    dcm_dir=os.path.join(save_dirs, file.filename.replace(".zip", ""))
    # 추출된 파일에 대해 inference 수행 (경로 수정 필요)
    inference(dcm_dir, result_directory)

    # 결과 파일 중 하나를 선택하여 반환
    result_path = glob(result_directory + "/*.dcm")[0]


    shutil.rmtree(save_dirs,)
    # shutil.rmtree(result_directory)
    # 결과 파일을 클라이언트로 전송
    return FileResponse(path=result_path, media_type="application/dicom", filename=os.path.basename(result_path))


# # FastAPI 애플리케이션 실행 (이 코드는 파일을 직접 실행할 때만 작동합니다)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
