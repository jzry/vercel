import React, { useState, useRef } from 'react';
import UploadIcon from "../../images/upload.png";
import BCEExtractedValues from './BCEExtractedValues';
import '../../styles/CTRHandWritingRecognitionStyles.css';
import axios from 'axios';

function GetPhotoBCE({ numberOfRiders, fastestRiderTime, heaviestRiderWeight }) {
  const [imageSrc1, setImageSrc1] = useState(null);
  const [imageSrc2, setImageSrc2] = useState(null);
  const [imageFile1, setImageFile1] = useState(null);
  const [imageFile2, setImageFile2] = useState(null);
  const [extractedDataList, setExtractedDataList] = useState([]);
  const [currentStep, setCurrentStep] = useState(1);
  const [loading, setLoading] = useState(false); // Loading state
  const [backendError, setBackendError] = useState(null); // Error state
  const fileInputRef = useRef(null);
  const apiUrl = process.env.REACT_APP_API_URL;

  const isTwoPhotosRequired = numberOfRiders > 5;

  const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (file) {
      const imageUrl = URL.createObjectURL(file);
      if (currentStep === 1) {
        setImageSrc1(imageUrl);
        setImageFile1(file);
      } else {
        setImageSrc2(imageUrl);
        setImageFile2(file);
      }
    }
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setLoading(true);
    setBackendError(null);

    const formData = new FormData();

    if (imageFile1 && !imageFile2) {
      formData.append('image', imageFile1);
    } else if (imageFile2) {
      formData.append('image', imageFile2);
    } else {
      console.error('No images available to submit');
      setLoading(false);
      return;
    }

    try {
      const response = await axios.post(apiUrl.concat('/bce'), formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });

      if (response.data.error) {
        throw new Error(response.data.error);
      }

      let bceData = [...extractedDataList];
      Object.keys(response.data).forEach((key) => {
        if (bceData.length < numberOfRiders) {
          bceData.push(response.data[key]);
        }
      });

      setExtractedDataList(bceData);

      if (!isTwoPhotosRequired && currentStep === 1) {
        setCurrentStep(3);
      }
    } catch (error) {
      setBackendError(error.message || "An unknown error occurred.");
    } finally {
      setLoading(false);
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
    if (isTwoPhotosRequired && currentStep === 1) {
      setCurrentStep(2);
    } else if (currentStep === 2) {
      setCurrentStep(3);
    }
  };

  const handleGoBackToUpload = () => {
    setCurrentStep(1);
    setImageSrc1(null);
    setImageSrc2(null);
    setImageFile1(null);
    setImageFile2(null);
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
            onGoBackToUpload={handleGoBackToUpload}
            heaviestRiderWeight={heaviestRiderWeight}
            fastestRiderTime={fastestRiderTime}
            numberOfRiders={numberOfRiders}
          />
        </div>
      ) : (
        <>
          {((currentStep === 1 && !imageSrc1) || (isTwoPhotosRequired && currentStep === 2 && !imageSrc2)) ? (
            <div className="button-container">
              <h2>
                {currentStep === 1 ? `Select Scorecard 1` : `Select Scorecard 2`}
              </h2>
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
            <div className="image-fullscreen-container">
              <img src={currentStep === 1 ? imageSrc1 : imageSrc2} alt="Preview" className="image-fullscreen" />
              <div className="action-buttons">
                <button className="scorecard-button" onClick={handleRetakePhoto}>
                  Retake Image
                </button>
                <button className="scorecard-button" onClick={(event) => { handleSubmit(event); handleContinue(); }}>
                  {isTwoPhotosRequired && currentStep === 1 ? "Continue to Scorecard 2" : "Continue"}
                </button>
              </div>
            </div>
          )}
          {backendError && <div className="error-message">{backendError}</div>}
        </>
      )}
    </div>
  );
}

export default GetPhotoBCE;
