import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import '../../styles/CTRHandWritingRecognitionStyles.css';
import GetPhotoBCE from './GetPhotoBCE';

// BCE Component: Handles input collection and navigation to GetPhotoBCE
function BCE() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    numberOfScorecards: '',
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
    if (formData.numberOfScorecards) {
      setShowGetPhotoBCE(true);
    } else {
      alert('Please fill in all fields before continuing.');
    }
  };

  return (
    <>
      <div className="bce-container">
        {showGetPhotoBCE ? (
          // Render GetPhotoBCE when user clicks continue
          <GetPhotoBCE
            numberOfScorecards={parseInt(formData.numberOfScorecards, 10)}
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
    </>
  );
}

export default BCE;
