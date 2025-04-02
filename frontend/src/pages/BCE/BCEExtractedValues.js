import React, { useState, useEffect } from 'react';
import BCEResults from './BCEResults';
import '../../styles/CTRHandWritingRecognitionStyles.css';

// Displays and edits extracted data for each rider
function BCEExtractedValues({ extractedDataList, onGoBackToUpload }) {
  const [currentRiderIndex, setCurrentRiderIndex] = useState(0); // Index to track the current rider
  const [data, setData] = useState({ ...extractedDataList[currentRiderIndex] }); // Initialize with the first rider's data
  const [step, setStep] = useState(1); // Tracks the current step (1: edit, 2: go back/calculate, 3: show score)
  const [showResults, setShowResults] = useState(false); // State to determine if we should show BCEResults

  // Updates component state when the current rider index changes
  useEffect(() => {
    if (extractedDataList[currentRiderIndex]) {
      setData({ ...extractedDataList[currentRiderIndex] });
    }
  }, [currentRiderIndex, extractedDataList]);

  // Updates the input value for a specific key
  const handleInputChange = (key, event) => {
    const newValue = event.target.value;
    setData(prevData => {
      const updatedData = {
        ...prevData,
        [key]: { ...prevData[key], value: newValue }, // Keep the value as string until final submission
      };
      // Update extractedDataList with the new value
      extractedDataList[currentRiderIndex] = updatedData;
      return updatedData;
    });
  };

  const getBorderColor = (confidence) => {
    if (confidence >= 95.0) return 'green';
    if (confidence >= 85.0) return 'gold';
    return 'red';
  };

  // Determines the border style based on confidence level
  const getBorderStyle = (confidence) => {
    if (confidence >= 95.0) return 'solid';
    if (confidence >= 85.0) return 'dashed';
    return 'dotted';
  };
  
  // concatenates the base64 string from the API with the needed info to read as an image
  const newSrc = (source) => {
    return "data:image;base64,"+source;
  }

  // Determines the border color based on confidence level
  const handleCalculateScore = () => {
    setShowResults(true); // Show the results after calculation
  };

  // Returns to the previous step or rider
  const handleGoBack = () => {
    if (step === 2) {
      setStep(1); // Go back to editing the current rider
    } else if (currentRiderIndex > 0) {
      setCurrentRiderIndex(currentRiderIndex - 1);
      setStep(1);
    } else {
      onGoBackToUpload();
    }
  };

  // Proceeds to the next rider or calculation step
  const handleContinue = () => {
    if (currentRiderIndex < extractedDataList.length - 1) {
      setCurrentRiderIndex(currentRiderIndex + 1);
      setStep(1);
    } else {
      setStep(2);
    }
  };

  if (showResults) {
    return <BCEResults extractedDataList={extractedDataList} />;
  }


  return (
    <div className="container">
      {step === 1 && (
        <div>
          <h3>Rider {currentRiderIndex + 1}</h3>
          {data && Object.keys(data).map((key, index) => (
            <div key={index} className="input-group">
              <label>{key}:</label>
              <input
                type="text"
                value={data[key].value || ""}
                onChange={(event) => handleInputChange(key, event)}
                style={{
                  borderColor: getBorderColor(data[key].confidence),
                  borderStyle: getBorderStyle(data[key].confidence),
                }}
              />
              <div className = "crop">
                <img src={newSrc(data[key].image)} alt="segments"/>
              </div>
            </div>
          ))}
          <div className="button-container">
            <button className="action-button" onClick={handleGoBack}>
              Go Back
            </button>
            <button className="submit-button" onClick={handleContinue}>
              Continue
            </button>
          </div>
        </div>
      )}

      {step === 2 && (
        <div className="result-container">
          <p>Would you like to continue editing or calculate your score?</p>
          <div className="button-container">
            <button className="action-button" onClick={handleGoBack}>
              Go Back
            </button>
            <button className="action-button" onClick={handleCalculateScore}>
              Calculate Score
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export default BCEExtractedValues;
