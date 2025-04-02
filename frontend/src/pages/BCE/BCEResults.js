import React from 'react';
import '../../styles/CTRHandWritingRecognitionStyles.css';

// Calculates and displays final scores for each rider
function BCEResults({ extractedDataList }) {

  // Calculates the veterinary score for a rider
  const calculateVeterinaryScore = (data) => {
    const { Recovery, Hydration, Lesions, Soundness, 'Qual Mvmt': QualMvmt } = data;
    return (parseFloat(Recovery.value, 10) + parseFloat(Hydration.value, 10) + parseFloat(Lesions.value, 10) + parseFloat(Soundness.value, 10) + parseFloat(QualMvmt.value, 10)) * 10;
  };

  // Finds the weight of the heaviest rider
  const findHeaviestWeight = () => {
    let heaviestWeight = 0;
    extractedDataList.forEach((rider) => {
      let riderWeight = parseInt(rider['Weight of this rider'].value, 10);
      if (riderWeight > heaviestWeight) heaviestWeight = riderWeight;
    });
    console.log(`Max weight: ${heaviestWeight}`);
    return heaviestWeight;
  };

  // Finds the time of the fastest rider
  const findFastestTime = () => {
    let fastestTime = 9999;
    extractedDataList.forEach((rider) => {
      let riderTime = parseInt(rider['Ride time, this rider'].value, 10);
      if (riderTime < fastestTime) fastestTime = riderTime;
    });
    console.log(`Fastest time: ${fastestTime}`);
    return fastestTime;
  };


  // The heaviest weight and fastest time for score calculations
  const heaviestRiderWeight = findHeaviestWeight()
  const fastestRiderTime = findFastestTime()

  // Calculates the weight score for a rider
  const calculateWeightScore = (weight) => {
    return 100 - (heaviestRiderWeight - weight) / 2;
  };

  // Calculates the weight score for a rider
  const calculateTimeScore = (rideTime) => {
    // Convert the three-digit time values to hours and minutes format if necessary
    const fastestTimeInMinutes = convertToMinutes(fastestRiderTime);
    const rideTimeInMinutes = convertToMinutes(rideTime);

    // Calculate time score
    return 200 - (rideTimeInMinutes - fastestTimeInMinutes);
  };

  // Converts time from HMM format to minutes
  const convertToMinutes = (time) => {
    // Convert time to hours and minutes format
    const hours = Math.floor(time / 100);
    const minutes = time % 100;
    return hours * 60 + minutes;
  };

  return (
    <div className="result-container">
      {extractedDataList.map((data, index) => {
        const totalVeterinaryScore = calculateVeterinaryScore(data);
        const totalWeightScore = calculateWeightScore(parseInt(data['Weight of this rider'].value, 10));
        const totalTimeScore = calculateTimeScore(parseInt(data['Ride time, this rider'].value, 10));

        return (
          <div key={index} className="bce-result">
            <div className = "row-container">
              <div className="row">
                <div className="column left">
                <h4>Rider number:</h4>
                </div>
                <div className="column right">
                  <h4>{data['Rider number'].value}</h4>
                </div>
              </div>
            </div>
            <div className = "row-container">
              <div className="row">
                <div className="column left">
                <p>Total Veterinary Score:</p>
                </div>
                <div className="column right">
                  <p>{totalVeterinaryScore}</p>
                </div>
              </div>
            </div>
            <div className = "row-container">
              <div className="row">
                <div className="column left">
                  <p>Total Time Score:</p>
                </div>              
                <div className="column right">
                  <p>{totalTimeScore}</p>
                </div>
              </div>
            </div>
            <div className = "row-container">
              <div className="row">
                <div className="column left">
                  <p>Total Weight Score: </p>
                </div>
                <div className="column right">
                  <p>{totalWeightScore}</p>
                </div>
              </div>
            </div>
            <div className = "row-container">
              <div className="row">
                <div className="column left">
                  <p>Total Score:</p>
                </div>
                <div className="column right">
                  <p>{totalVeterinaryScore + totalWeightScore + totalTimeScore}</p>
                </div>
              </div>
            </div>
          </div>
        );
      })}
      <div className="button-container">
        <button className="action-button" onClick={() => window.location.reload()}>Calculate New Score</button>
      </div>
    </div>
  );
}

export default BCEResults;
