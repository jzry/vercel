# API Documentation

## (POST) `/bce`

### Request

Receives an image and four corner coordinates.

- **Headers**
    - `Content-Type`: `multipart/form-data`

- **Form**
    - `image`: *\<image data\>*
    - `corners`: *\<JSON\>*

        ```javascript
        [    // An array of four JSON objects
            {
                "x": int,
                "y": int
            }
        ]
        ```

### Response

Returns a JSON object.

___

Status Code **200**

```javascript
{
    "riderData": [{     // An array of JSON objects
        "Rider number": Prediction,
        "Recovery": Prediction,
        "Hydration": Prediction,
        "Lesions": Prediction,
        "Soundness": Prediction,
        "Qual Mvmt": Prediction,
        "Ride time, this rider": Prediction,
        "Weight of this rider": Prediction
    }],
    "riderCount": int   // The length of the array
}

Prediction = {    // A JSON object
    "value": string,
    "confidence": float,    // As a percentage
    "image": string    // A JPEG image encoded as a base64 string
}
```

___

Status Code **400**
- Error uploading image

Status Code **429**
- Rate limit reached

Status Code **444**
- Unsupported or unknown file type

Status Code **445**
- Corrupted or unsafe image file

Status Code **500**
- Internal Server Error

Status Code **555**
- Supported image type not available...

```javascript
{
    "error": string
}
```

## (POST) `/ctr`

### Request

Receives an image and four corner coordinates.

- **Headers**
    - `Content-Type`: `multipart/form-data`

- **Form**
    - `image`: *\<image data\>*
    - `corners`: *\<JSON\>*

        ```javascript
        [    // An array of four JSON objects
            {
                "x": int,
                "y": int
            }
        ]
        ```

### Response

Returns a JSON object.

___

Status Code **200**

```javascript
{
    "riderData": {     // A JSON object
        "Pulse Before Trot Out": Prediction,
        "Pulse After Trot Out": Prediction,
        "Mucous Membrane": Prediction,
        "Capillary Refill": Prediction,
        "Skin Pinch": Prediction,
        "Jugular Vein Refill": Prediction,
        "Gut Sounds": Prediction,
        "Anal Tone": Prediction,
        "Muscle Tone": Prediction,
        "Unwillingness to trot": Prediction,
        "Tendons, Ligaments, Joints, Filings": Prediction,
        "Interferences": Prediction,
        "Grade 1": Prediction,
        "Grade 2": Prediction,
        "Back Tenderness": Prediction,
        "Tack Area": Prediction,
        "Hold on Trail": Prediction,
        "Time Penalty": Prediction
    }
}

Prediction = {    // A JSON object
    "value": string,
    "confidence": float,    // As a percentage
    "image": string    // A JPEG image encoded as a base64 string
}
```

___

Status Code **400**
- Error uploading image

Status Code **429**
- Rate limit reached

Status Code **444**
- Unsupported or unknown file type

Status Code **445**
- Corrupted or unsafe image file

Status Code **500**
- Internal Server Error

Status Code **555**
- Supported image type not available...

```javascript
{
    "error": string
}
```

## (POST) `/corners`

### Request

Receives a single image.

- **Headers**
    - `Content-Type`: `multipart/form-data`

- **Form**
    - `image`: *\<image data\>*

### Response

Returns a JSON object.

___

Status Code **200**

```javascript
{
    "corner_points": [{     // An array of JSON objects
        "x": int,
        "y": int
    }]
}
```

___

Status Code **400**
- Error uploading image

Status Code **429**
- Rate limit reached

Status Code **444**
- Unsupported or unknown file type

Status Code **445**
- Corrupted or unsafe image file

Status Code **500**
- Internal Server Error

Status Code **555**
- Supported image type not available...

```javascript
{
    "error": string
}
```


# Supported Image Formats

- \*.jpeg, \*.jpg
- \*.png
- \*.heic
- \*.bmp
- \*.tif, \*.tiff
- \*.pdf (single page only)
