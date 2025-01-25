import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import '../../styles/CTRHandWritingRecognitionStyles.css';
import GetPhotoBCE from './GetPhotoBCE';

// BCE Component: Handles input collection and navigation to GetPhotoBCE
function BCE() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    numberOfScorecards: '',
    numberOfRiders: '',
    fastestRiderTime: '',
    heaviestRiderWeight: '',
  });

  const [showGetPhotoBCE, setShowGetPhotoBCE] = useState(false);

  // Handles input changes for form fields
  const handleInputChange = (field, event) => {
    setFormData({
      ...formData,
      [field]: event.target.value,
    });
  };

  // Navigates back to the main menu
  const handleGoBack = () => {
    navigate('/');
  }

  // Validates form and navigates to photo upload step
  const handleContinue = () => {
    if (formData.numberOfRiders && formData.heaviestRiderWeight && formData.fastestRiderTime) {
      setShowGetPhotoBCE(true);
    } else {
      alert('Please fill in all fields before continuing.');
    }
  };

  return (
    <div className="bce-container">
      {showGetPhotoBCE ? (
        // Render GetPhotoBCE when user clicks continue
        <GetPhotoBCE
          numberOfRiders={parseInt(formData.numberOfRiders, 10)}
          fastestRiderTime={formData.fastestRiderTime}
          heaviestRiderWeight={parseFloat(formData.heaviestRiderWeight)}
        />
      ) : (
        <>
          <div className="input-group">
            <label>Number of scorecards:</label>
            <input
              type="number"
              value={formData.numberOfScorecards}
              onChange={(e) => handleInputChange('numberOfScorecards', e)}
            />
          </div>

          <div className="input-group">
            <label>Number of riders:</label>
            <input
              type="number"
              value={formData.numberOfRiders}
              onChange={(e) => handleInputChange('numberOfRiders', e)}
            />
          </div>

          <div className="input-group">
            <label>Fastest rider time:</label>
            <input
              type="text"
              placeholder="HMM" // Placeholder to indicate format
              value={formData.fastestRiderTime}
              onChange={(e) => handleInputChange('fastestRiderTime', e)}
            />
          </div>

          <div className="input-group">
            <label>Heaviest rider weight:</label>
            <input
              type="number"
              value={formData.heaviestRiderWeight}
              onChange={(e) => handleInputChange('heaviestRiderWeight', e)}
            />
          </div>

          <div className="button-container">
            <button className="action-button" onClick={handleGoBack}>
              Go back
            </button>
            <button className="action-button" onClick={handleContinue}>
              Continue
            </button>
          </div>
        </>
      )}
    </div>
  );
}

export default BCE;
