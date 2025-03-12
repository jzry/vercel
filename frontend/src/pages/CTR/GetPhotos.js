import React, { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import UploadIcon from "../../images/upload.png";
import CTRExtractedValues from './CTRExtractedValues.js';
import Corners from '../Test/Corners.js';
import '../../styles/CTRHandWritingRecognitionStyles.css';

function GetPhotos() {
  const [imageSrc, setImageSrc] = useState(null); // State to store the captured image
  const [imageFile, setImageFile] = useState(null); // State to store the image file for API
  const [extractedData, setExtractedData] = useState(null); // State to store extracted values from API
  const [loading, setLoading] = useState(false); // Loading state
  const [backendError, setBackendError] = useState(null); // Error state
    const [showCorners, setShowCorners] = useState(false);
  const fileInputRef = useRef(null); 
  const navigate = useNavigate();
  const apiUrl = process.env.REACT_APP_API_URL;

  // Handles file selection for uploading an image
  const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (file) {
      setImageSrc(URL.createObjectURL(file)); // Show the uploaded image
      setImageFile(file); // Store the image file for API submission
    }
  };

  // Clears the current image and allows retaking
  const handleRetakePhoto = () => {
    setImageSrc(null); // Clear the image preview
    setImageFile(null); // Clear the image file
  };

  // Submits the uploaded image to the backend
  const handleSubmit = async (event) => {
    event.preventDefault();
    setLoading(true); // Show loading spinner
    setBackendError(null); // Reset any previous errors

    if (imageFile) {
      const formData = new FormData();
      formData.append('image', imageFile);

      try {
        const response = await axios.post(apiUrl.concat('/ctr'), formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });

        if (response.data.error) {
          throw new Error(response.data.error);
        }

        console.log("Data Retrieved:", response.data);
        setExtractedData(response.data);
      } catch (error) {
        console.error('Error uploading file:', error);
        setBackendError(error.message || "An unknown error occurred.");
      } finally {
        setLoading(false); // Hide loading spinner
      }
    } else {
      console.error("No image to upload.");
      setLoading(false); // Hide loading spinner
    }
  };

  const handleGoBack = () => {
    navigate('/'); // Redirect to the home page
  };

  const handleContinue = () => {
    setShowCorners(true);
  };

  const handleCornersSubmit = (processedData) => {
    // console.log("Raw Processed Data:", processedData);

    // Check if processedData contains the correct structure


    setShowCorners(false);

    setExtractedData(processedData)
};


  return (
    <div className="App">
      {/* Show loading spinner */}
      {loading && (
        <div className="loading-overlay">
          <div className="spinner"></div>
        </div>
      )}

      {extractedData ? (
        <CTRExtractedValues extractedData={extractedData} />
      ) : showCorners ? (
        <Corners
          imageSrc={imageSrc}
          imageFile={imageFile}
          onSubmitCorners={handleCornersSubmit}
          mode={'ctr'}
        />
      ) : (
        !imageSrc ? (
          <div className="button-container">
            <input
              type="file"
              accept="image/*"
              capture="environment"
              ref={fileInputRef}
              onChange={handleFileChange}
              style={{ display: 'none' }}
            />
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
              <button className="go-back-button" onClick={handleGoBack}>Go Back</button>
            </div>
          </div>
        ) : (
          <div className="image-fullscreen-container">
            <img src={imageSrc} alt="Preview" className="image-fullscreen" />
            <div className="action-buttons">
              <button className="scorecard-button" onClick={handleRetakePhoto}>
                Retake Image
              </button>
              <button className="scorecard-button" onClick={handleContinue}>
                Continue
              </button>
            </div>
          </div>
        )
      )}

      {/* Show backend error message */}
      {backendError && <div className="error-message">{backendError}</div>}
    </div>
  );
}

export default GetPhotos;
