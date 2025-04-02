import React, { useState, useRef } from 'react';
import UploadIcon from "../../images/upload.png";
import BCEExtractedValues from './BCEExtractedValues';
import Corners from '../Test/Corners.js';
import '../../styles/CTRHandWritingRecognitionStyles.css';
import axios from 'axios';

function GetPhotoBCE({ numberOfScorecards }) {
  const [imageSrc1, setImageSrc1] = useState(null);
  const [imageSrc2, setImageSrc2] = useState(null);
  const [imageFile1, setImageFile1] = useState(null);
  const [imageFile2, setImageFile2] = useState(null);
  const [extractedDataList, setExtractedDataList] = useState([]);
  const [currentStep, setCurrentStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [backendError, setBackendError] = useState(null);
  const [showCorners, setShowCorners] = useState(false);
  const apiUrl = process.env.REACT_APP_API_URL;

  const isTwoPhotosRequired = (numberOfScorecards > 1);

  const [isRotated1, setIsRotated1] = useState(false);
  const [isRotated2, setIsRotated2] = useState(false);


  // const handleFileChange = (event) => {
  //   const file = event.target.files[0];
  //   if (file) {
  //     const imageUrl = URL.createObjectURL(file);
  //     if (currentStep === 1) {
  //       setImageSrc1(imageUrl);
  //       setImageFile1(file);
  //     } else {
  //       setImageSrc2(imageUrl);
  //       setImageFile2(file);
  //     }
  //   }
  // };

  const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (file) {
      const imageUrl = URL.createObjectURL(file);
      const img = new Image();
      img.src = imageUrl;
      img.onload = () => {
        const isLandscape = img.width > img.height;
        if (currentStep === 1) {
          setImageSrc1(imageUrl);
          setImageFile1(file);
          setIsRotated1(isLandscape);
        } else {
          setImageSrc2(imageUrl);
          setImageFile2(file);
          setIsRotated2(isLandscape);
        }
      };
    }
  };

  const handleRetakePhoto = () => {
    if (currentStep === 1) {
      setImageSrc1(null);
      setImageFile1(null);
    } else {
      setImageSrc2(null);
      setImageFile2(null);
    }
  };

  const handleContinue = () => {
    setShowCorners(true);
  };


  const handleCornersSubmit = (processedData) => {
    // console.log("Raw Processed Data:", processedData);

    // Check if processedData contains the correct structure
    if (processedData && processedData.riderData) {
        const riderDataArray = processedData.riderData; // Extracting array
        console.log("Extracted Rider Data:", riderDataArray);

        // Ensure it's an array before spreading
        if (Array.isArray(riderDataArray)) {
            setExtractedDataList((prevData) => [...prevData, ...riderDataArray]);
        }
    } else {
        console.error("Unexpected processedData format:", processedData);
    }

    setShowCorners(false);

    if (isTwoPhotosRequired && currentStep === 1) {
        setCurrentStep(2);
    } else {
        setCurrentStep(3);
    }
};



  return (
    <div className="App">
      {loading && (
        <div className="loading-overlay">
          <div className="spinner"></div>
        </div>
      )}
      {currentStep === 3 ? (
        <div className="bce-results-container">
          <BCEExtractedValues
            extractedDataList={extractedDataList}
            onGoBackToUpload={() => setCurrentStep(1)}
          />
        </div>
      ) : showCorners ? (
        <Corners
          imageSrc={currentStep === 1 ? imageSrc1 : imageSrc2}
          imageFile={currentStep === 1 ? imageFile1 : imageFile2}
          onSubmitCorners={handleCornersSubmit}
          mode={'bce'}
        />
      ) : (
        <>
          {((currentStep === 1 && !imageSrc1) || (isTwoPhotosRequired && currentStep === 2 && !imageSrc2)) ? (
            <div className="button-container">
              <h2>{currentStep === 1 ? `Upload Scorecard 1` : `Upload Scorecard 2`}</h2>
              <div className="icon-button">
                <input
                  type="file"
                  accept="image/*"
                  onChange={handleFileChange}
                  style={{ display: 'none' }}
                  id="upload-image"
                />
                <label htmlFor="upload-image" className="icon-button">
                  <img src={UploadIcon} alt="upload icon" />
                  <p>Upload an image</p>
                </label>
              </div>
            </div>
          ) : (
            <>
            <div className="image-fullscreen-container">
              <img
                src={currentStep === 1 ? imageSrc1 : imageSrc2}
                alt="Preview"
                className={`image-fullscreen ${currentStep === 1 ? (isRotated1 ? "rotated" : "") : (isRotated2 ? "rotated" : "")}`}
                // style={{
                //   width: "95vw",  // 🔹 Fill most of the screen width
                //   height: "auto",  // 🔹 Maintain aspect ratio
                //   maxWidth: "100%",
                //   maxHeight: "80vh", // 🔹 Prevent going out of bounds
                //   objectFit: "contain",
                //   display: "block",
                //   margin: "0 auto 20px auto",  // 🔹 Adds space below the image
                //   borderRadius: "10px",
                //   boxShadow: "0px 4px 8px rgba(0,0,0,0.2)",
                // }}
              />
            </div>

            <div className="action-buttons">
              <button className="scorecard-button" onClick={handleRetakePhoto}>
                Retake Image
              </button>
              <button className="scorecard-button" onClick={handleContinue}>
                {isTwoPhotosRequired && currentStep === 1 ? "Continue to Scorecard 2" : "Continue"}
              </button>
            </div>
            </>
          )}
          {backendError && <div className="error-message">{backendError}</div>}
        </>
      )}
    </div>
  );
}

export default GetPhotoBCE;
