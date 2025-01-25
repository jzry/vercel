require('dotenv').config({ path: '../process.env' });
const express = require('express');
const fileUpload = require('express-fileupload')
const cors = require('cors');
const cookieParser = require('cookie-parser')
const path = require('path')
const rateLimit = require('express-rate-limit')
const pyconnect = require('./pyconnect')

const devMode = process.env.MODE


// Request validation middleware for the CTR data from the OCR
// Because the CTR data is not currently sourced from an api endpoint, this function only simulates the functionality of Express Middleware
function validateData(/*req, res, next*/ fakeCTRData) {
  let req = { body: fakeCTRData }
  if (typeof req.body !== 'object' || req.body === null) {
    return res.status(400).json({ error: 'Invalid JSON object in request body.' });
  }

  for (const key in req.body) {
    const item = req.body[key];

    // Check if item is an object with "value" and "confidence" keys
    if (
      typeof item !== 'object' ||
      item === null ||
      !('value' in item) ||
      !('confidence' in item)
    ) {
      return res.status(400).json({ error: `Invalid format for key "${key}". Each value should contain "value" and "confidence" fields.` });
    }

    // Validate that the request
    if (!Number.isInteger(item.value)) {
      return res.status(400).json({ error: `Invalid value for "${key}". "value" must be an integer.` });
    }
    if (typeof item.confidence !== 'number' || item.confidence < 0 || item.confidence > 1) {
      return res.status(400).json({ error: `Invalid confidence for "${key}". "confidence" must be a float between 0 and 1.` });
    }
  }

  return

  // If all validations pass, proceed
  // next();
}

// Middleware function to validate the image input by the user
function validateImage(req, res, next) {
  const allowedFileTypes = ['image/jpeg', 'image/png'];
  const maxSize = 5 * 1024 * 1024; // 5 MB limit

  // Check if file exists
  if (!req.files || !req.files.image) {
    console.log('No file uploaded.')
    return res.status(400).send('No file uploaded.');
  }

  const image = req.files.image;

  // Check file size
  if (image.size > maxSize) {
    console.log('File size exceeds limit of 5 MB.')
    return res.status(400).send('File size exceeds limit of 5 MB.');
  }

  // Check file type
  if (!allowedFileTypes.includes(image.mimetype)) {
    console.log('Invalid file type. Only JPEG, PNG allowed.')
    return res.status(400).send('Invalid file type. Only JPEG, PNG allowed.');
  }

  // If all checks pass, proceed
  next();
}

// Cross-Origin Resource Sharing Middleware to only accept data originating from our frontend



// The express app
const app = express();

// Allow cross-origin resource sharing for our react development build
if (devMode === 'development') {
  const corsOptions = {
    origin: '*',
    optionsSuccessStatus: 200,
  };
  app.use(cors(corsOptions))
}

if (devMode === 'production') {
  app.use(express.static(path.join(__dirname, '../frontend/build')))

  app.get('/*', (req, res) => {
    res.sendFile(path.join(__dirname, '../frontend/build', 'index.html'));
  })
}

// Use cookie parser
app.use(cookieParser())

// Use express-fileupload
app.use(fileUpload())



// Configure API rate limiting
const limiter = rateLimit({
  windowMs: 20 * 1000,   // 20 seconds
  max: 4,                // Limit each IP to 4 requests per 'window'
  standardHeaders: true, // Return rate limit info in the 'RateLimit-*' headers
  legacyHeaders: false,  // Disable the 'X-RateLimit-*' headers
})

app.use(limiter)



function apiHitLogger(req, res, next)
{
    let timestamp = new Date()

    console.log(`${timestamp}\t| ${req.ip}\t| ${req.url}`)

    next()
}

app.use(apiHitLogger)


// Retrieve the uploaded image from the handleSubmit function in frontend/src/pages/crt/getPhotos.js

app.post('/ctr', validateImage, async (req, res) => {
  if (!req.files || Object.keys(req.files).length === 0) {
    return res.status(400).send('No files were uploaded.');
  }

  // The name of the input field (i.e. "sampleFile") is used to retrieve the uploaded file
  let sampleFile = req.files.image;

  //console.log('File received:', sampleFile.name);  // Log file details

  // Send the image to the Python code to be processed
  let output = await pyconnect.processCTR(sampleFile)

  if (output.error)
    res.status(500)

  res.json(output)
});

app.post('/bce', validateImage, async (req, res) => {
  if (!req.files || Object.keys(req.files).length === 0) {
    return res.status(400).send('No files were uploaded.');
  }

  // The name of the input field (i.e. "sampleFile") is used to retrieve the uploaded file
  let sampleFile = req.files.image;

  //console.log('File received:', sampleFile.name);  // Log file details

  // Send the image to the Python code to be processed
  let output = await pyconnect.processBCE(sampleFile)

  if (output.error)
    res.status(500)

  res.json(output)
});


module.exports = app
