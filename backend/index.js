require('dotenv').config({ path: '../process.env' });
const express = require('express');
const fileUpload = require('express-fileupload')
const cors = require('cors');
const cookieParser = require('cookie-parser')
const path = require('path')
const rateLimit = require('express-rate-limit')
const morgan = require('morgan')
const pyconnect = require('./pyconnect')

const devMode = process.env.MODE
const corsOrigin = (process.env.ORIGIN) ? process.env.ORIGIN : '*'

// A flag that determines if TorchServe is used or not
const torchserveFlag = (process.env.TORCHSERVE) ? process.env.TORCHSERVE.toLowerCase() === 'torchserve' : false


// Middleware function to validate the image input by the user
function validateImage(req, res, next) {
  const allowedFileTypes = [
    'image/jpeg',
    'image/png',
    'image/heic',
    'image/bmp',
    'image/tiff',
    'application/pdf'
  ];
  const maxSize = 10; // limit in mebibytes
  const maxSizeBytes = maxSize * 1024 * 1024;

  // Check if file exists
  if (!req.files || !req.files.image) {
    let errorMessage = 'No file uploaded'
    console.warn(errorMessage)
    return res.status(400).json({'error': errorMessage});
  }

  const image = req.files.image;

  // Check file size
  if (image.size > maxSizeBytes) {
    let errorMessage = `File size exceeds limit of ${maxSize} MiB`
    console.warn(errorMessage)
    return res.status(400).json({'error': errorMessage});
  }

  // Check file type
  if (!allowedFileTypes.includes(image.mimetype)) {
    let errorMessage = 'File type is not supported.'
    console.warn(errorMessage)
    return res.status(400).json({'error': errorMessage});
  }

  // If all checks pass, proceed
  next();
}


// Middleware function to validate the corner input by the user
function validateCorners(req, res, next) {

  if (req.body && req.body.corners)
  {
    try
    {
      if (typeof req.body.corners !== 'string')
      {
        throw 'req.body.corners is not a JSON string'
      }

      var corners = JSON.parse(req.body.corners)
    }
    catch (e)
    {
      console.error(e)
      res.status(400).json({'error': 'Corner data is not valid JSON'})
      return
    }

    req.corner_points = corners
  }

  // If all checks pass, proceed
  next();
}


// The express app
const app = express();

// Allow cross-origin resource sharing for our react development build
if (devMode === 'development') {
  // Configure API logging
  app.use(morgan('[:date] :method :url', { immediate: true}))
}
else if (devMode === 'production') {
  // Serve static frontend
  app.use(express.static(path.join(__dirname, '../frontend/build')))
  app.get('/*', (req, res) => {
    res.sendFile(path.join(__dirname, '../frontend/build', 'index.html'));
  })

  // Configure API logging
  app.use(morgan('[:date] :remote-addr (:status) :method :url (:response-time ms)'))
}
else {
  throw `Error: "${devMode}" is not a valid MODE - see ENV.md`
}

// Configure CORS requests
const corsOptions = {
  origin: corsOrigin,
  optionsSuccessStatus: 200,
};
app.use(cors(corsOptions))

// Use cookie parser
app.use(cookieParser())

// Use express-fileupload
app.use(fileUpload())



// Configure API rate limiting
const limiter = rateLimit({
  windowMs: 10 * 1000,   // 10 seconds
  max: 8,                // Limit each IP to 8 requests per 'window'
  standardHeaders: true, // Return rate limit info in the 'RateLimit-*' headers
  legacyHeaders: false,  // Disable the 'X-RateLimit-*' headers
})

app.use(limiter)


// Retrieve the uploaded image from the handleSubmit function in frontend/src/pages/crt/getPhotos.js

app.post('/ctr', validateImage, validateCorners, async (req, res) => {
  // The name of the input field (i.e. "sampleFile") is used to retrieve the uploaded file
  let sampleFile = req.files.image;

  //console.log('File received:', sampleFile.name);  // Log file details

  let args = { "torchserve": torchserveFlag }

  if (req.corner_points)
    args.corner_points = req.corner_points

  // Send the image to the Python code to be processed
  let output = await pyconnect.run('CTR.py', args, sampleFile)

  res.status(output.status).json(output.body)
});

app.post('/bce', validateImage, validateCorners, async (req, res) => {
  // The name of the input field (i.e. "sampleFile") is used to retrieve the uploaded file
  let sampleFile = req.files.image;

  //console.log('File received:', sampleFile.name);  // Log file details

  let args = { "torchserve": torchserveFlag }

  if (req.corner_points)
    args.corner_points = req.corner_points

  // Send the image to the Python code to be processed
  let output = await pyconnect.run('BCE.py', args, sampleFile)

  res.status(output.status).json(output.body)
});


app.post('/corners', validateImage, async (req, res) => {
  // The name of the input field (i.e. "imageFile") is used to retrieve the uploaded file
  let imageFile = req.files.image;

  // Send the image to the Python code to be processed
  let output = await pyconnect.run('corners.py', null, imageFile)

  res.status(output.status).json(output.body)
});


module.exports = app
